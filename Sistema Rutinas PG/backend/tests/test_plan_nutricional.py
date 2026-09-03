"""Pruebas funcionales del plan nutricional (historia HU-06, subfase 3.3).

Verifican el criterio de aceptacion de la Tabla 9 —tiempo de respuesta, margen de
error frente a las formulas y coherencia de los macronutrientes— y las reglas del
negocio *b*, *c* y *e* del apartado 4.3.4.
"""

import time

import pytest

from app.esquemas.plan import AVISO_PROFESIONAL
from app.modelos.enumeraciones import Objetivo
from app.motor import formulas
from tests.conftest import encabezado

RUTA_PERFIL = "/api/v1/perfil-biometrico"
RUTA_PLAN = "/api/v1/plan-nutricional"
RUTA_HISTORIAL_PLANES = "/api/v1/plan-nutricional/historial"

PERFIL_VALIDO = {
    "peso_kg": 78.0,
    "estatura_cm": 174.0,
    "edad": 28,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "mantenimiento",
    "nivel_experiencia": "intermedio",
    "dias_entrenamiento_semana": 4,
}


@pytest.fixture(name="con_perfil")
def fixture_con_perfil(cliente, token_usuario):
    """Deja registrado el perfil biométrico de la cuenta de pruebas."""
    respuesta = cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario))
    assert respuesta.status_code == 201
    return token_usuario


# --------------------------------------------------------------------------
# Validaciones previas (apartado 4.8.3)
# --------------------------------------------------------------------------


def test_no_se_genera_plan_sin_perfil_biometrico(cliente, token_usuario):
    """El sistema no genera un plan si el perfil biométrico está incompleto."""
    respuesta = cliente.post(RUTA_PLAN, headers=encabezado(token_usuario))

    assert respuesta.status_code == 409
    assert "perfil biométrico" in respuesta.json()["detail"]


def test_sin_sesion_no_se_genera_ni_se_consulta_el_plan(cliente):
    """La validación de acceso ocurre en el servidor (requerimiento 4.5.1)."""
    assert cliente.post(RUTA_PLAN).status_code == 401
    assert cliente.get(RUTA_PLAN).status_code == 401
    assert cliente.get(RUTA_HISTORIAL_PLANES).status_code == 401


def test_consultar_el_plan_antes_de_generarlo_devuelve_no_encontrado(cliente, con_perfil):
    """Tener perfil no implica tener plan: hay que generarlo."""
    respuesta = cliente.get(RUTA_PLAN, headers=encabezado(con_perfil))

    assert respuesta.status_code == 404


# --------------------------------------------------------------------------
# Criterios de aceptacion de la historia HU-06
# --------------------------------------------------------------------------


def test_el_plan_se_genera_en_menos_de_tres_segundos(cliente, con_perfil):
    """Criterio de aceptación: el requerimiento se calcula en menos de tres segundos.

    El modelo se precarga primero porque así opera el sistema real: el arranque
    lo deja en memoria y ninguna petición paga el costo de leerlo del disco.
    """
    from app.servicios.plan import obtener_motor

    obtener_motor()

    inicio = time.perf_counter()
    respuesta = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil))
    transcurrido = time.perf_counter() - inicio

    assert respuesta.status_code == 201
    assert transcurrido < 3.0


def test_el_arranque_deja_el_modelo_listo_para_la_primera_peticion():
    """El arranque precarga el modelo, de modo que ninguna petición lo cargue.

    Sin esta precarga el primer usuario esperaría varios segundos y el sistema
    incumpliría el criterio de aceptación de la historia HU-06.
    """
    from app.nucleo.arranque import precargar_modelo_neuronal
    from app.servicios import plan as servicio_plan

    servicio_plan.reiniciar_motor()
    precargar_modelo_neuronal()

    assert servicio_plan._carga_intentada is True


def test_el_plan_no_difiere_mas_del_cinco_por_ciento_de_las_formulas(cliente, con_perfil):
    """Criterio de aceptación: menos del 5 % frente a Mifflin-St Jeor y Harris-Benedict."""
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    assert plan["margen_error_porcentaje"] < 5.0
    assert plan["dentro_del_margen_admitido"] is True


def test_el_plan_almacena_los_dos_valores_de_referencia(cliente, con_perfil):
    """Cada plan guarda los valores de referencia con los que se comparó."""
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    assert plan["referencia_mifflin"] > 0
    assert plan["referencia_harris_benedict"] > 0
    assert plan["tasa_metabolica_basal"] > 0
    assert plan["gasto_energetico_total"] > 0


