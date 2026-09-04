"""Contratos de entrada y salida del seguimiento (historias HU-09 y HU-10).

La validacion de la fecha proviene del apartado 4.8.3: la fecha de registro de
progreso no puede ser posterior a la fecha actual. Los rangos de peso y estatura
son los mismos que acepta el perfil biometrico, para que una medicion de progreso
no pueda producir un perfil que el sistema rechazaria.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.esquemas.perfil import PESO_MAXIMO_KG, PESO_MINIMO_KG

PERIMETRO_MINIMO_CM = 40.0
PERIMETRO_MAXIMO_CM = 200.0
ADHERENCIA_MINIMA = 0
ADHERENCIA_MAXIMA = 100
SESIONES_MAXIMAS_SEMANA = 7


class RegistroProgresoEntrada(BaseModel):
    """Avance que el usuario reporta al final de la semana (historia HU-09)."""

    peso_kg: float = Field(description="Peso actual en kilogramos")
    perimetro_cintura_cm: float | None = Field(
        default=None, description="Perimetro de cintura en centimetros, opcional"
    )
    sesiones_cumplidas: int = Field(
        default=0, description="Sesiones de entrenamiento completadas en la semana"
    )
    adherencia_nutricional: int | None = Field(
        default=None, description="Porcentaje de cumplimiento del plan de alimentacion"
    )
    fecha_registro: date | None = Field(
        default=None, description="Fecha del registro; de forma predeterminada, hoy"
    )

    @field_validator("peso_kg")
    @classmethod
    def validar_peso(cls, valor: float) -> float:
        if not PESO_MINIMO_KG <= valor <= PESO_MAXIMO_KG:
            raise ValueError(
                f"El peso debe estar entre {PESO_MINIMO_KG:.0f} y {PESO_MAXIMO_KG:.0f} kilogramos."
            )
        return round(valor, 2)

    @field_validator("perimetro_cintura_cm")
    @classmethod
    def validar_perimetro(cls, valor: float | None) -> float | None:
        if valor is None:
            return None
        if not PERIMETRO_MINIMO_CM <= valor <= PERIMETRO_MAXIMO_CM:
            raise ValueError(
                f"El perímetro de cintura debe estar entre {PERIMETRO_MINIMO_CM:.0f} y "
                f"{PERIMETRO_MAXIMO_CM:.0f} centímetros."
            )
        return round(valor, 2)

    @field_validator("sesiones_cumplidas")
    @classmethod
    def validar_sesiones(cls, valor: int) -> int:
        if not 0 <= valor <= SESIONES_MAXIMAS_SEMANA:
            raise ValueError(
                f"Las sesiones cumplidas deben estar entre 0 y {SESIONES_MAXIMAS_SEMANA}."
            )
        return valor

    @field_validator("adherencia_nutricional")
    @classmethod
    def validar_adherencia(cls, valor: int | None) -> int | None:
        if valor is None:
            return None
        if not ADHERENCIA_MINIMA <= valor <= ADHERENCIA_MAXIMA:
            raise ValueError("La adherencia debe expresarse como un porcentaje entre 0 y 100.")
        return valor

    @field_validator("fecha_registro")
    @classmethod
    def validar_fecha(cls, valor: date | None) -> date | None:
        """Apartado 4.8.3: la fecha de registro no puede ser posterior a la actual."""
        if valor is None:
            return None
        if valor > date.today():
            raise ValueError("La fecha del registro no puede ser posterior a la fecha de hoy.")
        return valor


class RegistroProgresoPublico(BaseModel):
    """Registro de progreso tal como se devuelve a la interfaz."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    plan_id: int | None
    peso_kg: float
    perimetro_cintura_cm: float | None
    sesiones_cumplidas: int
    adherencia_nutricional: int | None
    fecha_registro: datetime


class ResultadoReajuste(BaseModel):
    """Explica que hizo el sistema con el progreso reportado (historia HU-09)."""

    reajusto_el_plan: bool
    motivo: str
    recomendacion: str
    cambio_peso_kg: float | None = None
    ritmo_semanal_kg: float | None = None
    plan_id_vigente: int | None = None


class RespuestaProgreso(BaseModel):
    """Registro guardado junto con el efecto que produjo sobre el plan."""

    registro: RegistroProgresoPublico
    reajuste: ResultadoReajuste


class PuntoEvolucion(BaseModel):
    """Un punto de las graficas de evolucion (historia HU-10)."""

    fecha: datetime
    peso_kg: float
    perimetro_cintura_cm: float | None = None
    sesiones_cumplidas: int = 0
    adherencia_nutricional: int | None = None


class ComparacionPlanes(BaseModel):
    """Contraste entre el primer plan generado y el que esta vigente."""

    plan_id_inicial: int
    plan_id_vigente: int
    calorias_inicial: float
    calorias_vigente: float
    proteina_inicial: float
    proteina_vigente: float
    carbohidrato_inicial: float
    carbohidrato_vigente: float
    grasa_inicial: float
    grasa_vigente: float
    fecha_inicial: datetime
    fecha_vigente: datetime

    @computed_field(description="Diferencia de energía entre el plan inicial y el vigente")
    @property
    def diferencia_calorias(self) -> float:
        return round(self.calorias_vigente - self.calorias_inicial, 2)

    @computed_field(description="Indica si el plan cambió respecto del inicial")
    @property
    def hubo_cambio(self) -> bool:
        """Se compara por identificador y no por fecha.

        La fecha de generación se almacena con resolución de segundo, de modo que
        un reajuste inmediato produciría dos planes con la misma marca de tiempo.
        """
        return self.plan_id_inicial != self.plan_id_vigente


class ReporteEvolucion(BaseModel):
    """Datos con que la interfaz dibuja los reportes graficos (historia HU-10)."""

    puntos: list[PuntoEvolucion]
    comparacion_planes: ComparacionPlanes | None = None

    @computed_field(description="Peso de la primera medición registrada")
    @property
    def peso_inicial(self) -> float | None:
        return self.puntos[0].peso_kg if self.puntos else None

    @computed_field(description="Peso de la última medición registrada")
    @property
    def peso_actual(self) -> float | None:
        return self.puntos[-1].peso_kg if self.puntos else None

    @computed_field(description="Cambio total de peso desde el primer registro")
    @property
    def cambio_total_kg(self) -> float | None:
        if len(self.puntos) < 2:
            return None
        return round(self.puntos[-1].peso_kg - self.puntos[0].peso_kg, 2)

    @computed_field(description="Total de sesiones de entrenamiento cumplidas")
    @property
    def sesiones_totales(self) -> int:
        return sum(punto.sesiones_cumplidas for punto in self.puntos)

    @computed_field(description="Promedio de adherencia al plan de alimentación")
    @property
    def adherencia_promedio(self) -> float | None:
        valores = [
            punto.adherencia_nutricional
            for punto in self.puntos
            if punto.adherencia_nutricional is not None
        ]
        if not valores:
            return None
        return round(sum(valores) / len(valores), 1)

    @computed_field(description="Registros de avance capturados")
    @property
    def registros_totales(self) -> int:
        return len(self.puntos)

    @computed_field(description="Semanas distintas con al menos un registro")
    @property
    def semanas_registradas(self) -> int:
        """Cuenta semanas del calendario, no registros.

        Antes devolvia la cantidad de registros: quien capturaba tres veces en
        una misma semana veia «3 semanas registradas», y el reporte de la
        historia HU-10 declaraba una constancia que no existia.
        """
        return len({punto.fecha.isocalendar()[:2] for punto in self.puntos})
