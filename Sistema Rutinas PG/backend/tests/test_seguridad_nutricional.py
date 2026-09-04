"""Pruebas de los guardarrailes clinicos del plan (regla del negocio *e*).

Verifican que el sistema no prescriba una dieta que no sea segura seguir sin
supervision, situacion que el calculo original no distinguia: aplicaba siempre
el deficit maximo, no tenia piso energetico y calculaba la proteina sobre el
peso corporal total.
"""

import pytest

from app.modelos.enumeraciones import NivelActividad, Objetivo, Sexo
from app.motor import formulas, seguridad

from .conftest import encabezado

PERFIL_COMPLETO = {
    "peso_kg": 78.0,
    "estatura_cm": 175.0,
    "edad": 28,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "mantenimiento",
    "nivel_experiencia": "principiante",
    "dias_entrenamiento_semana": 4,
}


def _plan_calculado(peso, estatura, edad, sexo, actividad, objetivo):
    """Reproduce el calculo de referencia sin los guardarrailes, para compararlo."""
    referencias = formulas.calcular_referencias(peso, estatura, edad, sexo, actividad)
    energia = formulas.ajustar_por_objetivo(referencias.gasto_promedio, objetivo)
    macros = formulas.distribuir_macronutrientes(energia, peso, objetivo)
    return referencias, macros


def _revisar(peso, estatura, edad, sexo, actividad, objetivo):
    referencias, macros = _plan_calculado(peso, estatura, edad, sexo, actividad, objetivo)
    return macros, seguridad.aplicar(
        energia_kcal=macros.energia_kcal,
        proteina_g=macros.proteina_g,
        carbohidrato_g=macros.carbohidrato_g,
        grasa_g=macros.grasa_g,
        peso_kg=peso,
        estatura_cm=estatura,
        sexo=sexo,
        objetivo=objetivo,
        gasto_energetico_total=referencias.gasto_promedio,
    )


# --------------------------------------------------------------------------
# Piso energetico
# --------------------------------------------------------------------------


def test_ninguna_mujer_recibe_menos_de_mil_doscientas_kilocalorias():
    """El calculo original prescribia 1 049 kcal a este perfil."""
    macros, revisado = _revisar(
        50, 155, 55, Sexo.FEMENINO, NivelActividad.SEDENTARIO, Objetivo.PERDIDA_GRASA
    )

    assert macros.energia_kcal < seguridad.ENERGIA_MINIMA_KCAL[Sexo.FEMENINO]
    assert revisado.energia_kcal >= seguridad.ENERGIA_MINIMA_KCAL[Sexo.FEMENINO]
    assert revisado.hubo_correccion


def test_ningun_hombre_recibe_menos_de_mil_quinientas_kilocalorias():
    _, revisado = _revisar(
        55, 165, 70, Sexo.MASCULINO, NivelActividad.SEDENTARIO, Objetivo.PERDIDA_GRASA
    )

    assert revisado.energia_kcal >= seguridad.ENERGIA_MINIMA_KCAL[Sexo.MASCULINO]


@pytest.mark.parametrize("sexo", list(Sexo))
@pytest.mark.parametrize("objetivo", list(Objetivo))
@pytest.mark.parametrize("peso", [30, 45, 60, 90, 130, 250])
def test_el_piso_energetico_se_respeta_en_todo_el_dominio(sexo, objetivo, peso):
    """Ningun perfil admitido por el sistema queda por debajo del piso."""
    _, revisado = _revisar(peso, 160, 40, sexo, NivelActividad.SEDENTARIO, objetivo)

    assert revisado.energia_kcal >= seguridad.energia_minima(sexo)


# --------------------------------------------------------------------------
# Deficit graduado por composicion corporal
# --------------------------------------------------------------------------


def test_el_bajo_peso_no_recibe_deficit():
    """Regla *e*: acotar la prescripcion no es diagnosticar."""
    indice = seguridad.indice_masa_corporal(40, 151)

    assert indice < seguridad.IMC_BAJO_PESO
    assert seguridad.ajuste_admitido(Objetivo.PERDIDA_GRASA, indice) == 0.0

    _, revisado = _revisar(
        40, 151, 22, Sexo.FEMENINO, NivelActividad.SEDENTARIO, Objetivo.PERDIDA_GRASA
    )
    assert revisado.advertencias, "debe advertir antes de acompañar una pérdida de peso"


