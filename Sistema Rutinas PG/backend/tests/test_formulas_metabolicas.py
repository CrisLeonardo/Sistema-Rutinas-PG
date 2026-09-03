"""Pruebas de las formulas de referencia y del conjunto de datos (subfase 3.1).

Verifican la aritmetica del apartado 2.4.2, las reglas del negocio *b* y *c* del
apartado 4.3.4 y la cobertura del conjunto con que se entrenara el modelo, cuya
insuficiencia de volumen es el segundo riesgo tecnico del apartado 4.9.1.
"""

import numpy as np
import pytest

from app.modelos.enumeraciones import NivelActividad, Objetivo, Sexo
from app.motor import conjunto_datos, formulas


# --------------------------------------------------------------------------
# Formulas de referencia (apartado 2.4.2)
# --------------------------------------------------------------------------


def test_mifflin_para_hombres_sigue_la_ecuacion_de_la_tesis():
    """Diez por el peso, mas 6.25 por la estatura, menos cinco por la edad, mas cinco."""
    esperado = (10 * 80) + (6.25 * 175) - (5 * 30) + 5

    obtenido = formulas.tasa_metabolica_basal_mifflin(80, 175, 30, Sexo.MASCULINO)

    assert obtenido == pytest.approx(esperado)
    assert obtenido == pytest.approx(1748.75)


def test_mifflin_para_mujeres_cambia_la_constante_final():
    """Para las mujeres la constante final es menos 161."""
    esperado = (10 * 65) + (6.25 * 162) - (5 * 30) - 161

    obtenido = formulas.tasa_metabolica_basal_mifflin(65, 162, 30, Sexo.FEMENINO)

    assert obtenido == pytest.approx(esperado)
    assert obtenido == pytest.approx(1351.5)


def test_harris_benedict_para_hombres():
    """Revision de Roza y Shizgal de la ecuacion de Harris-Benedict."""
    esperado = 88.362 + (13.397 * 80) + (4.799 * 175) - (5.677 * 30)

    obtenido = formulas.tasa_metabolica_basal_harris_benedict(80, 175, 30, Sexo.MASCULINO)

    assert obtenido == pytest.approx(esperado)


def test_harris_benedict_para_mujeres():
    """La ecuacion de las mujeres usa sus propios coeficientes."""
    esperado = 447.593 + (9.247 * 65) + (3.098 * 162) - (4.330 * 30)

    obtenido = formulas.tasa_metabolica_basal_harris_benedict(65, 162, 30, Sexo.FEMENINO)

    assert obtenido == pytest.approx(esperado)


def test_las_dos_formulas_no_difieren_mas_del_diez_por_ciento():
    """Ambas ecuaciones deben producir valores comparables para el mismo perfil.

    Si difirieran mucho, el promedio con que se entrena el modelo no seria una
    referencia defendible.
    """
    referencias = formulas.calcular_referencias(
        80, 175, 30, Sexo.MASCULINO, NivelActividad.MODERADO
    )

    assert referencias.discrepancia_relativa < 0.10


@pytest.mark.parametrize(
    ("nivel", "factor"),
    [
        (NivelActividad.SEDENTARIO, 1.2),
        (NivelActividad.LIGERO, 1.375),
        (NivelActividad.MODERADO, 1.55),
        (NivelActividad.ALTO, 1.725),
        (NivelActividad.MUY_ALTO, 1.9),
    ],
)
def test_factores_de_actividad(nivel, factor):
    """El factor de actividad multiplica la tasa metabolica basal."""
    assert formulas.factor_actividad(nivel) == factor
    assert formulas.gasto_energetico_total(1500, nivel) == pytest.approx(1500 * factor)


def test_los_factores_de_actividad_crecen_con_el_nivel():
    """A mayor actividad declarada, mayor gasto energetico estimado."""
    valores = [formulas.factor_actividad(nivel) for nivel in NivelActividad]

    assert valores == sorted(valores)


def test_todos_los_niveles_de_actividad_tienen_factor():
    """Ningun valor del catalogo puede quedar sin factor asignado."""
    assert set(formulas.FACTORES_ACTIVIDAD) == set(NivelActividad)


# --------------------------------------------------------------------------
# Regla del negocio *b*: deficit y superavit controlados
# --------------------------------------------------------------------------


def test_el_deficit_nunca_excede_el_veinte_por_ciento():
    """Regla del negocio b: el deficit maximo es del 20 % del gasto energetico."""
    ajustado = formulas.ajustar_por_objetivo(2500, Objetivo.PERDIDA_GRASA)

    assert ajustado == pytest.approx(2000)
    assert ajustado >= 2500 * (1 - formulas.DEFICIT_MAXIMO)


