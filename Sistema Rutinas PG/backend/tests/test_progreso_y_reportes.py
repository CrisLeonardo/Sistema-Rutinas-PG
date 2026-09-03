"""Pruebas funcionales del seguimiento y los reportes (historias HU-09 y HU-10).

Verifican la validacion de fecha del apartado 4.8.3, el reajuste automatico del
plan a partir del progreso registrado, la conservacion del historial de planes y
los datos con que se dibujan los reportes graficos.
"""

from datetime import date, timedelta

import pytest

from app.servicios.progreso import (
    ADHERENCIA_MINIMA_PARA_REAJUSTAR,
    CAMBIO_MINIMO_PARA_REAJUSTAR_KG,
)
from tests.conftest import encabezado

RUTA_PERFIL = "/api/v1/perfil-biometrico"
RUTA_PLAN = "/api/v1/plan-nutricional"
RUTA_HISTORIAL_PLANES = "/api/v1/plan-nutricional/historial"
RUTA_PROGRESO = "/api/v1/progreso"
RUTA_REPORTE = "/api/v1/progreso/reporte"

PERFIL_VALIDO = {
    "peso_kg": 85.0,
    "estatura_cm": 174.0,
    "edad": 28,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "perdida_grasa",
    "nivel_experiencia": "intermedio",
    "dias_entrenamiento_semana": 4,
}

PROGRESO_VALIDO = {
    "peso_kg": 84.0,
    "perimetro_cintura_cm": 92.0,
    "sesiones_cumplidas": 4,
    "adherencia_nutricional": 90,
}


@pytest.fixture(name="con_plan")
def fixture_con_plan(cliente, token_usuario):
    """Deja al usuario con perfil y plan, que es lo que HU-09 requiere."""
    assert (
        cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario)).status_code
        == 201
    )
    assert cliente.post(RUTA_PLAN, headers=encabezado(token_usuario)).status_code == 201
    return token_usuario


def registrar(cliente, token, **campos):
    """Envía un registro de progreso con los campos indicados."""
    return cliente.post(
        RUTA_PROGRESO, json={**PROGRESO_VALIDO, **campos}, headers=encabezado(token)
    )


# --------------------------------------------------------------------------
# HU-09. Registro del progreso
# --------------------------------------------------------------------------


def test_sin_sesion_no_se_registra_ni_se_consulta_el_progreso(cliente):
    """La validación de acceso ocurre en el servidor (requerimiento 4.5.1)."""
    assert cliente.post(RUTA_PROGRESO, json=PROGRESO_VALIDO).status_code == 401
    assert cliente.get(RUTA_PROGRESO).status_code == 401
    assert cliente.get(RUTA_REPORTE).status_code == 401


def test_no_se_registra_progreso_sin_plan_vigente(cliente, token_usuario):
    """Dependencia del apartado 4.6.3: el reajuste opera sobre un plan previo."""
    respuesta = registrar(cliente, token_usuario)

    assert respuesta.status_code == 409
    assert "plan" in respuesta.json()["detail"].lower()


def test_el_registro_guarda_las_cuatro_variables_del_avance(cliente, con_plan):
    """Registro semanal de peso, perímetro, sesiones cumplidas y adherencia."""
    respuesta = registrar(cliente, con_plan)

    assert respuesta.status_code == 201
    registro = respuesta.json()["registro"]
    assert registro["peso_kg"] == PROGRESO_VALIDO["peso_kg"]
    assert registro["perimetro_cintura_cm"] == PROGRESO_VALIDO["perimetro_cintura_cm"]
    assert registro["sesiones_cumplidas"] == PROGRESO_VALIDO["sesiones_cumplidas"]
    assert registro["adherencia_nutricional"] == PROGRESO_VALIDO["adherencia_nutricional"]


def test_el_perimetro_y_la_adherencia_son_opcionales(cliente, con_plan):
    """No todo usuario tiene cinta métrica; el registro no puede depender de ella."""
    respuesta = cliente.post(
        RUTA_PROGRESO,
        json={"peso_kg": 84.0, "sesiones_cumplidas": 3},
        headers=encabezado(con_plan),
    )

    assert respuesta.status_code == 201
    registro = respuesta.json()["registro"]
    assert registro["perimetro_cintura_cm"] is None
    assert registro["adherencia_nutricional"] is None


