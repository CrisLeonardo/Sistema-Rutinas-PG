"""Preparacion del conjunto de datos del modelo neuronal (subfase 3.1).

El trabajo de campo reunio 169 perfiles, volumen que el apartado 4.9.1 identifica
como un riesgo tecnico para un modelo de aprendizaje profundo. La mitigacion
prevista en la Tabla 12 es complementarlos con perfiles sinteticos que cubran
todo el rango antropometrico plausible, cuyas salidas esperadas se derivan de las
ecuaciones de referencia. Este modulo genera ese conjunto, lo normaliza y lo
separa en entrenamiento y validacion.

El aprendizaje es supervisado (apartado 2.3): las entradas son las variables
biometricas y las salidas esperadas, el promedio de Mifflin-St Jeor y
Harris-Benedict junto con la distribucion de macronutrientes que de el se deriva.
"""

from dataclasses import dataclass
from itertools import product

import numpy as np

from app.esquemas.perfil import (
    EDAD_MAXIMA,
    EDAD_MINIMA,
    ESTATURA_MAXIMA_CM,
    ESTATURA_MINIMA_CM,
    PESO_MAXIMO_KG,
    PESO_MINIMO_KG,
)
from app.modelos.enumeraciones import NivelActividad, NivelExperiencia, Objetivo, Sexo
from app.motor.formulas import (
    AJUSTES_POR_OBJETIVO,
    FACTORES_ACTIVIDAD,
    ajustar_por_objetivo,
    calcular_referencias,
    distribuir_macronutrientes,
    series_semanales_por_grupo,
)

# El nivel de experiencia entra a la red como escala ordinal y no como categoria:
# principiante, intermedio y avanzado guardan un orden natural, y el volumen que
# cada uno tolera crece de forma monotona con el.
ESCALA_EXPERIENCIA: dict[NivelExperiencia, float] = {
    NivelExperiencia.PRINCIPIANTE: 1.0,
    NivelExperiencia.INTERMEDIO: 2.0,
    NivelExperiencia.AVANZADO: 3.0,
}

# Orden de las columnas de entrada. Se declara una sola vez para que el
# entrenamiento y la prediccion no puedan desalinearse.
COLUMNAS_ENTRADA = (
    "peso_kg",
    "estatura_cm",
    "edad",
    "sexo_masculino",
    "factor_actividad",
    "ajuste_objetivo",
    "nivel_experiencia",
    "dias_entrenamiento_semana",
)

# Orden de las columnas de salida que la red aprende a predecir.
# El apartado 2.5.1 encarga a la red, ademas del requerimiento energetico y sus
# macronutrientes, el volumen semanal de series por grupo muscular, que el
# generador de rutinas reparte despues entre las sesiones disponibles.
COLUMNAS_SALIDA = (
    "energia_kcal",
    "proteina_g",
    "carbohidrato_g",
    "grasa_g",
    "series_semanales_por_grupo",
)

SEMILLA_PREDETERMINADA = 2026

# Frecuencia semanal habitual de cada nivel, usada solo por la malla de
# verificacion sistematica.
FRECUENCIA_TIPICA_POR_EXPERIENCIA: dict[NivelExperiencia, int] = {
    NivelExperiencia.PRINCIPIANTE: 3,
    NivelExperiencia.INTERMEDIO: 4,
    NivelExperiencia.AVANZADO: 6,
}

# Rangos de generacion. Coinciden con los que el servidor acepta al capturar el
# perfil biometrico, de modo que el modelo nunca reciba en produccion un valor
# fuera del dominio con el que fue entrenado.
RANGO_PESO = (PESO_MINIMO_KG, PESO_MAXIMO_KG)
RANGO_ESTATURA = (ESTATURA_MINIMA_CM, ESTATURA_MAXIMA_CM)
RANGO_EDAD = (EDAD_MINIMA, EDAD_MAXIMA)

# Los rangos de peso y estatura son independientes entre si, de modo que su
# combinacion libre produce perfiles imposibles: 30 kilogramos con 220
# centimetros dan un indice de masa corporal de 6.2, y 250 kilogramos con 120
# centimetros dan 173. Entrenar con esas combinaciones desperdicia capacidad del
# modelo en una region del espacio que ningun usuario real puede ocupar, asi que
# se descartan por su indice de masa corporal.
IMC_MINIMO_PLAUSIBLE = 13.0
IMC_MAXIMO_PLAUSIBLE = 60.0


