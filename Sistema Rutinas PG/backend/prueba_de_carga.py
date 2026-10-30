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
import json
from math import ceil
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
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
    esperadas: int = 0
    causas: dict[str, int] = field(default_factory=dict)

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
        posicion = max(ceil(len(ordenados) * 0.95) - 1, 0)
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
        return (self.fallos == 0 and (not self.esperadas or len(self.tiempos) == self.esperadas)
                and self.maximo <= self.limite_segundos)


async def _medir(medicion: Medicion, corrutina) -> httpx.Response | None:
    """Ejecuta una peticion y registra cuanto tardo."""
    inicio = time.perf_counter()
    try:
        respuesta = await corrutina
    except Exception as error:  # solo clase; nunca URL, token ni cuerpo
        medicion.fallos += 1
        causa = type(error).__name__
        medicion.causas[causa] = medicion.causas.get(causa, 0) + 1
        return None
    else:
        causa = str(respuesta.status_code)
        medicion.causas[causa] = medicion.causas.get(causa, 0) + 1
        if respuesta.status_code >= 400:
            medicion.fallos += 1
        return respuesta
    finally:
        # El tiempo de los fallos también pertenece al denominador.
        medicion.tiempos.append(time.perf_counter() - inicio)


async def _preparar_usuario(
    cliente: httpx.AsyncClient, numero: int, corrida: str = "ensayo"
) -> dict[str, str] | None:
    """Crea la cuenta y el perfil de un usuario. No se mide.

    Devuelve los encabezados de sesion, o None si la preparacion fallo.
    """
    # El dominio debe ser uno que el validador de correo acepte: los reservados
    # como .local se rechazan, igual que en el registro real.
    credenciales = {
        "correo": f"carga-{corrida}-{numero}@example.com",
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


@dataclass
class ResultadoCarga:
    mediciones: dict[str, Medicion]
    solicitados: int
    preparados: int
    preparacion_segundos: float
    calentamiento_segundos: float
    medicion_segundos: float


async def ejecutar(url_base: str, usuarios: int) -> ResultadoCarga:
    """Prepara las cuentas y despues somete al sistema a la carga concurrente."""
    mediciones = {
        "plan": Medicion("Generación del plan", LIMITE_PLAN_SEGUNDOS),
        "rutina": Medicion("Consulta de la rutina", LIMITE_PANTALLA_SEGUNDOS),
        "menu": Medicion("Consulta del menú", LIMITE_PANTALLA_SEGUNDOS),
        "progreso": Medicion("Registro de progreso", LIMITE_PLAN_SEGUNDOS),
        "reporte": Medicion("Reporte de evolución", LIMITE_PANTALLA_SEGUNDOS),
        "perfil": Medicion("Historial de medidas", LIMITE_PANTALLA_SEGUNDOS),
    }

    corrida = uuid4().hex[:12]
    inicio_preparacion = time.perf_counter()
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
                *(_preparar_usuario(cliente, numero, corrida) for numero in lote)
            )
            sesiones.extend(encabezados for encabezados in resultados if encabezados)

        if not sesiones:
            raise SystemExit("No se pudo preparar ninguna cuenta. Revise el sistema.")

        preparacion = time.perf_counter() - inicio_preparacion
        inicio_calentamiento = time.perf_counter()
        # Registra el coste aparte. Una entrada se repite; las otras son distintas.
        calentada = await cliente.post("/api/v1/plan-nutricional", headers=sesiones[0])
        if calentada.status_code != 201:
            raise SystemExit("Falló el calentamiento del plan; no se certifica una medición en caliente.")
        calentamiento = time.perf_counter() - inicio_calentamiento
        for medicion in mediciones.values():
            medicion.esperadas = usuarios
        print(f"Midiendo con {len(sesiones)} de {usuarios} usuarios preparados…")
        inicio_medicion = time.perf_counter()
        await asyncio.gather(
            *(_uso_concurrente(cliente, encabezados, mediciones) for encabezados in sesiones)
        )

    return ResultadoCarga(mediciones, usuarios, len(sesiones), preparacion, calentamiento, time.perf_counter()-inicio_medicion)


def informar(mediciones: dict[str, Medicion], usuarios: int, duracion: float, solicitados: int | None = None) -> bool:
    """Imprime el informe y devuelve si el sistema cumple el requerimiento."""
    print()
    print(f"Prueba de carga con {usuarios} usuarios concurrentes")
    print(f"Duración de la fase medida: {duracion:.1f} s")
    print()
    print(f"{'Operación':<24}{'Med.':>8}{'p95':>8}{'Máx.':>8}{'Límite':>8}{'Fallos':>8}  ")
    print("-" * 72)

    todo_bien = solicitados is None or usuarios == solicitados
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
    if solicitados is not None and usuarios != solicitados:
        print(f"Preparación incompleta: {usuarios}/{solicitados}; no acredita la concurrencia solicitada.")
    for clave, medicion in mediciones.items():
        print(f"{clave}: {len(medicion.tiempos)} intentos; estados/causas {medicion.causas}")
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
    analizador.add_argument("--json", type=Path, help="Guarda evidencia sin cuentas, tokens ni cuerpos de respuesta.")
    argumentos = analizador.parse_args()
    if not 1 <= argumentos.usuarios <= 500:
        analizador.error("--usuarios debe estar entre 1 y 500")

    resultado = asyncio.run(ejecutar(argumentos.url, argumentos.usuarios))
    cumple = informar(resultado.mediciones, resultado.preparados,
                      resultado.medicion_segundos, resultado.solicitados)
    print(f"Preparación: {resultado.preparacion_segundos:.2f} s; calentamiento: {resultado.calentamiento_segundos:.2f} s. Ambos separados de la medición.")
    if argumentos.json:
        datos = {
            "version_instrumento": 3,
            "criterio": "cero fallos, muestra completa y cada petición observada dentro del límite; p95 informativo",
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            "escenario": "usuarios simultáneos en seis operaciones secuenciales por cuenta; plan calentado; perfiles distintos; una entrada repetida por calentamiento",
            "solicitados": resultado.solicitados, "preparados": resultado.preparados,
            "preparacion_segundos": resultado.preparacion_segundos,
            "calentamiento_segundos": resultado.calentamiento_segundos,
            "medicion_segundos": resultado.medicion_segundos, "cumple_local": cumple,
            "operaciones": {k: {"intentos": len(m.tiempos), "esperadas": m.esperadas,
                "fallos": m.fallos, "causas": m.causas, "p95_segundos": m.percentil_95,
                "mediana_segundos": m.mediana, "maximo_segundos": m.maximo,
                "limite_segundos": m.limite_segundos, "cumple": m.cumple,
                "tiempos_segundos": m.tiempos} for k,m in resultado.mediciones.items()},
        }
        argumentos.json.parent.mkdir(parents=True, exist_ok=True)
        argumentos.json.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if cumple else 1



if __name__ == "__main__":
    sys.exit(principal())
