"""Progresion de la carga entre microciclos (regla del negocio *d*).

El apartado 2.5.2 describe la sobrecarga progresiva como el principio que hace
que el entrenamiento siga produciendo adaptacion: si la exigencia no aumenta, el
cuerpo deja de tener motivo para cambiar. La regla del negocio *d* del apartado
4.3.4 le pone el limite: el incremento no supera el 10 % del volumen previo, para
que la adaptacion alcance a producirse antes de la exigencia siguiente.

Este modulo decide, para cada ejercicio, con cuanto peso conviene entrenar la
proxima vez, a partir de lo que el usuario registro la anterior. El metodo es la
progresion doble, que es el que la literatura de referencia prescribe para el
principiante y el intermedio:

1. Se entrena dentro de un rango de repeticiones, no en un numero fijo.
2. Mientras no se alcance el extremo alto del rango en todas las series, se
   repite la misma carga y se busca sumar repeticiones.
3. Cuando se alcanza, se sube la carga y las repeticiones vuelven al extremo
   bajo del rango.

El paso 3 es el que la regla *d* acota. Y de esa cota sale una consecuencia que
importa: con cargas ligeras, el incremento mas pequeno que el gimnasio permite
—un disco de 1.25 kg por lado— ya supera el 10 %. En ese caso la respuesta
correcta no es saltarse la regla sino seguir progresando en repeticiones, y eso
es lo que el motor responde.

Como el resto del paquete `motor`, no depende de la base de datos: recibe el
historial ya leido y devuelve la recomendacion.
"""

from dataclasses import dataclass
from enum import StrEnum

from app.motor.formulas import INCREMENTO_MAXIMO_ENTRE_MICROCICLOS, progresion_admitida

# Incremento mas pequeno que se puede armar en una barra: un disco de 1.25 kg a
# cada lado. Es el escalon real del gimnasio, no una cifra teorica.
INCREMENTO_MINIMO_BARRA_KG = 2.5

# En mancuernas y maquinas el salto suele ser de una unidad o de una placa.
INCREMENTO_MINIMO_AISLADO_KG = 2.0

# Carga por debajo de la cual no tiene sentido hablar de incrementos: se progresa
# en repeticiones y en tecnica.
CARGA_MINIMA_SIGNIFICATIVA_KG = 2.5

# Sesiones consecutivas sin avanzar tras las cuales se sugiere descargar. El
# estancamiento sostenido con esfuerzo alto indica fatiga acumulada, no falta de
# estimulo, y ante eso subir la carga es contraproducente.
SESIONES_PARA_SUGERIR_DESCARGA = 3

# Reduccion de la carga en una semana de descarga.
FRACCION_DE_DESCARGA = 0.10

# Percepcion del esfuerzo, de 1 a 10, a partir de la cual la sesion se considera
# exigente. Se usa junto con el estancamiento para distinguir la fatiga de la
# falta de estimulo.
ESFUERZO_ALTO = 8


class Decision(StrEnum):
    """Que hacer con la carga en la sesion siguiente."""

    SUBIR_CARGA = "subir_carga"
    SUMAR_REPETICIONES = "sumar_repeticiones"
    MANTENER = "mantener"
    DESCARGAR = "descargar"
    PRIMERA_VEZ = "primera_vez"


@dataclass(frozen=True)
class SerieEjecutada:
    """Una serie tal como el usuario la registro."""

    repeticiones: int
    peso_kg: float | None


@dataclass(frozen=True)
class EjecucionPrevia:
    """Lo que el usuario hizo la ultima vez en un ejercicio."""

    series: list[SerieEjecutada]
    percepcion_esfuerzo: int | None = None

    @property
    def carga_maxima(self) -> float | None:
        """Peso mas alto que se movio, que es el que define la carga de trabajo."""
        pesos = [serie.peso_kg for serie in self.series if serie.peso_kg is not None]
        return max(pesos) if pesos else None

    @property
    def repeticiones_minimas(self) -> int:
        """Repeticiones de la serie mas floja, que es la que limita la progresion."""
        return min((serie.repeticiones for serie in self.series), default=0)


@dataclass(frozen=True)
class Recomendacion:
    """Que carga usar la proxima vez, y por que."""

    decision: Decision
    carga_sugerida_kg: float | None
    carga_previa_kg: float | None
    repeticiones_objetivo: int
    explicacion: str

    @property
    def hay_incremento(self) -> bool:
        return self.decision == Decision.SUBIR_CARGA


def incremento_minimo(es_compuesto: bool) -> float:
    """Salto de carga mas pequeno que el equipamiento permite armar."""
    return INCREMENTO_MINIMO_BARRA_KG if es_compuesto else INCREMENTO_MINIMO_AISLADO_KG


def cumplio_el_rango(ejecucion: EjecucionPrevia, repeticiones_max: int) -> bool:
    """Indica si todas las series alcanzaron el extremo alto del rango.

    Se exige en todas y no en promedio: la progresion doble avanza cuando el
    rango se domina por completo, no cuando una serie compensa a otra.
    """
    if not ejecucion.series:
        return False
    return all(serie.repeticiones >= repeticiones_max for serie in ejecucion.series)


