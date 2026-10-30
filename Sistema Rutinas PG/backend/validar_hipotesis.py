"""Comprobación de la hipótesis: la red neuronal frente a los métodos empíricos.

La hipótesis del apartado 1.7 afirma que el sistema calcula los planes con una
precisión que supera significativamente a los métodos empíricos y manuales con
que la población del municipio arma hoy su alimentación. El entrenamiento ya
demuestra la primera mitad —el margen frente a las fórmulas de Mifflin-St Jeor
y Harris-Benedict queda muy por debajo del 5 %—; este guion demuestra la
segunda, midiendo con la misma vara a tres métodos empíricos de uso común:

1. **Plan genérico de 2,000 kcal**, la dieta de referencia de las etiquetas
   nutricionales y de la mayoría de los planes descargados de internet.
2. **Valor por sexo**, 2,000 kcal para mujeres y 2,500 kcal para hombres, la
   orientación general que difunden las guías de salud pública.
3. **Regla de 30 kcal por kilogramo de peso**, el cálculo manual más difundido
   en los gimnasios.

A los dos últimos se les aplica el mismo ajuste por objetivo que aplica el
sistema (regla RN-02): así la comparación mide únicamente la estimación del
gasto, y los métodos empíricos compiten en su mejor versión.

Los perfiles se generan con una semilla distinta de la del entrenamiento, de
modo que la red se evalúa sobre personas que nunca vio. Se reportan dos
poblaciones: el rango completo que el sistema admite y la población típica de
un gimnasio (18 a 60 años, índice de masa corporal entre 18.5 y 35).

    uv run python validar_hipotesis.py
    uv run python validar_hipotesis.py --perfiles 10000 --salida resultados.json
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

from app.motor.conjunto_datos import COLUMNAS_ENTRADA, Normalizador, generar_perfiles_sinteticos
from app.motor.red_neuronal import MARGEN_ERROR_MAXIMO, RUTA_METADATOS, RUTA_MODELO

SEMILLA_EVALUACION = 2027


def _columna(nombre: str) -> int:
    return COLUMNAS_ENTRADA.index(nombre)


def predecir_energia(entradas: np.ndarray) -> np.ndarray:
    """Energía que predice la red entrenada para cada perfil."""
    import keras

    metadatos = json.loads(Path(RUTA_METADATOS).read_text(encoding="utf-8"))
    normalizador = Normalizador.desde_diccionario(metadatos["normalizador"])
    normalizador_salidas = Normalizador.desde_diccionario(metadatos["normalizador_salidas"])
    modelo = keras.models.load_model(RUTA_MODELO)
    salidas = modelo.predict(normalizador.aplicar(entradas), verbose=0, batch_size=1024)
    return normalizador_salidas.revertir(salidas)[:, 0]


def metodos_empiricos(entradas: np.ndarray) -> dict[str, np.ndarray]:
    """Energía que asignaría cada método empírico a cada perfil."""
    peso = entradas[:, _columna("peso_kg")]
    masculino = entradas[:, _columna("sexo_masculino")] == 1.0
    ajuste = entradas[:, _columna("ajuste_objetivo")]
    return {
        "Plan genérico de 2,000 kcal": np.full(len(entradas), 2000.0),
        "Valor por sexo (2,000 / 2,500 kcal)": np.where(masculino, 2500.0, 2000.0) * ajuste,
        "Regla de 30 kcal por kilogramo": 30.0 * peso * ajuste,
    }


def wilcoxon_pareado(errores_a: np.ndarray, errores_b: np.ndarray) -> tuple[float, float]:
    """Prueba de rangos con signo de Wilcoxon, por aproximación normal.

    Contrasta si los errores del método B son sistemáticamente mayores que los
    del método A sobre los mismos perfiles. Devuelve el estadístico z y el valor
    p unilateral. Con miles de pares la aproximación normal es exacta a efectos
    prácticos.
    """
    diferencias = errores_b - errores_a
    diferencias = diferencias[diferencias != 0]
    n = len(diferencias)
    rangos = np.empty(n)
    rangos[np.argsort(np.abs(diferencias))] = np.arange(1, n + 1)
    positivos = rangos[diferencias > 0].sum()
    media = n * (n + 1) / 4
    desviacion = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (positivos - media) / desviacion
    return z, 0.5 * math.erfc(z / math.sqrt(2))


def resumir(margenes: np.ndarray, errores_kcal: np.ndarray) -> dict[str, float]:
    return {
        "error_absoluto_medio_kcal": float(errores_kcal.mean()),
        "margen_medio_pct": float(margenes.mean() * 100),
        "margen_mediano_pct": float(np.median(margenes) * 100),
        "percentil_95_pct": float(np.percentile(margenes, 95) * 100),
        "margen_maximo_pct": float(margenes.max() * 100),
        "dentro_del_5_pct": float((margenes < MARGEN_ERROR_MAXIMO).mean() * 100),
    }


def evaluar(entradas: np.ndarray, referencia: np.ndarray, red: np.ndarray) -> dict:
    margen_red = np.abs(red - referencia) / referencia
    resultado = {
        "perfiles": int(len(entradas)),
        "metodos": {"Red neuronal del sistema": resumir(margen_red, np.abs(red - referencia))},
    }
    for nombre, estimacion in metodos_empiricos(entradas).items():
        margen = np.abs(estimacion - referencia) / referencia
        z, p = wilcoxon_pareado(margen_red, margen)
        resultado["metodos"][nombre] = {
            **resumir(margen, np.abs(estimacion - referencia)),
            "wilcoxon_z": z,
            "valor_p": p,
            "red_mejor_en_pct_de_perfiles": float((margen_red < margen).mean() * 100),
        }
    return resultado


def imprimir(titulo: str, resultado: dict) -> None:
    print(f"\n{titulo} ({resultado['perfiles']:,} perfiles)")
    print(f"{'Método':40s} {'Medio':>8s} {'Mediano':>8s} {'P95':>8s} {'Máximo':>8s} {'<5 %':>8s}")
    for nombre, m in resultado["metodos"].items():
        print(
            f"{nombre:40s} {m['margen_medio_pct']:7.2f}% {m['margen_mediano_pct']:7.2f}% "
            f"{m['percentil_95_pct']:7.2f}% {m['margen_maximo_pct']:7.2f}% {m['dentro_del_5_pct']:7.1f}%"
        )
        if "valor_p" in m:
            print(
                f"{'':40s} Wilcoxon z = {m['wilcoxon_z']:.1f}, p = {m['valor_p']:.2e}; "
                f"la red es más precisa en el {m['red_mejor_en_pct_de_perfiles']:.1f} % de los perfiles"
            )


def principal() -> int:
    analizador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analizador.add_argument("--perfiles", type=int, default=10_000)
    analizador.add_argument("--semilla", type=int, default=SEMILLA_EVALUACION)
    analizador.add_argument("--salida", type=Path, default=None)
    argumentos = analizador.parse_args()

    conjunto = generar_perfiles_sinteticos(argumentos.perfiles, semilla=argumentos.semilla)
    entradas, referencia = conjunto.entradas, conjunto.salidas[:, 0]
    red = predecir_energia(entradas)

    peso = entradas[:, _columna("peso_kg")]
    estatura_m = entradas[:, _columna("estatura_cm")] / 100
    edad = entradas[:, _columna("edad")]
    imc = peso / estatura_m**2
    gimnasio = (edad <= 60) & (imc >= 18.5) & (imc <= 35)

    resultados = {
        "semilla": argumentos.semilla,
        "rango_completo": evaluar(entradas, referencia, red),
        "poblacion_de_gimnasio": evaluar(entradas[gimnasio], referencia[gimnasio], red[gimnasio]),
    }

    imprimir("Rango completo que el sistema admite", resultados["rango_completo"])
    imprimir("Población típica de un gimnasio", resultados["poblacion_de_gimnasio"])

    if argumentos.salida:
        argumentos.salida.write_text(
            json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\nResultados guardados en {argumentos.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
