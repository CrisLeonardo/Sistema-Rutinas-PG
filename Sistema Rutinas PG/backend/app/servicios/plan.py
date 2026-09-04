"""Generacion del plan nutricional (epica E3, historia HU-06, subfase 3.3).

Une el motor de calculo con la persistencia: toma el perfil biometrico vigente,
obtiene el requerimiento energetico del modelo neuronal, aplica las reglas del
negocio y guarda el plan junto con los valores de referencia y el margen de error
obtenido, tal como exige el criterio de aceptacion de la historia HU-06.
"""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modelos.catalogo import Alimento, Ejercicio
from app.modelos.enumeraciones import Objetivo
from app.modelos.perfil import PerfilBiometrico
from app.modelos.plan import ComidaPlan, EjercicioSesion, Plan, SesionEntrenamiento
from app.modelos.usuario import Usuario
from app.motor import formulas, seguridad
from app.motor.red_neuronal import ModeloNoEntrenado, MotorNeuronal
from app.motor.menu import (
    AlimentoDisponible,
    CatalogoDeAlimentosInsuficiente,
    MenuDiario,
    generar_menu,
)
from app.motor.rutina import (
    CatalogoInsuficiente,
    EjercicioDisponible,
    RutinaSemanal,
    generar_rutina,
)
from app.servicios import perfil as servicio_perfil

bitacora = logging.getLogger(__name__)

ORIGEN_RED_NEURONAL = "red_neuronal"
ORIGEN_FORMULA = "formula"

EXPLICACION_MANTENIMIENTO = (
    "Su plan aporta la misma energía que usted gasta al día, de modo que conserve "
    "su composición corporal actual."
)


class PerfilIncompleto(Exception):
    """No se puede generar un plan porque falta el perfil biometrico.

    Corresponde a la validacion del apartado 4.8.3: el sistema no genera un plan
    si el perfil biometrico esta incompleto.
    """


# El motor se carga una sola vez por proceso. Cargarlo en cada peticion tardaria
# mas que los tres segundos que admite el criterio de aceptacion de HU-06.
_motor: MotorNeuronal | None = None
_carga_intentada = False


def obtener_motor() -> MotorNeuronal | None:
    """Devuelve el modelo entrenado, o None si todavia no se ha entrenado.

    No propaga el fallo: el sistema debe seguir generando planes con las formulas
    de referencia mientras el modelo no este disponible, en lugar de dejar al
    usuario sin plan.
    """
    global _motor, _carga_intentada
    if _motor is None and not _carga_intentada:
        _carga_intentada = True
        try:
            _motor = MotorNeuronal.cargar()
            bitacora.info("Modelo neuronal cargado. Métricas: %s", _motor.metricas)
        except ModeloNoEntrenado:
            bitacora.warning(
                "No hay modelo neuronal entrenado. Los planes se calcularán con las "
                "fórmulas de referencia. Ejecute: uv run python entrenar_modelo.py"
            )
        except Exception:  # pragma: no cover - depende del entorno de ejecucion
            bitacora.exception("No fue posible cargar el modelo neuronal.")
    return _motor


def reiniciar_motor() -> None:
    """Descarta el modelo cargado para que se vuelva a leer del disco.

    Permite reentrenar sin detener el servicio, como pide el requerimiento no
    funcional 4.5.6.
    """
    global _motor, _carga_intentada
    _motor = None
    _carga_intentada = False


def generar_plan(sesion: Session, usuario: Usuario) -> Plan:
    """Genera y almacena el plan nutricional del perfil biometrico vigente.

    El plan anterior deja de estar vigente pero se conserva, para poder comparar
    el plan inicial con el actual (historia HU-10).
    """
    try:
        perfil = servicio_perfil.obtener_perfil_vigente(sesion, usuario)
    except servicio_perfil.PerfilNoRegistrado as error:
        raise PerfilIncompleto(usuario.id) from error

    if not servicio_perfil.perfil_esta_completo(perfil):
        raise PerfilIncompleto(usuario.id)

    plan = construir_plan(perfil)

    # Solo un plan puede estar vigente a la vez.
    for anterior in sesion.execute(
        select(Plan).where(Plan.usuario_id == usuario.id, Plan.activo.is_(True))
    ).scalars():
        anterior.activo = False

    sesion.add(plan)
    sesion.flush()

    # La rutina se arma dentro de la misma transaccion que el plan: un plan
    # sin rutina describiria solo la mitad del incremento que el usuario pidio.
    try:
        rutina = construir_rutina(sesion, perfil, plan.series_semanales_por_grupo)
    except CatalogoInsuficiente:
        bitacora.warning(
            "El catálogo de ejercicios está vacío: el plan %s se guarda sin rutina.",
            plan.id,
        )
    else:
        _persistir_rutina(sesion, plan, rutina)

    # El menú se arma en la misma transacción, por la misma razón: el plan
    # que el usuario pidió incluye qué comer, no solo cuánta energía.
    try:
        menu = construir_menu(sesion, plan)
    except CatalogoDeAlimentosInsuficiente:
        bitacora.warning(
            "El catálogo de alimentos no alcanza: el plan %s se guarda sin menú.",
            plan.id,
        )
    else:
        _persistir_menu(sesion, plan, menu)

    sesion.commit()
    sesion.refresh(plan)
    return plan


