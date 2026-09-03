"""Generador de la rutina semanal de entrenamiento (historia HU-07).

El apartado 2.5.1 reparte el trabajo en dos: la red neuronal determina el volumen
semanal de series por grupo muscular, y este modulo lo distribuye entre las
sesiones que el usuario declaro disponibles, respetando los tiempos de
recuperacion. Las repeticiones en reserva definen la intensidad prescrita.

Como el resto del paquete `motor`, no depende de la base de datos: recibe la
lista de ejercicios disponibles y devuelve la rutina ya armada, de modo que su
logica pueda verificarse sin levantar el sistema completo.
"""

from dataclasses import dataclass, field
from math import ceil

from app.modelos.enumeraciones import GrupoMuscular, NivelExperiencia, Objetivo

# Esquemas semanales por numero de dias declarados. Cada par indica el dia de la
# semana (1 es lunes) y el grupo muscular que se estimula ese dia.
#
# Los dias se eligieron de modo que ningun grupo reciba estimulo en dos dias
# consecutivos, criterio de aceptacion de la historia HU-07. La comprobacion
# incluye el cierre de la semana: como el microciclo se repite, el ultimo dia
# tampoco puede chocar con el primero de la semana siguiente.
#
# Con tres dias o menos se prescribe cuerpo completo, porque repartir los grupos
# entre tan pocas sesiones dejaria a cada uno con una sola frecuencia semanal.
ESQUEMAS_SEMANALES: dict[int, tuple[tuple[int, GrupoMuscular], ...]] = {
    1: ((1, GrupoMuscular.CUERPO_COMPLETO),),
    2: (
        (1, GrupoMuscular.CUERPO_COMPLETO),
        (4, GrupoMuscular.CUERPO_COMPLETO),
    ),
    3: (
        (1, GrupoMuscular.CUERPO_COMPLETO),
        (3, GrupoMuscular.CUERPO_COMPLETO),
        (5, GrupoMuscular.CUERPO_COMPLETO),
    ),
    4: (
        (1, GrupoMuscular.PECHO),
        (2, GrupoMuscular.ESPALDA),
        (4, GrupoMuscular.PIERNA),
        (5, GrupoMuscular.HOMBRO),
    ),
    5: (
        (1, GrupoMuscular.PECHO),
        (2, GrupoMuscular.ESPALDA),
        (3, GrupoMuscular.PIERNA),
        (5, GrupoMuscular.HOMBRO),
        (6, GrupoMuscular.BRAZO),
    ),
    6: (
        (1, GrupoMuscular.PECHO),
        (2, GrupoMuscular.ESPALDA),
        (3, GrupoMuscular.PIERNA),
        (4, GrupoMuscular.HOMBRO),
        (5, GrupoMuscular.BRAZO),
        (6, GrupoMuscular.ABDOMEN),
    ),
    7: (
        (1, GrupoMuscular.PECHO),
        (2, GrupoMuscular.ESPALDA),
        (3, GrupoMuscular.PIERNA),
        (4, GrupoMuscular.HOMBRO),
        (5, GrupoMuscular.BRAZO),
        (6, GrupoMuscular.ABDOMEN),
        (7, GrupoMuscular.PIERNA),
    ),
}

# Grupos que una sesion de cuerpo completo estimula. Se usa tanto para elegir sus
# ejercicios como para verificar la restriccion de dias consecutivos.
GRUPOS_DE_CUERPO_COMPLETO = (
    GrupoMuscular.PIERNA,
    GrupoMuscular.ESPALDA,
    GrupoMuscular.PECHO,
    GrupoMuscular.HOMBRO,
    GrupoMuscular.BRAZO,
    GrupoMuscular.ABDOMEN,
)

NOMBRES_DIAS = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado",
    7: "Domingo",
}

DIAS_DE_LA_SEMANA = 7

# Repeticiones por serie segun el objetivo. El rango alto con el deficit
# calorico y el bajo con la ganancia de fuerza y masa (apartado 2.5.2).
REPETICIONES_POR_OBJETIVO: dict[Objetivo, tuple[int, int]] = {
    Objetivo.PERDIDA_GRASA: (12, 15),
    Objetivo.MANTENIMIENTO: (8, 12),
    Objetivo.GANANCIA_MUSCULAR: (6, 10),
}

# Repeticiones en reserva, que definen la intensidad prescrita. El principiante
# se detiene mas lejos del fallo porque todavia no ejecuta con tecnica estable
# bajo fatiga; el avanzado puede acercarse mas (apartado 2.5.1).
REPETICIONES_EN_RESERVA: dict[NivelExperiencia, int] = {
    NivelExperiencia.PRINCIPIANTE: 3,
    NivelExperiencia.INTERMEDIO: 2,
    NivelExperiencia.AVANZADO: 1,
}