def test_los_macronutrientes_se_expresan_en_gramos_y_en_porcentaje(cliente, con_perfil):
    """Criterio de aceptación: la distribución se expresa en gramos y en porcentaje."""
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()
    nombres = {macro["nombre"] for macro in plan["macronutrientes"]}

    assert nombres == {"Proteína", "Carbohidrato", "Grasa"}
    for macro in plan["macronutrientes"]:
        assert macro["gramos"] >= 0
        assert macro["porcentaje"] >= 0
        assert macro["explicacion"]


def test_la_suma_de_los_aportes_coincide_con_el_requerimiento_total(cliente, con_perfil):
    """Criterio de aceptación: la suma de los aportes coincide con el total."""
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    suma = sum(macro["kilocalorias"] for macro in plan["macronutrientes"])
    assert suma == plan["energia_de_los_macronutrientes"]
    assert suma == pytest.approx(plan["calorias_objetivo"], abs=1)


def test_los_porcentajes_de_los_macronutrientes_suman_cien(cliente, con_perfil):
    """El reparto porcentual debe cerrar en cien."""
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    suma = sum(macro["porcentaje"] for macro in plan["macronutrientes"])
    assert suma == pytest.approx(100, abs=0.3)


# --------------------------------------------------------------------------
# Reglas del negocio del apartado 4.3.4
# --------------------------------------------------------------------------


def test_todo_plan_muestra_el_aviso_de_consulta_profesional(cliente, con_perfil):
    """Regla del negocio e: el sistema no emite diagnósticos médicos."""
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    assert plan["aviso_profesional"] == AVISO_PROFESIONAL
    assert "no sustituye" in plan["aviso_profesional"].lower()


@pytest.mark.parametrize(
    "objetivo", ["perdida_grasa", "mantenimiento", "ganancia_muscular"]
)
def test_el_ajuste_calorico_respeta_los_limites(cliente, token_usuario, objetivo):
    """Regla del negocio b: nunca más de 20 % de déficit ni 15 % de superávit."""
    cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "objetivo": objetivo},
        headers=encabezado(token_usuario),
    )

    plan = cliente.post(RUTA_PLAN, headers=encabezado(token_usuario)).json()
    gasto = plan["gasto_energetico_total"]

    assert plan["calorias_objetivo"] >= gasto * (1 - formulas.DEFICIT_MAXIMO) * 0.95
    assert plan["calorias_objetivo"] <= gasto * (1 + formulas.SUPERAVIT_MAXIMO) * 1.05


@pytest.mark.parametrize(
    "objetivo", ["perdida_grasa", "mantenimiento", "ganancia_muscular"]
)
def test_la_proteina_se_mantiene_en_el_rango_permitido(cliente, token_usuario, objetivo):
    """Regla del negocio c: entre 1.6 y 2.2 gramos por kilogramo de peso corporal."""
    cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "objetivo": objetivo},
        headers=encabezado(token_usuario),
    )

    plan = cliente.post(RUTA_PLAN, headers=encabezado(token_usuario)).json()
    por_kilogramo = plan["proteina_g"] / PERFIL_VALIDO["peso_kg"]

    assert formulas.PROTEINA_MINIMA_POR_KG * 0.95 <= por_kilogramo
    assert por_kilogramo <= formulas.PROTEINA_MAXIMA_POR_KG * 1.05


def test_el_objetivo_altera_la_energia_en_la_direccion_correcta(cliente, token_usuario):
    """Perder grasa prescribe menos energía que ganar músculo."""
    energias = {}
    for objetivo in ("perdida_grasa", "mantenimiento", "ganancia_muscular"):
        cliente.post(
            RUTA_PERFIL,
            json={**PERFIL_VALIDO, "objetivo": objetivo},
            headers=encabezado(token_usuario),
        )
        energias[objetivo] = cliente.post(
            RUTA_PLAN, headers=encabezado(token_usuario)
        ).json()["calorias_objetivo"]

    assert (
        energias["perdida_grasa"]
        < energias["mantenimiento"]
        < energias["ganancia_muscular"]
    )


