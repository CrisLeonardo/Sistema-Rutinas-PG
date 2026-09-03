"""Formulas metabolicas de referencia (apartado 2.4.2 de la tesis).

Cumplen la doble funcion que les asigna el marco teorico: producen los valores de
salida con los que se entrena el modelo neuronal y constituyen el patron de
comparacion frente al cual se mide su precision, con el margen de error inferior
al 5 % que establece el tercer objetivo especifico de la investigacion.

Este modulo no depende de TensorFlow ni de la base de datos: es aritmetica pura,
de modo que pueda verificarse por separado del resto del sistema.
"""

from dataclasses import dataclass

from app.modelos.enumeraciones import (
    NivelActividad,
    NivelExperiencia,
    Objetivo,
    Sexo,
)

# Constantes de Atwater (apartado 2.4.3): energia que aporta un gramo de cada
# macronutriente, expresada en kilocalorias.
KCAL_POR_GRAMO_PROTEINA = 4
KCAL_POR_GRAMO_CARBOHIDRATO = 4
KCAL_POR_GRAMO_GRASA = 9

# Factores que multiplican la tasa metabolica basal para obtener el gasto
# energetico total diario, segun el nivel de actividad declarado (apartado 2.4.2).
FACTORES_ACTIVIDAD: dict[NivelActividad, float] = {
    NivelActividad.SEDENTARIO: 1.2,
    NivelActividad.LIGERO: 1.375,
    NivelActividad.MODERADO: 1.55,
    NivelActividad.ALTO: 1.725,
    NivelActividad.MUY_ALTO: 1.9,
}

# Regla del negocio *b* del apartado 4.3.4: el ajuste sobre el gasto energetico
# total nunca excede el 20 % en deficit ni el 15 % en superavit.
DEFICIT_MAXIMO = 0.20
SUPERAVIT_MAXIMO = 0.15

AJUSTES_POR_OBJETIVO: dict[Objetivo, float] = {
    Objetivo.PERDIDA_GRASA: -DEFICIT_MAXIMO,
    Objetivo.MANTENIMIENTO: 0.0,
    Objetivo.GANANCIA_MUSCULAR: SUPERAVIT_MAXIMO,
}

# Regla del negocio *c*: la proteina se mantiene entre 1.6 y 2.2 gramos por
# kilogramo de peso corporal (apartado 2.4.3).
PROTEINA_MINIMA_POR_KG = 1.6
PROTEINA_MAXIMA_POR_KG = 2.2

GRAMOS_PROTEINA_POR_OBJETIVO: dict[Objetivo, float] = {
    # En deficit se prescribe el extremo superior del rango, porque el aporte
    # proteico alto es el que preserva la masa muscular mientras se pierde grasa.
    Objetivo.PERDIDA_GRASA: 2.2,
    Objetivo.MANTENIMIENTO: 1.8,
    Objetivo.GANANCIA_MUSCULAR: 2.0,
}

# Proporcion de la energia diaria que se cubre con grasa. Se fija en el punto
# medio del rango saludable habitual, de 20 % a 35 %, y los carbohidratos ocupan
# la energia restante.
PROPORCION_GRASA = 0.25

# Mililitros de agua por kilogramo de peso corporal (apartado 2.4.4).
AGUA_ML_POR_KG = 35
AGUA_ADICIONAL_POR_ACTIVIDAD: dict[NivelActividad, int] = {
    NivelActividad.SEDENTARIO: 0,
    NivelActividad.LIGERO: 250,
    NivelActividad.MODERADO: 500,
    NivelActividad.ALTO: 750,
    NivelActividad.MUY_ALTO: 1000,
}


def tasa_metabolica_basal_mifflin(
    peso_kg: float, estatura_cm: float, edad: int, sexo: Sexo
) -> float:
    """Tasa metabolica basal segun Mifflin-St Jeor, en kilocalorias por dia.

    Para los hombres: diez por el peso en kilogramos, mas 6.25 por la estatura en
    centimetros, menos cinco por la edad en anios, mas cinco. Para las mujeres la
    constante final cambia a menos 161 (apartado 2.4.2).
    """
    base = (10 * peso_kg) + (6.25 * estatura_cm) - (5 * edad)
    constante = 5 if sexo == Sexo.MASCULINO else -161
    return base + constante