# Descanso entre series, en segundos. Los ejercicios compuestos involucran mas
# masa muscular y necesitan mas tiempo de recuperacion entre series.
DESCANSO_COMPUESTO = 120
DESCANSO_AISLADO = 75

SERIES_MINIMAS_POR_EJERCICIO = 2
# Seis series es el maximo que un mismo ejercicio admite antes de que la fatiga
# degrade la tecnica; a partir de ahi conviene repartir en otro ejercicio.
SERIES_MAXIMAS_POR_EJERCICIO = 6
EJERCICIOS_MAXIMOS_POR_GRUPO = 4
# Volumen a partir del cual conviene repartir en al menos dos ejercicios, para
# que el grupo reciba estimulo desde mas de un angulo.
SERIES_PARA_SEGUNDO_EJERCICIO = 6


@dataclass(frozen=True)
class EjercicioDisponible:
    """Ejercicio del catalogo, en la forma minima que el generador necesita.

    Se define aqui en lugar de usar la entidad de base de datos para que el
    generador pueda probarse sin sesion de base de datos.
    """

    id: int
    nombre: str
    grupo_muscular: GrupoMuscular
    nivel_minimo: NivelExperiencia
    es_compuesto: bool


@dataclass(frozen=True)
class EjercicioPrescrito:
    """Prescripcion concreta de un ejercicio dentro de una sesion."""

    ejercicio_id: int
    nombre: str
    grupo_muscular: GrupoMuscular
    orden: int
    series: int
    repeticiones_min: int
    repeticiones_max: int
    repeticiones_en_reserva: int
    descanso_segundos: int


@dataclass(frozen=True)
class SesionPrescrita:
    """Sesion de un dia de la semana con sus ejercicios."""

    dia: int
    grupo_muscular: GrupoMuscular
    ejercicios: list[EjercicioPrescrito] = field(default_factory=list)

    @property
    def nombre_dia(self) -> str:
        return NOMBRES_DIAS[self.dia]

    @property
    def series_totales(self) -> int:
        return sum(ejercicio.series for ejercicio in self.ejercicios)

    @property
    def grupos_estimulados(self) -> set[GrupoMuscular]:
        """Grupos que la sesion trabaja realmente.

        Una sesion de cuerpo completo estimula todos los grupos, no el valor
        `cuerpo_completo`; esta distincion es la que hace correcta la
        verificacion de dias consecutivos.
        """
        if self.grupo_muscular == GrupoMuscular.CUERPO_COMPLETO:
            return set(GRUPOS_DE_CUERPO_COMPLETO)
        return {self.grupo_muscular}


class CatalogoInsuficiente(Exception):
    """No hay ejercicios registrados con los que armar la rutina."""


def _nivel_alcanzado(nivel_usuario: NivelExperiencia, nivel_minimo: NivelExperiencia) -> bool:
    """Indica si el usuario tiene experiencia suficiente para el ejercicio."""
    orden = {
        NivelExperiencia.PRINCIPIANTE: 1,
        NivelExperiencia.INTERMEDIO: 2,
        NivelExperiencia.AVANZADO: 3,
    }
    return orden[nivel_usuario] >= orden[nivel_minimo]


def _repartir_series(total: int, cantidad_ejercicios: int) -> list[int]:
    """Reparte las series entre los ejercicios de la forma mas pareja posible.

    El residuo se asigna a los primeros ejercicios, que son los compuestos y los
    que conviene hacer con mas volumen mientras se esta menos fatigado.
    """
    if cantidad_ejercicios <= 0:
        return []

    base, residuo = divmod(total, cantidad_ejercicios)
    reparto = [base + (1 if posicion < residuo else 0) for posicion in range(cantidad_ejercicios)]
    return [
        min(max(series, SERIES_MINIMAS_POR_EJERCICIO), SERIES_MAXIMAS_POR_EJERCICIO)
        for series in reparto
    ]


def _elegir_ejercicios(
    disponibles: list[EjercicioDisponible],
    grupo: GrupoMuscular,
    nivel_usuario: NivelExperiencia,
    cantidad: int,
) -> list[EjercicioDisponible]:
    """Selecciona ejercicios de un grupo, con los compuestos primero.

    Los ejercicios compuestos encabezan la sesion porque involucran mas masa
    muscular y conviene ejecutarlos cuando todavia no hay fatiga acumulada
    (apartado 2.5.1).
    """
    del_grupo = [
        ejercicio
        for ejercicio in disponibles
        if ejercicio.grupo_muscular == grupo
        and _nivel_alcanzado(nivel_usuario, ejercicio.nivel_minimo)
    ]
    del_grupo.sort(key=lambda ejercicio: (not ejercicio.es_compuesto, ejercicio.id))
    return del_grupo[:cantidad]


