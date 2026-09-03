"""Motor de calculo del requerimiento energetico (epica E3, historia HU-06).

Reune la aritmetica de referencia, la preparacion del conjunto de datos y, a
partir de la subfase 3.2, el modelo de red neuronal entrenado con Keras. Se
mantiene separado de `servicios/` porque no depende de la base de datos ni de la
interfaz de programacion: puede entrenarse y evaluarse por su cuenta.
"""

from app.motor.formulas import (
    DistribucionMacronutrientes,
    ValoresReferencia,
    ajustar_por_objetivo,
    calcular_referencias,
    distribuir_macronutrientes,
    gasto_energetico_total,
    margen_de_error,
    tasa_metabolica_basal_harris_benedict,
    tasa_metabolica_basal_mifflin,
)

__all__ = [
    "DistribucionMacronutrientes",
    "ValoresReferencia",
    "ajustar_por_objetivo",
    "calcular_referencias",
    "distribuir_macronutrientes",
    "gasto_energetico_total",
    "margen_de_error",
    "tasa_metabolica_basal_harris_benedict",
    "tasa_metabolica_basal_mifflin",
]
