"""Logica de la bitacora de entrenamiento y de la progresion de carga.

Une el registro de lo ejecutado con el motor de progresion. Es lo que convierte
la regla del negocio *d* del apartado 4.3.4 —el incremento de carga no supera el
10 % entre microciclos— de una funcion que nadie invocaba en una regla que
gobierna lo que el usuario ve cada vez que entra al gimnasio.

Todas las consultas se filtran por el identificador de la cuenta en sesion, en
cumplimiento de la regla del negocio *f*: la bitacora es un dato personal y solo
la ve su titular.
"""

import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.esquemas.entrenamiento import SesionEjecutadaEntrada
from app.modelos.catalogo import Ejercicio
from app.modelos.entrenamiento import SerieRealizada, SesionRealizada
from app.modelos.plan import EjercicioSesion, SesionEntrenamiento
from app.modelos.usuario import Usuario
from app.motor import progresion
from app.motor.progresion import EjecucionPrevia, Recomendacion, SerieEjecutada

bitacora = logging.getLogger(__name__)

DIAS_POR_SEMANA = 7

# Sesiones hacia atras que se revisan para saber cuantas veces seguidas se
# repitio la misma carga en un ejercicio. Mas alla de eso, el dato ya no
# describe el momento actual del usuario.
SESIONES_A_REVISAR = 8


class SesionNoEncontrada(Exception):
    """La sesion prescrita indicada no existe o no pertenece al usuario."""


class EjercicioNoEncontrado(Exception):
    """El ejercicio indicado no existe en el catalogo."""


# --------------------------------------------------------------------------
# Registro
# --------------------------------------------------------------------------


def registrar_sesion(
    sesion: Session, usuario: Usuario, datos: SesionEjecutadaEntrada
) -> SesionRealizada:
    """Guarda lo que el usuario hizo en el gimnasio.

    La sesion prescrita se comprueba contra el usuario antes de enlazarla: sin esa
    comprobacion, cualquiera podria asociar su bitacora a la sesion de otra
    persona con solo enviar su identificador.
    """
    prescrita = None
    if datos.sesion_id is not None:
        prescrita = _sesion_prescrita_del_usuario(sesion, usuario, datos.sesion_id)

    ejercicios_validos = {
        identificador
        for (identificador,) in sesion.execute(select(Ejercicio.id)).all()
    }
    for serie in datos.series:
        if serie.ejercicio_id not in ejercicios_validos:
            raise EjercicioNoEncontrado(serie.ejercicio_id)

    realizada = SesionRealizada(
        usuario_id=usuario.id,
        sesion_id=prescrita.id if prescrita is not None else None,
        plan_id=prescrita.plan_id if prescrita is not None else None,
        fecha=datos.fecha or date.today(),
        duracion_minutos=datos.duracion_minutos,
        percepcion_esfuerzo=datos.percepcion_esfuerzo,
        notas=datos.notas,
    )
    realizada.series = [
        SerieRealizada(
            ejercicio_id=serie.ejercicio_id,
            numero_serie=serie.numero_serie,
            repeticiones=serie.repeticiones,
            peso_kg=serie.peso_kg,
            repeticiones_en_reserva=serie.repeticiones_en_reserva,
        )
        for serie in datos.series
    ]

    sesion.add(realizada)
    sesion.commit()
    sesion.refresh(realizada)

    bitacora.info(
        "Usuario %s registró una sesión de %s series con %s kg de volumen.",
        usuario.id,
        len(realizada.series),
        realizada.volumen_kg,
    )
    return realizada


def _sesion_prescrita_del_usuario(
    sesion: Session, usuario: Usuario, sesion_id: int
) -> SesionEntrenamiento:
    """Recupera una sesion prescrita comprobando que pertenezca al usuario."""
    from app.modelos.plan import Plan

    sentencia = (
        select(SesionEntrenamiento)
        .join(Plan, Plan.id == SesionEntrenamiento.plan_id)
        .where(SesionEntrenamiento.id == sesion_id, Plan.usuario_id == usuario.id)
    )
    prescrita = sesion.execute(sentencia).scalar_one_or_none()
    if prescrita is None:
        raise SesionNoEncontrada(sesion_id)
    return prescrita


# --------------------------------------------------------------------------
# Consulta
# --------------------------------------------------------------------------


def listar_sesiones(
    sesion: Session, usuario: Usuario, limite: int = 60
) -> list[SesionRealizada]:
    """Bitacora del usuario, de la sesion mas reciente a la mas antigua."""
    sentencia = (
        select(SesionRealizada)
        .where(SesionRealizada.usuario_id == usuario.id)
        .options(selectinload(SesionRealizada.series))
        .order_by(SesionRealizada.fecha.desc(), SesionRealizada.id.desc())
        .limit(limite)
    )
    return list(sesion.execute(sentencia).scalars())


