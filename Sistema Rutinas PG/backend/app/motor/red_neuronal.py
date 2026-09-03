"""Modelo de red neuronal artificial del requerimiento energetico (subfase 3.2).

Implementa la arquitectura descrita en el apartado 2.3 de la tesis: una capa de
entrada que recibe las variables biometricas, capas ocultas densas con activacion
ReLU que modelan las relaciones no lineales entre ellas, y una capa de salida que
entrega el requerimiento energetico diario junto con la distribucion de
macronutrientes y el volumen de entrenamiento sugerido.

Se emplea una red densa, y no una convolucional ni una recurrente, porque las
variables de entrada son numericas estructuradas (apartado 2.3.3).

TensorFlow se importa dentro de las funciones y no en la cabecera del modulo: la
interfaz de programacion no debe cargar la biblioteca completa para atender una
peticion que no involucre al modelo.
"""

from __future__ import annotations

import json
import logging
from collections import OrderedDict
from threading import Lock
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from app.motor.conjunto_datos import (
    COLUMNAS_ENTRADA,
    COLUMNAS_SALIDA,
    SEMILLA_PREDETERMINADA,
    ConjuntoDatos,
    DatosPreparados,
    Normalizador,
    generar_malla_de_verificacion,
    preparar_datos,
    vector_entrada,
)
from app.motor.formulas import (
    KCAL_POR_GRAMO_CARBOHIDRATO,
    KCAL_POR_GRAMO_GRASA,
    KCAL_POR_GRAMO_PROTEINA,
    SERIES_MAXIMAS_POR_GRUPO,
    SERIES_MINIMAS_POR_GRUPO,
)

if TYPE_CHECKING:  # pragma: no cover - solo para la revision de tipos
    from app.modelos.enumeraciones import (
        NivelActividad,
        NivelExperiencia,
        Objetivo,
        Sexo,
    )

bitacora = logging.getLogger(__name__)

# El modelo entrenado y sus metadatos viven fuera del control de versiones, como
# declara el .gitignore: son artefactos reproducibles a partir de este codigo.
DIRECTORIO_MODELO = Path(__file__).resolve().parents[2] / "modelo"
RUTA_MODELO = DIRECTORIO_MODELO / "requerimiento_energetico.keras"
RUTA_METADATOS = DIRECTORIO_MODELO / "requerimiento_energetico.json"

# Margen de error que el tercer objetivo especifico de la investigacion establece
# como criterio de aceptacion del modelo.
MARGEN_ERROR_MAXIMO = 0.05

# Predicciones que se conservan en memoria. Es la mitigacion que la Tabla 12
# prevé para la degradacion del rendimiento con usuarios concurrentes, y las
# pruebas de carga la hicieron necesaria: cincuenta invocaciones simultaneas del
# modelo llevaban la generacion del plan por encima de los tres segundos que
# admite el criterio de aceptacion de la historia HU-06.
#
# La memoria es correcta porque la prediccion es una funcion pura de las ocho
# variables de entrada: dos perfiles identicos producen siempre el mismo
# resultado. Y es eficaz porque los perfiles reales se repiten: la gente declara
# pesos y estaturas redondos.
TAMANIO_MEMORIA_PREDICCIONES = 512

NEURONAS_POR_CAPA_OCULTA = (128, 128, 64)
EPOCAS_PREDETERMINADAS = 250
TAMANIO_LOTE = 64


@dataclass(frozen=True)
class MetricasEntrenamiento:
    """Resultado de un entrenamiento, para documentar el modelo (subfase 3.2)."""

    perfiles_entrenamiento: int
    perfiles_validacion: int
    epocas: int
    error_absoluto_medio_kcal: float
    margen_error_medio: float
    margen_error_maximo: float
    proporcion_bajo_el_cinco_por_ciento: float
    error_absoluto_medio_series: float
    margen_error_medio_volumen: float

    @property
    def cumple_el_criterio(self) -> bool:
        """Indica si el modelo alcanza el margen de error exigido por la hipotesis."""
        return self.margen_error_medio < MARGEN_ERROR_MAXIMO

    def resumen(self) -> str:
        """Texto legible para la bitacora y para la documentacion de la tesis."""
        return (
            f"Perfiles: {self.perfiles_entrenamiento} de entrenamiento y "
            f"{self.perfiles_validacion} de validación. "
            f"Error absoluto medio: {self.error_absoluto_medio_kcal:.1f} kcal. "
            f"Margen de error medio: {self.margen_error_medio * 100:.2f} %, "
            f"máximo: {self.margen_error_maximo * 100:.2f} %. "
            f"Perfiles bajo el 5 %: {self.proporcion_bajo_el_cinco_por_ciento * 100:.2f} %. "
            f"Volumen de entrenamiento: {self.error_absoluto_medio_series:.2f} series de "
            f"error absoluto medio ({self.margen_error_medio_volumen * 100:.2f} %)."
        )