def es_perfil_plausible(peso_kg: float, estatura_cm: float) -> bool:
    """Indica si la combinacion de peso y estatura corresponde a una persona real."""
    indice = peso_kg / ((estatura_cm / 100) ** 2)
    return IMC_MINIMO_PLAUSIBLE <= indice <= IMC_MAXIMO_PLAUSIBLE


@dataclass(frozen=True)
class ConjuntoDatos:
    """Entradas y salidas de un conjunto, ya normalizadas o sin normalizar."""

    entradas: np.ndarray
    salidas: np.ndarray

    def __len__(self) -> int:
        return int(self.entradas.shape[0])


@dataclass(frozen=True)
class Normalizador:
    """Parametros de la normalizacion de las variables de entrada.

    Se guarda junto con el modelo entrenado: sin los mismos valores de media y
    desviacion, las predicciones sobre datos nuevos carecen de sentido.
    """

    medias: np.ndarray
    desviaciones: np.ndarray

    def aplicar(self, entradas: np.ndarray) -> np.ndarray:
        """Lleva cada variable a media cero y desviacion uno."""
        return (entradas - self.medias) / self.desviaciones

    def revertir(self, normalizadas: np.ndarray) -> np.ndarray:
        """Devuelve las variables a su escala original."""
        return (normalizadas * self.desviaciones) + self.medias

    def a_diccionario(self, columnas: tuple[str, ...] = COLUMNAS_ENTRADA) -> dict[str, list[float]]:
        """Representacion serializable, para almacenarla junto al modelo."""
        return {
            "medias": self.medias.tolist(),
            "desviaciones": self.desviaciones.tolist(),
            "columnas": list(columnas),
        }

    @classmethod
    def desde_diccionario(cls, datos: dict[str, list[float]]) -> "Normalizador":
        """Reconstruye el normalizador guardado junto al modelo."""
        return cls(
            medias=np.asarray(datos["medias"], dtype=np.float64),
            desviaciones=np.asarray(datos["desviaciones"], dtype=np.float64),
        )


def ajustar_normalizador(entradas: np.ndarray) -> Normalizador:
    """Calcula media y desviacion de cada columna del conjunto de entrenamiento.

    Solo debe ajustarse sobre el conjunto de entrenamiento: hacerlo sobre el
    total filtraria informacion del conjunto de validacion hacia el modelo.
    """
    medias = entradas.mean(axis=0)
    desviaciones = entradas.std(axis=0)
    # Una columna constante tendria desviacion cero y produciria una division
    # indefinida; se sustituye por uno, que la deja intacta.
    desviaciones = np.where(desviaciones == 0, 1.0, desviaciones)
    return Normalizador(medias=medias, desviaciones=desviaciones)


def vector_entrada(
    peso_kg: float,
    estatura_cm: float,
    edad: int,
    sexo: Sexo,
    nivel_actividad: NivelActividad,
    objetivo: Objetivo,
    nivel_experiencia: NivelExperiencia = NivelExperiencia.PRINCIPIANTE,
    dias_entrenamiento_semana: int = 3,
) -> np.ndarray:
    """Convierte un perfil biometrico en el vector que consume la red.

    El sexo se codifica como variable binaria y el nivel de actividad y el
    objetivo se representan por el multiplicador que cada uno aporta, en lugar de
    por una categoria: asi la red recibe una magnitud continua y monotona, que es
    la forma en que ambos intervienen en el calculo.
    """
    return np.asarray(
        [
            peso_kg,
            estatura_cm,
            edad,
            1.0 if sexo == Sexo.MASCULINO else 0.0,
            FACTORES_ACTIVIDAD[nivel_actividad],
            1 + AJUSTES_POR_OBJETIVO[objetivo],
            ESCALA_EXPERIENCIA[nivel_experiencia],
            float(dias_entrenamiento_semana),
        ],
        dtype=np.float64,
    )


