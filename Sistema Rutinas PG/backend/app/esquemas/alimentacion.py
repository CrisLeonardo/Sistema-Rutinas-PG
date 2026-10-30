"""Restricciones explícitas, diferentes de las preferencias voluntarias."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

ALERGENOS = {
    "leche": "Leche", "huevo": "Huevo", "pescado": "Pescado",
    "crustaceos": "Crustáceos", "mani": "Maní", "frutos_secos": "Frutos secos",
    "trigo": "Trigo", "soya": "Soya", "sesamo": "Sésamo",
}
INTOLERANCIAS = {"lactosa": "Lactosa", "gluten": "Gluten / enfermedad celíaca"}


class PreferenciasEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patron: Literal["omnivoro", "vegetariano", "vegano"] = "omnivoro"
    alergias: list[str] = Field(default_factory=list, max_length=9)
    intolerancias: list[str] = Field(default_factory=list, max_length=2)
    alimentos_excluidos: list[int] = Field(default_factory=list, max_length=100)
    otra_restriccion: bool = False

    @field_validator("alergias", "intolerancias")
    @classmethod
    def validar_claves(cls, valores, info):
        permitidas = ALERGENOS if info.field_name == "alergias" else INTOLERANCIAS
        if any(valor not in permitidas for valor in valores):
            raise ValueError("Seleccione una restricción del catálogo; para otras use «Otra restricción».")
        return sorted(set(valores))

    @field_validator("alimentos_excluidos")
    @classmethod
    def validar_identificadores(cls, valores):
        if any(valor <= 0 for valor in valores):
            raise ValueError("Los identificadores de alimentos deben ser positivos.")
        return sorted(set(valores))


class CambioComida(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=1)
    dia: int = Field(ge=1, le=7)
    tiempo: int = Field(ge=0, le=4)
    receta_id: str = Field(min_length=1, max_length=80)