def test_la_fecha_no_puede_ser_posterior_a_la_actual(cliente, con_plan):
    """Apartado 4.8.3: la fecha de registro no puede ser posterior a hoy."""
    manana = (date.today() + timedelta(days=1)).isoformat()

    respuesta = registrar(cliente, con_plan, fecha_registro=manana)

    assert respuesta.status_code == 422
    assert "posterior" in respuesta.text


def test_la_fecha_de_hoy_si_se_acepta(cliente, con_plan):
    """El límite es inclusivo: hoy es una fecha válida."""
    respuesta = registrar(cliente, con_plan, fecha_registro=date.today().isoformat())

    assert respuesta.status_code == 201


def test_se_aceptan_fechas_pasadas(cliente, con_plan):
    """El usuario puede registrar el avance de una semana que ya pasó."""
    hace_una_semana = (date.today() - timedelta(days=7)).isoformat()

    respuesta = registrar(cliente, con_plan, fecha_registro=hace_una_semana)

    assert respuesta.status_code == 201


@pytest.mark.parametrize("peso", [29.9, 250.1, 0])
def test_el_peso_del_progreso_respeta_el_mismo_rango_del_perfil(cliente, con_plan, peso):
    """Un progreso no puede producir un perfil que el sistema rechazaría."""
    assert registrar(cliente, con_plan, peso_kg=peso).status_code == 422


@pytest.mark.parametrize("adherencia", [-1, 101, 150])
def test_la_adherencia_se_expresa_como_porcentaje(cliente, con_plan, adherencia):
    """Fuera de cero a cien el dato no significa nada."""
    assert registrar(cliente, con_plan, adherencia_nutricional=adherencia).status_code == 422


@pytest.mark.parametrize("sesiones", [-1, 8, 20])
def test_las_sesiones_cumplidas_caben_en_una_semana(cliente, con_plan, sesiones):
    """No se pueden cumplir más sesiones que días tiene la semana."""
    assert registrar(cliente, con_plan, sesiones_cumplidas=sesiones).status_code == 422


@pytest.mark.parametrize("perimetro", [39.0, 201.0])
def test_el_perimetro_de_cintura_respeta_un_rango_plausible(cliente, con_plan, perimetro):
    """Un valor fuera de rango sería un error de captura."""
    assert registrar(cliente, con_plan, perimetro_cintura_cm=perimetro).status_code == 422


# --------------------------------------------------------------------------
# HU-09. Reajuste automático del plan
# --------------------------------------------------------------------------


def test_un_cambio_de_peso_apreciable_reajusta_el_plan(cliente, con_plan):
    """Reajuste automático del plan a partir del progreso registrado."""
    plan_previo = cliente.get(RUTA_PLAN, headers=encabezado(con_plan)).json()

    reajuste = registrar(cliente, con_plan, peso_kg=82.0).json()["reajuste"]

    assert reajuste["reajusto_el_plan"] is True
    assert reajuste["plan_id_vigente"] != plan_previo["id"]
    assert reajuste["cambio_peso_kg"] == pytest.approx(-3.0)


def test_el_plan_reajustado_recalcula_la_energia_con_el_peso_nuevo(cliente, con_plan):
    """El reajuste reutiliza la cadena completa, no un ajuste inventado."""
    antes = cliente.get(RUTA_PLAN, headers=encabezado(con_plan)).json()

    registrar(cliente, con_plan, peso_kg=78.0)
    despues = cliente.get(RUTA_PLAN, headers=encabezado(con_plan)).json()

    # Al bajar de peso, el gasto energético baja y el plan prescribe menos energía.
    assert despues["calorias_objetivo"] < antes["calorias_objetivo"]
    assert despues["margen_error_porcentaje"] < 5.0