def _sesion_de_un_grupo(
    dia: int,
    grupo: GrupoMuscular,
    series_de_la_sesion: int,
    disponibles: list[EjercicioDisponible],
    nivel_usuario: NivelExperiencia,
    objetivo: Objetivo,
) -> SesionPrescrita:
    """Arma una sesion dedicada a un solo grupo muscular."""
    # Se toman tantos ejercicios como haga falta para que el volumen de la sesion
    # quepa sin superar el maximo de series por ejercicio.
    necesarios = ceil(series_de_la_sesion / SERIES_MAXIMAS_POR_EJERCICIO)
    if series_de_la_sesion >= SERIES_PARA_SEGUNDO_EJERCICIO:
        necesarios = max(necesarios, 2)
    cantidad = min(max(necesarios, 1), EJERCICIOS_MAXIMOS_POR_GRUPO)
    elegidos = _elegir_ejercicios(disponibles, grupo, nivel_usuario, cantidad)
    if not elegidos:
        return SesionPrescrita(dia=dia, grupo_muscular=grupo, ejercicios=[])

    reparto = _repartir_series(series_de_la_sesion, len(elegidos))
    repeticiones_min, repeticiones_max = REPETICIONES_POR_OBJETIVO[objetivo]

    ejercicios = [
        EjercicioPrescrito(
            ejercicio_id=ejercicio.id,
            nombre=ejercicio.nombre,
            grupo_muscular=ejercicio.grupo_muscular,
            orden=posicion,
            series=series,
            repeticiones_min=repeticiones_min,
            repeticiones_max=repeticiones_max,
            repeticiones_en_reserva=REPETICIONES_EN_RESERVA[nivel_usuario],
            descanso_segundos=DESCANSO_COMPUESTO if ejercicio.es_compuesto else DESCANSO_AISLADO,
        )
        for posicion, (ejercicio, series) in enumerate(zip(elegidos, reparto), start=1)
    ]
    return SesionPrescrita(dia=dia, grupo_muscular=grupo, ejercicios=ejercicios)


def _sesion_de_cuerpo_completo(
    dia: int,
    series_por_grupo_en_la_sesion: int,
    disponibles: list[EjercicioDisponible],
    nivel_usuario: NivelExperiencia,
    objetivo: Objetivo,
) -> SesionPrescrita:
    """Arma una sesion que recorre todos los grupos musculares.

    A cada grupo le corresponde un solo ejercicio, para que la sesion no se haga
    interminable: son seis grupos en una misma jornada.
    """
    repeticiones_min, repeticiones_max = REPETICIONES_POR_OBJETIVO[objetivo]
    # En cuerpo completo cada grupo aporta un unico ejercicio, de modo que ese
    # ejercicio admite una serie mas que en las sesiones dedicadas a un grupo.
    series = min(
        max(series_por_grupo_en_la_sesion, SERIES_MINIMAS_POR_EJERCICIO),
        SERIES_MAXIMAS_POR_EJERCICIO + 1,
    )

    ejercicios: list[EjercicioPrescrito] = []
    for grupo in GRUPOS_DE_CUERPO_COMPLETO:
        elegidos = _elegir_ejercicios(disponibles, grupo, nivel_usuario, 1)
        if not elegidos:
            continue
        ejercicio = elegidos[0]
        ejercicios.append(
            EjercicioPrescrito(
                ejercicio_id=ejercicio.id,
                nombre=ejercicio.nombre,
                grupo_muscular=ejercicio.grupo_muscular,
                orden=len(ejercicios) + 1,
                series=series,
                repeticiones_min=repeticiones_min,
                repeticiones_max=repeticiones_max,
                repeticiones_en_reserva=REPETICIONES_EN_RESERVA[nivel_usuario],
                descanso_segundos=(
                    DESCANSO_COMPUESTO if ejercicio.es_compuesto else DESCANSO_AISLADO
                ),
            )
        )

    return SesionPrescrita(
        dia=dia, grupo_muscular=GrupoMuscular.CUERPO_COMPLETO, ejercicios=ejercicios
    )


