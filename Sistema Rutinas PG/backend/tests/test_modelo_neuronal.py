"""Pruebas del modelo de red neuronal (subfase 3.2, historia HU-06).

Verifican la arquitectura del apartado 2.3 y el criterio de aceptacion que
sostiene la hipotesis de la investigacion: un margen de error inferior al 5 %
frente a las formulas de Mifflin-St Jeor y Harris-Benedict.

Las pruebas que entrenan la red tardan mas que el resto de la suite. Se marcan
como `lenta` para poder excluirlas durante el desarrollo:

    uv run pytest -m "not lenta"
"""

import numpy as np
import pytest

from app.modelos.enumeraciones import NivelActividad, Objetivo, Sexo
from app.motor import conjunto_datos, formulas
from app.motor.red_neuronal import (
    MARGEN_ERROR_MAXIMO,
    ModeloNoEntrenado,
    MotorNeuronal,
    construir_modelo,
    entrenar,
    evaluar_margen_de_error,
)

PERFIL_DE_PRUEBA = {
    "peso_kg": 78.0,
    "estatura_cm": 174.0,
    "edad": 28,
    "sexo": Sexo.MASCULINO,
    "nivel_actividad": NivelActividad.MODERADO,
    "objetivo": Objetivo.MANTENIMIENTO,
}


@pytest.fixture(scope="module", name="modelo_entrenado")
def fixture_modelo_entrenado():
    """Entrena una red pequeña una sola vez para todas las pruebas del módulo."""
    datos = conjunto_datos.preparar_datos(cantidad=4000, semilla=2026)
    modelo, metricas = entrenar(datos=datos, epocas=150, verbosidad=0)
    return modelo, metricas, datos


# --------------------------------------------------------------------------
# Arquitectura de la red (apartado 2.3)
# --------------------------------------------------------------------------


def test_la_red_recibe_las_seis_variables_biometricas():
    """La capa de entrada corresponde a las variables del perfil biométrico."""
    modelo = construir_modelo()

    assert modelo.input_shape == (None, len(conjunto_datos.COLUMNAS_ENTRADA))


def test_la_red_entrega_el_requerimiento_y_los_macronutrientes():
    """La capa de salida entrega la energía y los tres macronutrientes."""
    modelo = construir_modelo()

    assert modelo.output_shape == (None, len(conjunto_datos.COLUMNAS_SALIDA))


def test_las_capas_ocultas_usan_activacion_relu():
    """El apartado 2.3 prescribe capas ocultas densas con activación ReLU."""
    modelo = construir_modelo()
    ocultas = [capa for capa in modelo.layers if capa.name.startswith("capa_oculta")]

    assert len(ocultas) == 3
    assert all(capa.activation.__name__ == "relu" for capa in ocultas)


def test_la_capa_de_salida_es_lineal():
    """El problema es de regresión: la salida no se acota con una activación."""
    salida = modelo_salida = construir_modelo().layers[-1]

    assert modelo_salida.activation.__name__ == "linear"
    assert salida.units == len(conjunto_datos.COLUMNAS_SALIDA)


def test_la_construccion_es_reproducible_con_la_misma_semilla():
    """Con la misma semilla, los pesos iniciales deben coincidir."""
    primero = construir_modelo(semilla=11).get_weights()
    segundo = construir_modelo(semilla=11).get_weights()

    assert all(np.array_equal(a, b) for a, b in zip(primero, segundo))


# --------------------------------------------------------------------------
# Criterio de aceptacion: margen de error inferior al 5 %
# --------------------------------------------------------------------------


@pytest.mark.lenta
def test_el_margen_de_error_medio_es_inferior_al_cinco_por_ciento(modelo_entrenado):
    """Criterio que sostiene la hipótesis: menos del 5 % frente a las fórmulas."""
    _, metricas, _ = modelo_entrenado

    assert metricas.margen_error_medio < MARGEN_ERROR_MAXIMO
    assert metricas.cumple_el_criterio


@pytest.mark.lenta
def test_la_gran_mayoria_de_los_perfiles_queda_bajo_el_cinco_por_ciento(modelo_entrenado):
    """No basta con la media: el criterio debe cumplirse perfil por perfil."""
    _, metricas, _ = modelo_entrenado

    assert metricas.proporcion_bajo_el_cinco_por_ciento > 0.95


@pytest.mark.lenta
def test_el_margen_se_mantiene_en_los_extremos_del_dominio(modelo_entrenado):
    """La malla sistemática comprueba el error donde el muestreo deja menos ejemplos."""
    modelo, _, datos = modelo_entrenado

    malla = conjunto_datos.generar_malla_de_verificacion()
    normalizada = conjunto_datos.ConjuntoDatos(
        entradas=datos.normalizador.aplicar(malla.entradas),
        salidas=datos.normalizador_salidas.aplicar(malla.salidas),
    )
    medidas = evaluar_margen_de_error(modelo, normalizada, datos.normalizador_salidas)

    assert medidas["margen_error_medio"] < MARGEN_ERROR_MAXIMO