def _limitar_hilos_de_tensorflow() -> None:
    """Restringe a un hilo el paralelismo interno de TensorFlow.

    En produccion el servicio corre con varios procesos de trabajo. Si cada uno
    reparte una prediccion entre todos los nucleos de la maquina, los procesos
    compiten por la misma CPU y el conjunto rinde menos que si cada prediccion
    usara un solo hilo: las predicciones de este sistema son de una sola fila y
    no se benefician del paralelismo interno, pero si sufren su coordinacion.

    Debe invocarse antes de la primera operacion de TensorFlow; despues, la
    biblioteca ignora el cambio y lo advierte, de modo que el fallo se registra
    y no interrumpe el arranque.
    """
    import tensorflow as tf

    try:
        tf.config.threading.set_intra_op_parallelism_threads(1)
        tf.config.threading.set_inter_op_parallelism_threads(1)
    except RuntimeError:
        bitacora.debug(
            "TensorFlow ya estaba inicializado: se conserva su configuración de hilos."
        )


def construir_modelo(semilla: int = SEMILLA_PREDETERMINADA) -> Any:
    """Define la arquitectura de la red descrita en el apartado 2.3.

    La capa de salida es lineal porque el problema es de regresion: predice
    magnitudes continuas —kilocalorias y gramos— y no probabilidades de clase.
    """
    import keras
    import tensorflow as tf

    tf.keras.utils.set_random_seed(semilla)

    capas = [keras.layers.Input(shape=(len(COLUMNAS_ENTRADA),), name="variables_biometricas")]
    for posicion, neuronas in enumerate(NEURONAS_POR_CAPA_OCULTA, start=1):
        capas.append(
            keras.layers.Dense(neuronas, activation="relu", name=f"capa_oculta_{posicion}")
        )
    capas.append(
        keras.layers.Dense(len(COLUMNAS_SALIDA), name="requerimiento_macros_y_volumen")
    )

    modelo = keras.Sequential(capas, name="requerimiento_energetico")
    modelo.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        # El error cuadratico medio penaliza con fuerza las desviaciones grandes,
        # que son las que harian incumplir el margen del 5 %.
        loss="mse",
        metrics=["mae"],
    )
    return modelo


def evaluar_margen_de_error(
    modelo: Any, conjunto: ConjuntoDatos, normalizador_salidas: Normalizador
) -> dict[str, float]:
    """Mide el error del modelo frente a los valores de las formulas de referencia.

    El margen se calcula sobre el requerimiento energetico, que es la magnitud
    que la hipotesis de la investigacion somete al criterio del 5 %. Tanto la
    prediccion como la referencia se devuelven a kilocalorias antes de compararlas.
    """
    predicciones = normalizador_salidas.revertir(modelo.predict(conjunto.entradas, verbose=0))
    referencias = normalizador_salidas.revertir(conjunto.salidas)
    energia_predicha = predicciones[:, 0]
    energia_referencia = referencias[:, 0]

    margenes = np.abs(energia_predicha - energia_referencia) / np.abs(energia_referencia)

    # El volumen de entrenamiento es la quinta salida de la red (apartado 2.5.1).
    # Se mide aparte porque se expresa en series y no en kilocalorias.
    volumen_predicho = predicciones[:, 4]
    volumen_referencia = referencias[:, 4]
    margenes_volumen = np.abs(volumen_predicho - volumen_referencia) / np.abs(
        volumen_referencia
    )

    return {
        "error_absoluto_medio_kcal": float(np.abs(energia_predicha - energia_referencia).mean()),
        "margen_error_medio": float(margenes.mean()),
        "margen_error_maximo": float(margenes.max()),
        "proporcion_bajo_el_cinco_por_ciento": float(
            (margenes < MARGEN_ERROR_MAXIMO).mean()
        ),
        "error_absoluto_medio_series": float(
            np.abs(volumen_predicho - volumen_referencia).mean()
        ),
        "margen_error_medio_volumen": float(margenes_volumen.mean()),
    }


