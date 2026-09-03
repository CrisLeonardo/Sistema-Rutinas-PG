"""Prueba de carga del sistema (requerimiento no funcional 4.5.2).

El apartado 4.5.2 exige que el sistema soporte cincuenta usuarios concurrentes
sin degradar su tiempo de respuesta, que el plan completo se genere en menos de
tres segundos y que las pantallas carguen en menos de dos.

    uv run python prueba_de_carga.py
    uv run python prueba_de_carga.py --usuarios 50 --url http://127.0.0.1:8010

La prueba tiene dos fases. La primera prepara las cuentas y los perfiles, y no se
mide: crear cincuenta cuentas en el mismo instante satura la funcion de cifrado
de contrasenas, que es deliberadamente costosa, y produciria un numero que no
describe ningun escenario real. La segunda somete al sistema a las operaciones de
uso —generar el plan, consultar la rutina y el menu, registrar el avance y ver el
reporte— con todos los usuarios a la vez, que es lo que el requerimiento describe.

**Sobre la base de datos.** La medicion es valida solo contra el gestor que se
usara en produccion. PostgreSQL admite escrituras concurrentes; SQLite las serializa
y, con cincuenta usuarios simultaneos, devuelve errores de bloqueo que no
provienen del sistema sino del gestor. Antes de dar por verificado el
requerimiento, ejecute esta prueba contra el entorno de pruebas, que levanta
PostgreSQL en contenedor, o contra el sistema ya publicado en Render.

Se escribe con `httpx`, que ya es dependencia de las pruebas, para no incorporar
una herramienta de carga solo para esto.
"""

import argparse
import asyncio
import statistics
import sys
import time
from dataclasses import dataclass, field

import httpx

# Umbrales del apartado 4.5.2. El plan es la operacion mas costosa porque
# invoca el modelo neuronal; el resto son consultas de pantalla.
LIMITE_PLAN_SEGUNDOS = 3.0
LIMITE_PANTALLA_SEGUNDOS = 2.0

# Los perfiles se varian a proposito. Si todos los usuarios simulados tuvieran
# las mismas medidas, la memoria de planes recientes acertaria siempre y la
# medicion diria que el sistema es mas rapido de lo que es.
SEXOS = ("masculino", "femenino")
NIVELES_ACTIVIDAD = ("sedentario", "ligero", "moderado", "alto", "muy_alto")
OBJETIVOS = ("perdida_grasa", "mantenimiento", "ganancia_muscular")
NIVELES_EXPERIENCIA = ("principiante", "intermedio", "avanzado")


def perfil_de(numero: int) -> dict:
    """Construye un perfil distinto para cada usuario simulado."""
    return {
        "peso_kg": 55.0 + (numero * 1.3) % 60,
        "estatura_cm": 150.0 + (numero * 2.1) % 40,
        "edad": 18 + (numero * 3) % 50,
        "sexo": SEXOS[numero % len(SEXOS)],
        "nivel_actividad": NIVELES_ACTIVIDAD[numero % len(NIVELES_ACTIVIDAD)],
        "objetivo": OBJETIVOS[numero % len(OBJETIVOS)],
        "nivel_experiencia": NIVELES_EXPERIENCIA[numero % len(NIVELES_EXPERIENCIA)],
        "dias_entrenamiento_semana": 3 + numero % 4,
    }


@dataclass
class Medicion:
    """Tiempos observados para una operacion."""

    nombre: str
    limite_segundos: float
    tiempos: list[float] = field(default_factory=list)
    fallos: int = 0

    @property
    def promedio(self) -> float:
        return statistics.mean(self.tiempos) if self.tiempos else 0.0

    @property
    def mediana(self) -> float:
        return statistics.median(self.tiempos) if self.tiempos else 0.0

    @property
    def percentil_95(self) -> float:
        """Tiempo que no supera el 95 % de las peticiones.

        Es la cifra que importa: el promedio esconde a los usuarios que peor la
        pasaron, y son ellos los que abandonan el sistema.
        """
        if not self.tiempos:
            return 0.0
        ordenados = sorted(self.tiempos)
        posicion = max(int(len(ordenados) * 0.95) - 1, 0)
        return ordenados[posicion]

    @property
    def maximo(self) -> float:
        return max(self.tiempos) if self.tiempos else 0.0

    @property
    def cumple(self) -> bool:
        """Una operacion sin mediciones no cumple: no llego a ejecutarse.

        Sin esta condicion, un recorrido que se interrumpe antes de tiempo
        dejaria las operaciones siguientes con la lista vacia y el informe las
        daria por buenas.
        """
        if not self.tiempos:
            return False
        return self.fallos == 0 and self.percentil_95 <= self.limite_segundos