def hay_sesion_registrada(
    sesion: Session, usuario: Usuario, sesion_id: int, dia: date | None = None
) -> bool:
    """Indica si el usuario ya registro esa sesion prescrita en el dia indicado.

    Evita que la pantalla anime a registrar dos veces el mismo entrenamiento, que
    duplicaria el volumen y falsearia la progresion.
    """
    sentencia = select(SesionRealizada.id).where(
        SesionRealizada.usuario_id == usuario.id,
        SesionRealizada.sesion_id == sesion_id,
        SesionRealizada.fecha == (dia or date.today()),
    )
    return sesion.execute(sentencia).first() is not None


def ejecuciones_de_ejercicio(
    sesion: Session, usuario: Usuario, ejercicio_id: int, limite: int = SESIONES_A_REVISAR
) -> list[tuple[date, list[SerieRealizada], int | None]]:
    """Historial de un ejercicio agrupado por sesion, de la mas reciente hacia atras.

    Devuelve tripletas de fecha, series y percepcion del esfuerzo de la sesion.
    """
    sentencia = (
        select(SesionRealizada)
        .join(SerieRealizada, SerieRealizada.sesion_realizada_id == SesionRealizada.id)
        .where(
            SesionRealizada.usuario_id == usuario.id,
            SerieRealizada.ejercicio_id == ejercicio_id,
        )
        .options(selectinload(SesionRealizada.series))
        .order_by(SesionRealizada.fecha.desc(), SesionRealizada.id.desc())
        .distinct()
        .limit(limite)
    )
    realizadas = list(sesion.execute(sentencia).scalars())
    return [
        (
            realizada.fecha,
            [serie for serie in realizada.series if serie.ejercicio_id == ejercicio_id],
            realizada.percepcion_esfuerzo,
        )
        for realizada in realizadas
    ]


def _a_ejecucion(
    series: list[SerieRealizada], esfuerzo: int | None
) -> EjecucionPrevia:
    """Traduce las series guardadas a la forma que el motor de progresion espera."""
    return EjecucionPrevia(
        series=[
            SerieEjecutada(
                repeticiones=serie.repeticiones,
                peso_kg=float(serie.peso_kg) if serie.peso_kg is not None else None,
            )
            for serie in sorted(series, key=lambda s: s.numero_serie)
        ],
        percepcion_esfuerzo=esfuerzo,
    )


def _sesiones_sin_avanzar(
    historial: list[tuple[date, list[SerieRealizada], int | None]],
) -> int:
    """Cuenta cuantas sesiones seguidas se repitio la misma carga maxima.

    Es lo que distingue un estancamiento real de una semana suelta sin avance.
    """
    if len(historial) < 2:
        return 0

    def carga_maxima(series: list[SerieRealizada]) -> float | None:
        pesos = [float(s.peso_kg) for s in series if s.peso_kg is not None]
        return max(pesos) if pesos else None

    referencia = carga_maxima(historial[0][1])
    if referencia is None:
        return 0

    repeticiones = 1
    for _, series, _ in historial[1:]:
        if carga_maxima(series) != referencia:
            break
        repeticiones += 1
    return repeticiones


def recomendar_carga(
    sesion: Session,
    usuario: Usuario,
    ejercicio: Ejercicio,
    repeticiones_min: int,
    repeticiones_max: int,
) -> tuple[Recomendacion, list[SerieRealizada], date | None]:
    """Decide con cuanta carga entrenar un ejercicio la proxima vez.

    Devuelve la recomendacion junto con lo que se hizo la ultima vez, para que la
    pantalla pueda mostrar ambas cosas: la sugerencia sin el antecedente no se
    puede juzgar.
    """
    historial = ejecuciones_de_ejercicio(sesion, usuario, ejercicio.id)
    if not historial:
        return (
            progresion.calcular(
                None, repeticiones_min, repeticiones_max, ejercicio.es_compuesto
            ),
            [],
            None,
        )

    fecha, series, esfuerzo = historial[0]
    recomendacion = progresion.calcular(
        _a_ejecucion(series, esfuerzo),
        repeticiones_min,
        repeticiones_max,
        ejercicio.es_compuesto,
        sesiones_sin_avanzar=_sesiones_sin_avanzar(historial),
    )
    return recomendacion, sorted(series, key=lambda s: s.numero_serie), fecha


