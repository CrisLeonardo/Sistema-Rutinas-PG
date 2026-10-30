from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class CrearGrupo(Entrada):
    nombre: str = Field(min_length=3, max_length=60, pattern=r"^[\w áéíóúÁÉÍÓÚñÑ.-]+$")
    alias: str = Field(min_length=2, max_length=30, pattern=r"^[\w áéíóúÁÉÍÓÚñÑ.-]+$")
    consentimiento: Literal[True]

class ResponderInvitacion(Entrada):
    codigo: str = Field(min_length=30, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    aceptar: bool
    alias: str = Field(default="", max_length=30, pattern=r"^[\w áéíóúÁÉÍÓÚñÑ.-]*$")
    consentimiento: bool = False

class Participar(Entrada):
    meta: int = Field(ge=2, le=5)
    consentimiento: Literal[True]

class Denunciar(Entrada):
    miembro_id: str = Field(min_length=32, max_length=32)
    motivo: Literal["acoso", "alias_inapropiado", "registro_anomalo", "otro"]

class MiembroPublico(BaseModel):
    id: str
    alias: str
    soy_yo: bool
    puntos: int | None
    estado: str

class GrupoPublico(BaseModel):
    id: str
    nombre: str
    soy_propietario: bool
    semana: str
    objetivo_colectivo: int
    puntos_colectivos: int
    miembros: list[MiembroPublico]

class InvitacionPublica(BaseModel):
    codigo: str
    vence: str

class DenunciaPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    miembro_id: str
    motivo: str
    resuelta: bool