async def _medir(medicion: Medicion, corrutina) -> httpx.Response | None:
    """Ejecuta una peticion y registra cuanto tardo."""
    inicio = time.perf_counter()
    try:
        respuesta = await corrutina
    except Exception:  # pragma: no cover - depende del sistema bajo prueba
        medicion.fallos += 1
        return None

    transcurrido = time.perf_counter() - inicio
    if respuesta.status_code >= 400:
        medicion.fallos += 1
        return respuesta

    medicion.tiempos.append(transcurrido)
    return respuesta


async def _preparar_usuario(
    cliente: httpx.AsyncClient, numero: int
) -> dict[str, str] | None:
    """Crea la cuenta y el perfil de un usuario. No se mide.

    Devuelve los encabezados de sesion, o None si la preparacion fallo.
    """
    # El dominio debe ser uno que el validador de correo acepte: los reservados
    # como .local se rechazan, igual que en el registro real.
    credenciales = {
        "correo": f"carga{numero}@pruebadecarga.gt",
        "contrasena": "PruebaCarga2026",
    }

    try:
        await cliente.post(
            "/api/v1/autenticacion/registro",
            json={**credenciales, "nombre": f"Usuario de carga {numero}"},
        )
        respuesta = await cliente.post("/api/v1/autenticacion/acceso", json=credenciales)
        if respuesta.status_code >= 400:
            return None

        encabezados = {"Authorization": f"Bearer {respuesta.json()['token_acceso']}"}
        perfil = await cliente.post(
            "/api/v1/perfil-biometrico", json=perfil_de(numero), headers=encabezados
        )
        if perfil.status_code >= 400:
            return None
    except Exception:  # pragma: no cover - depende del sistema bajo prueba
        return None

    return encabezados


async def _uso_concurrente(
    cliente: httpx.AsyncClient, encabezados: dict[str, str], mediciones: dict[str, Medicion]
) -> None:
    """Recorre las operaciones de uso del sistema. Esta fase si se mide."""
    await _medir(
        mediciones["plan"], cliente.post("/api/v1/plan-nutricional", headers=encabezados)
    )
    await _medir(mediciones["rutina"], cliente.get("/api/v1/rutina", headers=encabezados))
    await _medir(
        mediciones["menu"], cliente.get("/api/v1/plan-nutricional/menu", headers=encabezados)
    )
    await _medir(
        mediciones["progreso"],
        cliente.post(
            "/api/v1/progreso",
            json={"peso_kg": 77.0, "sesiones_cumplidas": 4, "adherencia_nutricional": 90},
            headers=encabezados,
        ),
    )
    await _medir(
        mediciones["reporte"], cliente.get("/api/v1/progreso/reporte", headers=encabezados)
    )
    await _medir(
        mediciones["perfil"],
        cliente.get("/api/v1/perfil-biometrico/historial", headers=encabezados),
    )


