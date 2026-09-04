"""Logica de negocio del acceso seguro (epica E1).

Concentra las reglas de las historias HU-01, HU-02 y HU-03 para mantenerlas
independientes de los controladores, conforme al patron modelo-vista-controlador
adoptado en el apartado 3.1.2 de la tesis.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.esquemas.usuario import RegistroUsuario
from app.modelos.enumeraciones import RolUsuario
from app.modelos.usuario import Usuario
from app.nucleo.seguridad import cifrar_contrasena, verificar_contrasena

# Resumen de una contrasena ficticia. Se verifica cuando el correo no existe para
# que el tiempo de respuesta sea equivalente al de un correo registrado y no
# permita deducir que cuentas existen.
_RESUMEN_SENUELO = cifrar_contrasena("contrasena-senuelo-sin-uso-real-1")


class CorreoYaRegistrado(Exception):
    """El correo indicado ya pertenece a una cuenta existente."""


class CredencialesInvalidas(Exception):
    """El correo o la contrasena no corresponden a una cuenta activa."""


class CuentaDesactivada(Exception):
    """La cuenta existe pero fue desactivada por un administrador."""


def buscar_por_correo(sesion: Session, correo: str) -> Usuario | None:
    """Recupera una cuenta por su correo, sin distinguir mayusculas."""
    sentencia = select(Usuario).where(func.lower(Usuario.correo) == correo.strip().lower())
    return sesion.execute(sentencia).scalar_one_or_none()


def registrar_usuario(
    sesion: Session,
    datos: RegistroUsuario,
    rol: RolUsuario = RolUsuario.USUARIO,
) -> Usuario:
    """Crea una cuenta nueva con la contrasena cifrada (historia HU-01).

    El rol predeterminado es el de usuario deportista; solo el proceso de
    arranque del sistema crea cuentas con rol de administrador.
    """
    correo = datos.correo.strip().lower()
    if buscar_por_correo(sesion, correo) is not None:
        raise CorreoYaRegistrado(correo)

    usuario = Usuario(
        correo=correo,
        nombre=datos.nombre,
        contrasena_cifrada=cifrar_contrasena(datos.contrasena),
        rol=rol,
        activo=True,
    )
    sesion.add(usuario)
    try:
        sesion.commit()
    except IntegrityError as error:
        # Cubre la condicion de carrera entre la consulta previa y la insercion,
        # que la restriccion de unicidad de la base de datos detiene.
        sesion.rollback()
        raise CorreoYaRegistrado(correo) from error

    sesion.refresh(usuario)
    return usuario


def autenticar_usuario(sesion: Session, correo: str, contrasena: str) -> Usuario:
    """Valida las credenciales y registra el acceso (historia HU-02).

    Ante un correo inexistente o una contrasena incorrecta se lanza siempre la
    misma excepcion, para no revelar cual de los dos datos es erroneo.
    """
    usuario = buscar_por_correo(sesion, correo)

    if usuario is None:
        verificar_contrasena(contrasena, _RESUMEN_SENUELO)
        raise CredencialesInvalidas

    if not verificar_contrasena(contrasena, usuario.contrasena_cifrada):
        raise CredencialesInvalidas

    if not usuario.activo:
        raise CuentaDesactivada

    usuario.ultimo_acceso = datetime.now(timezone.utc)
    sesion.commit()
    sesion.refresh(usuario)
    return usuario


def contrasena_coincide(usuario: Usuario, contrasena: str) -> bool:
    """Comprueba la contrasena vigente de una cuenta ya autenticada."""
    return verificar_contrasena(contrasena, usuario.contrasena_cifrada)


def cambiar_contrasena(sesion: Session, usuario: Usuario, contrasena_nueva: str) -> Usuario:
    """Sustituye la contrasena de la cuenta por su resumen criptografico nuevo."""
    usuario.contrasena_cifrada = cifrar_contrasena(contrasena_nueva)
    sesion.commit()
    sesion.refresh(usuario)
    return usuario


def listar_usuarios(sesion: Session) -> list[Usuario]:
    """Devuelve todas las cuentas ordenadas por fecha de registro."""
    sentencia = select(Usuario).order_by(Usuario.fecha_registro.desc())
    return list(sesion.execute(sentencia).scalars())


def cambiar_rol(sesion: Session, usuario: Usuario, rol: RolUsuario) -> Usuario:
    """Asigna un rol distinto a una cuenta (historia HU-03)."""
    usuario.rol = rol
    sesion.commit()
    sesion.refresh(usuario)
    return usuario


def cambiar_estado(sesion: Session, usuario: Usuario, activo: bool) -> Usuario:
    """Activa o desactiva una cuenta sin eliminar su historial."""
    usuario.activo = activo
    sesion.commit()
    sesion.refresh(usuario)
    return usuario


def contar_administradores(sesion: Session, solo_activos: bool = True) -> int:
    """Cuenta los administradores existentes.

    Permite impedir que el sistema quede sin ninguna cuenta capaz de administrar
    los catalogos y los roles.
    """
    sentencia = select(func.count()).select_from(Usuario).where(
        Usuario.rol == RolUsuario.ADMINISTRADOR
    )
    if solo_activos:
        sentencia = sentencia.where(Usuario.activo.is_(True))
    return sesion.execute(sentencia).scalar_one()