def ejercicios_disponibles(sesion: Session) -> list[EjercicioDisponible]:
    """Lee del catalogo los ejercicios con que se puede armar una rutina.

    Solo entran los marcados como disponibles localmente: el criterio de
    aceptacion de la historia HU-08 exige que todo ejercicio propuesto sea
    ejecutable con el equipamiento registrado para la institucion.
    """
    sentencia = (
        select(Ejercicio)
        .where(Ejercicio.disponible_localmente.is_(True))
        .order_by(Ejercicio.id)
    )
    return [
        EjercicioDisponible(
            id=ejercicio.id,
            nombre=ejercicio.nombre,
            grupo_muscular=ejercicio.grupo_muscular,
            nivel_minimo=ejercicio.nivel_minimo,
            es_compuesto=ejercicio.es_compuesto,
        )
        for ejercicio in sesion.execute(sentencia).scalars()
    ]


def construir_rutina(
    sesion: Session, perfil: PerfilBiometrico, series_semanales_por_grupo: float
) -> RutinaSemanal:
    """Arma la rutina semanal del perfil con los ejercicios del catalogo."""
    return generar_rutina(
        series_semanales_por_grupo=series_semanales_por_grupo,
        dias_entrenamiento_semana=perfil.dias_entrenamiento_semana,
        nivel_experiencia=perfil.nivel_experiencia,
        objetivo=perfil.objetivo,
        disponibles=ejercicios_disponibles(sesion),
    )


def _persistir_rutina(sesion: Session, plan: Plan, rutina: RutinaSemanal) -> None:
    """Guarda las sesiones y sus ejercicios asociados al plan.

    Los ejercicios se enlazan por la relacion del modelo y no por el
    identificador: asi SQLAlchemy resuelve el orden de las inserciones y las
    envia todas juntas, en lugar de exigir una descarga a la base de datos por
    cada sesion para conocer su identificador. Con siete sesiones semanales eso
    ahorra seis viajes por plan, que bajo carga concurrente se notan.
    """
    for prescrita in rutina.sesiones:
        entidad = SesionEntrenamiento(
            plan_id=plan.id,
            dia=prescrita.dia,
            grupo_muscular=prescrita.grupo_muscular,
        )
        entidad.ejercicios = [
            EjercicioSesion(
                ejercicio_id=ejercicio.ejercicio_id,
                orden=ejercicio.orden,
                series=ejercicio.series,
                repeticiones_min=ejercicio.repeticiones_min,
                repeticiones_max=ejercicio.repeticiones_max,
                repeticiones_en_reserva=ejercicio.repeticiones_en_reserva,
                descanso_segundos=ejercicio.descanso_segundos,
            )
            for ejercicio in prescrita.ejercicios
        ]
        sesion.add(entidad)


def alimentos_disponibles(sesion: Session) -> list[AlimentoDisponible]:
    """Lee del catalogo los alimentos con que se puede armar un menu.

    Solo entran los marcados como disponibles localmente: el criterio de
    aceptacion de la historia HU-08 exige que todo alimento propuesto exista en
    el catalogo local.
    """
    sentencia = (
        select(Alimento)
        .where(Alimento.disponible_localmente.is_(True))
        .order_by(Alimento.id)
    )
    return [
        AlimentoDisponible(
            id=alimento.id,
            nombre=alimento.nombre,
            categoria=alimento.categoria,
            energia_kcal_100g=float(alimento.energia_kcal_100g),
            proteina_g_100g=float(alimento.proteina_g_100g),
            carbohidrato_g_100g=float(alimento.carbohidrato_g_100g),
            grasa_g_100g=float(alimento.grasa_g_100g),
            medida_casera=alimento.medida_casera,
            costo_quetzales_100g=(
                float(alimento.costo_aproximado_quetzales)
                if alimento.costo_aproximado_quetzales is not None
                else None
            ),
        )
        for alimento in sesion.execute(sentencia).scalars()
    ]


