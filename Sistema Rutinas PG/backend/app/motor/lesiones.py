"""Adaptacion de la rutina al historial de lesiones del usuario.

El objetivo especifico *a* del Capitulo I pide estructurar cargas de
entrenamiento adaptadas al perfil individual, y el alcance *b* incluye el
historial de lesiones en ese perfil. La adaptacion que se hace aqui es la mas
conservadora posible: un ejercicio que carga una zona lesionada no se prescribe.
No se intenta dosificarlo, porque decidir cuanta carga tolera una articulacion
lesionada es una valoracion clinica que el apartado 1.6.2 deja fuera del
sistema.

Como el resto del paquete `motor`, no consulta la base de datos: recibe los
ejercicios disponibles y las zonas lesionadas, y devuelve los que se pueden
prescribir.
"""

from app.modelos.enumeraciones import GrupoMuscular, ZonaLesion
from app.motor.rutina import EjercicioDisponible

HOMBRO = ZonaLesion.HOMBRO
CODO_MUNECA = ZonaLesion.CODO_MUNECA
ESPALDA_BAJA = ZonaLesion.ESPALDA_BAJA
RODILLA = ZonaLesion.RODILLA
TOBILLO = ZonaLesion.TOBILLO

# Zonas que carga cada ejercicio del catalogo inicial. Se declaran por nombre
# porque el catalogo es pequeno y conocido, y porque la zona que carga un
# ejercicio no se deduce de su grupo muscular: la sentadilla es de pierna y
# carga la espalda baja; el press militar es de hombro y tambien la carga.
ZONAS_POR_EJERCICIO: dict[str, frozenset[ZonaLesion]] = {
    "Press de banca con barra": frozenset({HOMBRO, CODO_MUNECA}),
    "Press inclinado con mancuernas": frozenset({HOMBRO, CODO_MUNECA}),
    "Aperturas con mancuernas": frozenset({HOMBRO}),
    "Lagartijas": frozenset({HOMBRO, CODO_MUNECA}),
    "Remo con barra": frozenset({ESPALDA_BAJA, CODO_MUNECA}),
    "Jalón al pecho en polea": frozenset({HOMBRO, CODO_MUNECA}),
    "Remo con mancuerna a una mano": frozenset({CODO_MUNECA}),
    "Dominadas": frozenset({HOMBRO, CODO_MUNECA}),
    "Sentadilla con barra": frozenset({RODILLA, ESPALDA_BAJA, TOBILLO}),
    "Prensa de piernas": frozenset({RODILLA}),
    "Peso muerto rumano": frozenset({ESPALDA_BAJA}),
    "Zancadas con mancuernas": frozenset({RODILLA, TOBILLO}),
    "Elevación de talones de pie": frozenset({TOBILLO}),
    "Press militar con barra": frozenset({HOMBRO, CODO_MUNECA, ESPALDA_BAJA}),
    "Elevaciones laterales con mancuernas": frozenset({HOMBRO}),
    "Pájaros con mancuernas": frozenset({HOMBRO}),
    "Press Arnold con mancuernas": frozenset({HOMBRO, CODO_MUNECA}),
    "Curl de bíceps con barra": frozenset({CODO_MUNECA}),
    "Curl alterno con mancuernas": frozenset({CODO_MUNECA}),
    "Extensión de tríceps en polea": frozenset({CODO_MUNECA}),
    "Fondos entre bancas": frozenset({HOMBRO, CODO_MUNECA}),
    "Plancha frontal": frozenset(),
    "Abdominales en el suelo": frozenset(),
    "Rueda abdominal o rodillo": frozenset({ESPALDA_BAJA, HOMBRO}),
    "Elevación de piernas colgado": frozenset({HOMBRO, ESPALDA_BAJA}),
}

# Para los ejercicios que el administrador agregue despues (historia HU-11) no
# hay declaracion por nombre, asi que se supone lo que carga su grupo. La
# suposicion peca de prudente: es preferible omitir un ejercicio seguro que
# prescribir uno que cargue la lesion.
ZONAS_POR_GRUPO: dict[GrupoMuscular, frozenset[ZonaLesion]] = {
    GrupoMuscular.PECHO: frozenset({HOMBRO, CODO_MUNECA}),
    GrupoMuscular.ESPALDA: frozenset({HOMBRO, CODO_MUNECA, ESPALDA_BAJA}),
    GrupoMuscular.PIERNA: frozenset({RODILLA, TOBILLO, ESPALDA_BAJA}),
    GrupoMuscular.HOMBRO: frozenset({HOMBRO, CODO_MUNECA}),
    GrupoMuscular.BRAZO: frozenset({CODO_MUNECA}),
    GrupoMuscular.ABDOMEN: frozenset({ESPALDA_BAJA}),
    GrupoMuscular.CUERPO_COMPLETO: frozenset(ZonaLesion),
}

NOMBRES_ZONA: dict[ZonaLesion, str] = {
    HOMBRO: "hombro",
    CODO_MUNECA: "codo o muñeca",
    ESPALDA_BAJA: "espalda baja",
    RODILLA: "rodilla",
    TOBILLO: "tobillo",
}


def zonas_que_carga(ejercicio: EjercicioDisponible) -> frozenset[ZonaLesion]:
    """Articulaciones que el ejercicio somete a carga."""
    declaradas = ZONAS_POR_EJERCICIO.get(ejercicio.nombre)
    if declaradas is not None:
        return declaradas
    return ZONAS_POR_GRUPO[ejercicio.grupo_muscular]


def ejercicios_compatibles(
    disponibles: list[EjercicioDisponible], lesiones: list[ZonaLesion]
) -> list[EjercicioDisponible]:
    """Deja fuera los ejercicios que cargan alguna de las zonas lesionadas."""
    if not lesiones:
        return list(disponibles)
    lesionadas = set(lesiones)
    return [
        ejercicio for ejercicio in disponibles if not zonas_que_carga(ejercicio) & lesionadas
    ]


def describir_zonas(lesiones: list[ZonaLesion]) -> str:
    """Lista las zonas en lenguaje sencillo: «hombro y rodilla»."""
    nombres = [NOMBRES_ZONA[zona] for zona in lesiones]
    if len(nombres) <= 1:
        return "".join(nombres)
    return f"{', '.join(nombres[:-1])} y {nombres[-1]}"