def progresiones_de_la_sesion(
    sesion: Session, usuario: Usuario, realizada: SesionRealizada
) -> list[Recomendacion]:
    """Recomendaciones para los ejercicios que la sesion recien registrada incluyo."""
    prescritos = _prescripcion_por_ejercicio(sesion, realizada.sesion_id)

    recomendaciones: list[Recomendacion] = []
    vistos: set[int] = set()
    for serie in realizada.series:
        if serie.ejercicio_id in vistos:
            continue
        vistos.add(serie.ejercicio_id)

        ejercicio = sesion.get(Ejercicio, serie.ejercicio_id)
        if ejercicio is None:
            continue
        rango = prescritos.get(serie.ejercicio_id, (8, 12))
        recomendacion, _, _ = recomendar_carga(sesion, usuario, ejercicio, *rango)
        recomendaciones.append(recomendacion)
    return recomendaciones


def _prescripcion_por_ejercicio(
    sesion: Session, sesion_id: int | None
) -> dict[int, tuple[int, int]]:
    """Rango de repeticiones que la sesion prescribio para cada ejercicio."""
    if sesion_id is None:
        return {}
    sentencia = select(EjercicioSesion).where(EjercicioSesion.sesion_id == sesion_id)
    return {
        prescrito.ejercicio_id: (prescrito.repeticiones_min, prescrito.repeticiones_max)
        for prescrito in sesion.execute(sentencia).scalars()
    }


# --------------------------------------------------------------------------
# Marcas y resumen
# --------------------------------------------------------------------------


def marca_personal(
    sesion: Session, usuario: Usuario, ejercicio_id: int
) -> tuple[float | None, int | None, date | None]:
    """Mejor carga registrada en un ejercicio, con sus repeticiones y su fecha."""
    sentencia = (
        select(SerieRealizada, SesionRealizada.fecha)
        .join(SesionRealizada, SesionRealizada.id == SerieRealizada.sesion_realizada_id)
        .where(
            SesionRealizada.usuario_id == usuario.id,
            SerieRealizada.ejercicio_id == ejercicio_id,
            SerieRealizada.peso_kg.is_not(None),
        )
        .order_by(SerieRealizada.peso_kg.desc(), SerieRealizada.repeticiones.desc())
        .limit(1)
    )
    fila = sesion.execute(sentencia).first()
    if fila is None:
        return None, None, None
    serie, fecha = fila
    return float(serie.peso_kg), serie.repeticiones, fecha


def _inicio_de_semana(dia: date) -> date:
    """Lunes de la semana a la que pertenece la fecha."""
    return dia - timedelta(days=dia.weekday())


def resumen(sesion: Session, usuario: Usuario) -> dict:
    """Cifras de la bitacora para el panel y los reportes."""
    todas = listar_sesiones(sesion, usuario, limite=200)

    hoy = date.today()
    esta_semana = _inicio_de_semana(hoy)
    semana_pasada = esta_semana - timedelta(days=DIAS_POR_SEMANA)

    de_esta = [s for s in todas if s.fecha >= esta_semana]
    de_la_pasada = [s for s in todas if semana_pasada <= s.fecha < esta_semana]

    return {
        "sesiones_totales": len(todas),
        "sesiones_esta_semana": len(de_esta),
        "sesiones_semana_pasada": len(de_la_pasada),
        "volumen_esta_semana_kg": round(sum(s.volumen_kg for s in de_esta), 1),
        "volumen_semana_pasada_kg": round(sum(s.volumen_kg for s in de_la_pasada), 1),
        "racha_semanas": _racha_de_semanas(todas, esta_semana),
        "ultima_sesion": todas[0].fecha if todas else None,
    }


def _racha_de_semanas(sesiones: list[SesionRealizada], esta_semana: date) -> int:
    """Semanas consecutivas con al menos una sesion registrada.

    La semana en curso no rompe la racha aunque todavia no tenga sesiones: quien
    entrena los jueves no deberia ver su racha en cero cada lunes.
    """
    if not sesiones:
        return 0

    semanas = {_inicio_de_semana(s.fecha) for s in sesiones}
    inicio = esta_semana if esta_semana in semanas else esta_semana - timedelta(
        days=DIAS_POR_SEMANA
    )
    if inicio not in semanas:
        return 0

    racha = 0
    cursor = inicio
    while cursor in semanas:
        racha += 1
        cursor -= timedelta(days=DIAS_POR_SEMANA)
    return racha


def sesiones_cumplidas_en_la_semana(sesion: Session, usuario: Usuario) -> int:
    """Sesiones registradas en la semana en curso.

    La usa el registro de progreso semanal para proponer el dato en lugar de
    pedirle al usuario que lo recuerde.
    """
    esta_semana = _inicio_de_semana(date.today())
    sentencia = select(SesionRealizada.id).where(
        SesionRealizada.usuario_id == usuario.id,
        SesionRealizada.fecha >= esta_semana,
    )
    return len(sesion.execute(sentencia).all())
