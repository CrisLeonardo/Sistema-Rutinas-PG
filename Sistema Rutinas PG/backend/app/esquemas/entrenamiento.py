"""Contratos de la bitacora de entrenamiento.

No corresponden a ninguna de las once historias de la pila de producto. La
bitacora se agrega porque sin ella la regla del negocio *d* del apartado 4.3.4
—el incremento de carga no supera el 10 % entre microciclos— no se puede aplicar:
el sistema no tenia forma de saber con cuanto peso entreno el usuario, de modo
que la rutina de la semana doce era identica a la de la primera.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.motor.progresion import Decision

PESO_MAXIMO_KG = 500.0
REPETICIONES_MAXIMAS = 100
SERIES_MAXIMAS_POR_SESION = 60
ESFUERZO_MINIMO = 1
ESFUERZO_MAXIMO = 10
DURACION_MAXIMA_MINUTOS = 300


# --------------------------------------------------------------------------
# Entrada
# --------------------------------------------------------------------------


class SerieEjecutadaEntrada(BaseModel):
    """Una serie que el usuario completo."""

    ejercicio_id: int
    numero_serie: int = Field(ge=1, le=SERIES_MAXIMAS_POR_SESION)
    repeticiones: int = Field(ge=0, le=REPETICIONES_MAXIMAS)
    peso_kg: float | None = Field(
        default=None, description="Peso movido. Vacío en los ejercicios de peso corporal"
    )
    repeticiones_en_reserva: int | None = Field(default=None, ge=0, le=10)

    @field_validator("peso_kg")
    @classmethod
    def validar_peso(cls, valor: float | None) -> float | None:
        if valor is None:
            return None
        if not 0 <= valor <= PESO_MAXIMO_KG:
            raise ValueError(f"El peso debe estar entre 0 y {PESO_MAXIMO_KG:.0f} kilogramos.")
        return round(valor, 2)


class SesionEjecutadaEntrada(BaseModel):
    """Lo que el usuario registra al terminar de entrenar."""

    sesion_id: int | None = Field(
        default=None, description="Sesión prescrita que se estaba ejecutando"
    )
    fecha: date | None = Field(default=None, description="Fecha del entrenamiento; hoy por omisión")
    duracion_minutos: int | None = Field(default=None, ge=1, le=DURACION_MAXIMA_MINUTOS)
    percepcion_esfuerzo: int | None = Field(
        default=None,
        ge=ESFUERZO_MINIMO,
        le=ESFUERZO_MAXIMO,
        description="Qué tan exigente resultó la sesión, de 1 a 10",
    )
    notas: str | None = Field(default=None, max_length=500)
    series: list[SerieEjecutadaEntrada] = Field(min_length=1)

    @field_validator("fecha")
    @classmethod
    def validar_fecha(cls, valor: date | None) -> date | None:
        """Misma regla que el registro de progreso: no se entrena en el futuro."""
        if valor is not None and valor > date.today():
            raise ValueError("La fecha del entrenamiento no puede ser posterior a hoy.")
        return valor

    @field_validator("series")
    @classmethod
    def validar_series(
        cls, valor: list[SerieEjecutadaEntrada]
    ) -> list[SerieEjecutadaEntrada]:
        if len(valor) > SERIES_MAXIMAS_POR_SESION:
            raise ValueError(
                f"Una sesión no puede tener más de {SERIES_MAXIMAS_POR_SESION} series."
            )
        return valor


# --------------------------------------------------------------------------
# Salida
# --------------------------------------------------------------------------


class SeriePublica(BaseModel):
    """Una serie registrada, tal como se devuelve."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ejercicio_id: int
    numero_serie: int
    repeticiones: int
    peso_kg: float | None
    repeticiones_en_reserva: int | None