def test_el_superavit_nunca_excede_el_quince_por_ciento():
    """Regla del negocio b: el superavit maximo es del 15 % del gasto energetico."""
    ajustado = formulas.ajustar_por_objetivo(2500, Objetivo.GANANCIA_MUSCULAR)

    assert ajustado == pytest.approx(2875)
    assert ajustado <= 2500 * (1 + formulas.SUPERAVIT_MAXIMO)


def test_el_mantenimiento_no_altera_el_gasto_energetico():
    """Sin cambio de composicion corporal, la energia prescrita es la del gasto."""
    assert formulas.ajustar_por_objetivo(2500, Objetivo.MANTENIMIENTO) == pytest.approx(2500)


@pytest.mark.parametrize("objetivo", list(Objetivo))
def test_el_ajuste_se_mantiene_dentro_de_los_limites_para_todo_objetivo(objetivo):
    """Ningun objetivo del catalogo puede salirse del rango permitido."""
    gasto = 2200
    ajustado = formulas.ajustar_por_objetivo(gasto, objetivo)

    assert gasto * (1 - formulas.DEFICIT_MAXIMO) <= ajustado
    assert ajustado <= gasto * (1 + formulas.SUPERAVIT_MAXIMO)


# --------------------------------------------------------------------------
# Regla del negocio *c*: aporte proteico
# --------------------------------------------------------------------------


@pytest.mark.parametrize("objetivo", list(Objetivo))
@pytest.mark.parametrize("peso", [30, 55.5, 80, 120, 250])
def test_la_proteina_se_mantiene_entre_uno_seis_y_dos_dos_por_kilogramo(peso, objetivo):
    """Regla del negocio c: entre 1.6 y 2.2 gramos por kilogramo de peso corporal."""
    gramos = formulas.gramos_proteina(peso, objetivo)
    por_kilogramo = gramos / peso

    assert formulas.PROTEINA_MINIMA_POR_KG <= por_kilogramo <= formulas.PROTEINA_MAXIMA_POR_KG


def test_la_perdida_de_grasa_prescribe_mas_proteina_que_el_mantenimiento():
    """En deficit el aporte proteico sube, porque preserva la masa muscular."""
    en_deficit = formulas.gramos_proteina(80, Objetivo.PERDIDA_GRASA)
    en_mantenimiento = formulas.gramos_proteina(80, Objetivo.MANTENIMIENTO)

    assert en_deficit > en_mantenimiento


# --------------------------------------------------------------------------
# Distribucion de macronutrientes y constantes de Atwater (apartado 2.4.3)
# --------------------------------------------------------------------------


@pytest.mark.parametrize("objetivo", list(Objetivo))
@pytest.mark.parametrize(("peso", "energia"), [(30, 1200), (60, 2000), (95, 2800), (250, 4200)])
def test_la_suma_de_los_macronutrientes_coincide_con_la_energia_total(peso, energia, objetivo):
    """Criterio de aceptacion de HU-06: la suma de los aportes coincide con el total."""
    macros = formulas.distribuir_macronutrientes(energia, peso, objetivo)

    assert macros.energia_de_los_macronutrientes == macros.energia_kcal


@pytest.mark.parametrize("objetivo", list(Objetivo))
@pytest.mark.parametrize(("peso", "energia"), [(30, 1200), (60, 2000), (95, 2800), (250, 4200)])
def test_los_porcentajes_de_los_macronutrientes_suman_cien(peso, energia, objetivo):
    """Los macronutrientes se expresan en gramos y en porcentaje."""
    macros = formulas.distribuir_macronutrientes(energia, peso, objetivo)
    suma = macros.porcentaje_proteina + macros.porcentaje_carbohidrato + macros.porcentaje_grasa

    assert suma == pytest.approx(100, abs=0.3)


def test_las_constantes_de_atwater_son_las_del_marco_teorico():
    """Carbohidrato y proteina aportan 4 kilocalorias por gramo; la grasa, 9."""
    assert formulas.KCAL_POR_GRAMO_PROTEINA == 4
    assert formulas.KCAL_POR_GRAMO_CARBOHIDRATO == 4
    assert formulas.KCAL_POR_GRAMO_GRASA == 9


@pytest.mark.parametrize("objetivo", list(Objetivo))
@pytest.mark.parametrize(("peso", "energia"), [(30, 1100), (45, 1300), (80, 2400), (250, 4500)])
def test_ningun_macronutriente_resulta_negativo(peso, energia, objetivo):
    """Ni siquiera en los perfiles de menor peso y mayor deficit."""
    macros = formulas.distribuir_macronutrientes(energia, peso, objetivo)

    assert macros.proteina_g > 0
    assert macros.carbohidrato_g >= 0
    assert macros.grasa_g >= 0


