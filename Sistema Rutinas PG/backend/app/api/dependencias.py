"""Dependencias compartidas por los controladores de la interfaz de programacion.

Implementan la validacion de acceso en el servidor exigida por el requerimiento
no funcional 4.5.1: ninguna comprobacion de rol descansa unicamente en la
interfaz de cliente.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.modelos.enumeraciones import RolUsuario
from app.modelos.usuario import Usuario
from app.nucleo.base_datos import obtener_sesion
from app.nucleo.seguridad import leer_token_sesion

esquema_autenticacion = HTTPBearer(auto_error=False, description="Token de sesion")

SesionBD = Annotated[Session, Depends(obtener_sesion)]

_SIN_SESION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Su sesión no está activa o ha expirado. Inicie sesión nuevamente.",
    headers={"WWW-Authenticate": "Bearer"},
)


def obtener_usuario_actual(
    sesion: SesionBD,
    credenciales: Annotated[
        HTTPAuthorizationCredentials | None, Depends(esquema_autenticacion)
    ] = None,
) -> Usuario:
    """Resuelve la cuenta asociada al token recibido.

    Rechaza la peticion cuando no hay token, cuando esta vencido o alterado, y
    cuando la cuenta fue eliminada o desactivada despues de emitirlo.
    """
    if credenciales is None or not credenciales.credentials:
        raise _SIN_SESION

    contenido = leer_token_sesion(credenciales.credentials)
    if contenido is None:
        raise _SIN_SESION

    identificador = contenido.get("sub")
    if identificador is None:
        raise _SIN_SESION

    try:
        usuario = sesion.get(Usuario, int(identificador))
    except (TypeError, ValueError):
        raise _SIN_SESION from None

    if usuario is None or not usuario.activo:
        raise _SIN_SESION

    return usuario


UsuarioAutenticado = Annotated[Usuario, Depends(obtener_usuario_actual)]


def requerir_administrador(usuario: UsuarioAutenticado) -> Usuario:
    """Restringe el recurso a las cuentas con rol de administrador (historia HU-03)."""
    if usuario.rol != RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación está reservada a las cuentas de administrador.",
        )
    return usuario


Administrador = Annotated[Usuario, Depends(requerir_administrador)]