def vector_salida(
    peso_kg: float,
    estatura_cm: float,
    edad: int,
    sexo: Sexo,
    nivel_actividad: NivelActividad,
    objetivo: Objetivo,
    nivel_experiencia: NivelExperiencia = NivelExperiencia.PRINCIPIANTE,
    dias_entrenamiento_semana: int = 3,
) -> np.ndarray:
    """Calcula la salida esperada de un perfil con las reglas de referencia."""
    referencias = calcular_referencias(peso_kg, estatura_cm, edad, sexo, nivel_actividad)
    energia = ajustar_por_objetivo(referencias.gasto_promedio, objetivo)
    macros = distribuir_macronutrientes(energia, peso_kg, objetivo)
    volumen = series_semanales_por_grupo(
        nivel_experiencia, dias_entrenamiento_semana, edad, objetivo
    )
    return np.asarray(
        [
            macros.energia_kcal,
            macros.proteina_g,
            macros.carbohidrato_g,
            macros.grasa_g,
            volumen,
        ],
        dtype=np.float64,
    )


def generar_perfiles_sinteticos(
    cantidad: int = 20_000, semilla: int = SEMILLA_PREDETERMINADA
) -> ConjuntoDatos:
    """Genera perfiles aleatorios que cubren todo el rango antropometrico plausible.

    El peso y la estatura se extraen de distribuciones uniformes sobre los rangos
    que el sistema admite, de modo que el modelo quede igual de entrenado en los
    extremos que en el centro, donde se concentrarian los datos reales. Se
    descartan las combinaciones cuyo indice de masa corporal resulta imposible.
    """
    if cantidad <= 0:
        raise ValueError("La cantidad de perfiles debe ser mayor que cero.")

    generador = np.random.default_rng(semilla)
    sexos = list(Sexo)
    niveles = list(NivelActividad)
    objetivos = list(Objetivo)
    experiencias = list(NivelExperiencia)

    entradas = np.empty((cantidad, len(COLUMNAS_ENTRADA)), dtype=np.float64)
    salidas = np.empty((cantidad, len(COLUMNAS_SALIDA)), dtype=np.float64)

    fila = 0
    while fila < cantidad:
        # Se muestrea la estatura primero y el peso despues, dentro del intervalo
        # que esa estatura hace plausible, en lugar de sortear ambos por separado
        # y descartar: asi la cobertura del rango de estatura no se degrada.
        estatura = round(float(generador.uniform(*RANGO_ESTATURA)), 1)
        estatura_m = estatura / 100
        peso_minimo = max(RANGO_PESO[0], IMC_MINIMO_PLAUSIBLE * estatura_m**2)
        peso_maximo = min(RANGO_PESO[1], IMC_MAXIMO_PLAUSIBLE * estatura_m**2)
        peso = round(float(generador.uniform(peso_minimo, peso_maximo)), 1)
        if not es_perfil_plausible(peso, estatura):
            continue

        edad = int(generador.integers(RANGO_EDAD[0], RANGO_EDAD[1] + 1))
        sexo = sexos[int(generador.integers(len(sexos)))]
        nivel = niveles[int(generador.integers(len(niveles)))]
        objetivo = objetivos[int(generador.integers(len(objetivos)))]
        experiencia = experiencias[int(generador.integers(len(experiencias)))]
        dias = int(generador.integers(1, 8))

        argumentos = (peso, estatura, edad, sexo, nivel, objetivo, experiencia, dias)
        entradas[fila] = vector_entrada(*argumentos)
        salidas[fila] = vector_salida(*argumentos)
        fila += 1

    return ConjuntoDatos(entradas=entradas, salidas=salidas)