@pytest.mark.lenta
def test_las_metricas_documentan_el_tamanio_de_los_conjuntos(modelo_entrenado):
    """El resumen debe poder trasladarse a la documentación del modelo."""
    _, metricas, _ = modelo_entrenado

    assert metricas.perfiles_entrenamiento == 3200
    assert metricas.perfiles_validacion == 800
    assert "Margen de error medio" in metricas.resumen()


# --------------------------------------------------------------------------
# Prediccion sobre un perfil concreto
# --------------------------------------------------------------------------


@pytest.mark.lenta
def test_la_prediccion_reparte_la_energia_entre_los_tres_macronutrientes(modelo_entrenado):
    """Criterio de HU-06: la suma de los aportes coincide con el total declarado."""
    modelo, _, datos = modelo_entrenado
    motor = MotorNeuronal(modelo, datos.normalizador, datos.normalizador_salidas, {})

    prediccion = motor.predecir(**PERFIL_DE_PRUEBA)

    aporte = (
        prediccion.proteina_g * formulas.KCAL_POR_GRAMO_PROTEINA
        + prediccion.carbohidrato_g * formulas.KCAL_POR_GRAMO_CARBOHIDRATO
        + prediccion.grasa_g * formulas.KCAL_POR_GRAMO_GRASA
    )
    assert aporte == prediccion.energia_kcal


@pytest.mark.lenta
def test_la_prediccion_se_aproxima_a_las_formulas_de_referencia(modelo_entrenado):
    """El valor predicho no difiere en más del 5 % del de las fórmulas."""
    modelo, _, datos = modelo_entrenado
    motor = MotorNeuronal(modelo, datos.normalizador, datos.normalizador_salidas, {})

    prediccion = motor.predecir(**PERFIL_DE_PRUEBA)
    referencias = formulas.calcular_referencias(
        PERFIL_DE_PRUEBA["peso_kg"],
        PERFIL_DE_PRUEBA["estatura_cm"],
        PERFIL_DE_PRUEBA["edad"],
        PERFIL_DE_PRUEBA["sexo"],
        PERFIL_DE_PRUEBA["nivel_actividad"],
    )
    esperado = formulas.ajustar_por_objetivo(
        referencias.gasto_promedio, PERFIL_DE_PRUEBA["objetivo"]
    )

    assert formulas.margen_de_error(prediccion.energia_kcal, esperado) < MARGEN_ERROR_MAXIMO


@pytest.mark.lenta
def test_ningun_macronutriente_predicho_es_negativo(modelo_entrenado):
    """Una salida negativa produciría un plan sin sentido."""
    modelo, _, datos = modelo_entrenado
    motor = MotorNeuronal(modelo, datos.normalizador, datos.normalizador_salidas, {})

    for objetivo in Objetivo:
        prediccion = motor.predecir(**{**PERFIL_DE_PRUEBA, "objetivo": objetivo})

        assert prediccion.energia_kcal > 0
        assert prediccion.proteina_g > 0
        assert prediccion.carbohidrato_g >= 0
        assert prediccion.grasa_g >= 0


@pytest.mark.lenta
def test_el_deficit_produce_menos_energia_que_el_superavit(modelo_entrenado):
    """El objetivo declarado debe alterar el resultado en la dirección correcta."""
    modelo, _, datos = modelo_entrenado
    motor = MotorNeuronal(modelo, datos.normalizador, datos.normalizador_salidas, {})

    perdida = motor.predecir(**{**PERFIL_DE_PRUEBA, "objetivo": Objetivo.PERDIDA_GRASA})
    mantenimiento = motor.predecir(**{**PERFIL_DE_PRUEBA, "objetivo": Objetivo.MANTENIMIENTO})
    ganancia = motor.predecir(**{**PERFIL_DE_PRUEBA, "objetivo": Objetivo.GANANCIA_MUSCULAR})

    assert perdida.energia_kcal < mantenimiento.energia_kcal < ganancia.energia_kcal


@pytest.mark.lenta
def test_la_prediccion_responde_en_menos_de_tres_segundos(modelo_entrenado):
    """Criterio de aceptación de HU-06: el cálculo se completa en menos de tres segundos."""
    import time

    modelo, _, datos = modelo_entrenado
    motor = MotorNeuronal(modelo, datos.normalizador, datos.normalizador_salidas, {})
    motor.predecir(**PERFIL_DE_PRUEBA)  # descarta el costo de la primera invocación

    inicio = time.perf_counter()
    motor.predecir(**PERFIL_DE_PRUEBA)
    transcurrido = time.perf_counter() - inicio

    assert transcurrido < 3.0


def test_cargar_sin_modelo_entrenado_falla_con_un_error_explicito(monkeypatch, tmp_path):
    """Si el modelo no se ha entrenado, el sistema lo dice en lugar de fallar de forma opaca."""
    from app.motor import red_neuronal

    monkeypatch.setattr(red_neuronal, "RUTA_MODELO", tmp_path / "inexistente.keras")
    monkeypatch.setattr(red_neuronal, "RUTA_METADATOS", tmp_path / "inexistente.json")

    with pytest.raises(ModeloNoEntrenado):
        red_neuronal.MotorNeuronal.cargar()