def test_la_energia_declarada_no_se_aleja_de_la_solicitada():
    """El redondeo a gramos enteros no debe desviar el total de forma apreciable."""
    macros = formulas.distribuir_macronutrientes(2500, 80, Objetivo.MANTENIMIENTO)

    assert formulas.margen_de_error(macros.energia_kcal, 2500) < 0.01


def test_el_agua_recomendada_crece_con_el_peso_y_la_actividad():
    """La hidratacion se calcula a partir del peso y del nivel de actividad (2.4.4)."""
    ligera = formulas.agua_recomendada_ml(70, NivelActividad.SEDENTARIO)
    intensa = formulas.agua_recomendada_ml(70, NivelActividad.MUY_ALTO)
    pesada = formulas.agua_recomendada_ml(100, NivelActividad.SEDENTARIO)

    assert ligera == 70 * 35
    assert intensa > ligera
    assert pesada > ligera


def test_el_margen_de_error_es_relativo_y_simetrico():
    """El margen de error se expresa como fraccion del valor de referencia."""
    assert formulas.margen_de_error(2100, 2000) == pytest.approx(0.05)
    assert formulas.margen_de_error(1900, 2000) == pytest.approx(0.05)

    with pytest.raises(ValueError):
        formulas.margen_de_error(100, 0)


# --------------------------------------------------------------------------
# Conjunto de datos de entrenamiento (subfase 3.1)
# --------------------------------------------------------------------------


def test_el_conjunto_sintetico_tiene_la_cantidad_y_la_forma_esperadas():
    """Cada perfil aporta seis variables de entrada y cuatro de salida."""
    conjunto = conjunto_datos.generar_perfiles_sinteticos(cantidad=500)

    assert len(conjunto) == 500
    assert conjunto.entradas.shape == (500, len(conjunto_datos.COLUMNAS_ENTRADA))
    assert conjunto.salidas.shape == (500, len(conjunto_datos.COLUMNAS_SALIDA))


def test_el_conjunto_sintetico_cubre_todo_el_rango_antropometrico():
    """Mitigacion del riesgo de volumen insuficiente: los extremos quedan representados."""
    conjunto = conjunto_datos.generar_perfiles_sinteticos(cantidad=5000)
    pesos = conjunto.entradas[:, 0]
    estaturas = conjunto.entradas[:, 1]
    edades = conjunto.entradas[:, 2]

    assert pesos.min() < 40 and pesos.max() > 240
    assert estaturas.min() < 130 and estaturas.max() > 210
    assert edades.min() == conjunto_datos.EDAD_MINIMA
    assert edades.max() >= conjunto_datos.EDAD_MAXIMA - 1


def test_el_conjunto_sintetico_representa_ambos_sexos_y_todos_los_niveles():
    """Ninguna categoria del catalogo puede quedar fuera del entrenamiento."""
    conjunto = conjunto_datos.generar_perfiles_sinteticos(cantidad=3000)

    assert set(np.unique(conjunto.entradas[:, 3])) == {0.0, 1.0}
    assert len(np.unique(conjunto.entradas[:, 4])) == len(NivelActividad)
    assert len(np.unique(conjunto.entradas[:, 5])) == len(Objetivo)


def test_la_generacion_es_reproducible_con_la_misma_semilla():
    """El conjunto debe poder reconstruirse igual para que el modelo sea auditable."""
    primero = conjunto_datos.generar_perfiles_sinteticos(cantidad=200, semilla=7)
    segundo = conjunto_datos.generar_perfiles_sinteticos(cantidad=200, semilla=7)
    distinto = conjunto_datos.generar_perfiles_sinteticos(cantidad=200, semilla=8)

    assert np.array_equal(primero.entradas, segundo.entradas)
    assert not np.array_equal(primero.entradas, distinto.entradas)


def test_las_salidas_del_conjunto_respetan_las_reglas_del_negocio():
    """Toda fila generada cumple las reglas *b* y *c* y la identidad de Atwater."""
    conjunto = conjunto_datos.generar_perfiles_sinteticos(cantidad=1000)
    pesos = conjunto.entradas[:, 0]
    energia, proteina, carbohidrato, grasa, volumen = conjunto.salidas.T

    aporte = (
        proteina * formulas.KCAL_POR_GRAMO_PROTEINA
        + carbohidrato * formulas.KCAL_POR_GRAMO_CARBOHIDRATO
        + grasa * formulas.KCAL_POR_GRAMO_GRASA
    )
    proteina_por_kg = proteina / pesos

    assert np.allclose(aporte, energia)
    assert (proteina_por_kg >= formulas.PROTEINA_MINIMA_POR_KG - 0.05).all()
    assert (proteina_por_kg <= formulas.PROTEINA_MAXIMA_POR_KG + 0.05).all()
    assert (energia > 0).all()
    # Regla del apartado 2.5.1: el volumen semanal se mantiene en el rango que
    # el cuerpo puede recuperar.
    assert (volumen >= formulas.SERIES_MINIMAS_POR_GRUPO).all()
    assert (volumen <= formulas.SERIES_MAXIMAS_POR_GRUPO).all()


