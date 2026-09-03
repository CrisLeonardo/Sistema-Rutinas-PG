"""Seguimiento del progreso y reajuste del plan (epica E4, historia HU-09).

El apartado 2.7 describe la retroalimentacion como el mecanismo por el cual la
salida del sistema se reintroduce como entrada, de modo que el sistema capture su
nuevo estado y reajuste sus variables para mantenerse orientado a su objetivo.
Este modulo implementa ese ciclo: el peso que el usuario reporta se convierte en
una medicion biometrica nueva, y esa medicion regenera el plan.

El reajuste no inventa un mecanismo propio de correccion calorica. Reutiliza la
misma cadena que genero el plan original —perfil biometrico, red neuronal,
reglas del negocio— con el peso actualizado, de modo que las reglas *b* y *c* se
sigan cumpliendo por construccion.
"""

import logging
from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.esquemas.progreso import RegistroProgresoEntrada, ResultadoReajuste
from app.modelos.enumeraciones import Objetivo
from app.modelos.perfil import PerfilBiometrico, RegistroProgreso
from app.modelos.plan import Plan
from app.modelos.usuario import Usuario
from app.servicios import perfil as servicio_perfil
from app.servicios import plan as servicio_plan

bitacora = logging.getLogger(__name__)

# Adherencia por debajo de la cual el sistema no reajusta el plan. Si el usuario
# no esta siguiendo el plan vigente, el estancamiento no se explica por un
# calculo erroneo, y bajar aun mas las calorias seria contraproducente.
ADHERENCIA_MINIMA_PARA_REAJUSTAR = 70

# Cambio de peso, como fraccion del peso corporal por semana, que se considera
# adecuado para cada objetivo (apartado 2.5.2). Fuera de estos limites el ritmo
# se advierte, aunque el plan se reajuste igual con el peso nuevo.
RITMOS_SEMANALES_ESPERADOS: dict[Objetivo, tuple[float, float]] = {
    # (minimo, maximo) como fraccion del peso corporal. Negativo es perdida.
    Objetivo.PERDIDA_GRASA: (-0.010, -0.002),
    Objetivo.MANTENIMIENTO: (-0.005, 0.005),
    Objetivo.GANANCIA_MUSCULAR: (0.001, 0.005),
}

# Diferencia de peso a partir de la cual se considera que el cuerpo cambio lo
# suficiente como para justificar recalcular el plan. Por debajo, la variacion
# cabe dentro de la fluctuacion normal de agua y contenido intestinal.
CAMBIO_MINIMO_PARA_REAJUSTAR_KG = 0.5

DIAS_POR_SEMANA = 7


class SinPlanVigente(Exception):
    """No se puede registrar progreso porque el usuario no tiene plan.

    Corresponde a la dependencia declarada en el apartado 4.6.3: la historia
    HU-09 opera sobre un plan previamente generado.
    """


def listar_progreso(sesion: Session, usuario: Usuario) -> list[RegistroProgreso]:
    """Devuelve los registros del usuario, del mas antiguo al mas reciente.

    El orden ascendente es el que necesitan las graficas de evolucion de la
    historia HU-10, que se leen de izquierda a derecha en el tiempo.
    """
    sentencia = (
        select(RegistroProgreso)
        .where(RegistroProgreso.usuario_id == usuario.id)
        .order_by(RegistroProgreso.fecha_registro.asc(), RegistroProgreso.id.asc())
    )
    return list(sesion.execute(sentencia).scalars())


def obtener_ultimo_registro(sesion: Session, usuario: Usuario) -> RegistroProgreso | None:
    """Recupera el registro de progreso mas reciente del usuario."""
    sentencia = (
        select(RegistroProgreso)
        .where(RegistroProgreso.usuario_id == usuario.id)
        .order_by(RegistroProgreso.fecha_registro.desc(), RegistroProgreso.id.desc())
        .limit(1)
    )
    return sesion.execute(sentencia).scalar_one_or_none()