@dataclass(frozen=True)
class RutinaSemanal:
    """Rutina completa de un microciclo, con el volumen objetivo y el efectivo.

    Ambos volumenes se declaran por separado a proposito. En los esquemas de
    cuerpo completo —de uno a tres dias— seis grupos musculares comparten la
    misma jornada, y el volumen que la red determino no cabe entero sin que la
    sesion se alargue de forma impracticable. En ese caso el generador prescribe
    lo que si cabe y lo dice, en lugar de declarar un volumen que la rutina no
    entrega.
    """

    sesiones: list[SesionPrescrita]
    series_objetivo_por_grupo: float
    dias_entrenamiento_semana: int

    @property
    def series_totales(self) -> int:
        return sum(sesion.series_totales for sesion in self.sesiones)

    @property
    def series_efectivas_por_grupo(self) -> dict[GrupoMuscular, int]:
        """Series semanales que cada grupo recibe realmente en esta rutina."""
        acumulado: dict[GrupoMuscular, int] = {}
        for sesion in self.sesiones:
            for ejercicio in sesion.ejercicios:
                acumulado[ejercicio.grupo_muscular] = (
                    acumulado.get(ejercicio.grupo_muscular, 0) + ejercicio.series
                )
        return acumulado

    @property
    def alcanza_el_volumen_objetivo(self) -> bool:
        """Indica si todos los grupos trabajados llegan al volumen determinado."""
        efectivas = self.series_efectivas_por_grupo
        if not efectivas:
            return False
        # Se admite una serie de diferencia por el redondeo al repartir entre
        # las sesiones.
        return all(
            series >= self.series_objetivo_por_grupo - 1 for series in efectivas.values()
        )

    @property
    def grupos_sin_trabajo_directo(self) -> list[GrupoMuscular]:
        """Grupos que el esquema no estimula de forma directa.

        Con cuatro sesiones semanales el brazo y el abdomen no reciben una
        sesion propia: trabajan de forma indirecta en los press y los remos. Se
        declaran para que el usuario sepa por que no aparecen.
        """
        trabajados = set(self.series_efectivas_por_grupo)
        return [
            grupo
            for grupo in GRUPOS_DE_CUERPO_COMPLETO
            if grupo not in trabajados
        ]


def generar_rutina(
    series_semanales_por_grupo: float,
    dias_entrenamiento_semana: int,
    nivel_experiencia: NivelExperiencia,
    objetivo: Objetivo,
    disponibles: list[EjercicioDisponible],
) -> RutinaSemanal:
    """Construye la rutina semanal (historia HU-07).

    Recibe el volumen que determino la red neuronal y lo reparte entre las
    sesiones del esquema que corresponde a la frecuencia declarada. El numero de
    sesiones devueltas coincide siempre con esa frecuencia.
    """
    if not disponibles:
        raise CatalogoInsuficiente(
            "No hay ejercicios registrados en el catálogo con los que armar la rutina."
        )

    dias = min(max(dias_entrenamiento_semana, 1), DIAS_DE_LA_SEMANA)
    esquema = ESQUEMAS_SEMANALES[dias]

    # Cuantas veces recibe estimulo cada grupo en la semana, para repartir entre
    # esas sesiones el volumen semanal que le corresponde.
    frecuencias: dict[GrupoMuscular, int] = {}
    for _, grupo in esquema:
        for estimulado in (
            GRUPOS_DE_CUERPO_COMPLETO
            if grupo == GrupoMuscular.CUERPO_COMPLETO
            else (grupo,)
        ):
            frecuencias[estimulado] = frecuencias.get(estimulado, 0) + 1

    sesiones: list[SesionPrescrita] = []
    for dia, grupo in esquema:
        if grupo == GrupoMuscular.CUERPO_COMPLETO:
            series = round(series_semanales_por_grupo / frecuencias[GrupoMuscular.PIERNA])
            sesiones.append(
                _sesion_de_cuerpo_completo(
                    dia, series, disponibles, nivel_experiencia, objetivo
                )
            )
        else:
            series = round(series_semanales_por_grupo / frecuencias[grupo])
            sesiones.append(
                _sesion_de_un_grupo(
                    dia, grupo, series, disponibles, nivel_experiencia, objetivo
                )
            )

    return RutinaSemanal(
        sesiones=sesiones,
        series_objetivo_por_grupo=series_semanales_por_grupo,
        dias_entrenamiento_semana=dias,
    )


def hay_grupo_en_dias_consecutivos(sesiones: list[SesionPrescrita]) -> bool:
    """Comprueba el criterio de aceptacion de la historia HU-07.

    Devuelve verdadero si algun grupo muscular recibe estimulo en dos dias
    seguidos. La semana se recorre de forma circular porque el microciclo se
    repite: el ultimo dia de una semana precede al primero de la siguiente.
    """
    if len(sesiones) < 2:
        return False

    por_dia = {sesion.dia: sesion.grupos_estimulados for sesion in sesiones}
    for dia, grupos in por_dia.items():
        siguiente = dia % DIAS_DE_LA_SEMANA + 1
        if siguiente in por_dia and grupos & por_dia[siguiente]:
            return True
    return False