def construir_menu(sesion: Session, plan: Plan) -> MenuDiario:
    """Arma el menu diario que corresponde al plan con el catalogo local."""
    return generar_menu(
        energia_kcal=float(plan.calorias_objetivo),
        proteina_g=float(plan.proteina_g),
        disponibles=alimentos_disponibles(sesion),
    )


def _persistir_menu(sesion: Session, plan: Plan, menu: MenuDiario) -> None:
    """Guarda las porciones del menu asociadas al plan."""
    for tiempo in menu.tiempos:
        for porcion in tiempo.porciones:
            sesion.add(
                ComidaPlan(
                    plan_id=plan.id,
                    alimento_id=porcion.alimento_id,
                    tiempo_comida=tiempo.nombre,
                    cantidad_g=porcion.gramos,
                )
            )


def volumen_de_referencia(perfil: PerfilBiometrico) -> float:
    """Volumen semanal por grupo muscular segun la regla de referencia.

    Sirve de patron de comparacion frente al valor que produce la red, igual
    que las dos formulas metabolicas lo son para el requerimiento energetico.
    """
    return formulas.series_semanales_por_grupo(
        perfil.nivel_experiencia,
        perfil.dias_entrenamiento_semana,
        perfil.edad,
        perfil.objetivo,
    )


def construir_plan(perfil: PerfilBiometrico) -> Plan:
    """Calcula el plan de un perfil, sin tocar la base de datos.

    Se mantiene separado de `generar_plan` para poder verificar la aritmetica del
    plan sin necesidad de una sesion de base de datos.
    """
    peso = float(perfil.peso_kg)
    estatura = float(perfil.estatura_cm)

    referencias = formulas.calcular_referencias(
        peso, estatura, perfil.edad, perfil.sexo, perfil.nivel_actividad
    )
    energia_referencia = formulas.ajustar_por_objetivo(
        referencias.gasto_promedio, perfil.objetivo
    )

    motor = obtener_motor()
    if motor is not None:
        prediccion = motor.predecir(
            peso,
            estatura,
            perfil.edad,
            perfil.sexo,
            perfil.nivel_actividad,
            perfil.objetivo,
            perfil.nivel_experiencia,
            perfil.dias_entrenamiento_semana,
        )
        calorias = float(prediccion.energia_kcal)
        proteina_g = float(prediccion.proteina_g)
        carbohidrato_g = float(prediccion.carbohidrato_g)
        grasa_g = float(prediccion.grasa_g)
        volumen = prediccion.series_semanales_por_grupo
        origen = ORIGEN_RED_NEURONAL
    else:
        macros = formulas.distribuir_macronutrientes(energia_referencia, peso, perfil.objetivo)
        calorias = float(macros.energia_kcal)
        proteina_g = float(macros.proteina_g)
        carbohidrato_g = float(macros.carbohidrato_g)
        grasa_g = float(macros.grasa_g)
        volumen = formulas.series_semanales_por_grupo(
            perfil.nivel_experiencia,
            perfil.dias_entrenamiento_semana,
            perfil.edad,
            perfil.objetivo,
        )
        origen = ORIGEN_FORMULA

    # El margen se mide sobre el valor que el modelo produjo, antes de que los
    # guardarrailes clinicos lo acoten: es lo que evalua la precision de la red
    # frente a las formulas de referencia, que es el criterio de aceptacion de la
    # historia HU-06. La correccion de seguridad que viene despues es una regla
    # del negocio, no un error del modelo, y confundirlas haria que un plan
    # correcto se reportara como fuera del margen admitido.
    margen = formulas.margen_de_error(calorias, energia_referencia) * 100

    # Los guardarrailes clinicos acotan lo prescrito a lo que es seguro comer.
    revisado = seguridad.aplicar(
        energia_kcal=calorias,
        proteina_g=proteina_g,
        carbohidrato_g=carbohidrato_g,
        grasa_g=grasa_g,
        peso_kg=peso,
        estatura_cm=estatura,
        sexo=perfil.sexo,
        objetivo=perfil.objetivo,
        gasto_energetico_total=referencias.gasto_promedio,
    )
    if revisado.hubo_correccion:
        bitacora.info(
            "El plan del perfil %s se ajustó por seguridad: %s kcal calculadas, "
            "%s kcal prescritas.",
            perfil.id,
            revisado.energia_calculada_kcal,
            revisado.energia_kcal,
        )
    calorias = float(revisado.energia_kcal)
    proteina_g = float(revisado.proteina_g)
    carbohidrato_g = float(revisado.carbohidrato_g)
    grasa_g = float(revisado.grasa_g)

    plan = Plan(
        usuario_id=perfil.usuario_id,
        perfil_id=perfil.id,
        tasa_metabolica_basal=round(
            (referencias.basal_mifflin + referencias.basal_harris_benedict) / 2, 2
        ),
        gasto_energetico_total=round(referencias.gasto_promedio, 2),
        calorias_objetivo=round(calorias, 2),
        referencia_mifflin=round(
            formulas.ajustar_por_objetivo(referencias.gasto_mifflin, perfil.objetivo), 2
        ),
        referencia_harris_benedict=round(
            formulas.ajustar_por_objetivo(referencias.gasto_harris_benedict, perfil.objetivo), 2
        ),
        margen_error_porcentaje=round(margen, 2),
        proteina_g=proteina_g,
        carbohidrato_g=carbohidrato_g,
        grasa_g=grasa_g,
        origen_calculo=origen,
        activo=True,
    )
    # El volumen viaja junto al plan sin columna propia: la entidad `Plan` del
    # apartado 3.4.3 no la contempla, y el dato queda materializado en las
    # series de cada `EjercicioSesion` que la rutina genera a continuacion.
    plan.series_semanales_por_grupo = volumen
    return plan


