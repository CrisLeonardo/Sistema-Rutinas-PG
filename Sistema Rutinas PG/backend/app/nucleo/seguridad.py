"""Cifrado de contrasenas y emision de tokens de sesion.

Cumple el requerimiento no funcional 4.5.1 de la tesis: las contrasenas se
almacenan mediante funciones de resumen criptografico con sal, de modo que no
puedan recuperarse en texto plano.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.nucleo.configuracion import configuracion

# bcrypt trunca la entrada a 72 bytes; se valida antes para no aceptar en
# silencio una contrasena mas larga de la que realmente se verifica.
LONGITUD_MAXIMA_BYTES = 72


def cifrar_contrasena(contrasena: str) -> str:
    """Devuelve el resumen criptografico de la contrasena con sal aleatoria."""
    bytes_contrasena = contrasena.encode("utf-8")
    if len(bytes_contrasena) > LONGITUD_MAXIMA_BYTES:
        raise ValueError(
            f"La contrasena no puede exceder {LONGITUD_MAXIMA_BYTES} bytes."
        )
    return bcrypt.hashpw(bytes_contrasena, bcrypt.gensalt()).decode("utf-8")


def verificar_contrasena(contrasena: str, resumen: str) -> bool:
    """Comprueba si la contrasena en texto plano corresponde al resumen guardado."""
    bytes_contrasena = contrasena.encode("utf-8")
    if len(bytes_contrasena) > LONGITUD_MAXIMA_BYTES:
        return False
    try:
        return bcrypt.checkpw(bytes_contrasena, resumen.encode("utf-8"))
    except ValueError:
        # El resumen almacenado no tiene un formato bcrypt valido.
        return False


def crear_token_sesion(id_usuario: int, rol: str) -> tuple[str, int]:
    """Emite el token de sesion y devuelve tambien su duracion en segundos.

    La vigencia corresponde a los minutos configurados de inactividad. La
    interfaz de cliente renueva el token mientras el usuario permanezca activo,
    de modo que la sesion caduca solo tras el periodo sin interaccion exigido
    por el criterio de aceptacion de la historia HU-02.
    """
    duracion = timedelta(minutes=configuracion.minutos_expiracion_sesion)
    emitido_en = datetime.now(timezone.utc)
    contenido = {
        "sub": str(id_usuario),
        "rol": rol,
        "iat": emitido_en,
        "exp": emitido_en + duracion,
    }
    token = jwt.encode(
        contenido,
        configuracion.clave_secreta,
        algorithm=configuracion.algoritmo_firma,
    )
    return token, int(duracion.total_seconds())


def leer_token_sesion(token: str) -> dict | None:
    """Valida la firma y la vigencia del token; devuelve None si no es valido."""
    try:
        return jwt.decode(
            token,
            configuracion.clave_secreta,
            algorithms=[configuracion.algoritmo_firma],
        )
    except jwt.PyJWTError:
        return None