def tasa_metabolica_basal_harris_benedict(
    peso_kg: float, estatura_cm: float, edad: int, sexo: Sexo
) -> float:
    """Tasa metabolica basal segun Harris-Benedict, en kilocalorias por dia.

    Se emplea la revision de Roza y Shizgal, que es la formulacion vigente de la
    ecuacion original de 1919 y la que reportan las obras de referencia citadas
    en el apartado 2.4.2.
    """
    if sexo == Sexo.MASCULINO:
        return 88.362 + (13.397 * peso_kg) + (4.799 * estatura_cm) - (5.677 * edad)
    return 447.593 + (9.247 * peso_kg) + (3.098 * estatura_cm) - (4.330 * edad)


def factor_actividad(nivel: NivelActividad) -> float:
    """Multiplicador de la tasa metabolica basal segun el nivel de actividad."""
    return FACTORES_ACTIVIDAD[nivel]


def gasto_energetico_total(tasa_basal: float, nivel: NivelActividad) -> float:
    """Gasto energetico total diario: la tasa basal multiplicada por el factor de actividad."""
    return tasa_basal * factor_actividad(nivel)


@dataclass(frozen=True)
class ValoresReferencia:
    """Resultado de las dos formulas de referencia para un mismo perfil.

    El promedio de ambas es el valor con que se entrena el modelo neuronal y
    contra el que se mide su margen de error.
    """

    basal_mifflin: float
    basal_harris_benedict: float
    gasto_mifflin: float
    gasto_harris_benedict: float

    @property
    def gasto_promedio(self) -> float:
        """Promedio de los dos gastos energeticos totales."""
        return (self.gasto_mifflin + self.gasto_harris_benedict) / 2

    @property
    def discrepancia_relativa(self) -> float:
        """Diferencia entre ambas formulas, como fraccion del promedio.

        Sirve de referencia para interpretar el margen de error del modelo: las
        dos ecuaciones tampoco coinciden exactamente entre si.
        """
        return abs(self.gasto_mifflin - self.gasto_harris_benedict) / self.gasto_promedio


def calcular_referencias(
    peso_kg: float,
    estatura_cm: float,
    edad: int,
    sexo: Sexo,
    nivel_actividad: NivelActividad,
) -> ValoresReferencia:
    """Aplica las dos formulas de referencia al mismo perfil biometrico."""
    basal_mifflin = tasa_metabolica_basal_mifflin(peso_kg, estatura_cm, edad, sexo)
    basal_harris = tasa_metabolica_basal_harris_benedict(peso_kg, estatura_cm, edad, sexo)
    return ValoresReferencia(
        basal_mifflin=basal_mifflin,
        basal_harris_benedict=basal_harris,
        gasto_mifflin=gasto_energetico_total(basal_mifflin, nivel_actividad),
        gasto_harris_benedict=gasto_energetico_total(basal_harris, nivel_actividad),
    )


def ajustar_por_objetivo(gasto_energetico: float, objetivo: Objetivo) -> float:
    """Aplica el deficit o el superavit calorico que corresponde al objetivo.

    Regla del negocio *b*: el ajuste nunca excede el 20 % en deficit ni el 15 %
    en superavit, para evitar descompensaciones metabolicas.
    """
    return gasto_energetico * (1 + AJUSTES_POR_OBJETIVO[objetivo])


def gramos_proteina(peso_kg: float, objetivo: Objetivo) -> float:
    """Gramos diarios de proteina segun el objetivo declarado.

    Regla del negocio *c*: el resultado siempre queda entre 1.6 y 2.2 gramos por
    kilogramo de peso corporal.
    """
    por_kilogramo = GRAMOS_PROTEINA_POR_OBJETIVO[objetivo]
    acotado = min(max(por_kilogramo, PROTEINA_MINIMA_POR_KG), PROTEINA_MAXIMA_POR_KG)
    return peso_kg * acotado