def obtener_plan_vigente(sesion: Session, usuario: Usuario) -> Plan | None:
    """Devuelve el plan activo del usuario, si lo tiene."""
    sentencia = (
        select(Plan)
        .where(Plan.usuario_id == usuario.id, Plan.activo.is_(True))
        .order_by(Plan.fecha_generacion.desc(), Plan.id.desc())
        .limit(1)
    )
    return sesion.execute(sentencia).scalar_one_or_none()


def listar_planes(sesion: Session, usuario: Usuario) -> list[Plan]:
    """Historial de planes del usuario, del mas reciente al mas antiguo."""
    sentencia = (
        select(Plan)
        .where(Plan.usuario_id == usuario.id)
        .order_by(Plan.fecha_generacion.desc(), Plan.id.desc())
    )
    return list(sesion.execute(sentencia).scalars())


def agua_recomendada(perfil: PerfilBiometrico) -> int:
    """Mililitros de agua sugeridos para el perfil (apartado 2.4.4)."""
    return formulas.agua_recomendada_ml(float(perfil.peso_kg), perfil.nivel_actividad)


def explicacion_objetivo(perfil: PerfilBiometrico) -> str:
    """Explica en lenguaje sencillo por que el plan tiene esa cantidad de energia.

    El porcentaje se calcula para el perfil concreto y no se declara fijo: los
    guardarrailes clinicos reducen el ajuste cuando la composicion corporal no
    admite el maximo de la regla del negocio *b*, y anunciar un 20 % que el plan
    no aplica seria describirle al usuario un plan distinto del que recibio.
    """
    indice = seguridad.indice_masa_corporal(float(perfil.peso_kg), float(perfil.estatura_cm))
    ajuste = seguridad.ajuste_admitido(perfil.objetivo, indice)

    if perfil.objetivo == Objetivo.MANTENIMIENTO or ajuste == 0:
        if perfil.objetivo == Objetivo.PERDIDA_GRASA:
            return (
                "Su plan aporta la energía que usted gasta al día. El sistema no le "
                "recorta energía porque su peso ya está por debajo de lo normal: la "
                "grasa se reduce entrenando, no comiendo menos."
            )
        return EXPLICACION_MANTENIMIENTO

    if perfil.objetivo == Objetivo.PERDIDA_GRASA:
        return (
            f"Su plan tiene un {abs(ajuste) * 100:.0f} % menos de energía que su gasto "
            "diario. Es el recorte que su composición corporal admite: uno mayor haría "
            "que perdiera músculo junto con la grasa."
        )

    return (
        f"Su plan tiene un {ajuste * 100:.0f} % más de energía que su gasto diario. Ese "
        "excedente es el material con que se construye el músculo nuevo; uno mayor se "
        "acumularía sobre todo como grasa."
    )


def notas_de_seguridad(perfil: PerfilBiometrico, plan: Plan) -> tuple[list[str], list[str]]:
    """Correcciones y advertencias clinicas que gobiernan el plan del perfil."""
    return seguridad.notas_del_perfil(
        peso_kg=float(perfil.peso_kg),
        estatura_cm=float(perfil.estatura_cm),
        sexo=perfil.sexo,
        objetivo=perfil.objetivo,
        energia_prescrita_kcal=float(plan.calorias_objetivo),
    )
