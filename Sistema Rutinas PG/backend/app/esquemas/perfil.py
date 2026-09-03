"""Contratos de entrada y salida de las historias HU-04 y HU-05.

Los rangos declarados aqui son los del criterio de aceptacion de la Tabla 9 del
Capitulo IV y los de la regla del negocio *a* del apartado 4.3.4. Se validan en
el servidor y no unicamente en la interfaz, conforme al apartado 4.8.3.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.modelos.enumeraciones import NivelActividad, NivelExperiencia, Objetivo, Sexo

PESO_MINIMO_KG = 30.0
PESO_MAXIMO_KG = 250.0
ESTATURA_MINIMA_CM = 120.0
ESTATURA_MAXIMA_CM = 220.0
EDAD_MINIMA = 18
EDAD_MAXIMA = 100
DIAS_MINIMOS_SEMANA = 1
DIAS_MAXIMOS_SEMANA = 7


class RegistroPerfilBiometrico(BaseModel):
    """Medidas y objetivos que el usuario declara (historia HU-04).

    Los seis primeros campos son obligatorios por criterio de aceptacion. El
    nivel de experiencia y la frecuencia semanal tienen valor predeterminado
    porque los consume la generacion de la rutina en la Iteracion 3.
    """

    peso_kg: float = Field(description="Peso corporal en kilogramos, entre 30 y 250")
    estatura_cm: float = Field(description="Estatura en centimetros, entre 120 y 220")
    edad: int = Field(description="Edad cumplida en anios, desde 18")
    sexo: Sexo
    nivel_actividad: NivelActividad
    objetivo: Objetivo
    nivel_experiencia: NivelExperiencia = NivelExperiencia.PRINCIPIANTE
    dias_entrenamiento_semana: int = Field(
        default=3, description="Sesiones de entrenamiento previstas por semana, entre 1 y 7"
    )

    @field_validator("peso_kg")
    @classmethod
    def validar_peso(cls, valor: float) -> float:
        if not PESO_MINIMO_KG <= valor <= PESO_MAXIMO_KG:
            raise ValueError(
                f"El peso debe estar entre {PESO_MINIMO_KG:.0f} y {PESO_MAXIMO_KG:.0f} kilogramos."
            )
        return round(valor, 2)

    @field_validator("estatura_cm")
    @classmethod
    def validar_estatura(cls, valor: float) -> float:
        if not ESTATURA_MINIMA_CM <= valor <= ESTATURA_MAXIMA_CM:
            raise ValueError(
                f"La estatura debe estar entre {ESTATURA_MINIMA_CM:.0f} y "
                f"{ESTATURA_MAXIMA_CM:.0f} centímetros."
            )
        return round(valor, 2)

    @field_validator("edad")
    @classmethod
    def validar_edad(cls, valor: int) -> int:
        # Regla del negocio *a*: los menores de edad quedan excluidos porque
        # requieren valoracion pediatrica especializada.
        if valor < EDAD_MINIMA:
            raise ValueError(
                "El sistema solo genera planes para personas mayores de dieciocho años."
            )
        if valor > EDAD_MAXIMA:
            raise ValueError(f"La edad no puede superar los {EDAD_MAXIMA} años.")
        return valor

    @field_validator("dias_entrenamiento_semana")
    @classmethod
    def validar_dias(cls, valor: int) -> int:
        if not DIAS_MINIMOS_SEMANA <= valor <= DIAS_MAXIMOS_SEMANA:
            raise ValueError(
                f"Los días de entrenamiento deben estar entre {DIAS_MINIMOS_SEMANA} "
                f"y {DIAS_MAXIMOS_SEMANA} por semana."
            )
        return valor


class PerfilBiometricoPublico(BaseModel):
    """Perfil devuelto a la interfaz, con el indice de masa corporal calculado."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    peso_kg: float
    estatura_cm: float
    edad: int
    sexo: Sexo
    nivel_actividad: NivelActividad
    objetivo: Objetivo
    nivel_experiencia: NivelExperiencia
    dias_entrenamiento_semana: int
    fecha_registro: datetime

    @computed_field(description="Índice de masa corporal, en kilogramos por metro cuadrado")
    @property
    def indice_masa_corporal(self) -> float:
        """Calcula el indice de masa corporal a partir del peso y la estatura."""
        estatura_m = self.estatura_cm / 100
        return round(self.peso_kg / (estatura_m**2), 2)

    @computed_field(description="Lectura del índice en lenguaje sencillo (apartado 4.5.3)")
    @property
    def clasificacion_masa_corporal(self) -> str:
        """Traduce el indice a una categoria comprensible sin formacion en nutricion."""
        return clasificar_indice_masa_corporal(self.indice_masa_corporal)


def clasificar_indice_masa_corporal(indice: float) -> str:
    """Devuelve la categoria de la Organizacion Mundial de la Salud del indice.

    Es una lectura descriptiva, no un diagnostico medico: la regla del negocio
    *e* del apartado 4.3.4 excluye al sistema de emitir diagnosticos.
    """
    if indice < 18.5:
        return "Peso por debajo de lo normal"
    if indice < 25:
        return "Peso normal"
    if indice < 30:
        return "Sobrepeso"
    return "Obesidad"