def generar_malla_de_verificacion(paso_peso: float = 25.0) -> ConjuntoDatos:
    """Conjunto sistematico que recorre los extremos de cada variable.

    A diferencia del muestreo aleatorio, esta malla garantiza que ninguna
    combinacion de sexo, nivel de actividad y objetivo quede sin representar en
    los limites del dominio. Se usa para comprobar el margen de error del modelo
    donde es mas probable que falle. Igual que en el muestreo aleatorio, se
    excluyen las combinaciones de peso y estatura fisiologicamente imposibles.
    """
    pesos = np.arange(RANGO_PESO[0], RANGO_PESO[1] + 0.1, paso_peso)
    estaturas = [RANGO_ESTATURA[0], 150.0, 170.0, 190.0, RANGO_ESTATURA[1]]
    edades = [EDAD_MINIMA, 30, 45, 60, EDAD_MAXIMA]

    filas_entrada: list[np.ndarray] = []
    filas_salida: list[np.ndarray] = []
    combinaciones = product(
        pesos, estaturas, edades, Sexo, NivelActividad, Objetivo, NivelExperiencia
    )
    for peso, estatura, edad, sexo, nivel, objetivo, experiencia in combinaciones:
        if not es_perfil_plausible(float(peso), estatura):
            continue
        # La frecuencia se ata al nivel de experiencia para no multiplicar la
        # malla por siete: el resto de sus valores ya los cubre el muestreo.
        dias = FRECUENCIA_TIPICA_POR_EXPERIENCIA[experiencia]
        argumentos = (float(peso), estatura, edad, sexo, nivel, objetivo, experiencia, dias)
        filas_entrada.append(vector_entrada(*argumentos))
        filas_salida.append(vector_salida(*argumentos))

    return ConjuntoDatos(
        entradas=np.vstack(filas_entrada),
        salidas=np.vstack(filas_salida),
    )


def separar_entrenamiento_validacion(
    conjunto: ConjuntoDatos,
    proporcion_validacion: float = 0.2,
    semilla: int = SEMILLA_PREDETERMINADA,
) -> tuple[ConjuntoDatos, ConjuntoDatos]:
    """Divide el conjunto en entrenamiento y validacion, mezclandolo antes.

    La mezcla evita que el orden de generacion introduzca sesgo en la division.
    """
    if not 0 < proporcion_validacion < 1:
        raise ValueError("La proporcion de validación debe estar entre 0 y 1.")

    total = len(conjunto)
    generador = np.random.default_rng(semilla)
    orden = generador.permutation(total)

    corte = total - int(round(total * proporcion_validacion))
    if corte <= 0 or corte >= total:
        raise ValueError("El conjunto es demasiado pequeño para esa proporción de validación.")

    indices_entrenamiento = orden[:corte]
    indices_validacion = orden[corte:]

    entrenamiento = ConjuntoDatos(
        entradas=conjunto.entradas[indices_entrenamiento],
        salidas=conjunto.salidas[indices_entrenamiento],
    )
    validacion = ConjuntoDatos(
        entradas=conjunto.entradas[indices_validacion],
        salidas=conjunto.salidas[indices_validacion],
    )
    return entrenamiento, validacion


@dataclass(frozen=True)
class DatosPreparados:
    """Conjunto listo para entrenar: normalizado y ya dividido."""

    entrenamiento: ConjuntoDatos
    validacion: ConjuntoDatos
    normalizador: Normalizador
    normalizador_salidas: Normalizador


def preparar_datos(
    cantidad: int = 20_000,
    proporcion_validacion: float = 0.2,
    semilla: int = SEMILLA_PREDETERMINADA,
) -> DatosPreparados:
    """Ejecuta en orden la generacion, la division y la normalizacion.

    Las salidas se normalizan igual que las entradas. Sin ese paso, la energia
    —del orden de los millares— dominaria la funcion de perdida frente a los
    gramos de grasa —del orden de las decenas—, y el modelo aprenderia bien la
    primera a costa de los segundos.

    Es el punto de entrada que consume el entrenamiento de la subfase 3.2.
    """
    conjunto = generar_perfiles_sinteticos(cantidad=cantidad, semilla=semilla)
    entrenamiento, validacion = separar_entrenamiento_validacion(
        conjunto, proporcion_validacion=proporcion_validacion, semilla=semilla
    )

    normalizador = ajustar_normalizador(entrenamiento.entradas)
    normalizador_salidas = ajustar_normalizador(entrenamiento.salidas)
    return DatosPreparados(
        entrenamiento=ConjuntoDatos(
            entradas=normalizador.aplicar(entrenamiento.entradas),
            salidas=normalizador_salidas.aplicar(entrenamiento.salidas),
        ),
        validacion=ConjuntoDatos(
            entradas=normalizador.aplicar(validacion.entradas),
            salidas=normalizador_salidas.aplicar(validacion.salidas),
        ),
        normalizador=normalizador,
        normalizador_salidas=normalizador_salidas,
    )