def test_el_plan_reajustado_sigue_cumpliendo_las_reglas_del_negocio(cliente, con_plan):
    """Las reglas *b* y *c* se cumplen por construcción también tras el reajuste."""
    from app.motor import formulas

    registrar(cliente, con_plan, peso_kg=79.0)
    plan = cliente.get(RUTA_PLAN, headers=encabezado(con_plan)).json()

    proteina_por_kg = plan["proteina_g"] / 79.0
    gasto = plan["gasto_energetico_total"]

    assert formulas.PROTEINA_MINIMA_POR_KG * 0.95 <= proteina_por_kg
    assert proteina_por_kg <= formulas.PROTEINA_MAXIMA_POR_KG * 1.05
    assert plan["calorias_objetivo"] >= gasto * (1 - formulas.DEFICIT_MAXIMO) * 0.95


def test_un_cambio_minimo_no_reajusta_el_plan(cliente, con_plan):
    """Una variación menor cabe dentro de la fluctuación normal del día a día."""
    plan_previo = cliente.get(RUTA_PLAN, headers=encabezado(con_plan)).json()

    reajuste = registrar(cliente, con_plan, peso_kg=84.8).json()["reajuste"]

    assert reajuste["reajusto_el_plan"] is False
    assert reajuste["plan_id_vigente"] == plan_previo["id"]
    assert abs(reajuste["cambio_peso_kg"]) < CAMBIO_MINIMO_PARA_REAJUSTAR_KG


def test_con_adherencia_baja_no_se_reajusta_el_plan(cliente, con_plan):
    """Si el usuario no siguió el plan, el estancamiento no se explica por el cálculo."""
    reajuste = registrar(
        cliente, con_plan, peso_kg=80.0, adherencia_nutricional=40
    ).json()["reajuste"]

    assert reajuste["reajusto_el_plan"] is False
    assert str(ADHERENCIA_MINIMA_PARA_REAJUSTAR) in reajuste["motivo"]


def test_el_sistema_explica_siempre_que_hizo_con_el_plan(cliente, con_plan):
    """El reajuste no ocurre en silencio: la respuesta lo dice."""
    for peso in (84.9, 80.0):
        reajuste = registrar(cliente, con_plan, peso_kg=peso).json()["reajuste"]

        assert len(reajuste["motivo"]) > 20
        assert len(reajuste["recomendacion"]) > 20


def test_el_reajuste_calcula_el_ritmo_semanal(cliente, con_plan):
    """El ritmo permite comparar el avance con lo esperado para el objetivo."""
    hace_una_semana = (date.today() - timedelta(days=7)).isoformat()
    registrar(cliente, con_plan, peso_kg=85.0, fecha_registro=hace_una_semana)

    reajuste = registrar(cliente, con_plan, peso_kg=84.0).json()["reajuste"]

    assert reajuste["ritmo_semanal_kg"] == pytest.approx(-1.0, abs=0.05)


def test_el_historial_de_planes_se_conserva_tras_el_reajuste(cliente, con_plan):
    """Se conserva el historial de planes y se marca cuál está vigente."""
    registrar(cliente, con_plan, peso_kg=82.0)

    historial = cliente.get(RUTA_HISTORIAL_PLANES, headers=encabezado(con_plan)).json()
    vigentes = [plan for plan in historial if plan["activo"]]

    assert len(historial) >= 2
    assert len(vigentes) == 1


def test_el_reajuste_produce_tambien_una_rutina_nueva(cliente, con_plan):
    """El plan y la rutina siempre viajan juntos, también al reajustar."""
    registrar(cliente, con_plan, peso_kg=80.0)

    rutina = cliente.get("/api/v1/rutina", headers=encabezado(con_plan)).json()

    assert rutina["sesiones"]
    assert rutina["cumple_separacion_de_grupos"] is True


def test_el_historial_de_progreso_se_devuelve_del_mas_antiguo_al_mas_reciente(
    cliente, con_plan
):
    """Es el orden que necesitan las gráficas de evolución."""
    for dias, peso in ((14, 85.0), (7, 84.0), (0, 83.0)):
        registrar(
            cliente,
            con_plan,
            peso_kg=peso,
            fecha_registro=(date.today() - timedelta(days=dias)).isoformat(),
        )

    historial = cliente.get(RUTA_PROGRESO, headers=encabezado(con_plan)).json()

    assert [registro["peso_kg"] for registro in historial] == [85.0, 84.0, 83.0]


def test_el_progreso_solo_es_visible_para_su_titular(cliente, con_plan, token_segundo_usuario):
    """Regla del negocio f: cada cuenta ve únicamente su propio avance."""
    registrar(cliente, con_plan)

    ajeno = cliente.get(RUTA_PROGRESO, headers=encabezado(token_segundo_usuario))

    assert ajeno.json() == []


