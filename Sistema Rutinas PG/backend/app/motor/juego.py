"""Reglas de los puntos, los niveles y los logros.

No corresponde a ninguna de las once historias de la pila de producto. Se agrega
por un hueco que la bitacora dejo abierto: el sistema ya sabe con detalle lo que
el usuario hizo —cada serie, cada kilogramo, cada pesaje semanal— pero no le
devolvia ninguna señal de continuidad. La sesion cuarenta se veia igual que la
primera, y el abandono en el gimnasio no ocurre por falta de plan sino por falta
de evidencia de que el plan esta sirviendo para algo.

Lo delicado de un sistema de recompensas en una aplicacion de salud no es cuanto
premia, sino QUE premia. Un contador que sumara volumen sin techo premiaria
entrenar mas de lo que el programa prescribe, que es exactamente lo que el
apartado 2.5.2 advierte que produce sobreentrenamiento y lesion. De ahi las
cuatro decisiones que gobiernan este modulo:

1. Solo la primera sesion del dia puntua. Registrar dos entrenamientos el mismo
   dia no da el doble de puntos, porque el sistema no debe pedirlo.
2. El volumen tiene techo. A partir de `VOLUMEN_CON_TECHO_KG` un kilogramo mas
   no suma nada: la diferencia entre una sesion buena y una sesion excesiva no
   puede ser una diferencia de premio.
3. La racha se cuenta en semanas y no en dias, con la misma regla que
   `servicios.entrenamiento._racha_de_semanas`. Una racha diaria obligaria a
   entrenar sin descanso para no perderla.
4. Respetar el descanso puntua. Quien cumple sus dias prescritos y no se pasa de
   ellos recibe puntos por eso, de modo que el sistema premie seguir el programa
   y no exceder el programa.

Todo lo que vive aqui son tablas y funciones sin estado: no consulta la base de
datos ni conoce al usuario. Eso es lo que permite probar las reglas por separado,
igual que `motor.formulas` y `motor.progresion`.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

# --------------------------------------------------------------------------
# Niveles
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Nivel:
    """Un nivel de la senda, con el atavio que le corresponde a la mascota.

    `gala` es el grado de atavio —de 0 a 4— con que se dibuja la mascota en ese
    nivel. Es lo que hace visible el avance sin obligar a leer una cifra: el
    lobo aparece con cinta de laurel, con corona, con capa y finalmente con
    aureola dorada.
    """

    numero: int
    nombre: str
    lema: str
    xp_requerido: int
    gala: int


# La curva se calibro contra el presupuesto real de puntos del usuario que el
# sistema describe: tres sesiones por semana en tres dias distintos, con su
# pesaje semanal y buena adherencia. Con las reglas de este modulo eso rinde
# 651 puntos en una semana estable —147 por sesion, 80 de racha, 60 del pesaje,
# 40 de adherencia y 30 de descanso— y algo mas en las primeras semanas, porque
# las insignias de arranque reparten de golpe buena parte de los 3 920 puntos
# que suma el catalogo entero.
#
# Sobre ese presupuesto, el ultimo nivel queda a unas cincuenta semanas de
# constancia: un ano. Los umbrales no son redondos por gusto sino por dos
# extremos que hay que evitar. Con tramos cortos, el usuario cruza tres niveles
# en la primera semana y llega al techo antes de que el habito exista, de modo
# que la senda se convierte en algo que se termina y se abandona. Con tramos
# largos, los primeros meses no muestran avance, que es justamente cuando el
# usuario decide si sigue. De ahi que el segundo nivel caiga al cerrar la
# primera semana —la primera señal llega pronto— y que cada tramo valga entre
# una cuarta parte y un tercio mas que el anterior.
NIVELES: tuple[Nivel, ...] = (
    #                                                                   xp    gala
    Nivel(1, "Cachorro", "Toda manada empieza con un cachorro.", 0, 0),
    Nivel(2, "Rastreador", "Ya sabe seguir el rastro de su propio avance.", 900, 0),
    Nivel(3, "Cazador", "La constancia dejó de ser un intento.", 2_000, 1),
    Nivel(4, "Guardián", "Aparece aunque nadie lo esté viendo.", 3_600, 1),
    Nivel(5, "Alfa", "La manada sigue a quien no falta.", 6_000, 2),
    Nivel(6, "Espartano", "Volvió con el escudo, no sobre el escudo.", 9_000, 2),
    Nivel(7, "Olímpico", "Compite contra quien fue el mes pasado.", 13_000, 3),
    Nivel(8, "Semidiós", "El esfuerzo dejó de pesar y empezó a rendir.", 18_500, 3),
    Nivel(9, "Titán", "Ya no levanta peso: levanta meses de trabajo.", 26_000, 4),
    Nivel(10, "Leyenda", "Su historial es el argumento.", 36_000, 4),
)

NIVEL_MAXIMO = NIVELES[-1].numero


def nivel_para(puntos: int) -> Nivel:
    """Nivel que corresponde a un acumulado de puntos."""
    alcanzado = NIVELES[0]
    for nivel in NIVELES:
        if puntos >= nivel.xp_requerido:
            alcanzado = nivel
        else:
            break
    return alcanzado


def gala_de_nivel(numero: int) -> int:
    """Grado de atavio que le toca a la mascota en ese nivel.

    Lo necesita la respuesta de una accion, que conoce el numero del nivel
    alcanzado pero no la tabla: sin esto, la pantalla que celebra una subida
    dibujaria al lobo con el atavio del nivel anterior.
    """
    for nivel in NIVELES:
        if nivel.numero == numero:
            return nivel.gala
    return NIVELES[-1].gala if numero > NIVEL_MAXIMO else NIVELES[0].gala


def siguiente_nivel(nivel: Nivel) -> Nivel | None:
    """Nivel que sigue al indicado, o nada si ya es el ultimo."""
    if nivel.numero >= NIVEL_MAXIMO:
        return None
    return NIVELES[nivel.numero]


@dataclass(frozen=True)
class AvanceDeNivel:
    """Posicion del usuario dentro de su nivel actual.

    La pantalla necesita las cifras a la vez: sin el tramo, el porcentaje no se
    puede dibujar, y sin lo que falta, el porcentaje no dice que hacer.
    """

    nivel: Nivel
    proximo: Nivel | None
    puntos_totales: int
    puntos_en_el_nivel: int
    puntos_del_tramo: int
    puntos_para_el_proximo: int
    porcentaje: int


def avance_de_nivel(puntos: int) -> AvanceDeNivel:
    """Calcula en que punto del nivel esta el usuario."""
    puntos = max(puntos, 0)
    nivel = nivel_para(puntos)
    proximo = siguiente_nivel(nivel)

    if proximo is None:
        return AvanceDeNivel(nivel, None, puntos, 0, 0, 0, 100)

    tramo = proximo.xp_requerido - nivel.xp_requerido
    en_el_nivel = puntos - nivel.xp_requerido
    return AvanceDeNivel(
        nivel=nivel,
        proximo=proximo,
        puntos_totales=puntos,
        puntos_en_el_nivel=en_el_nivel,
        puntos_del_tramo=tramo,
        puntos_para_el_proximo=tramo - en_el_nivel,
        porcentaje=round(en_el_nivel / tramo * 100),
    )


# --------------------------------------------------------------------------
# Puntos
# --------------------------------------------------------------------------


class TipoEvento(StrEnum):
    """Motivos por los que el sistema otorga puntos.

    El valor es el que queda guardado en la bitacora de eventos, de modo que
    cualquier total sea reconstruible: los puntos no se guardan como un numero
    suelto que haya que creer, sino como la suma de hechos con fecha y motivo.
    """

    SESION = "sesion"
    VOLUMEN = "volumen"
    SESION_PRESCRITA = "sesion_prescrita"
    MARCA_PERSONAL = "marca_personal"
    RACHA_SEMANAL = "racha_semanal"
    AVANCE_SEMANAL = "avance_semanal"
    ADHERENCIA = "adherencia"
    DESCANSO_RESPETADO = "descanso_respetado"
    LOGRO = "logro"


#: Como se lee cada motivo en la pantalla que explica de donde salen los puntos.
#: Un sistema de recompensas cuyas reglas no se pueden leer no motiva: desconcierta.
MOTIVOS: dict[TipoEvento, str] = {
    TipoEvento.SESION: "Registrar la sesión del día",
    TipoEvento.VOLUMEN: "Volumen de carga de la sesión",
    TipoEvento.SESION_PRESCRITA: "Cumplir la sesión que tocaba",
    TipoEvento.MARCA_PERSONAL: "Marca personal nueva",
    TipoEvento.RACHA_SEMANAL: "Semanas seguidas entrenando",
    TipoEvento.AVANCE_SEMANAL: "Anotar el peso de la semana",
    TipoEvento.ADHERENCIA: "Seguir el plan de comidas",
    TipoEvento.DESCANSO_RESPETADO: "Respetar los días de descanso",
    TipoEvento.LOGRO: "Insignia conseguida",
}

PUNTOS_POR_SESION = 100
PUNTOS_POR_SESION_PRESCRITA = 25
PUNTOS_POR_MARCA = 60
PUNTOS_POR_AVANCE_SEMANAL = 60
PUNTOS_POR_ADHERENCIA = 40
PUNTOS_POR_DESCANSO = 30

# Marcas que puntuan en una misma sesion. Sin este limite, la primera sesion de
# un usuario nuevo —donde todo ejercicio es marca personal por no tener
# antecedente— valdria mas que un mes de trabajo.
MARCAS_QUE_PUNTUAN_POR_SESION = 2

# Adherencia nutricional desde la cual el registro semanal puntua. Es el mismo
# umbral con que `servicios.progreso` decide si tiene sentido reajustar el plan.
ADHERENCIA_QUE_PUNTUA = 80

KILOGRAMOS_POR_PUNTO_DE_VOLUMEN = 250
PUNTOS_MAXIMOS_POR_VOLUMEN = 40
#: Volumen desde el que un kilogramo mas ya no suma nada.
VOLUMEN_CON_TECHO_KG = KILOGRAMOS_POR_PUNTO_DE_VOLUMEN * PUNTOS_MAXIMOS_POR_VOLUMEN

PUNTOS_POR_SEMANA_DE_RACHA = 10
PUNTOS_MAXIMOS_POR_RACHA = 80


def puntos_por_volumen(volumen_kg: float) -> int:
    """Puntos que aporta el volumen de carga de una sesion, con techo.

    El techo es la regla de seguridad del modulo: a partir de
    `VOLUMEN_CON_TECHO_KG` el sistema deja de recompensar mas carga, porque
    seguir recompensandola seria pedirle al usuario que entrene por encima de lo
    que su rutina prescribe.
    """
    if volumen_kg <= 0:
        return 0
    return min(
        int(volumen_kg // KILOGRAMOS_POR_PUNTO_DE_VOLUMEN), PUNTOS_MAXIMOS_POR_VOLUMEN
    )


def puntos_por_racha(semanas: int) -> int:
    """Puntos de la racha de la semana, crecientes y con techo.

    Crecen para que la semana octava valga mas que la segunda, y tienen techo
    para que perder una racha larga no se sienta como perder todo lo ganado:
    quien reinicia vuelve a los diez puntos, no a cero puntos posibles.
    """
    if semanas <= 0:
        return 0
    return min(semanas * PUNTOS_POR_SEMANA_DE_RACHA, PUNTOS_MAXIMOS_POR_RACHA)


# --------------------------------------------------------------------------
# Logros
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Trayectoria:
    """Los hechos del historial del usuario contra los que se miden los logros.

    Es una fotografia: la arma el servicio a partir de la bitacora y del registro
    de avance, y este modulo la lee sin saber de donde vino. Asi las condiciones
    de los logros son funciones puras y se pueden probar sin base de datos.
    """

    sesiones_totales: int = 0
    racha_semanas: int = 0
    racha_maxima_semanas: int = 0
    volumen_acumulado_kg: float = 0.0
    marcas_personales: int = 0
    semanas_completas: int = 0
    grupos_en_una_semana: int = 0
    pesajes_consecutivos: int = 0
    adherencia_maxima: int = 0
    sesiones_de_madrugada: int = 0
    semanas_sin_exceso: int = 0


@dataclass(frozen=True)
class Logro:
    """Una insignia: quien la consigue, como se anuncia y cuanto vale.

    `pista` es el texto que se muestra mientras la insignia esta bloqueada. Una
    insignia bloqueada sin pista es decoracion; con pista es un objetivo.
    """

    clave: str
    nombre: str
    descripcion: str
    pista: str
    puntos: int
    categoria: str
    condicion: Callable[[Trayectoria], bool]


CONSTANCIA = "Constancia"
FUERZA = "Fuerza"
DISCIPLINA = "Disciplina"

LOGROS: tuple[Logro, ...] = (
    Logro(
        "primera_sesion",
        "Primer aullido",
        "Registró su primera sesión de entrenamiento.",
        "Registre su primera sesión en el gimnasio.",
        50,
        CONSTANCIA,
        lambda t: t.sesiones_totales >= 1,
    ),
    Logro(
        "diez_sesiones",
        "Diez veces",
        "Diez sesiones registradas.",
        "Registre 10 sesiones.",
        100,
        CONSTANCIA,
        lambda t: t.sesiones_totales >= 10,
    ),
    Logro(
        "cincuenta_sesiones",
        "Medio centenar",
        "Cincuenta sesiones registradas.",
        "Registre 50 sesiones.",
        250,
        CONSTANCIA,
        lambda t: t.sesiones_totales >= 50,
    ),
    Logro(
        "cien_sesiones",
        "Cien sesiones",
        "Cien sesiones registradas.",
        "Registre 100 sesiones.",
        500,
        CONSTANCIA,
        lambda t: t.sesiones_totales >= 100,
    ),
    Logro(
        "racha_4",
        "Un mes sin faltar",
        "Cuatro semanas seguidas con entrenamiento.",
        "Entrene al menos una vez por semana, cuatro semanas seguidas.",
        150,
        CONSTANCIA,
        lambda t: t.racha_maxima_semanas >= 4,
    ),
    Logro(
        "racha_12",
        "Un trimestre",
        "Doce semanas seguidas con entrenamiento.",
        "Sostenga la racha doce semanas.",
        400,
        CONSTANCIA,
        lambda t: t.racha_maxima_semanas >= 12,
    ),
    Logro(
        "racha_26",
        "Medio año de manada",
        "Veintiséis semanas seguidas con entrenamiento.",
        "Sostenga la racha veintiséis semanas.",
        800,
        CONSTANCIA,
        lambda t: t.racha_maxima_semanas >= 26,
    ),
    Logro(
        "primera_marca",
        "Marca propia",
        "Estableció su primera marca personal.",
        "Levante su primera carga registrada en un ejercicio.",
        60,
        FUERZA,
        lambda t: t.marcas_personales >= 1,
    ),
    Logro(
        "diez_marcas",
        "Diez marcas",
        "Tiene marca personal en diez ejercicios distintos.",
        "Consiga marca personal en 10 ejercicios.",
        200,
        FUERZA,
        lambda t: t.marcas_personales >= 10,
    ),
    Logro(
        "una_tonelada",
        "Una tonelada",
        "Mil kilogramos de volumen de carga acumulado.",
        "Acumule 1,000 kg de volumen de carga.",
        80,
        FUERZA,
        lambda t: t.volumen_acumulado_kg >= 1_000,
    ),
    Logro(
        "diez_toneladas",
        "Diez toneladas",
        "Diez mil kilogramos de volumen de carga acumulado.",
        "Acumule 10,000 kg de volumen de carga.",
        150,
        FUERZA,
        lambda t: t.volumen_acumulado_kg >= 10_000,
    ),
    Logro(
        "cien_toneladas",
        "Cien toneladas",
        "Cien mil kilogramos de volumen de carga acumulado.",
        "Acumule 100,000 kg de volumen de carga.",
        400,
        FUERZA,
        lambda t: t.volumen_acumulado_kg >= 100_000,
    ),
    Logro(
        "semana_completa",
        "Semana redonda",
        "Cumplió en una semana todas las sesiones que su rutina prescribe.",
        "Complete en una semana todas las sesiones de su rutina.",
        120,
        DISCIPLINA,
        lambda t: t.semanas_completas >= 1,
    ),
    Logro(
        "cuerpo_completo",
        "Sin saltarse nada",
        "Trabajó tres grupos musculares distintos en una misma semana.",
        "Trabaje tres grupos musculares distintos en una semana.",
        150,
        DISCIPLINA,
        lambda t: t.grupos_en_una_semana >= 3,
    ),
    Logro(
        "cuatro_pesajes",
        "Balanza fiel",
        "Cuatro pesajes semanales consecutivos.",
        "Anote su peso cuatro semanas seguidas.",
        150,
        DISCIPLINA,
        lambda t: t.pesajes_consecutivos >= 4,
    ),
    Logro(
        "plan_al_dia",
        "Plan al día",
        "Reportó un cumplimiento del plan de comidas del 90 % o más.",
        "Reporte un cumplimiento del plan de comidas del 90 % o más.",
        100,
        DISCIPLINA,
        lambda t: t.adherencia_maxima >= 90,
    ),
    Logro(
        "madrugador",
        "Antes del sol",
        "Registró una sesión antes de las siete de la mañana.",
        "Registre una sesión antes de las 7:00.",
        60,
        DISCIPLINA,
        lambda t: t.sesiones_de_madrugada >= 1,
    ),
    Logro(
        "descanso_respetado",
        "El descanso también entrena",
        "Cuatro semanas sin exceder los días que prescribe su plan.",
        "Pase cuatro semanas sin exceder los días que prescribe su plan.",
        200,
        DISCIPLINA,
        lambda t: t.semanas_sin_exceso >= 4,
    ),
)

LOGROS_POR_CLAVE: dict[str, Logro] = {logro.clave: logro for logro in LOGROS}

#: Orden en que las categorias se dibujan en la pantalla de insignias.
CATEGORIAS: tuple[str, ...] = (CONSTANCIA, FUERZA, DISCIPLINA)


def logros_cumplidos(trayectoria: Trayectoria) -> tuple[str, ...]:
    """Claves de los logros que el historial del usuario ya satisface.

    Devuelve todos los cumplidos, no solo los nuevos: quien decide cuales son
    nuevos es el servicio, que es el unico que sabe cuales estaban ya guardados.
    """
    return tuple(logro.clave for logro in LOGROS if logro.condicion(trayectoria))


# --------------------------------------------------------------------------
# Animo de la mascota
# --------------------------------------------------------------------------


class Animo(StrEnum):
    """Estado con que se dibuja la mascota.

    La mascota no es un adorno con una sola pose: es el canal por el que el
    sistema dice en una imagen lo que la pantalla dice en cifras. Cada estado
    corresponde a una situacion real del usuario, y por eso se decide aqui, del
    lado del servidor, y no en la interfaz: la situacion se deduce de la
    bitacora completa, que la interfaz no tiene.
    """

    SALUDO = "saludo"
    ANIMANDO = "animando"
    ENTRENANDO = "entrenando"
    DESCANSO = "descanso"
    DORMIDO = "dormido"
    ALERTA = "alerta"
    CELEBRANDO = "celebrando"
    PENSANDO = "pensando"


# Dias sin entrenar tras los cuales la mascota aparece dormida. Por debajo de
# este plazo, un usuario que entrena tres veces por semana veria al lobo dormido
# cada dia de descanso, y el estado dejaria de significar nada.
DIAS_PARA_DORMIR = 10

# Dia de la semana —lunes es 1— desde el que una semana sin sesiones pone en
# riesgo la racha. Antes del jueves todavia no hay nada que advertir.
DIA_EN_QUE_LA_RACHA_PELIGRA = 4


def animo_del_usuario(
    *,
    sesiones_totales: int,
    dias_desde_la_ultima_sesion: int | None,
    sesiones_esta_semana: int,
    racha_semanas: int,
    dia_de_la_semana: int,
    entreno_hoy: bool,
    toca_sesion_hoy: bool,
) -> Animo:
    """Decide con que animo se dibuja la mascota.

    El orden de las comprobaciones es la prioridad: felicitar a quien acaba de
    entrenar importa mas que advertirle de una racha, y advertir de una racha en
    riesgo importa mas que saludar.
    """
    if sesiones_totales == 0:
        return Animo.PENSANDO
    if entreno_hoy:
        return Animo.ANIMANDO
    if (
        dias_desde_la_ultima_sesion is not None
        and dias_desde_la_ultima_sesion >= DIAS_PARA_DORMIR
    ):
        return Animo.DORMIDO
    if (
        racha_semanas > 0
        and sesiones_esta_semana == 0
        and dia_de_la_semana >= DIA_EN_QUE_LA_RACHA_PELIGRA
    ):
        return Animo.ALERTA
    if toca_sesion_hoy:
        return Animo.ENTRENANDO
    if sesiones_esta_semana > 0:
        return Animo.DESCANSO
    return Animo.SALUDO