async def ejecutar(url_base: str, usuarios: int) -> tuple[dict[str, Medicion], int]:
    """Prepara las cuentas y despues somete al sistema a la carga concurrente."""
    mediciones = {
        "plan": Medicion("Generación del plan", LIMITE_PLAN_SEGUNDOS),
        "rutina": Medicion("Consulta de la rutina", LIMITE_PANTALLA_SEGUNDOS),
        "menu": Medicion("Consulta del menú", LIMITE_PANTALLA_SEGUNDOS),
        "progreso": Medicion("Registro de progreso", LIMITE_PLAN_SEGUNDOS),
        "reporte": Medicion("Reporte de evolución", LIMITE_PANTALLA_SEGUNDOS),
        "perfil": Medicion("Historial de medidas", LIMITE_PANTALLA_SEGUNDOS),
    }

    limites = httpx.Limits(max_connections=usuarios * 2, max_keepalive_connections=usuarios)
    async with httpx.AsyncClient(base_url=url_base, timeout=60.0, limits=limites) as cliente:
        # Se comprueba primero que el sistema responde, para no confundir un
        # servicio caído con un problema de rendimiento.
        try:
            estado = await cliente.get("/api/v1/estado")
            estado.raise_for_status()
        except Exception as error:
            raise SystemExit(
                f"El sistema no responde en {url_base}. Levántelo antes de medir. ({error})"
            ) from error

        print(f"Preparando {usuarios} cuentas…")
        # La preparación va en lotes pequeños: crear cincuenta cuentas de golpe
        # satura la función de cifrado y hace fallar la propia preparación.
        sesiones: list[dict[str, str]] = []
        tamanio_lote = 10
        for principio in range(0, usuarios, tamanio_lote):
            lote = range(principio, min(principio + tamanio_lote, usuarios))
            resultados = await asyncio.gather(
                *(_preparar_usuario(cliente, numero) for numero in lote)
            )
            sesiones.extend(encabezados for encabezados in resultados if encabezados)

        if not sesiones:
            raise SystemExit("No se pudo preparar ninguna cuenta. Revise el sistema.")

        print(f"Midiendo con {len(sesiones)} usuarios concurrentes…")
        await asyncio.gather(
            *(_uso_concurrente(cliente, encabezados, mediciones) for encabezados in sesiones)
        )

    return mediciones, len(sesiones)


def informar(mediciones: dict[str, Medicion], usuarios: int, duracion: float) -> bool:
    """Imprime el informe y devuelve si el sistema cumple el requerimiento."""
    print()
    print(f"Prueba de carga con {usuarios} usuarios concurrentes")
    print(f"Duración de la fase medida: {duracion:.1f} s")
    print()
    print(f"{'Operación':<24}{'Med.':>8}{'p95':>8}{'Máx.':>8}{'Límite':>8}{'Fallos':>8}  ")
    print("-" * 72)

    todo_bien = True
    for medicion in mediciones.values():
        if not medicion.tiempos:
            marca = "SIN DATOS"
        elif medicion.cumple:
            marca = "cumple"
        else:
            marca = "NO CUMPLE"
        if not medicion.cumple:
            todo_bien = False
        print(
            f"{medicion.nombre:<24}"
            f"{medicion.mediana:>7.2f}s"
            f"{medicion.percentil_95:>7.2f}s"
            f"{medicion.maximo:>7.2f}s"
            f"{medicion.limite_segundos:>7.1f}s"
            f"{medicion.fallos:>8}  {marca}"
        )

    print()
    if todo_bien:
        print(
            f"El sistema atiende a {usuarios} usuarios concurrentes dentro de los "
            "tiempos del requerimiento 4.5.2."
        )
    else:
        print(
            "Alguna operación superó su límite o falló. Revise las filas marcadas "
            "como NO CUMPLE."
        )
    print(
        "Recuerde: la medición solo es concluyente contra el gestor de base de datos "
        "de producción."
    )
    return todo_bien


def principal() -> int:
    analizador = argparse.ArgumentParser(
        description="Somete el sistema a la carga del requerimiento 4.5.2."
    )
    analizador.add_argument(
        "--url",
        default="http://127.0.0.1:8010",
        help="Dirección del sistema a medir (predeterminado: http://127.0.0.1:8010).",
    )
    analizador.add_argument(
        "--usuarios",
        type=int,
        default=50,
        help="Usuarios concurrentes a simular (predeterminado: 50).",
    )
    argumentos = analizador.parse_args()

    inicio_total = time.perf_counter()
    mediciones, preparados = asyncio.run(ejecutar(argumentos.url, argumentos.usuarios))
    duracion = time.perf_counter() - inicio_total

    return 0 if informar(mediciones, preparados, duracion) else 1


if __name__ == "__main__":
    sys.exit(principal())