def _ritmo_semanal(
    peso_actual: float, peso_previo: float, dias_transcurridos: int
) -> float | None:
    """Cambio de peso por semana, en kilogramos.

    Devuelve None cuando los dos registros son del mismo dia: sin tiempo
    transcurrido no hay ritmo que calcular.
    """
    if dias_transcurridos <= 0:
        return None
    semanas = dias_transcurridos / DIAS_POR_SEMANA
    return round((peso_actual - peso_previo) / semanas, 3)


def _describir_ritmo(ritmo_semanal: float, peso: float, objetivo: Objetivo) -> str:
    """Compara el ritmo observado con el esperado para el objetivo declarado."""
    minimo, maximo = RITMOS_SEMANALES_ESPERADOS[objetivo]
    fraccion = ritmo_semanal / peso if peso else 0.0

    if fraccion < minimo:
        if objetivo == Objetivo.PERDIDA_GRASA:
            return (
                "Está bajando de peso más rápido de lo recomendable. Un descenso muy "
                "acelerado hace perder músculo junto con la grasa: coma un poco más y "
                "sostenga el entrenamiento."
            )
        return (
            "Está perdiendo peso cuando su objetivo no es ese. Revise si está comiendo "
            "las cantidades indicadas en su plan."
        )

    if fraccion > maximo:
        if objetivo == Objetivo.GANANCIA_MUSCULAR:
            return (
                "Está subiendo de peso más rápido de lo recomendable. Buena parte de ese "
                "aumento será grasa: modere las porciones y siga entrenando igual."
            )
        if objetivo == Objetivo.PERDIDA_GRASA:
            return (
                "Su peso no está bajando. Revise las porciones, sobre todo las de aceite "
                "y bebidas, que suman energía sin llenar."
            )
        return "Su peso está subiendo más de lo esperado para el mantenimiento."

    return "Su ritmo de avance está dentro de lo esperado para su objetivo. Siga así."


def registrar_progreso(
    sesion: Session, usuario: Usuario, datos: RegistroProgresoEntrada
) -> tuple[RegistroProgreso, ResultadoReajuste]:
    """Guarda el avance semanal y reajusta el plan cuando corresponde.

    Devuelve el registro creado junto con la explicacion de lo que el sistema
    hizo, para que la interfaz pueda decirselo al usuario en lugar de reajustar
    en silencio.
    """
    plan_vigente = servicio_plan.obtener_plan_vigente(sesion, usuario)
    if plan_vigente is None:
        raise SinPlanVigente(usuario.id)

    perfil = servicio_perfil.obtener_perfil_vigente(sesion, usuario)
    anterior = obtener_ultimo_registro(sesion, usuario)

    fecha = datos.fecha_registro or date.today()
    registro = RegistroProgreso(
        usuario_id=usuario.id,
        plan_id=plan_vigente.id,
        peso_kg=datos.peso_kg,
        perimetro_cintura_cm=datos.perimetro_cintura_cm,
        sesiones_cumplidas=datos.sesiones_cumplidas,
        adherencia_nutricional=datos.adherencia_nutricional,
        fecha_registro=datetime.combine(fecha, time.min),
    )
    sesion.add(registro)
    sesion.flush()

    reajuste = _evaluar_y_reajustar(sesion, usuario, perfil, registro, anterior)

    sesion.commit()
    sesion.refresh(registro)
    return registro, reajuste