def calcular(
    ejecucion: EjecucionPrevia | None,
    repeticiones_min: int,
    repeticiones_max: int,
    es_compuesto: bool,
    sesiones_sin_avanzar: int = 0,
) -> Recomendacion:
    """Decide la carga de la sesion siguiente a partir de la anterior.

    Cuando no hay historial devuelve una recomendacion de primera vez: el sistema
    no puede saber con cuanto peso empieza alguien, y proponerle una cifra
    inventada seria peor que no proponer ninguna.
    """
    if ejecucion is None or not ejecucion.series:
        return Recomendacion(
            decision=Decision.PRIMERA_VEZ,
            carga_sugerida_kg=None,
            carga_previa_kg=None,
            repeticiones_objetivo=repeticiones_min,
            explicacion=(
                "Es la primera vez que registra este ejercicio. Empiece con un peso que "
                f"le permita completar {repeticiones_min} repeticiones con buena técnica "
                "y guárdelo: a partir de la próxima sesión el sistema le dirá cuánto subir."
            ),
        )

    carga_previa = ejecucion.carga_maxima

    # Ejercicios de peso corporal: no hay carga que anotar, se progresa en
    # repeticiones.
    if carga_previa is None or carga_previa < CARGA_MINIMA_SIGNIFICATIVA_KG:
        return Recomendacion(
            decision=Decision.SUMAR_REPETICIONES,
            carga_sugerida_kg=carga_previa,
            carga_previa_kg=carga_previa,
            repeticiones_objetivo=min(ejecucion.repeticiones_minimas + 1, repeticiones_max),
            explicacion=(
                "Este ejercicio se hace con su propio peso: progrese sumando "
                "repeticiones, no carga. Intente una repetición más que la última vez "
                "en cada serie."
            ),
        )

    # Estancamiento sostenido con esfuerzo alto: la fatiga acumulada explica el
    # estancamiento mejor que la falta de estimulo, y subir la carga lo agravaria.
    esfuerzo = ejecucion.percepcion_esfuerzo
    if (
        sesiones_sin_avanzar >= SESIONES_PARA_SUGERIR_DESCARGA
        and esfuerzo is not None
        and esfuerzo >= ESFUERZO_ALTO
    ):
        descargada = _redondear_al_escalon(
            carga_previa * (1 - FRACCION_DE_DESCARGA), es_compuesto
        )
        return Recomendacion(
            decision=Decision.DESCARGAR,
            carga_sugerida_kg=descargada,
            carga_previa_kg=carga_previa,
            repeticiones_objetivo=repeticiones_max,
            explicacion=(
                f"Lleva {sesiones_sin_avanzar} sesiones sin avanzar y reportando un "
                "esfuerzo alto. Baje la carga esta semana y recupere: el músculo crece "
                "mientras descansa, no mientras se fatiga más."
            ),
        )

    if not cumplio_el_rango(ejecucion, repeticiones_max):
        return Recomendacion(
            decision=Decision.MANTENER,
            carga_sugerida_kg=carga_previa,
            carga_previa_kg=carga_previa,
            repeticiones_objetivo=repeticiones_max,
            explicacion=(
                f"Repita los {_formatear(carga_previa)} kg de la última vez. Suba de peso "
                f"cuando complete las {repeticiones_max} repeticiones en todas las series."
            ),
        )

    # Se domino el rango: toca subir, dentro del limite de la regla *d*.
    tope = progresion_admitida(carga_previa)
    escalon = incremento_minimo(es_compuesto)

    if carga_previa + escalon > tope:
        porcentaje = escalon / carga_previa * 100
        return Recomendacion(
            decision=Decision.SUMAR_REPETICIONES,
            carga_sugerida_kg=carga_previa,
            carga_previa_kg=carga_previa,
            repeticiones_objetivo=min(ejecucion.repeticiones_minimas + 1, repeticiones_max + 2),
            explicacion=(
                f"Ya domina las {repeticiones_max} repeticiones, pero el disco más pequeño "
                f"del gimnasio subiría la carga un {porcentaje:.0f} %, por encima del "
                f"{INCREMENTO_MAXIMO_ENTRE_MICROCICLOS * 100:.0f} % que el cuerpo alcanza a "
                "asimilar. Siga con el mismo peso y sume repeticiones hasta que el salto "
                "quede dentro del límite."
            ),
        )

    sugerida = _redondear_al_escalon(min(carga_previa + escalon, tope), es_compuesto)
    # El redondeo hacia abajo no debe dejar la sugerencia en la carga previa.
    if sugerida <= carga_previa:
        sugerida = carga_previa + escalon

    return Recomendacion(
        decision=Decision.SUBIR_CARGA,
        carga_sugerida_kg=sugerida,
        carga_previa_kg=carga_previa,
        repeticiones_objetivo=repeticiones_min,
        explicacion=(
            f"Completó las {repeticiones_max} repeticiones en todas las series con "
            f"{_formatear(carga_previa)} kg: suba a {_formatear(sugerida)} kg. Las "
            f"repeticiones bajarán a {repeticiones_min} y volverá a subirlas desde ahí."
        ),
    )


def _redondear_al_escalon(carga: float, es_compuesto: bool) -> float:
    """Ajusta la carga al escalon que el equipamiento permite armar."""
    escalon = incremento_minimo(es_compuesto)
    return round(round(carga / escalon) * escalon, 2)


def _formatear(carga: float) -> str:
    """Escribe la carga sin decimales cuando no los necesita."""
    return f"{carga:g}"