class SesionRealizadaPublica(BaseModel):
    """Una sesión de la bitácora."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sesion_id: int | None
    plan_id: int | None
    fecha: date
    duracion_minutos: int | None
    percepcion_esfuerzo: int | None
    notas: str | None
    nombre_grupo: str | None = None
    series: list[SeriePublica]

    @computed_field(description="Series que registró la sesión")
    @property
    def series_totales(self) -> int:
        return len(self.series)

    @computed_field(description="Repeticiones que sumó la sesión")
    @property
    def repeticiones_totales(self) -> int:
        return sum(serie.repeticiones for serie in self.series)

    @computed_field(description="Volumen de carga: la suma de peso por repeticiones")
    @property
    def volumen_kg(self) -> float:
        return round(
            sum(
                serie.peso_kg * serie.repeticiones
                for serie in self.series
                if serie.peso_kg is not None
            ),
            1,
        )


class RecomendacionPublica(BaseModel):
    """Con cuánto peso conviene entrenar un ejercicio la próxima vez."""

    decision: Decision
    carga_sugerida_kg: float | None
    carga_previa_kg: float | None
    repeticiones_objetivo: int
    explicacion: str

    @computed_field(description="Indica si la recomendación sube la carga")
    @property
    def hay_incremento(self) -> bool:
        return self.decision == Decision.SUBIR_CARGA


class SeriePrevia(BaseModel):
    """Lo que se hizo en una serie la última vez que se entrenó el ejercicio."""

    numero_serie: int
    repeticiones: int
    peso_kg: float | None


class EjercicioParaEntrenar(BaseModel):
    """Un ejercicio de la sesión, con su prescripción y su historial."""

    ejercicio_id: int
    nombre: str
    equipamiento: str
    descripcion: str | None
    grupo_muscular: str
    orden: int

    series: int
    repeticiones_min: int
    repeticiones_max: int
    repeticiones_en_reserva: int
    descanso_segundos: int

    recomendacion: RecomendacionPublica
    ultima_vez: list[SeriePrevia] = []
    fecha_ultima_vez: date | None = None

    @computed_field(description="Prescripción resumida, tal como se lee en el gimnasio")
    @property
    def prescripcion(self) -> str:
        return (
            f"{self.series} series de {self.repeticiones_min} a "
            f"{self.repeticiones_max} repeticiones"
        )


class SesionParaEntrenar(BaseModel):
    """Todo lo que la pantalla necesita para acompañar una sesión de gimnasio."""

    sesion_id: int
    dia: int
    nombre_dia: str
    nombre_grupo: str
    plan_id: int
    duracion_estimada_minutos: int
    ya_registrada_hoy: bool
    ejercicios: list[EjercicioParaEntrenar]

    @computed_field(description="Series que la sesión prescribe")
    @property
    def series_totales(self) -> int:
        return sum(ejercicio.series for ejercicio in self.ejercicios)


class MarcaPersonal(BaseModel):
    """El mejor registro del usuario en un ejercicio."""

    ejercicio_id: int
    nombre: str
    carga_maxima_kg: float | None
    repeticiones_en_la_maxima: int | None
    fecha: date | None

    @computed_field(description="Repetición máxima estimada por la fórmula de Epley")
    @property
    def repeticion_maxima_estimada_kg(self) -> float | None:
        """Carga que el usuario levantaría una sola vez, estimada.

        La fórmula de Epley —peso por uno más las repeticiones entre treinta—
        permite comparar series de repeticiones distintas en una sola cifra, que
        es lo que hace legible el avance. Es una estimación, no una medición: el
        sistema nunca le pide a nadie levantar su máximo.
        """
        if self.carga_maxima_kg is None or not self.repeticiones_en_la_maxima:
            return None
        return round(self.carga_maxima_kg * (1 + self.repeticiones_en_la_maxima / 30), 1)


class PuntoDeCarga(BaseModel):
    """Un punto de la evolución de la carga de un ejercicio."""

    fecha: date
    carga_maxima_kg: float | None
    volumen_kg: float
    repeticiones_totales: int


class HistorialDeEjercicio(BaseModel):
    """Cómo ha evolucionado un ejercicio a lo largo de las sesiones."""

    ejercicio_id: int
    nombre: str
    grupo_muscular: str
    marca: MarcaPersonal
    puntos: list[PuntoDeCarga]

    @computed_field(description="Sesiones en que se registró este ejercicio")
    @property
    def sesiones_registradas(self) -> int:
        return len(self.puntos)

    @computed_field(description="Cambio de carga desde el primer registro")
    @property
    def cambio_carga_kg(self) -> float | None:
        cargas = [punto.carga_maxima_kg for punto in self.puntos if punto.carga_maxima_kg]
        if len(cargas) < 2:
            return None
        return round(cargas[-1] - cargas[0], 1)


class ResumenEntrenamiento(BaseModel):
    """Cifras de la bitácora para el panel y los reportes."""

    sesiones_totales: int
    sesiones_esta_semana: int
    sesiones_semana_pasada: int
    volumen_esta_semana_kg: float
    volumen_semana_pasada_kg: float
    racha_semanas: int
    ultima_sesion: date | None
    marcas: list[MarcaPersonal] = []

    @computed_field(description="Cambio de volumen respecto de la semana pasada")
    @property
    def cambio_volumen_porcentaje(self) -> float | None:
        if not self.volumen_semana_pasada_kg:
            return None
        return round(
            (self.volumen_esta_semana_kg - self.volumen_semana_pasada_kg)
            / self.volumen_semana_pasada_kg
            * 100,
            1,
        )


class RespuestaSesionRegistrada(BaseModel):
    """La sesión guardada junto con lo que el sistema hará la próxima vez."""

    sesion: SesionRealizadaPublica
    progresiones: list[RecomendacionPublica]
    mensaje: str