# --------------------------------------------------------------------------
# HU-10. Reportes gráficos de evolución
# --------------------------------------------------------------------------


def test_el_reporte_entrega_los_puntos_de_la_grafica_de_peso(cliente, con_plan):
    """Gráfica de evolución del peso en el tiempo."""
    for dias, peso in ((14, 85.0), (7, 84.0), (0, 83.0)):
        registrar(
            cliente,
            con_plan,
            peso_kg=peso,
            fecha_registro=(date.today() - timedelta(days=dias)).isoformat(),
        )

    reporte = cliente.get(RUTA_REPORTE, headers=encabezado(con_plan)).json()

    assert [punto["peso_kg"] for punto in reporte["puntos"]] == [85.0, 84.0, 83.0]
    assert reporte["peso_inicial"] == 85.0
    assert reporte["peso_actual"] == 83.0
    assert reporte["cambio_total_kg"] == pytest.approx(-2.0)


def test_el_reporte_entrega_la_adherencia_y_las_sesiones_cumplidas(cliente, con_plan):
    """Gráfica de adherencia y sesiones cumplidas."""
    registrar(cliente, con_plan, sesiones_cumplidas=4, adherencia_nutricional=90)
    registrar(cliente, con_plan, peso_kg=83.0, sesiones_cumplidas=3, adherencia_nutricional=80)

    reporte = cliente.get(RUTA_REPORTE, headers=encabezado(con_plan)).json()

    assert reporte["sesiones_totales"] == 7
    assert reporte["adherencia_promedio"] == pytest.approx(85.0)
    assert reporte["semanas_registradas"] == 2


def test_el_reporte_compara_el_plan_inicial_con_el_vigente(cliente, con_plan):
    """Comparación entre el plan inicial y el vigente."""
    inicial = cliente.get(RUTA_PLAN, headers=encabezado(con_plan)).json()
    registrar(cliente, con_plan, peso_kg=80.0)

    comparacion = cliente.get(RUTA_REPORTE, headers=encabezado(con_plan)).json()[
        "comparacion_planes"
    ]

    assert comparacion["calorias_inicial"] == inicial["calorias_objetivo"]
    assert comparacion["calorias_vigente"] < comparacion["calorias_inicial"]
    assert comparacion["diferencia_calorias"] < 0
    assert comparacion["hubo_cambio"] is True


def test_sin_reajuste_la_comparacion_indica_que_no_hubo_cambio(cliente, con_plan):
    """El plan inicial y el vigente son el mismo mientras no se reajuste."""
    comparacion = cliente.get(RUTA_REPORTE, headers=encabezado(con_plan)).json()[
        "comparacion_planes"
    ]

    assert comparacion["hubo_cambio"] is False
    assert comparacion["diferencia_calorias"] == 0


def test_el_reporte_de_una_cuenta_sin_avance_no_falla(cliente, con_plan):
    """Una cuenta recién creada tiene un reporte vacío, no un error."""
    reporte = cliente.get(RUTA_REPORTE, headers=encabezado(con_plan))

    assert reporte.status_code == 200
    cuerpo = reporte.json()
    assert cuerpo["puntos"] == []
    assert cuerpo["cambio_total_kg"] is None
    assert cuerpo["adherencia_promedio"] is None
    assert cuerpo["sesiones_totales"] == 0


def test_el_reporte_sin_plan_no_trae_comparacion(cliente, token_usuario):
    """Sin planes generados no hay nada que comparar."""
    cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario))

    reporte = cliente.get(RUTA_REPORTE, headers=encabezado(token_usuario)).json()

    assert reporte["comparacion_planes"] is None


def test_el_reporte_solo_muestra_los_datos_de_su_titular(
    cliente, con_plan, token_segundo_usuario
):
    """Regla del negocio f, verificada también sobre los reportes."""
    registrar(cliente, con_plan)

    ajeno = cliente.get(RUTA_REPORTE, headers=encabezado(token_segundo_usuario)).json()

    assert ajeno["puntos"] == []
    assert ajeno["comparacion_planes"] is None