def entrenar(
    datos: DatosPreparados | None = None,
    epocas: int = EPOCAS_PREDETERMINADAS,
    semilla: int = SEMILLA_PREDETERMINADA,
    verbosidad: int = 0,
) -> tuple[Any, MetricasEntrenamiento]:
    """Entrena la red y devuelve el modelo junto con sus metricas.

    La detencion temprana evita seguir ajustando cuando la perdida de validacion
    deja de mejorar, lo que sobreajustaria el modelo al conjunto de entrenamiento.
    """
    import keras

    if datos is None:
        datos = preparar_datos(semilla=semilla)

    modelo = construir_modelo(semilla=semilla)
    modelo.fit(
        datos.entrenamiento.entradas,
        datos.entrenamiento.salidas,
        validation_data=(datos.validacion.entradas, datos.validacion.salidas),
        epochs=epocas,
        batch_size=TAMANIO_LOTE,
        verbose=verbosidad,
        callbacks=[
            keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=30,
                restore_best_weights=True,
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=12,
                min_lr=1e-5,
            ),
        ],
    )

    medidas = evaluar_margen_de_error(modelo, datos.validacion, datos.normalizador_salidas)
    metricas = MetricasEntrenamiento(
        perfiles_entrenamiento=len(datos.entrenamiento),
        perfiles_validacion=len(datos.validacion),
        epocas=epocas,
        **medidas,
    )
    return modelo, metricas