def _evaluar_y_reajustar(
    sesion: Session,
    usuario: Usuario,
    perfil: PerfilBiometrico,
    registro: RegistroProgreso,
    anterior: RegistroProgreso | None,
) -> ResultadoReajuste:
    """Decide si el progreso reportado justifica regenerar el plan."""
    peso_previo = float(anterior.peso_kg) if anterior is not None else float(perfil.peso_kg)
    peso_actual = float(registro.peso_kg)
    cambio = round(peso_actual - peso_previo, 2)

    referencia = (
        anterior.fecha_registro if anterior is not None else perfil.fecha_registro
    )
    dias = (registro.fecha_registro - referencia).days
    ritmo = _ritmo_semanal(peso_actual, peso_previo, dias)

    adherencia = registro.adherencia_nutricional
    if adherencia is not None and adherencia < ADHERENCIA_MINIMA_PARA_REAJUSTAR:
        # El plan no se toca: cambiarlo cuando no se está siguiendo produciría un
        # ajuste sobre un dato que no refleja el efecto del plan.
        return ResultadoReajuste(
            reajusto_el_plan=False,
            motivo=(
                f"Su adherencia al plan fue del {adherencia} %, por debajo del "
                f"{ADHERENCIA_MINIMA_PARA_REAJUSTAR} % que el sistema necesita para "
                "saber si el plan está funcionando."
            ),
            recomendacion=(
                "No se cambió su plan. Antes de ajustarlo conviene completar una semana "
                "siguiéndolo de cerca: así el sistema sabrá si el problema son las "
                "cantidades o el cumplimiento."
            ),
            cambio_peso_kg=cambio,
            ritmo_semanal_kg=ritmo,
            plan_id_vigente=registro.plan_id,
        )

    if abs(cambio) < CAMBIO_MINIMO_PARA_REAJUSTAR_KG:
        return ResultadoReajuste(
            reajusto_el_plan=False,
            motivo=(
                f"Su peso cambió {abs(cambio):.2f} kg, una variación que cabe dentro de "
                "la fluctuación normal del día a día."
            ),
            recomendacion=(
                "Su plan sigue vigente sin cambios. Continúe registrando su avance cada "
                "semana."
            ),
            cambio_peso_kg=cambio,
            ritmo_semanal_kg=ritmo,
            plan_id_vigente=registro.plan_id,
        )

    # El peso cambió lo suficiente: se registra una medición biométrica nueva con
    # el peso reportado y se regenera el plan a partir de ella. Es el mismo camino
    # que sigue una actualización manual de medidas, de modo que las reglas del
    # negocio se cumplen por construcción.
    medicion = PerfilBiometrico(
        usuario_id=usuario.id,
        peso_kg=peso_actual,
        estatura_cm=perfil.estatura_cm,
        edad=perfil.edad,
        sexo=perfil.sexo,
        nivel_actividad=perfil.nivel_actividad,
        objetivo=perfil.objetivo,
        nivel_experiencia=perfil.nivel_experiencia,
        dias_entrenamiento_semana=perfil.dias_entrenamiento_semana,
    )
    sesion.add(medicion)
    sesion.flush()

    plan_nuevo = servicio_plan.generar_plan(sesion, usuario)
    registro.plan_id = plan_nuevo.id

    recomendacion = (
        _describir_ritmo(ritmo, peso_actual, perfil.objetivo)
        if ritmo is not None
        else "Registre su avance dentro de una semana para poder medir su ritmo."
    )

    bitacora.info(
        "Se reajustó el plan del usuario %s: peso %.2f kg, plan %s.",
        usuario.id,
        peso_actual,
        plan_nuevo.id,
    )
    return ResultadoReajuste(
        reajusto_el_plan=True,
        motivo=(
            f"Su peso cambió {cambio:+.2f} kg, así que el sistema recalculó su "
            "requerimiento de energía con sus medidas actuales."
        ),
        recomendacion=recomendacion,
        cambio_peso_kg=cambio,
        ritmo_semanal_kg=ritmo,
        plan_id_vigente=plan_nuevo.id,
    )


def obtener_plan_inicial(sesion: Session, usuario: Usuario) -> Plan | None:
    """Recupera el primer plan que el usuario genero.

    Es el termino de comparacion del reporte de la historia HU-10, que contrasta
    el plan inicial con el vigente.
    """
    sentencia = (
        select(Plan)
        .where(Plan.usuario_id == usuario.id)
        .order_by(Plan.fecha_generacion.asc(), Plan.id.asc())
        .limit(1)
    )
    return sesion.execute(sentencia).scalar_one_or_none()