def test_el_plan_explica_su_objetivo_en_lenguaje_sencillo(cliente, con_perfil):
    """Requerimiento 4.5.3: toda cifra técnica lleva su explicación."""
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    assert plan["objetivo"] == PERFIL_VALIDO["objetivo"]
    assert len(plan["explicacion_objetivo"]) > 40


def test_el_plan_incluye_la_recomendacion_de_hidratacion(cliente, con_perfil):
    """La hidratación se calcula a partir del peso y la actividad (apartado 2.4.4)."""
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    assert plan["agua_ml"] > 1000


# --------------------------------------------------------------------------
# Vigencia e historial de planes
# --------------------------------------------------------------------------


def test_generar_un_plan_nuevo_deja_el_anterior_fuera_de_vigencia(cliente, con_perfil):
    """Se conserva el historial de planes y se marca cuál está vigente."""
    primero = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()
    segundo = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    historial = cliente.get(RUTA_HISTORIAL_PLANES, headers=encabezado(con_perfil)).json()
    por_identificador = {plan["id"]: plan for plan in historial}

    assert len(historial) == 2
    assert por_identificador[primero["id"]]["activo"] is False
    assert por_identificador[segundo["id"]]["activo"] is True


def test_el_plan_vigente_es_el_ultimo_generado(cliente, con_perfil):
    """La consulta devuelve siempre el plan activo."""
    cliente.post(RUTA_PLAN, headers=encabezado(con_perfil))
    segundo = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    vigente = cliente.get(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    assert vigente["id"] == segundo["id"]
    assert vigente["activo"] is True


def test_el_plan_se_asocia_al_perfil_que_lo_origino(cliente, con_perfil):
    """Permite reconstruir con qué medidas se calculó cada plan."""
    perfil = cliente.get(RUTA_PERFIL, headers=encabezado(con_perfil)).json()
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    assert plan["perfil_id"] == perfil["id"]
    assert plan["usuario_id"] == perfil["usuario_id"]


def test_los_planes_solo_son_visibles_para_su_titular(
    cliente, con_perfil, token_segundo_usuario
):
    """Regla del negocio f: cada cuenta ve únicamente sus propios planes."""
    cliente.post(RUTA_PLAN, headers=encabezado(con_perfil))

    ajeno = cliente.get(RUTA_HISTORIAL_PLANES, headers=encabezado(token_segundo_usuario))

    assert ajeno.json() == []
    assert cliente.get(RUTA_PLAN, headers=encabezado(token_segundo_usuario)).status_code == 404


def test_el_plan_declara_con_que_se_calculo(cliente, con_perfil):
    """El origen distingue el modelo neuronal de las fórmulas de respaldo."""
    plan = cliente.post(RUTA_PLAN, headers=encabezado(con_perfil)).json()

    assert plan["origen_calculo"] in {"red_neuronal", "formula"}


# --------------------------------------------------------------------------
# Construccion del plan sin base de datos
# --------------------------------------------------------------------------


@pytest.mark.parametrize("objetivo", list(Objetivo))
@pytest.mark.parametrize(("peso", "estatura", "edad"), [(52.0, 158.0, 22), (95.0, 182.0, 45)])
def test_la_construccion_del_plan_es_coherente_para_distintos_perfiles(
    peso, estatura, edad, objetivo
):
    """La aritmética del plan se verifica sin necesidad de base de datos."""
    from app.modelos.enumeraciones import NivelActividad, NivelExperiencia, Sexo
    from app.modelos.perfil import PerfilBiometrico
    from app.servicios.plan import construir_plan

    # Los valores predeterminados de la entidad solo se aplican al insertar en la
    # base de datos, de modo que aquí se declaran todos de forma explícita.
    perfil = PerfilBiometrico(
        usuario_id=1,
        peso_kg=peso,
        estatura_cm=estatura,
        edad=edad,
        sexo=Sexo.FEMENINO,
        nivel_actividad=NivelActividad.LIGERO,
        objetivo=objetivo,
        nivel_experiencia=NivelExperiencia.PRINCIPIANTE,
        dias_entrenamiento_semana=3,
    )
    perfil.id = 1

    plan = construir_plan(perfil)

    assert float(plan.margen_error_porcentaje) < 5.0
    assert float(plan.calorias_objetivo) > 0
    assert float(plan.proteina_g) / peso >= formulas.PROTEINA_MINIMA_POR_KG * 0.95
    assert float(plan.proteina_g) / peso <= formulas.PROTEINA_MAXIMA_POR_KG * 1.05
