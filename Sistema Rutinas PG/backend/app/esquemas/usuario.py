"""Contratos de entrada y salida de las historias HU-01, HU-02 y HU-03."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.modelos.enumeraciones import RolUsuario

LONGITUD_MINIMA_CONTRASENA = 8


def _validar_robustez(valor: str) -> str:
    """Reglas de robustez de la contrasena, compartidas por el alta y el cambio."""
    if valor.strip() != valor:
        raise ValueError("La contraseña no puede iniciar ni terminar con espacios.")
    if not any(caracter.isalpha() for caracter in valor):
        raise ValueError("La contraseña debe incluir al menos una letra.")
    if not any(caracter.isdigit() for caracter in valor):
        raise ValueError("La contraseña debe incluir al menos un número.")
    return valor


class RegistroUsuario(BaseModel):
    """Datos requeridos para dar de alta una cuenta (historia HU-01)."""

    correo: EmailStr = Field(description="Correo electronico, unico por cuenta")
    nombre: str = Field(min_length=2, max_length=120)
    contrasena: str = Field(
        min_length=LONGITUD_MINIMA_CONTRASENA,
        max_length=72,
        description="Minimo ocho caracteres; se almacena cifrada",
    )

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, valor: str) -> str:
        nombre = " ".join(valor.split())
        if len(nombre) < 2:
            raise ValueError("El nombre debe tener al menos dos caracteres.")
        return nombre

    @field_validator("contrasena")
    @classmethod
    def validar_robustez(cls, valor: str) -> str:
        return _validar_robustez(valor)


class CambioContrasena(BaseModel):
    """Sustitucion de la contrasena por parte de su propio titular.

    Se exige la contrasena vigente ademas de la sesion activa: un telefono
    desbloqueado y desatendido no debe bastar para quedarse con la cuenta.
    """

    contrasena_actual: str = Field(min_length=1, max_length=72)
    contrasena_nueva: str = Field(
        min_length=LONGITUD_MINIMA_CONTRASENA,
        max_length=72,
        description="Minimo ocho caracteres, con al menos una letra y un numero",
    )

    @field_validator("contrasena_nueva")
    @classmethod
    def validar_robustez(cls, valor: str) -> str:
        return _validar_robustez(valor)


class CredencialesAcceso(BaseModel):
    """Credenciales enviadas al iniciar sesion (historia HU-02)."""

    correo: EmailStr
    contrasena: str = Field(min_length=1, max_length=72)


class CambioRol(BaseModel):
    """Rol que el administrador asigna a una cuenta (historia HU-03)."""

    rol: RolUsuario


class CambioEstado(BaseModel):
    """Activacion o desactivacion de una cuenta por parte del administrador."""

    activo: bool


class UsuarioPublico(BaseModel):
    """Representacion de la cuenta que se devuelve a la interfaz de cliente.

    No expone en ningun caso el resumen criptografico de la contrasena.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    correo: EmailStr
    nombre: str
    rol: RolUsuario
    activo: bool
    fecha_registro: datetime
    ultimo_acceso: datetime | None = None


class TokenSesion(BaseModel):
    """Token emitido tras un inicio de sesion correcto."""

    token_acceso: str
    tipo_token: str = "bearer"
    expira_en_segundos: int
    usuario: UsuarioPublico
