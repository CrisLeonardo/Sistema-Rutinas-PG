"""Controlador de gestion de cuentas y roles (historia HU-03)."""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import Administrador, SesionBD
from app.esquemas.usuario import CambioEstado, CambioRol, UsuarioPublico
from app.modelos.enumeraciones import RolUsuario
from app.modelos.usuario import Usuario
from app.servicios import autenticacion

enrutador = APIRouter(prefix="/usuarios", tags=["Gestion de cuentas"])


def _obtener_cuenta(sesion: SesionBD, usuario_id: int) -> Usuario:
    """Recupera la cuenta indicada o interrumpe la peticion si no existe."""
    cuenta = sesion.get(Usuario, usuario_id)
    if cuenta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La cuenta indicada no existe.",
        )
    return cuenta


@enrutador.get(
    "",
    response_model=list[UsuarioPublico],
    summary="Listar las cuentas registradas",
)
def listar(sesion: SesionBD, administrador: Administrador) -> list[UsuarioPublico]:
    """Devuelve todas las cuentas. Reservado al administrador."""
    return [
        UsuarioPublico.model_validate(cuenta) for cuenta in autenticacion.listar_usuarios(sesion)
    ]


@enrutador.put(
    "/{usuario_id}/rol",
    response_model=UsuarioPublico,
    summary="Asignar o modificar el rol de una cuenta",
)
def asignar_rol(
    usuario_id: int,
    datos: CambioRol,
    sesion: SesionBD,
    administrador: Administrador,
) -> UsuarioPublico:
    """Cambia el rol de una cuenta (historia HU-03).

    Impide que se retire el rol al ultimo administrador activo, situacion que
    dejaria al sistema sin ninguna cuenta capaz de administrar los catalogos.
    """
    cuenta = _obtener_cuenta(sesion, usuario_id)

    retira_administrador = (
        cuenta.rol == RolUsuario.ADMINISTRADOR and datos.rol != RolUsuario.ADMINISTRADOR
    )
    if retira_administrador and autenticacion.contar_administradores(sesion) <= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No es posible retirar el rol al único administrador activo del sistema.",
        )

    return UsuarioPublico.model_validate(autenticacion.cambiar_rol(sesion, cuenta, datos.rol))


@enrutador.put(
    "/{usuario_id}/estado",
    response_model=UsuarioPublico,
    summary="Activar o desactivar una cuenta",
)
def cambiar_estado(
    usuario_id: int,
    datos: CambioEstado,
    sesion: SesionBD,
    administrador: Administrador,
) -> UsuarioPublico:
    """Habilita o inhabilita el acceso de una cuenta sin borrar su historial."""
    cuenta = _obtener_cuenta(sesion, usuario_id)

    if not datos.activo:
        if cuenta.id == administrador.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No es posible desactivar la cuenta con la que inició sesión.",
            )
        if (
            cuenta.rol == RolUsuario.ADMINISTRADOR
            and autenticacion.contar_administradores(sesion) <= 1
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No es posible desactivar al único administrador activo del sistema.",
            )

    return UsuarioPublico.model_validate(
        autenticacion.cambiar_estado(sesion, cuenta, datos.activo)
    )
