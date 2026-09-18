"""Otorgamiento de puntos, evaluacion de insignias y armado de la senda.

Este modulo es el unico que escribe eventos de juego. Las dos puertas por las
que entra el avance del usuario —registrar una sesion de gimnasio y anotar el
peso de la semana— lo invocan al terminar su propio trabajo, de modo que los
puntos sean una consecuencia de lo que el usuario hizo y no algo que se pueda
pedir por separado: no existe ninguna ruta que sume puntos.

Hay una decision que conviene explicar porque no es la obvia. Las insignias se
reevaluan enteras en cada otorgamiento, contra el historial completo, en lugar
de comprobar solo la que podria haberse desbloqueado. Cuesta unas consultas mas
—que son las mismas que el resumen de la bitacora ya hace— y a cambio el sistema
se vuelve autocorrectivo: una insignia agregada al catalogo despues de que el
usuario ya cumplia su condicion se le concede la proxima vez que entrene, sin
proceso de migracion ni tarea programada. Con la comprobacion puntual, esa
insignia no se habria concedido nunca.

Todas las consultas se filtran por el identificador de la cuenta en sesion, en
cumplimiento de la regla del negocio *f* del apartado 4.3.4.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.modelos.entrenamiento import SerieRealizada, SesionRealizada
from app.modelos.juego import EventoJuego, LogroObtenido
from app.modelos.perfil import PerfilBiometrico, RegistroProgreso
from app.modelos.plan import SesionEntrenamiento
from app.modelos.usuario import Usuario
from app.motor import juego as motor
from app.motor.juego import Animo, TipoEvento

bitacora = logging.getLogger(__name__)

DIAS_POR_SEMANA = 7

# Sesiones de la bitacora que se recorren para armar la trayectoria. Es el mismo
# limite que usa el resumen de la bitacora: doscientas sesiones son mas de un ano
# de entrenamiento a cuatro por semana.
SESIONES_A_CONSIDERAR = 200

# Dias de entrenamiento por semana que se suponen cuando el usuario no tiene
# perfil biometrico. Es el valor por omision de la propia entidad.
DIAS_PRESCRITOS_POR_OMISION = 3


# --------------------------------------------------------------------------
# Resultado de un otorgamiento
# --------------------------------------------------------------------------


@dataclass
class PuntoGanado:
    """Un motivo por el que se acaba de sumar puntos, tal como se le muestra."""

    tipo: TipoEvento
    motivo: str
    puntos: int


@dataclass
class Recompensa:
    """Lo que el usuario gano con la accion que acaba de realizar.

    La devuelve la misma respuesta que confirma la accion. Un sistema de puntos
    que solo se ve entrando a otra pantalla no cierra el circuito: el usuario
    tiene que enterarse en el momento, donde todavia esta el esfuerzo fresco.
    """

    puntos_ganados: int = 0
    puntos_totales: int = 0
    detalle: list[PuntoGanado] = field(default_factory=list)
    nivel_anterior: int = 1
    nivel_actual: int = 1
    nombre_nivel: str = motor.NIVELES[0].nombre
    logros_nuevos: list[str] = field(default_factory=list)

    @property
    def subio_de_nivel(self) -> bool:
        return self.nivel_actual > self.nivel_anterior


# --------------------------------------------------------------------------
# Escritura
# --------------------------------------------------------------------------


def _ya_otorgado(
    sesion: Session, usuario: Usuario, tipo: TipoEvento, referencia: str
) -> bool:
    """Indica si ese hecho concreto ya tiene sus puntos."""
    fila = sesion.execute(
        select(EventoJuego.id).where(
            EventoJuego.usuario_id == usuario.id,
            EventoJuego.tipo == str(tipo),
            EventoJuego.referencia == referencia,
        )
    ).first()
    return fila is not None


def _otorgar(
    sesion: Session,
    usuario: Usuario,
    tipo: TipoEvento,
    referencia: str,
    puntos: int,
) -> int:
    """Registra un evento y devuelve los puntos que efectivamente sumo.

    Devuelve cero cuando el hecho ya estaba pagado. La comprobacion se hace
    consultando, y no dejando que la restriccion de unicidad de la tabla lo
    resuelva, porque un error de integridad invalida la transaccion completa y
    se llevaria consigo los eventos ya encolados en la misma llamada. La
    restriccion sigue siendo la ultima guarda: si dos peticiones simultaneas
    llegaran a atravesar la comprobacion, la que pierde la carrera falla, y
    `recompensar_entrenamiento` absorbe ese fallo sin costarle al usuario la
    sesion que ya quedo guardada.
    """
    if puntos <= 0 or _ya_otorgado(sesion, usuario, tipo, referencia):
        return 0

    sesion.add(
        EventoJuego(
            usuario_id=usuario.id, tipo=str(tipo), referencia=referencia, puntos=puntos
        )
    )
    sesion.flush()
    return puntos


def puntos_totales(sesion: Session, usuario: Usuario) -> int:
    """Suma de los puntos del usuario."""
    total = sesion.execute(
        select(func.coalesce(func.sum(EventoJuego.puntos), 0)).where(
            EventoJuego.usuario_id == usuario.id
        )
    ).scalar_one()
    return int(total)


def _claves_obtenidas(sesion: Session, usuario: Usuario) -> dict[str, datetime]:
    """Insignias que el usuario ya tiene, con la fecha en que las consiguio."""
    filas = sesion.execute(
        select(LogroObtenido.clave, LogroObtenido.fecha).where(
            LogroObtenido.usuario_id == usuario.id
        )
    ).all()
    return {clave: fecha for clave, fecha in filas}


def _conceder_logros(
    sesion: Session, usuario: Usuario, trayectoria: motor.Trayectoria
) -> tuple[list[str], list[PuntoGanado]]:
    """Concede las insignias que el historial ya satisface y no estaban dadas."""
    obtenidas = set(_claves_obtenidas(sesion, usuario))
    nuevas: list[str] = []
    detalle: list[PuntoGanado] = []

    for clave in motor.logros_cumplidos(trayectoria):
        if clave in obtenidas:
            continue
        logro = motor.LOGROS_POR_CLAVE[clave]

        sesion.add(LogroObtenido(usuario_id=usuario.id, clave=clave))
        sesion.flush()

        ganados = _otorgar(sesion, usuario, TipoEvento.LOGRO, clave, logro.puntos)
        nuevas.append(clave)
        if ganados:
            detalle.append(PuntoGanado(TipoEvento.LOGRO, logro.nombre, ganados))

    return nuevas, detalle


def _cerrar(
    sesion: Session,
    usuario: Usuario,
    nivel_anterior: int,
    detalle: list[PuntoGanado],
    logros_nuevos: list[str],
) -> Recompensa:
    """Confirma la transaccion y arma la recompensa que se le devuelve al usuario."""
    sesion.commit()

    total = puntos_totales(sesion, usuario)
    avance = motor.avance_de_nivel(total)
    recompensa = Recompensa(
        puntos_ganados=sum(punto.puntos for punto in detalle),
        puntos_totales=total,
        detalle=detalle,
        nivel_anterior=nivel_anterior,
        nivel_actual=avance.nivel.numero,
        nombre_nivel=avance.nivel.nombre,
        logros_nuevos=logros_nuevos,
    )

    if recompensa.subio_de_nivel:
        bitacora.info(
            "Usuario %s subió al nivel %s (%s) con %s puntos.",
            usuario.id,
            recompensa.nivel_actual,
            recompensa.nombre_nivel,
            total,
        )
    return recompensa


def registrar_entrenamiento(
    sesion: Session, usuario: Usuario, realizada: SesionRealizada
) -> Recompensa:
    """Otorga los puntos de una sesion de gimnasio recien registrada.

    La sesion y su volumen se referencian por el dia, no por el identificador de
    la sesion registrada. Es lo que hace que la segunda sesion de un mismo dia no
    vuelva a pagar: el sistema no debe recompensar entrenar dos veces al dia.
    """
    nivel_anterior = motor.nivel_para(puntos_totales(sesion, usuario)).numero
    detalle: list[PuntoGanado] = []

    dia = realizada.fecha.isoformat()

    ganados = _otorgar(
        sesion, usuario, TipoEvento.SESION, dia, motor.PUNTOS_POR_SESION
    )
    if ganados:
        detalle.append(
            PuntoGanado(TipoEvento.SESION, motor.MOTIVOS[TipoEvento.SESION], ganados)
        )

    ganados = _otorgar(
        sesion,
        usuario,
        TipoEvento.VOLUMEN,
        dia,
        motor.puntos_por_volumen(realizada.volumen_kg),
    )
    if ganados:
        detalle.append(
            PuntoGanado(TipoEvento.VOLUMEN, motor.MOTIVOS[TipoEvento.VOLUMEN], ganados)
        )

    if realizada.sesion_id is not None:
        ganados = _otorgar(
            sesion,
            usuario,
            TipoEvento.SESION_PRESCRITA,
            f"sesion:{realizada.sesion_id}:{dia}",
            motor.PUNTOS_POR_SESION_PRESCRITA,
        )
        if ganados:
            detalle.append(
                PuntoGanado(
                    TipoEvento.SESION_PRESCRITA,
                    motor.MOTIVOS[TipoEvento.SESION_PRESCRITA],
                    ganados,
                )
            )

    detalle.extend(_puntos_por_marcas(sesion, usuario, realizada))

    historial = _historial(sesion, usuario)
    racha = _racha_de_semanas(historial.semanas_con_sesion, _inicio_de_semana(date.today()))
    ganados = _otorgar(
        sesion,
        usuario,
        TipoEvento.RACHA_SEMANAL,
        f"semana:{_inicio_de_semana(realizada.fecha).isoformat()}",
        motor.puntos_por_racha(racha),
    )
    if ganados:
        detalle.append(
            PuntoGanado(
                TipoEvento.RACHA_SEMANAL, motor.MOTIVOS[TipoEvento.RACHA_SEMANAL], ganados
            )
        )

    nuevos, detalle_logros = _conceder_logros(
        sesion, usuario, _trayectoria(sesion, usuario, historial)
    )
    detalle.extend(detalle_logros)

    return _cerrar(sesion, usuario, nivel_anterior, detalle, nuevos)


def _puntos_por_marcas(
    sesion: Session, usuario: Usuario, realizada: SesionRealizada
) -> list[PuntoGanado]:
    """Puntos de las marcas personales que la sesion establecio.

    Una marca se referencia por ejercicio y por carga, de modo que cada carga
    nueva se pague una sola vez y repetirla no vuelva a pagar. Se limitan a
    `MARCAS_QUE_PUNTUAN_POR_SESION`, porque en la primera sesion de un usuario
    todo ejercicio es marca por no tener antecedente.
    """
    mejor_por_ejercicio: dict[int, float] = {}
    for serie in realizada.series:
        if serie.peso_kg is None:
            continue
        peso = float(serie.peso_kg)
        if peso > mejor_por_ejercicio.get(serie.ejercicio_id, 0.0):
            mejor_por_ejercicio[serie.ejercicio_id] = peso

    detalle: list[PuntoGanado] = []
    for ejercicio_id, peso in sorted(
        mejor_por_ejercicio.items(), key=lambda par: par[1], reverse=True
    ):
        if len(detalle) >= motor.MARCAS_QUE_PUNTUAN_POR_SESION:
            break
        if not _es_marca_personal(sesion, usuario, ejercicio_id, peso, realizada.id):
            continue
        ganados = _otorgar(
            sesion,
            usuario,
            TipoEvento.MARCA_PERSONAL,
            f"ejercicio:{ejercicio_id}:{peso:.2f}",
            motor.PUNTOS_POR_MARCA,
        )
        if ganados:
            detalle.append(
                PuntoGanado(
                    TipoEvento.MARCA_PERSONAL,
                    motor.MOTIVOS[TipoEvento.MARCA_PERSONAL],
                    ganados,
                )
            )
    return detalle


def _es_marca_personal(
    sesion: Session,
    usuario: Usuario,
    ejercicio_id: int,
    peso: float,
    excluyendo_sesion: int,
) -> bool:
    """Indica si esa carga supera todo lo anterior del usuario en el ejercicio.

    La sesion que se acaba de registrar se excluye de la comparacion: si se
    incluyera, la carga se compararia contra si misma y nunca seria marca.
    """
    anterior = sesion.execute(
        select(func.max(SerieRealizada.peso_kg))
        .join(
            SesionRealizada, SesionRealizada.id == SerieRealizada.sesion_realizada_id
        )
        .where(
            SesionRealizada.usuario_id == usuario.id,
            SesionRealizada.id != excluyendo_sesion,
            SerieRealizada.ejercicio_id == ejercicio_id,
        )
    ).scalar_one()
    return anterior is None or peso > float(anterior)


def registrar_avance_semanal(
    sesion: Session, usuario: Usuario, registro: RegistroProgreso
) -> Recompensa:
    """Otorga los puntos del pesaje semanal.

    Los tres motivos se referencian por la semana del registro: anotar el peso
    dos veces en la misma semana no paga dos veces, porque el dato que el sistema
    necesita para reajustar el plan es uno por semana.
    """
    nivel_anterior = motor.nivel_para(puntos_totales(sesion, usuario)).numero
    detalle: list[PuntoGanado] = []

    semana = f"semana:{_inicio_de_semana(registro.fecha_registro.date()).isoformat()}"

    ganados = _otorgar(
        sesion, usuario, TipoEvento.AVANCE_SEMANAL, semana, motor.PUNTOS_POR_AVANCE_SEMANAL
    )
    if ganados:
        detalle.append(
            PuntoGanado(
                TipoEvento.AVANCE_SEMANAL, motor.MOTIVOS[TipoEvento.AVANCE_SEMANAL], ganados
            )
        )

    if (registro.adherencia_nutricional or 0) >= motor.ADHERENCIA_QUE_PUNTUA:
        ganados = _otorgar(
            sesion, usuario, TipoEvento.ADHERENCIA, semana, motor.PUNTOS_POR_ADHERENCIA
        )
        if ganados:
            detalle.append(
                PuntoGanado(
                    TipoEvento.ADHERENCIA, motor.MOTIVOS[TipoEvento.ADHERENCIA], ganados
                )
            )

    historial = _historial(sesion, usuario)
    # Los puntos por descanso se pagan aqui y no al registrar la sesion porque
    # solo al cerrar la semana se sabe si el usuario se paso de sus dias.
    if 0 < registro.sesiones_cumplidas <= historial.dias_prescritos:
        ganados = _otorgar(
            sesion, usuario, TipoEvento.DESCANSO_RESPETADO, semana, motor.PUNTOS_POR_DESCANSO
        )
        if ganados:
            detalle.append(
                PuntoGanado(
                    TipoEvento.DESCANSO_RESPETADO,
                    motor.MOTIVOS[TipoEvento.DESCANSO_RESPETADO],
                    ganados,
                )
            )

    nuevos, detalle_logros = _conceder_logros(
        sesion, usuario, _trayectoria(sesion, usuario, historial)
    )
    detalle.extend(detalle_logros)

    return _cerrar(sesion, usuario, nivel_anterior, detalle, nuevos)


def recompensar_entrenamiento(
    sesion: Session, usuario: Usuario, realizada: SesionRealizada
) -> Recompensa | None:
    """Otorga los puntos de la sesion sin arriesgar el registro de la sesion.

    Los puntos son un añadido sobre un dato que ya quedo guardado y confirmado.
    Un fallo aqui —una insignia mal definida, un choque de concurrencia que no se
    previo— no debe costarle al usuario el entrenamiento que acaba de anotar ni
    devolverle un error por algo que ya se guardo bien. Se registra en la
    bitacora del servicio, la respuesta sale sin recompensa y los puntos se
    recuperan la proxima vez, porque las insignias se reevaluan completas y los
    eventos de la sesion se referencian por su dia.
    """
    try:
        return registrar_entrenamiento(sesion, usuario, realizada)
    except Exception:  # noqa: BLE001
        sesion.rollback()
        bitacora.exception(
            "No se pudieron otorgar los puntos de la sesión %s del usuario %s.",
            realizada.id,
            usuario.id,
        )
        return None


def recompensar_avance_semanal(
    sesion: Session, usuario: Usuario, registro: RegistroProgreso
) -> Recompensa | None:
    """Otorga los puntos del pesaje sin arriesgar el registro ni el reajuste.

    Misma tolerancia que `recompensar_entrenamiento`, y por el mismo motivo: el
    reajuste del plan de la historia HU-09 ya se ejecuto y se confirmo.
    """
    try:
        return registrar_avance_semanal(sesion, usuario, registro)
    except Exception:  # noqa: BLE001
        sesion.rollback()
        bitacora.exception(
            "No se pudieron otorgar los puntos del avance %s del usuario %s.",
            registro.id,
            usuario.id,
        )
        return None


# --------------------------------------------------------------------------
# Lectura del historial
# --------------------------------------------------------------------------


@dataclass
class Historial:
    """Lo que se lee una sola vez de la base de datos para todo lo demas.

    Armar la trayectoria, calcular la racha y decidir el animo de la mascota
    necesitan los mismos datos. Sin esta estructura intermedia, cada uno los
    volveria a consultar.
    """

    sesiones: list[SesionRealizada] = field(default_factory=list)
    registros: list[RegistroProgreso] = field(default_factory=list)
    grupos_por_sesion: dict[int, str] = field(default_factory=dict)
    dias_prescritos: int = DIAS_PRESCRITOS_POR_OMISION

    @property
    def semanas_con_sesion(self) -> set[date]:
        return {_inicio_de_semana(s.fecha) for s in self.sesiones}


def _historial(sesion: Session, usuario: Usuario) -> Historial:
    """Recupera la bitacora, el avance semanal y los dias que el plan prescribe."""
    sesiones = list(
        sesion.execute(
            select(SesionRealizada)
            .where(SesionRealizada.usuario_id == usuario.id)
            .options(selectinload(SesionRealizada.series))
            .order_by(SesionRealizada.fecha.desc(), SesionRealizada.id.desc())
            .limit(SESIONES_A_CONSIDERAR)
        ).scalars()
    )

    registros = list(
        sesion.execute(
            select(RegistroProgreso)
            .where(RegistroProgreso.usuario_id == usuario.id)
            .order_by(RegistroProgreso.fecha_registro.asc())
        ).scalars()
    )

    # Grupo muscular de cada sesion prescrita que la bitacora referencia. Es lo
    # que permite saber si una semana toco grupos distintos o repitio el mismo.
    identificadores = {s.sesion_id for s in sesiones if s.sesion_id is not None}
    grupos: dict[int, str] = {}
    if identificadores:
        filas = sesion.execute(
            select(SesionEntrenamiento.id, SesionEntrenamiento.grupo_muscular).where(
                SesionEntrenamiento.id.in_(identificadores)
            )
        ).all()
        # El grupo muscular es un tipo enumerado. Se guarda su valor de texto
        # porque lo unico que se hace con el es contar cuantos distintos hubo en
        # una semana, y el texto es estable entre procesos.
        grupos = {identificador: str(grupo) for identificador, grupo in filas}

    perfil = sesion.execute(
        select(PerfilBiometrico.dias_entrenamiento_semana)
        .where(PerfilBiometrico.usuario_id == usuario.id)
        .order_by(PerfilBiometrico.fecha_registro.desc())
        .limit(1)
    ).scalar_one_or_none()

    return Historial(
        sesiones=sesiones,
        registros=registros,
        grupos_por_sesion=grupos,
        dias_prescritos=perfil or DIAS_PRESCRITOS_POR_OMISION,
    )


def _inicio_de_semana(dia: date) -> date:
    """Lunes de la semana a la que pertenece la fecha."""
    return dia - timedelta(days=dia.weekday())


def _racha_de_semanas(semanas: set[date], esta_semana: date) -> int:
    """Semanas consecutivas con al menos una sesion.

    Repite la regla de `servicios.entrenamiento._racha_de_semanas`, incluida la
    tolerancia de la semana en curso: quien entrena los jueves no debe ver su
    racha en cero cada lunes. Si las dos reglas divergieran, el panel y la senda
    mostrarian rachas distintas para el mismo usuario.
    """
    if not semanas:
        return 0

    inicio = (
        esta_semana
        if esta_semana in semanas
        else esta_semana - timedelta(days=DIAS_POR_SEMANA)
    )
    if inicio not in semanas:
        return 0

    racha = 0
    cursor = inicio
    while cursor in semanas:
        racha += 1
        cursor -= timedelta(days=DIAS_POR_SEMANA)
    return racha


def _racha_maxima(semanas: set[date]) -> int:
    """La racha mas larga que el usuario haya sostenido.

    Los logros se miden contra esta y no contra la racha en curso: una insignia
    que se pierde al faltar una semana no premia lo que ya se hizo, y lo que ya
    se hizo es un hecho.
    """
    if not semanas:
        return 0

    mejor = 0
    for semana in semanas:
        # Solo se cuenta desde el inicio de cada tramo, para no recorrer el mismo
        # tramo una vez por semana que lo compone.
        if semana - timedelta(days=DIAS_POR_SEMANA) in semanas:
            continue
        largo = 0
        cursor = semana
        while cursor in semanas:
            largo += 1
            cursor += timedelta(days=DIAS_POR_SEMANA)
        mejor = max(mejor, largo)
    return mejor


def _trayectoria(
    sesion: Session, usuario: Usuario, historial: Historial
) -> motor.Trayectoria:
    """Convierte el historial en la fotografia contra la que se miden los logros."""
    sesiones = historial.sesiones
    semanas = historial.semanas_con_sesion

    por_semana: dict[date, list[SesionRealizada]] = defaultdict(list)
    for realizada in sesiones:
        por_semana[_inicio_de_semana(realizada.fecha)].append(realizada)

    grupos_en_una_semana = 0
    semanas_completas = 0
    for _, de_la_semana in por_semana.items():
        distintos = {
            historial.grupos_por_sesion[s.sesion_id]
            for s in de_la_semana
            if s.sesion_id is not None and s.sesion_id in historial.grupos_por_sesion
        }
        grupos_en_una_semana = max(grupos_en_una_semana, len(distintos))
        if len(de_la_semana) >= historial.dias_prescritos:
            semanas_completas += 1

    # Semanas seguidas, hasta la ultima cerrada, en que el usuario no se paso de
    # los dias que su plan prescribe. La semana en curso no cuenta: todavia puede
    # excederse en ella.
    esta_semana = _inicio_de_semana(date.today())
    sin_exceso = 0
    cursor = esta_semana - timedelta(days=DIAS_POR_SEMANA)
    while cursor in por_semana:
        if len(por_semana[cursor]) > historial.dias_prescritos:
            break
        sin_exceso += 1
        cursor -= timedelta(days=DIAS_POR_SEMANA)

    marcas = sesion.execute(
        select(func.count(func.distinct(SerieRealizada.ejercicio_id)))
        .join(
            SesionRealizada, SesionRealizada.id == SerieRealizada.sesion_realizada_id
        )
        .where(
            SesionRealizada.usuario_id == usuario.id,
            SerieRealizada.peso_kg.is_not(None),
        )
    ).scalar_one()

    return motor.Trayectoria(
        sesiones_totales=len(sesiones),
        racha_semanas=_racha_de_semanas(semanas, esta_semana),
        racha_maxima_semanas=_racha_maxima(semanas),
        volumen_acumulado_kg=round(sum(s.volumen_kg for s in sesiones), 1),
        marcas_personales=int(marcas or 0),
        semanas_completas=semanas_completas,
        grupos_en_una_semana=grupos_en_una_semana,
        pesajes_consecutivos=_pesajes_consecutivos(historial.registros),
        adherencia_maxima=max(
            (r.adherencia_nutricional or 0 for r in historial.registros), default=0
        ),
        sesiones_de_madrugada=sum(
            1
            for s in sesiones
            if s.fecha_registro is not None and s.fecha_registro.hour < 7
        ),
        semanas_sin_exceso=sin_exceso,
    )


def _pesajes_consecutivos(registros: list[RegistroProgreso]) -> int:
    """La tanda mas larga de pesajes en semanas seguidas.

    Se cuenta por semana y no por registro: dos pesajes en la misma semana son
    un solo dato para el reajuste del plan y no deberian valer como dos. Y se
    devuelve la tanda mas larga, no la que llega hasta hoy, por lo mismo que la
    racha maxima: una insignia no deberia perderse por una semana faltada.
    """
    if not registros:
        return 0

    semanas = sorted({_inicio_de_semana(r.fecha_registro.date()) for r in registros})
    mejor = 1
    seguidas = 1
    for anterior, actual in zip(semanas, semanas[1:], strict=False):
        seguidas = (
            seguidas + 1 if actual - anterior == timedelta(days=DIAS_POR_SEMANA) else 1
        )
        mejor = max(mejor, seguidas)
    return mejor


# --------------------------------------------------------------------------
# Estado completo para la pantalla de la senda
# --------------------------------------------------------------------------


@dataclass
class Hito:
    """Un momento del camino recorrido: un nivel alcanzado o una insignia."""

    tipo: str
    titulo: str
    detalle: str
    fecha: datetime
    puntos: int = 0


def estado(sesion: Session, usuario: Usuario, toca_sesion_hoy: bool = False) -> dict:
    """Todo lo que la pantalla de la senda y el panel necesitan, en una consulta.

    Se arma completo del lado del servidor por la misma razon que el reporte de
    evolucion: la interfaz solo dibuja, y las cifras son las mismas cualquiera
    que sea el dispositivo desde el que se consulten.
    """
    historial = _historial(sesion, usuario)
    trayectoria = _trayectoria(sesion, usuario, historial)
    total = puntos_totales(sesion, usuario)
    avance = motor.avance_de_nivel(total)

    hoy = date.today()
    ultima = historial.sesiones[0].fecha if historial.sesiones else None
    esta_semana = _inicio_de_semana(hoy)
    sesiones_esta_semana = sum(1 for s in historial.sesiones if s.fecha >= esta_semana)

    animo = motor.animo_del_usuario(
        sesiones_totales=trayectoria.sesiones_totales,
        dias_desde_la_ultima_sesion=(hoy - ultima).days if ultima else None,
        sesiones_esta_semana=sesiones_esta_semana,
        racha_semanas=trayectoria.racha_semanas,
        dia_de_la_semana=hoy.isoweekday(),
        entreno_hoy=ultima == hoy,
        toca_sesion_hoy=toca_sesion_hoy,
    )

    return {
        "nivel": avance.nivel.numero,
        "nombre_nivel": avance.nivel.nombre,
        "lema": avance.nivel.lema,
        "gala": avance.nivel.gala,
        "nivel_maximo": motor.NIVEL_MAXIMO,
        "puntos_totales": total,
        "puntos_en_el_nivel": avance.puntos_en_el_nivel,
        "puntos_del_tramo": avance.puntos_del_tramo,
        "puntos_para_el_proximo": avance.puntos_para_el_proximo,
        "porcentaje": avance.porcentaje,
        "nombre_proximo_nivel": avance.proximo.nombre if avance.proximo else None,
        "animo": animo,
        "racha_semanas": trayectoria.racha_semanas,
        "racha_maxima_semanas": trayectoria.racha_maxima_semanas,
        "sesiones_totales": trayectoria.sesiones_totales,
        "volumen_acumulado_kg": trayectoria.volumen_acumulado_kg,
        "marcas_personales": trayectoria.marcas_personales,
        "logros": _logros_publicos(sesion, usuario, trayectoria),
        "hitos": _camino_recorrido(sesion, usuario),
        "motivos": [
            {
                "motivo": texto,
                "puntos": _puntos_de_referencia(tipo),
                "variable": tipo in MOTIVOS_VARIABLES,
            }
            for tipo, texto in motor.MOTIVOS.items()
            if tipo != TipoEvento.LOGRO
        ],
    }


#: Motivos cuyos puntos dependen de la sesion. Se anuncian por su techo, y la
#: pantalla los escribe como «hasta +N»: escribir «hasta» delante de un valor
#: fijo seria falso, y escribir el techo sin «hasta» prometeria de mas.
MOTIVOS_VARIABLES = frozenset({TipoEvento.VOLUMEN, TipoEvento.RACHA_SEMANAL})


def _puntos_de_referencia(tipo: TipoEvento) -> int:
    """Cuanto vale cada motivo, para la lista que explica las reglas.

    Los motivos de `MOTIVOS_VARIABLES` se anuncian por su techo: es la cifra que
    el usuario puede tomar como referencia, y anunciar un valor que depende de la
    sesion obligaria a explicar la formula en la pantalla.
    """
    return {
        TipoEvento.SESION: motor.PUNTOS_POR_SESION,
        TipoEvento.VOLUMEN: motor.PUNTOS_MAXIMOS_POR_VOLUMEN,
        TipoEvento.SESION_PRESCRITA: motor.PUNTOS_POR_SESION_PRESCRITA,
        TipoEvento.MARCA_PERSONAL: motor.PUNTOS_POR_MARCA,
        TipoEvento.RACHA_SEMANAL: motor.PUNTOS_MAXIMOS_POR_RACHA,
        TipoEvento.AVANCE_SEMANAL: motor.PUNTOS_POR_AVANCE_SEMANAL,
        TipoEvento.ADHERENCIA: motor.PUNTOS_POR_ADHERENCIA,
        TipoEvento.DESCANSO_RESPETADO: motor.PUNTOS_POR_DESCANSO,
    }.get(tipo, 0)


def _logros_publicos(
    sesion: Session, usuario: Usuario, trayectoria: motor.Trayectoria
) -> list[dict]:
    """El catalogo completo de insignias, marcando las que el usuario ya tiene.

    Se devuelven todas, incluidas las bloqueadas: una insignia bloqueada con su
    pista es lo que le dice al usuario que hacer a continuacion. Lo que nunca se
    devuelve es una lista vacia para quien no tiene ninguna, porque entonces la
    pantalla no tendria nada que mostrar el primer dia.
    """
    obtenidas = _claves_obtenidas(sesion, usuario)
    return [
        {
            "clave": logro.clave,
            "nombre": logro.nombre,
            "descripcion": logro.descripcion,
            "pista": logro.pista,
            "puntos": logro.puntos,
            "categoria": logro.categoria,
            "obtenido": logro.clave in obtenidas,
            "fecha": obtenidas.get(logro.clave),
        }
        for logro in motor.LOGROS
    ]


def _camino_recorrido(sesion: Session, usuario: Usuario) -> list[Hito]:
    """El camino del usuario, del hito mas reciente al mas antiguo.

    Los niveles no tienen fecha propia guardada: se deducen recorriendo los
    eventos en orden y viendo en que momento el acumulado cruzo cada umbral. Es
    la razon por la que los puntos se guardan como bitacora y no como contador.
    """
    eventos = sesion.execute(
        select(EventoJuego.puntos, EventoJuego.fecha)
        .where(EventoJuego.usuario_id == usuario.id)
        .order_by(EventoJuego.fecha.asc(), EventoJuego.id.asc())
    ).all()

    hitos: list[Hito] = []
    acumulado = 0
    pendientes = [nivel for nivel in motor.NIVELES if nivel.numero > 1]
    for puntos, fecha in eventos:
        acumulado += puntos
        while pendientes and acumulado >= pendientes[0].xp_requerido:
            nivel = pendientes.pop(0)
            hitos.append(
                Hito(
                    tipo="nivel",
                    titulo=f"Nivel {nivel.numero}: {nivel.nombre}",
                    detalle=nivel.lema,
                    fecha=fecha,
                    puntos=nivel.xp_requerido,
                )
            )

    for clave, fecha in _claves_obtenidas(sesion, usuario).items():
        logro = motor.LOGROS_POR_CLAVE.get(clave)
        if logro is None:
            # Insignia retirada del catalogo. Se omite en lugar de romper la
            # pantalla de quien la consiguio cuando existia.
            continue
        hitos.append(
            Hito(
                tipo="logro",
                titulo=logro.nombre,
                detalle=logro.descripcion,
                fecha=fecha,
                puntos=logro.puntos,
            )
        )

    hitos.append(
        Hito(
            tipo="inicio",
            titulo="Se unió a la manada",
            detalle="Creó su cuenta y empezó el camino.",
            fecha=usuario.fecha_registro,
        )
    )

    hitos.sort(key=lambda hito: hito.fecha, reverse=True)
    return hitos