def test_el_deficit_crece_con_el_indice_de_masa_corporal():
    """A mayor reserva de grasa, mayor recorte tolerable."""
    ajustes = [
        abs(seguridad.ajuste_admitido(Objetivo.PERDIDA_GRASA, indice))
        for indice in (17.0, 20.0, 23.0, 33.0)
    ]

    assert ajustes == sorted(ajustes)
    assert ajustes[0] == 0.0
    assert ajustes[-1] == formulas.DEFICIT_MAXIMO


def test_el_ajuste_nunca_excede_los_limites_de_la_regla_b():
    """El guardarrail acota, nunca amplia lo que la regla del negocio admite."""
    for indice in (15.0, 18.5, 21.0, 25.0, 30.0, 45.0):
        deficit = seguridad.ajuste_admitido(Objetivo.PERDIDA_GRASA, indice)
        superavit = seguridad.ajuste_admitido(Objetivo.GANANCIA_MUSCULAR, indice)

        assert -formulas.DEFICIT_MAXIMO <= deficit <= 0
        assert 0 <= superavit <= formulas.SUPERAVIT_MAXIMO


def test_el_superavit_se_modera_con_exceso_de_grasa_corporal():
    delgado = seguridad.ajuste_admitido(Objetivo.GANANCIA_MUSCULAR, 22.0)
    con_obesidad = seguridad.ajuste_admitido(Objetivo.GANANCIA_MUSCULAR, 33.0)

    assert con_obesidad < delgado


def test_el_mantenimiento_no_se_ajusta():
    for indice in (17.0, 22.0, 27.0, 35.0):
        assert seguridad.ajuste_admitido(Objetivo.MANTENIMIENTO, indice) == 0.0


# --------------------------------------------------------------------------
# Proteina sobre peso de referencia
# --------------------------------------------------------------------------


def test_la_proteina_no_se_calcula_sobre_el_peso_total_en_obesidad():
    """El calculo original pedia 286 gramos diarios a este perfil."""
    macros, revisado = _revisar(
        130, 175, 40, Sexo.MASCULINO, NivelActividad.SEDENTARIO, Objetivo.PERDIDA_GRASA
    )

    assert macros.proteina_g > 250
    assert revisado.proteina_g < macros.proteina_g
    assert revisado.proteina_g >= 100, "sigue siendo un aporte proteico alto"


def test_el_peso_de_referencia_coincide_con_el_real_sin_obesidad():
    for peso, estatura in ((60, 165), (78, 175), (85, 180)):
        assert seguridad.peso_de_referencia_proteico(peso, estatura) == peso


def test_la_proteina_no_supera_el_tope_de_energia():
    for peso in (60, 90, 130, 200):
        _, revisado = _revisar(
            peso, 170, 35, Sexo.MASCULINO, NivelActividad.SEDENTARIO, Objetivo.PERDIDA_GRASA
        )
        energia_proteica = revisado.proteina_g * formulas.KCAL_POR_GRAMO_PROTEINA

        assert energia_proteica <= revisado.energia_kcal * (
            seguridad.PROPORCION_MAXIMA_PROTEINA + 0.01
        )


# --------------------------------------------------------------------------
# Coherencia del plan corregido
# --------------------------------------------------------------------------


@pytest.mark.parametrize("objetivo", list(Objetivo))
@pytest.mark.parametrize(("peso", "estatura"), [(45, 155), (70, 170), (130, 175)])
def test_los_macronutrientes_siempre_suman_la_energia_declarada(objetivo, peso, estatura):
    """El criterio de aceptacion de HU-06 exige que la suma cuadre sin residuo."""
    _, revisado = _revisar(
        peso, estatura, 30, Sexo.FEMENINO, NivelActividad.MODERADO, objetivo
    )
    suma = (
        revisado.proteina_g * formulas.KCAL_POR_GRAMO_PROTEINA
        + revisado.carbohidrato_g * formulas.KCAL_POR_GRAMO_CARBOHIDRATO
        + revisado.grasa_g * formulas.KCAL_POR_GRAMO_GRASA
    )

    assert suma == revisado.energia_kcal