@dataclass(frozen=True)
class DistribucionMacronutrientes:
    """Reparto de la energia diaria entre proteina, grasa y carbohidrato.

    Los gramos se expresan redondeados al entero, tal como se presentan al
    usuario, y los porcentajes se calculan sobre la energia que esos mismos
    gramos aportan, de modo que la suma coincida con el total (criterio de
    aceptacion de la historia HU-06).
    """

    energia_kcal: int
    proteina_g: int
    carbohidrato_g: int
    grasa_g: int

    @property
    def energia_proteina(self) -> int:
        return self.proteina_g * KCAL_POR_GRAMO_PROTEINA

    @property
    def energia_carbohidrato(self) -> int:
        return self.carbohidrato_g * KCAL_POR_GRAMO_CARBOHIDRATO

    @property
    def energia_grasa(self) -> int:
        return self.grasa_g * KCAL_POR_GRAMO_GRASA

    @property
    def energia_de_los_macronutrientes(self) -> int:
        """Suma de los aportes energeticos de los tres macronutrientes."""
        return self.energia_proteina + self.energia_carbohidrato + self.energia_grasa

    @property
    def porcentaje_proteina(self) -> float:
        return round(100 * self.energia_proteina / self.energia_de_los_macronutrientes, 1)

    @property
    def porcentaje_carbohidrato(self) -> float:
        return round(100 * self.energia_carbohidrato / self.energia_de_los_macronutrientes, 1)

    @property
    def porcentaje_grasa(self) -> float:
        return round(100 * self.energia_grasa / self.energia_de_los_macronutrientes, 1)


def distribuir_macronutrientes(
    energia_kcal: float, peso_kg: float, objetivo: Objetivo
) -> DistribucionMacronutrientes:
    """Reparte la energia diaria en gramos de cada macronutriente.

    Primero se fija la proteina segun el peso corporal (regla del negocio *c*),
    despues la grasa como proporcion de la energia total y, por ultimo, los
    carbohidratos ocupan la energia restante. La energia declarada es la que
    aportan los gramos ya redondeados, para que la suma cuadre exactamente.
    """
    proteina_g = round(gramos_proteina(peso_kg, objetivo))
    grasa_g = round((energia_kcal * PROPORCION_GRASA) / KCAL_POR_GRAMO_GRASA)

    energia_restante = (
        energia_kcal
        - (proteina_g * KCAL_POR_GRAMO_PROTEINA)
        - (grasa_g * KCAL_POR_GRAMO_GRASA)
    )
    # En perfiles de poco peso y objetivo de perdida de grasa, la proteina y la
    # grasa pueden agotar la energia disponible. En ese caso se reduce la grasa
    # hasta dejar un aporte minimo de carbohidrato, antes que recortar la
    # proteina, que es la que sostiene la masa muscular.
    if energia_restante < 0:
        grasa_g = max(round(grasa_g + energia_restante / KCAL_POR_GRAMO_GRASA), 0)
        energia_restante = (
            energia_kcal
            - (proteina_g * KCAL_POR_GRAMO_PROTEINA)
            - (grasa_g * KCAL_POR_GRAMO_GRASA)
        )

    carbohidrato_g = max(round(energia_restante / KCAL_POR_GRAMO_CARBOHIDRATO), 0)

    distribucion = DistribucionMacronutrientes(
        energia_kcal=0,
        proteina_g=proteina_g,
        carbohidrato_g=carbohidrato_g,
        grasa_g=grasa_g,
    )
    return DistribucionMacronutrientes(
        energia_kcal=distribucion.energia_de_los_macronutrientes,
        proteina_g=proteina_g,
        carbohidrato_g=carbohidrato_g,
        grasa_g=grasa_g,
    )


def agua_recomendada_ml(peso_kg: float, nivel_actividad: NivelActividad) -> int:
    """Mililitros de agua sugeridos al dia (apartado 2.4.4).

    Es una recomendacion calculada en funcion del peso corporal y del nivel de
    actividad, no una prescripcion clinica.
    """
    return round(peso_kg * AGUA_ML_POR_KG) + AGUA_ADICIONAL_POR_ACTIVIDAD[nivel_actividad]


def margen_de_error(valor_estimado: float, valor_referencia: float) -> float:
    """Error relativo del valor estimado frente al de referencia, como fraccion.

    Multiplicado por cien es el porcentaje que el tercer objetivo especifico de
    la investigacion exige mantener por debajo de cinco.
    """
    if valor_referencia == 0:
        raise ValueError("El valor de referencia no puede ser cero.")
    return abs(valor_estimado - valor_referencia) / abs(valor_referencia)


