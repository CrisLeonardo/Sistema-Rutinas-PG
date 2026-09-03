"""Contratos de los catalogos maestros (historia HU-11).

El alta y la modificacion estan reservadas al administrador; la consulta esta
abierta a cualquier cuenta autenticada, porque el usuario deportista necesita ver
los alimentos y ejercicios que su plan le propone.
"""

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.modelos.enumeraciones import CategoriaAlimento, GrupoMuscular, NivelExperiencia

ENERGIA_MAXIMA_100G = 900.0
GRAMOS_EN_CIEN = 100.0
# Tolerancia al comparar la energia declarada con la que aportan los
# macronutrientes. Las tablas de composicion redondean sus cifras, de modo que
# una coincidencia exacta seria una exigencia irreal.
TOLERANCIA_ENERGIA_KCAL = 25.0


class AlimentoEntrada(BaseModel):
    """Datos con que el administrador da de alta o modifica un alimento."""

    nombre: str = Field(min_length=2, max_length=120)
    categoria: CategoriaAlimento
    energia_kcal_100g: float = Field(description="Kilocalorias por cada 100 gramos")
    proteina_g_100g: float = Field(description="Gramos de proteina por cada 100 gramos")
    carbohidrato_g_100g: float = Field(description="Gramos de carbohidrato por cada 100 gramos")
    grasa_g_100g: float = Field(description="Gramos de grasa por cada 100 gramos")
    costo_aproximado_quetzales: float | None = None
    medida_casera: str | None = Field(default=None, max_length=80)
    disponible_localmente: bool = True

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, valor: str) -> str:
        nombre = " ".join(valor.split())
        if len(nombre) < 2:
            raise ValueError("El nombre del alimento debe tener al menos dos caracteres.")
        return nombre

    @field_validator("energia_kcal_100g")
    @classmethod
    def validar_energia(cls, valor: float) -> float:
        if not 0 <= valor <= ENERGIA_MAXIMA_100G:
            raise ValueError(
                f"La energía debe estar entre 0 y {ENERGIA_MAXIMA_100G:.0f} kilocalorías "
                "por cada 100 gramos."
            )
        return round(valor, 2)

    @field_validator("proteina_g_100g", "carbohidrato_g_100g", "grasa_g_100g")
    @classmethod
    def validar_macronutriente(cls, valor: float) -> float:
        if not 0 <= valor <= GRAMOS_EN_CIEN:
            raise ValueError(
                "Cada macronutriente debe estar entre 0 y 100 gramos por cada 100 gramos "
                "de alimento."
            )
        return round(valor, 2)

    @field_validator("costo_aproximado_quetzales")
    @classmethod
    def validar_costo(cls, valor: float | None) -> float | None:
        if valor is None:
            return None
        if valor < 0:
            raise ValueError("El costo no puede ser negativo.")
        return round(valor, 2)

    def energia_de_los_macronutrientes(self) -> float:
        """Energia que aportan los gramos declarados, segun las constantes de Atwater."""
        return (
            self.proteina_g_100g * 4 + self.carbohidrato_g_100g * 4 + self.grasa_g_100g * 9
        )


class AlimentoPublico(BaseModel):
    """Alimento tal como se devuelve a la interfaz."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    categoria: CategoriaAlimento
    energia_kcal_100g: float
    proteina_g_100g: float
    carbohidrato_g_100g: float
    grasa_g_100g: float
    costo_aproximado_quetzales: float | None
    medida_casera: str | None
    disponible_localmente: bool

    @computed_field(description="Nombre legible de la categoría")
    @property
    def nombre_categoria(self) -> str:
        return NOMBRES_CATEGORIA[self.categoria]


class EjercicioEntrada(BaseModel):
    """Datos con que el administrador da de alta o modifica un ejercicio."""

    nombre: str = Field(min_length=2, max_length=120)
    grupo_muscular: GrupoMuscular
    nivel_minimo: NivelExperiencia = NivelExperiencia.PRINCIPIANTE
    equipamiento: str = Field(min_length=2, max_length=120)
    descripcion: str | None = None
    es_compuesto: bool = False
    disponible_localmente: bool = True

    @field_validator("nombre", "equipamiento")
    @classmethod
    def limpiar_texto(cls, valor: str) -> str:
        texto = " ".join(valor.split())
        if len(texto) < 2:
            raise ValueError("El texto debe tener al menos dos caracteres.")
        return texto


class EjercicioPublico(BaseModel):
    """Ejercicio tal como se devuelve a la interfaz."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    grupo_muscular: GrupoMuscular
    nivel_minimo: NivelExperiencia
    equipamiento: str
    descripcion: str | None
    es_compuesto: bool
    disponible_localmente: bool

    @computed_field(description="Nombre legible del grupo muscular")
    @property
    def nombre_grupo(self) -> str:
        from app.esquemas.rutina import NOMBRES_GRUPO

        return NOMBRES_GRUPO[self.grupo_muscular]


NOMBRES_CATEGORIA = {
    CategoriaAlimento.CEREAL: "Cereal",
    CategoriaAlimento.PROTEINA_ANIMAL: "Proteína animal",
    CategoriaAlimento.LEGUMINOSA: "Leguminosa",
    CategoriaAlimento.LACTEO: "Lácteo",
    CategoriaAlimento.FRUTA: "Fruta",
    CategoriaAlimento.VERDURA: "Verdura",
    CategoriaAlimento.GRASA: "Grasa",
    CategoriaAlimento.TUBERCULO: "Tubérculo",
}