def test_un_perfil_sin_riesgo_no_se_corrige():
    """El guardarrail no debe intervenir donde el calculo ya era seguro."""
    _, revisado = _revisar(
        78, 175, 28, Sexo.MASCULINO, NivelActividad.MODERADO, Objetivo.MANTENIMIENTO
    )

    assert not revisado.hubo_correccion
    assert revisado.correcciones == []
    assert revisado.energia_kcal == revisado.energia_calculada_kcal


def test_ningun_macronutriente_resulta_negativo():
    for peso in (30, 45, 78, 130, 250):
        for objetivo in Objetivo:
            _, revisado = _revisar(
                peso, 160, 65, Sexo.FEMENINO, NivelActividad.SEDENTARIO, objetivo
            )
            assert revisado.proteina_g > 0
            assert revisado.carbohidrato_g >= 0
            assert revisado.grasa_g >= 0


# --------------------------------------------------------------------------
# Integracion con la interfaz de programacion
# --------------------------------------------------------------------------


def _registrar_perfil(cliente, token, **cambios):
    datos = {**PERFIL_COMPLETO, **cambios}
    respuesta = cliente.post(
        "/api/v1/perfil-biometrico", json=datos, headers=encabezado(token)
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_el_plan_declara_las_correcciones_de_seguridad(cliente, token_usuario):
    """El usuario debe leer por que su plan no es el calculo crudo."""
    _registrar_perfil(
        cliente,
        token_usuario,
        peso_kg=50.0,
        estatura_cm=155.0,
        edad=55,
        sexo="femenino",
        nivel_actividad="sedentario",
        objetivo="perdida_grasa",
    )
    plan = cliente.post("/api/v1/plan-nutricional", headers=encabezado(token_usuario)).json()

    assert plan["ajustado_por_seguridad"] is True
    assert plan["correcciones_de_seguridad"], "debe explicar el ajuste"
    assert plan["advertencias_de_salud"], "debe advertir sobre el mínimo alimentario"
    assert plan["calorias_objetivo"] >= seguridad.ENERGIA_MINIMA_KCAL[Sexo.FEMENINO]


def test_un_plan_sin_ajuste_no_declara_correcciones(cliente, token_usuario):
    _registrar_perfil(cliente, token_usuario)
    plan = cliente.post("/api/v1/plan-nutricional", headers=encabezado(token_usuario)).json()

    assert plan["ajustado_por_seguridad"] is False
    assert plan["correcciones_de_seguridad"] == []
    assert plan["advertencias_de_salud"] == []


def test_la_explicacion_del_objetivo_declara_el_porcentaje_real(cliente, token_usuario):
    """Anunciar un 20 % que el plan no aplica describiria un plan distinto."""
    _registrar_perfil(
        cliente,
        token_usuario,
        peso_kg=45.0,
        estatura_cm=152.0,
        edad=25,
        sexo="femenino",
        nivel_actividad="sedentario",
        objetivo="perdida_grasa",
    )
    plan = cliente.post("/api/v1/plan-nutricional", headers=encabezado(token_usuario)).json()

    assert "20 %" not in plan["explicacion_objetivo"]
    assert "10 %" in plan["explicacion_objetivo"]


def test_el_margen_de_error_sigue_midiendo_el_modelo_y_no_el_guardarrail(
    cliente, token_usuario
):
    """El ajuste de seguridad es una regla del negocio, no un error del modelo.

    Si el margen se midiera sobre el valor ya corregido, un plan correcto se
    reportaria como fuera del margen del 5 % que exige la historia HU-06.
    """
    _registrar_perfil(
        cliente,
        token_usuario,
        peso_kg=50.0,
        estatura_cm=155.0,
        edad=55,
        sexo="femenino",
        nivel_actividad="sedentario",
        objetivo="perdida_grasa",
    )
    plan = cliente.post("/api/v1/plan-nutricional", headers=encabezado(token_usuario)).json()

    assert plan["ajustado_por_seguridad"] is True
    assert plan["dentro_del_margen_admitido"] is True
    assert plan["margen_error_porcentaje"] < 5.0
