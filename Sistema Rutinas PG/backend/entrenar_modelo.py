"""Script de entrenamiento del modelo neuronal (subfase 3.2).

Genera el conjunto de datos, entrena la red, evalua su margen de error frente a
las formulas de Mifflin-St Jeor y Harris-Benedict, y guarda el modelo junto con
su normalizador y sus metricas.

    uv run python entrenar_modelo.py
    uv run python entrenar_modelo.py --perfiles 40000 --epocas 300

El modelo entrenado no se versiona: se regenera con este script, que es lo que
permite reentrenarlo sin modificar el codigo del servicio que lo consume
(requerimiento no funcional 4.5.6).
"""

import argparse
import logging
import sys

from app.motor.red_neuronal import (
    EPOCAS_PREDETERMINADAS,
    MARGEN_ERROR_MAXIMO,
    entrenar_y_guardar,
)


def principal() -> int:
    """Ejecuta el entrenamiento y devuelve el codigo de salida del proceso."""
    analizador = argparse.ArgumentParser(
        description="Entrena el modelo de red neuronal del requerimiento energético."
    )
    analizador.add_argument(
        "--perfiles",
        type=int,
        default=40_000,
        help="Cantidad de perfiles sintéticos a generar (predeterminado: 40000).",
    )
    analizador.add_argument(
        "--epocas",
        type=int,
        default=EPOCAS_PREDETERMINADAS,
        help=f"Épocas máximas de entrenamiento (predeterminado: {EPOCAS_PREDETERMINADAS}).",
    )
    analizador.add_argument(
        "--semilla",
        type=int,
        default=2026,
        help="Semilla aleatoria, para que el entrenamiento sea reproducible.",
    )
    argumentos = analizador.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")

    metricas = entrenar_y_guardar(
        cantidad=argumentos.perfiles,
        epocas=argumentos.epocas,
        semilla=argumentos.semilla,
        verbosidad=1,
    )

    print()
    print(metricas.resumen())
    if metricas.cumple_el_criterio:
        print(
            f"El modelo cumple el criterio de aceptación: margen de error medio por "
            f"debajo del {MARGEN_ERROR_MAXIMO * 100:.0f} %."
        )
        return 0

    print(
        f"ATENCIÓN: el margen de error medio supera el {MARGEN_ERROR_MAXIMO * 100:.0f} % "
        "exigido por la hipótesis. Ajuste los hiperparámetros y vuelva a entrenar."
    )
    return 1


if __name__ == "__main__":
    sys.exit(principal())
