"""Enlaces aleatorios, persistencia de hashes y consumo atómico de un solo uso."""

import hashlib
import base64
import json
import logging
import secrets
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.modelos.recuperacion import RecuperacionAcceso
from app.modelos.usuario import Usuario
from app.nucleo.configuracion import configuracion
from app.nucleo.seguridad import cifrar_contrasena

MINUTOS_VIGENCIA = 15
REGISTRO = logging.getLogger(__name__)


class EnlaceNoValido(Exception):
    pass


def ahora_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def resumen(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def enviar_correo(destinatario: str, enlace: str) -> None:
    """Gmail por HTTPS o SMTP, sin registrar destinatarios, secretos ni enlaces."""
    mensaje = EmailMessage()
    mensaje["Subject"] = "Recupera tu acceso a Senda"
    mensaje["From"] = str(configuracion.correo_remitente if configuracion.correo_transporte == "gmail_api" else configuracion.smtp_remitente)
    mensaje["To"] = destinatario
    mensaje.set_content(
        f"Se solicitó cambiar tu contraseña de Senda.\n\n{enlace}\n\n"
        f"Este enlace se puede usar una sola vez y vence en {MINUTOS_VIGENCIA} minutos.\n"
        "Si no lo solicitaste, ignora este correo. Tu contraseña no ha cambiado.\n"
    )
    if configuracion.correo_transporte == "gmail_api":
        enviar_por_gmail(mensaje)
        return
    contexto = ssl.create_default_context()
    if configuracion.smtp_seguridad == "ssl":
        transporte = smtplib.SMTP_SSL(configuracion.smtp_servidor, configuracion.smtp_puerto, timeout=10, context=contexto)
    else:
        transporte = smtplib.SMTP(configuracion.smtp_servidor, configuracion.smtp_puerto, timeout=10)
    with transporte as servidor:
        if configuracion.smtp_seguridad == "starttls":
            servidor.starttls(context=contexto)
        if configuracion.smtp_usuario:
            secreto = configuracion.smtp_contrasena
            servidor.login(configuracion.smtp_usuario, secreto.get_secret_value() if secreto else "")
        servidor.send_message(mensaje)


def enviar_por_gmail(mensaje: EmailMessage) -> None:
    """Solo requiere gmail.send. No lee mensajes ni comparte acceso con deportistas."""
    credenciales = urlencode({
        "client_id": configuracion.gmail_cliente_id,
        "client_secret": configuracion.gmail_cliente_secreto.get_secret_value(),
        "refresh_token": configuracion.gmail_refresh_token.get_secret_value(),
        "grant_type": "refresh_token",
    }).encode()
    peticion = Request("https://oauth2.googleapis.com/token", data=credenciales,
                       headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urlopen(peticion, timeout=10) as respuesta:
        token = json.load(respuesta)["access_token"]
    contenido = json.dumps({"raw": base64.urlsafe_b64encode(mensaje.as_bytes()).decode("ascii")}).encode()
    peticion = Request("https://gmail.googleapis.com/gmail/v1/users/me/messages/send", data=contenido,
                       headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
    with urlopen(peticion, timeout=10) as respuesta:
        if not json.load(respuesta).get("id"):
            raise RuntimeError("El proveedor no confirmó la aceptación del mensaje.")


def procesar_solicitud(correo: str, fabrica_sesiones) -> None:
    """Se ejecuta después de la respuesta, también para direcciones inexistentes.

    Abre su propia sesión. Una tarea interrumpida se reintenta solicitando otro
    enlace; no se presenta como una cola duradera de correo.
    """
    digest = None
    try:
        with fabrica_sesiones() as sesion:
            usuario = sesion.scalar(select(Usuario).where(
                Usuario.correo == correo, Usuario.activo.is_(True)
            ).with_for_update())
            if usuario is None:
                return
            token = secrets.token_urlsafe(32)
            digest = resumen(token)
            sesion.execute(delete(RecuperacionAcceso).where(RecuperacionAcceso.usuario_id == usuario.id))
            sesion.add(RecuperacionAcceso(
                usuario_id=usuario.id, resumen_token=digest,
                vence_en=ahora_utc() + timedelta(minutes=MINUTOS_VIGENCIA),
            ))
            destino = usuario.correo
            sesion.commit()
        # El fragmento evita que el token llegue al servidor web o al Referer.
        enviar_correo(destino, f"{configuracion.url_publica_frontend}/restablecer-acceso#token={token}")
    except Exception:
        # No incluir str(error), traceback, correo o token: los errores SMTP
        # pueden contener destinatarios o respuestas del proveedor.
        REGISTRO.error("No se completó una tarea de recuperación de acceso.")
        if digest:
            try:
                with fabrica_sesiones() as sesion:
                    sesion.execute(delete(RecuperacionAcceso).where(RecuperacionAcceso.resumen_token == digest))
                    sesion.commit()
            except Exception:
                REGISTRO.error("No se pudo retirar el enlace de una entrega fallida.")


def restablecer(sesion: Session, token: str, contrasena: str) -> None:
    digest = resumen(token)
    registro = sesion.scalar(select(RecuperacionAcceso).where(RecuperacionAcceso.resumen_token == digest))
    if registro is None:
        raise EnlaceNoValido
    # Orden de bloqueos consistente con emisión/cambio autenticado.
    usuario = sesion.scalar(select(Usuario).where(Usuario.id == registro.usuario_id).with_for_update())
    if usuario is None or not usuario.activo:
        raise EnlaceNoValido
    consumido = sesion.execute(delete(RecuperacionAcceso).where(
        RecuperacionAcceso.resumen_token == digest,
        RecuperacionAcceso.vence_en > ahora_utc(),
    ).returning(RecuperacionAcceso.usuario_id)).scalar_one_or_none()
    if consumido is None:
        sesion.rollback()
        raise EnlaceNoValido
    sesion.execute(update(Usuario).where(Usuario.id == consumido).values(
        contrasena_cifrada=cifrar_contrasena(contrasena),
        version_sesion=Usuario.version_sesion + 1,
    ))
    sesion.commit()