def guardar(
    modelo: Any,
    normalizador: Normalizador,
    normalizador_salidas: Normalizador,
    metricas: MetricasEntrenamiento,
) -> None:
    """Guarda el modelo, el normalizador y las metricas obtenidas.

    Los tres se almacenan juntos porque solo tienen sentido juntos: el modelo sin
    su normalizador produce predicciones sin significado, y sin sus metricas no
    puede documentarse que cumple el criterio de aceptacion.
    """
    DIRECTORIO_MODELO.mkdir(parents=True, exist_ok=True)
    modelo.save(RUTA_MODELO)
    RUTA_METADATOS.write_text(
        json.dumps(
            {
                "normalizador": normalizador.a_diccionario(COLUMNAS_ENTRADA),
                "normalizador_salidas": normalizador_salidas.a_diccionario(COLUMNAS_SALIDA),
                "columnas_entrada": list(COLUMNAS_ENTRADA),
                "columnas_salida": list(COLUMNAS_SALIDA),
                "metricas": asdict(metricas),
                "margen_error_maximo_admitido": MARGEN_ERROR_MAXIMO,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    bitacora.info("Modelo guardado en %s. %s", RUTA_MODELO, metricas.resumen())


@dataclass(frozen=True)
class Prediccion:
    """Salida de la red para un perfil biometrico, ya redondeada.

    Los gramos se ajustan para que su aporte energetico coincida exactamente con
    la energia declarada, requisito del criterio de aceptacion de la historia
    HU-06.
    """

    energia_kcal: int
    proteina_g: int
    carbohidrato_g: int
    grasa_g: int
    series_semanales_por_grupo: float


class ModeloNoEntrenado(Exception):
    """No existe un modelo guardado que se pueda cargar."""


class MotorNeuronal:
    """Modelo entrenado, listo para predecir.

    Se carga una sola vez y se conserva en memoria: el criterio de aceptacion de
    la historia HU-06 exige responder en menos de tres segundos, y cargar el
    modelo en cada peticion no lo permitiria.
    """

    def __init__(
        self,
        modelo: Any,
        normalizador: Normalizador,
        normalizador_salidas: Normalizador,
        metricas: dict[str, Any],
    ) -> None:
        self._modelo = modelo
        self._normalizador = normalizador
        self._normalizador_salidas = normalizador_salidas
        self.metricas = metricas
        # Memoria de predicciones recientes, protegida por un cerrojo porque el
        # servidor atiende cada peticion en un hilo distinto.
        self._memoria: OrderedDict[tuple, Prediccion] = OrderedDict()
        self._cerrojo = Lock()
        self.aciertos_de_memoria = 0
        self.consultas = 0

    @classmethod
    def cargar(cls) -> "MotorNeuronal":
        """Recupera del disco el modelo entrenado y su normalizador."""
        _limitar_hilos_de_tensorflow()

        import keras

        if not RUTA_MODELO.exists() or not RUTA_METADATOS.exists():
            raise ModeloNoEntrenado(str(RUTA_MODELO))

        metadatos = json.loads(RUTA_METADATOS.read_text(encoding="utf-8"))
        return cls(
            modelo=keras.models.load_model(RUTA_MODELO),
            normalizador=Normalizador.desde_diccionario(metadatos["normalizador"]),
            normalizador_salidas=Normalizador.desde_diccionario(
                metadatos["normalizador_salidas"]
            ),
            metricas=metadatos.get("metricas", {}),
        )

    def predecir(
        self,
        peso_kg: float,
        estatura_cm: float,
        edad: int,
        sexo: "Sexo",
        nivel_actividad: "NivelActividad",
        objetivo: "Objetivo",
        nivel_experiencia: "NivelExperiencia" = None,
        dias_entrenamiento_semana: int = 3,
    ) -> Prediccion:
        """Calcula el requerimiento energetico, los macronutrientes y el volumen."""
        from app.modelos.enumeraciones import NivelExperiencia as _NivelExperiencia

        if nivel_experiencia is None:
            nivel_experiencia = _NivelExperiencia.PRINCIPIANTE

        clave = (
            round(float(peso_kg), 1),
            round(float(estatura_cm), 1),
            int(edad),
            sexo.value,
            nivel_actividad.value,
            objetivo.value,
            nivel_experiencia.value,
            int(dias_entrenamiento_semana),
        )

        with self._cerrojo:
            self.consultas += 1
            recordada = self._memoria.get(clave)
            if recordada is not None:
                # Se mueve al final para que la memoria descarte primero lo que
                # hace mas tiempo que no se consulta.
                self._memoria.move_to_end(clave)
                self.aciertos_de_memoria += 1
                return recordada

        entrada = vector_entrada(
            peso_kg,
            estatura_cm,
            edad,
            sexo,
            nivel_actividad,
            objetivo,
            nivel_experiencia,
            dias_entrenamiento_semana,
        ).reshape(1, -1)
        normalizada = self._modelo.predict(self._normalizador.aplicar(entrada), verbose=0)
        salida = self._normalizador_salidas.revertir(normalizada)[0]

        proteina_g = max(int(round(float(salida[1]))), 1)
        carbohidrato_g = max(int(round(float(salida[2]))), 0)
        grasa_g = max(int(round(float(salida[3]))), 0)
        # La energia declarada es la que aportan los gramos ya redondeados, de
        # modo que la suma coincida con el total sin residuo.
        energia = (
            proteina_g * KCAL_POR_GRAMO_PROTEINA
            + carbohidrato_g * KCAL_POR_GRAMO_CARBOHIDRATO
            + grasa_g * KCAL_POR_GRAMO_GRASA
        )
        # El volumen no puede ser negativo ni salirse del rango que la regla de
        # referencia admite, por muy extremo que sea el perfil recibido.
        volumen = float(
            min(
                max(round(float(salida[4]), 1), SERIES_MINIMAS_POR_GRUPO),
                SERIES_MAXIMAS_POR_GRUPO,
            )
        )
        prediccion = Prediccion(
            energia_kcal=energia,
            proteina_g=proteina_g,
            carbohidrato_g=carbohidrato_g,
            grasa_g=grasa_g,
            series_semanales_por_grupo=volumen,
        )

        with self._cerrojo:
            self._memoria[clave] = prediccion
            if len(self._memoria) > TAMANIO_MEMORIA_PREDICCIONES:
                self._memoria.popitem(last=False)

        return prediccion

    @property
    def tasa_de_aciertos(self) -> float:
        """Proporcion de predicciones que se resolvieron desde la memoria."""
        if not self.consultas:
            return 0.0
        return round(self.aciertos_de_memoria / self.consultas, 3)

    def vaciar_memoria(self) -> None:
        """Descarta las predicciones recordadas.

        Se invoca al recargar el modelo: las predicciones de la version anterior
        dejan de ser validas en cuanto el modelo cambia.
        """
        with self._cerrojo:
            self._memoria.clear()
            self.aciertos_de_memoria = 0
            self.consultas = 0


def entrenar_y_guardar(
    cantidad: int = 20_000,
    epocas: int = EPOCAS_PREDETERMINADAS,
    semilla: int = SEMILLA_PREDETERMINADA,
    verbosidad: int = 1,
) -> MetricasEntrenamiento:
    """Ejecuta el entrenamiento completo y deja el modelo listo para el servicio.

    Es el punto de entrada del script de entrenamiento y de la comprobacion del
    requerimiento 4.5.6: el modelo puede reentrenarse sin modificar el codigo del
    servicio que lo consume.
    """
    datos = preparar_datos(cantidad=cantidad, semilla=semilla)
    modelo, metricas = entrenar(datos=datos, epocas=epocas, semilla=semilla, verbosidad=verbosidad)

    # La malla sistematica comprueba el margen de error en los extremos del
    # dominio, donde el muestreo aleatorio deja menos ejemplos.
    malla = generar_malla_de_verificacion()
    malla_normalizada = ConjuntoDatos(
        entradas=datos.normalizador.aplicar(malla.entradas),
        salidas=datos.normalizador_salidas.aplicar(malla.salidas),
    )
    medidas_extremos = evaluar_margen_de_error(
        modelo, malla_normalizada, datos.normalizador_salidas
    )
    bitacora.info(
        "Margen de error en los extremos del dominio: medio %.2f %%, máximo %.2f %%.",
        medidas_extremos["margen_error_medio"] * 100,
        medidas_extremos["margen_error_maximo"] * 100,
    )

    guardar(modelo, datos.normalizador, datos.normalizador_salidas, metricas)
    return metricas