# --------------------------------------------------------------------------
# Volumen de entrenamiento (apartado 2.5.1)
# --------------------------------------------------------------------------

# Series semanales por grupo muscular segun el nivel de experiencia. Son los
# rangos que reporta la literatura de referencia del apartado 2.5.1: el
# principiante progresa con poco volumen y tolera mal la fatiga acumulada,
# mientras que el avanzado necesita mas estimulo para seguir adaptandose.
SERIES_SEMANALES_BASE: dict[NivelExperiencia, float] = {
    NivelExperiencia.PRINCIPIANTE: 10.0,
    NivelExperiencia.INTERMEDIO: 14.0,
    NivelExperiencia.AVANZADO: 18.0,
}

# Limites absolutos del volumen semanal por grupo muscular. Por debajo del
# minimo no hay estimulo suficiente; por encima del maximo la fatiga supera la
# capacidad de recuperacion y aparece el sobreentrenamiento.
SERIES_MINIMAS_POR_GRUPO = 6
SERIES_MAXIMAS_POR_GRUPO = 22

# Series de un mismo grupo muscular que caben en una sesion sin que las ultimas
# se ejecuten ya demasiado fatigadas.
SERIES_MAXIMAS_POR_SESION = 10

# Edad a partir de la cual se descuenta volumen, y descuento por cada decada
# cumplida despues de ella. La capacidad de recuperacion disminuye con la edad.
EDAD_INICIO_DESCUENTO = 40
DESCUENTO_POR_DECADA = 0.05

# El deficit calorico reduce la capacidad de recuperacion, y el superavit la
# aumenta ligeramente (apartado 2.5.2).
FACTORES_RECUPERACION_POR_OBJETIVO: dict[Objetivo, float] = {
    Objetivo.PERDIDA_GRASA: 0.90,
    Objetivo.MANTENIMIENTO: 1.0,
    Objetivo.GANANCIA_MUSCULAR: 1.05,
}

# Regla del negocio *d* del apartado 4.3.4: el incremento de carga entre
# microciclos no supera el 10 % del volumen previo.
INCREMENTO_MAXIMO_ENTRE_MICROCICLOS = 0.10


def series_semanales_por_grupo(
    nivel_experiencia: NivelExperiencia,
    dias_entrenamiento_semana: int,
    edad: int,
    objetivo: Objetivo,
) -> float:
    """Volumen semanal de series por grupo muscular (apartado 2.5.1).

    Es el valor que el modelo neuronal aprende a predecir y que el generador de
    rutinas reparte entre las sesiones que el usuario declaro disponibles.

    Parte del volumen que corresponde al nivel de experiencia y lo corrige por
    los dos factores que limitan la recuperacion —la edad y el deficit
    calorico—, para acotarlo despues por lo que fisicamente cabe en las sesiones
    disponibles.
    """
    volumen = SERIES_SEMANALES_BASE[nivel_experiencia]

    if edad > EDAD_INICIO_DESCUENTO:
        decadas = (edad - EDAD_INICIO_DESCUENTO) / 10
        volumen *= max(1 - decadas * DESCUENTO_POR_DECADA, 0.7)

    volumen *= FACTORES_RECUPERACION_POR_OBJETIVO[objetivo]

    # Con pocas sesiones a la semana no es posible acumular el volumen completo
    # sin que las ultimas series de cada grupo se hagan ya muy fatigadas.
    tope_por_frecuencia = dias_entrenamiento_semana * SERIES_MAXIMAS_POR_SESION
    volumen = min(volumen, tope_por_frecuencia)

    return round(
        min(max(volumen, SERIES_MINIMAS_POR_GRUPO), SERIES_MAXIMAS_POR_GRUPO), 1
    )


def progresion_admitida(volumen_previo: float) -> float:
    """Volumen maximo que puede prescribirse en el microciclo siguiente.

    Regla del negocio *d*: el incremento no supera el 10 % del volumen previo,
    en aplicacion del principio de sobrecarga progresiva (apartado 2.5.2).
    """
    return volumen_previo * (1 + INCREMENTO_MAXIMO_ENTRE_MICROCICLOS)
