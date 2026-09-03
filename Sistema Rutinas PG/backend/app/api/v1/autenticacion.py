"""Controlador de registro y sesion (historias HU-01 y HU-02)."""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.usuario import (
    CredencialesAcceso,
    RegistroUsuario,
    TokenSesion,
    UsuarioPublico,
)
from app.nucleo.seguridad import crear_token_sesion
from app.servicios import autenticacion

enrutador = APIRouter(prefix="/autenticacion", tags=["Acceso seguro"])

_MENSAJE_CREDENCIALES = "El correo o la contraseña son incorrectos."


@enrutador.post(
    "/registro",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una cuenta nueva",
)
def registrar(datos: RegistroUsuario, sesion: SesionBD) -> UsuarioPublico:
    """Da de alta una cuenta con rol de usuario deportista (historia HU-01)."""
    try:
        usuario = autenticacion.registrar_usuario(sesion, datos)
    except autenticacion.CorreoYaRegistrado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta registrada con ese correo.",
        ) from None
    return UsuarioPublico.model_validate(usuario)


@enrutador.post(
    "/acceso",
    response_model=TokenSesion,
    summary="Iniciar sesion",
)
def iniciar_sesion(credenciales: CredencialesAcceso, sesion: SesionBD) -> TokenSesion:
    """Valida las credenciales y emite el token de sesion (historia HU-02)."""
    try:
        usuario = autenticacion.autenticar_usuario(
            sesion, credenciales.correo, credenciales.contrasena
        )
    except autenticacion.CredencialesInvalidas:
        # Mensaje unico para correo inexistente y contrasena incorrecta.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MENSAJE_CREDENCIALES,
        ) from None
    except autenticacion.CuentaDesactivada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta se encuentra desactivada. Comuníquese con el administrador.",
        ) from None

    token, vigencia = crear_token_sesion(usuario.id, usuario.rol.value)
    return TokenSesion(
        token_acceso=token,
        expira_en_segundos=vigencia,
        usuario=UsuarioPublico.model_validate(usuario),
    )


@enrutador.post(
    "/renovacion",
    response_model=TokenSesion,
    summary="Renovar la sesion activa",
)
def renovar_sesion(usuario: UsuarioAutenticado) -> TokenSesion:
    """Emite un token nuevo mientras el usuario permanezca activo.

    Es el mecanismo que convierte la vigencia fija del token en la expiracion
    por inactividad que exige el criterio de aceptacion de la historia HU-02.
    """
    token, vigencia = crear_token_sesion(usuario.id, usuario.rol.value)
    return TokenSesion(
        token_acceso=token,
        expira_en_segundos=vigencia,
        usuario=UsuarioPublico.model_validate(usuario),
    )


@enrutador.get(
    "/sesion",
    response_model=UsuarioPublico,
    summary="Consultar la cuenta de la sesion actual",
)
def consultar_sesion(usuario: UsuarioAutenticado) -> UsuarioPublico:
    """Devuelve los datos de la cuenta autenticada."""
    return UsuarioPublico.model_validate(usuario)