def test_la_normalizacion_deja_media_cero_y_desviacion_uno():
    """Las variables de entrada se normalizan antes de entrar a la red."""
    conjunto = conjunto_datos.generar_perfiles_sinteticos(cantidad=1000)
    normalizador = conjunto_datos.ajustar_normalizador(conjunto.entradas)

    normalizadas = normalizador.aplicar(conjunto.entradas)

    assert np.allclose(normalizadas.mean(axis=0), 0, atol=1e-9)
    assert np.allclose(normalizadas.std(axis=0), 1, atol=1e-9)


def test_la_normalizacion_es_reversible():
    """Sin esta propiedad no seria posible interpretar lo que la red recibe."""
    conjunto = conjunto_datos.generar_perfiles_sinteticos(cantidad=100)
    normalizador = conjunto_datos.ajustar_normalizador(conjunto.entradas)

    ida_y_vuelta = normalizador.revertir(normalizador.aplicar(conjunto.entradas))

    assert np.allclose(ida_y_vuelta, conjunto.entradas)


def test_el_normalizador_se_puede_guardar_y_recuperar():
    """Se almacena junto al modelo entrenado; sin el, las predicciones no valen."""
    conjunto = conjunto_datos.generar_perfiles_sinteticos(cantidad=100)
    original = conjunto_datos.ajustar_normalizador(conjunto.entradas)

    recuperado = conjunto_datos.Normalizador.desde_diccionario(original.a_diccionario())

    assert np.allclose(original.aplicar(conjunto.entradas), recuperado.aplicar(conjunto.entradas))


def test_la_division_reparte_todas_las_filas_sin_repetirlas():
    """Entrenamiento y validacion son conjuntos disjuntos que suman el total."""
    conjunto = conjunto_datos.generar_perfiles_sinteticos(cantidad=1000)

    entrenamiento, validacion = conjunto_datos.separar_entrenamiento_validacion(
        conjunto, proporcion_validacion=0.2
    )

    assert len(entrenamiento) == 800
    assert len(validacion) == 200
    filas_totales = {tuple(fila) for fila in conjunto.entradas}
    filas_divididas = {tuple(fila) for fila in entrenamiento.entradas} | {
        tuple(fila) for fila in validacion.entradas
    }
    assert filas_divididas == filas_totales


@pytest.mark.parametrize("proporcion", [0, 1, -0.1, 1.5])
def test_la_division_rechaza_proporciones_imposibles(proporcion):
    """Una proporcion fuera de cero a uno dejaria un conjunto vacio."""
    conjunto = conjunto_datos.generar_perfiles_sinteticos(cantidad=100)

    with pytest.raises(ValueError):
        conjunto_datos.separar_entrenamiento_validacion(
            conjunto, proporcion_validacion=proporcion
        )


def test_preparar_datos_normaliza_solo_con_el_conjunto_de_entrenamiento():
    """Normalizar con el total filtraria informacion de la validacion al modelo."""
    preparados = conjunto_datos.preparar_datos(cantidad=1000)

    assert np.allclose(preparados.entrenamiento.entradas.mean(axis=0), 0, atol=1e-9)
    # La validacion se transforma con los parametros del entrenamiento, de modo
    # que su media no tiene por que ser exactamente cero.
    assert len(preparados.validacion) == 200


def test_la_malla_de_verificacion_recorre_los_extremos_del_dominio():
    """Garantiza que ninguna combinacion quede sin representar en los limites."""
    malla = conjunto_datos.generar_malla_de_verificacion()

    assert len(malla) > 1000
    assert malla.entradas[:, 0].min() == conjunto_datos.RANGO_PESO[0]
    assert set(np.unique(malla.entradas[:, 3])) == {0.0, 1.0}
    assert len(np.unique(malla.entradas[:, 4])) == len(NivelActividad)


def test_el_vector_de_entrada_conserva_el_orden_declarado():
    """El orden de las columnas no puede cambiar entre entrenamiento y prediccion."""
    vector = conjunto_datos.vector_entrada(
        80, 175, 30, Sexo.MASCULINO, NivelActividad.MODERADO, Objetivo.MANTENIMIENTO
    )

    assert len(vector) == len(conjunto_datos.COLUMNAS_ENTRADA)
    assert vector[0] == 80
    assert vector[1] == 175
    assert vector[2] == 30
    assert vector[3] == 1.0
    assert vector[4] == formulas.factor_actividad(NivelActividad.MODERADO)
    assert vector[5] == pytest.approx(1.0)
