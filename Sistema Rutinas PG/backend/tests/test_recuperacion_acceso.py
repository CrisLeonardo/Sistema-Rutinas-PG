"""Recuperación sin enumeración, caducidad, revocación y consumo concurrente."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit
from io import BytesIO
from email.message import EmailMessage
import json
import base64

import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.api.v1.autenticacion import limitador_recuperacion, limitador_restablecimiento
from app.modelos.recuperacion import RecuperacionAcceso
from app.modelos.usuario import Usuario
from app.nucleo.base_datos import Base
from app.nucleo.configuracion import Configuracion, configuracion
from app.nucleo.limitador import limitador_de_acceso, limitador_de_registro
from app.servicios import recuperacion
from .conftest import CORREO_DEPORTISTA, CONTRASENA_DEPORTISTA, encabezado

SOLICITAR = "/api/v1/autenticacion/recuperacion"
RESTABLECER = "/api/v1/autenticacion/restablecimiento"


@pytest.fixture(autouse=True)
def correo_ficticio(monkeypatch):
    monkeypatch.setattr(configuracion, "correo_transporte", "smtp")
    for limitador in (limitador_recuperacion, limitador_restablecimiento, limitador_de_acceso, limitador_de_registro):
        limitador.reiniciar()
    monkeypatch.setattr(configuracion, "smtp_servidor", "smtp.example.com")
    monkeypatch.setattr(configuracion, "smtp_remitente", "senda@example.com")
    monkeypatch.setattr(configuracion, "smtp_usuario", "")
    monkeypatch.setattr(configuracion, "url_publica_frontend", "https://senda.example.com")
    mensajes = []
    monkeypatch.setattr(recuperacion, "enviar_correo", lambda destino, enlace: mensajes.append((destino, enlace)))
    yield mensajes
    for limitador in (limitador_recuperacion, limitador_restablecimiento, limitador_de_acceso, limitador_de_registro):
        limitador.reiniciar()


def solicitar_token(cliente, mensajes):
    assert cliente.post(SOLICITAR, json={"correo": CORREO_DEPORTISTA}).status_code == 202
    return parse_qs(urlsplit(mensajes[-1][1]).fragment)["token"][0]


def test_respuesta_no_enumera_cuentas_y_solo_guarda_hash(cliente, token_usuario, fabrica_sesiones, correo_ficticio):
    existente = cliente.post(SOLICITAR, json={"correo": CORREO_DEPORTISTA})
    inexistente = cliente.post(SOLICITAR, json={"correo": "inexistente@example.com"})
    assert existente.status_code == inexistente.status_code == 202
    assert existente.json() == inexistente.json()
    assert len(correo_ficticio) == 1
    enlace = correo_ficticio[0][1]
    token = parse_qs(urlsplit(enlace).fragment)["token"][0]
    assert urlsplit(enlace).query == ""
    with fabrica_sesiones() as sesion:
        registro = sesion.scalar(select(RecuperacionAcceso))
        assert registro.resumen_token == recuperacion.resumen(token)
        assert token not in existente.text and token != registro.resumen_token


def test_recuperar_revoca_sesiones_y_no_inicia_sesion_automaticamente(cliente, token_usuario, correo_ficticio):
    token = solicitar_token(cliente, correo_ficticio)
    respuesta = cliente.post(RESTABLECER, json={"token": token, "contrasena_nueva": "NuevaSenda2026"})
    assert respuesta.status_code == 200 and "token_acceso" not in respuesta.json()
    for ruta in ("/sesion", "/renovacion"):
        metodo = cliente.get if ruta == "/sesion" else cliente.post
        assert metodo("/api/v1/autenticacion" + ruta, headers=encabezado(token_usuario)).status_code == 401
    for clave, estado in ((CONTRASENA_DEPORTISTA, 401), ("NuevaSenda2026", 200)):
        assert cliente.post("/api/v1/autenticacion/acceso", json={"correo": CORREO_DEPORTISTA, "contrasena": clave}).status_code == estado
    assert cliente.post(RESTABLECER, json={"token": token, "contrasena_nueva": "OtraSenda2026"}).status_code == 400


def test_enlace_vencido_no_cambia_contrasena(cliente, token_usuario, fabrica_sesiones, correo_ficticio):
    token = solicitar_token(cliente, correo_ficticio)
    with fabrica_sesiones() as sesion:
        sesion.scalar(select(RecuperacionAcceso)).vence_en = recuperacion.ahora_utc() - timedelta(seconds=1)
        sesion.commit()
    assert cliente.post(RESTABLECER, json={"token": token, "contrasena_nueva": "NuevaSenda2026"}).status_code == 400
    assert cliente.get("/api/v1/autenticacion/sesion", headers=encabezado(token_usuario)).status_code == 200


def test_solicitud_nueva_invalida_enlace_anterior(cliente, token_usuario, correo_ficticio):
    primero = solicitar_token(cliente, correo_ficticio)
    segundo = solicitar_token(cliente, correo_ficticio)
    assert primero != segundo
    assert cliente.post(RESTABLECER, json={"token": primero, "contrasena_nueva": "NuevaSenda2026"}).status_code == 400
    assert cliente.post(RESTABLECER, json={"token": segundo, "contrasena_nueva": "NuevaSenda2026"}).status_code == 200


def test_cambio_autenticado_revoca_enlace_y_sesion_anteriores(cliente, token_usuario, correo_ficticio):
    token = solicitar_token(cliente, correo_ficticio)
    cambio = cliente.post("/api/v1/autenticacion/cambio-de-contrasena", headers=encabezado(token_usuario), json={
        "contrasena_actual": CONTRASENA_DEPORTISTA, "contrasena_nueva": "NuevaSenda2026",
    })
    assert cambio.status_code == 200
    assert cliente.get("/api/v1/autenticacion/sesion", headers=encabezado(token_usuario)).status_code == 401
    assert cliente.get("/api/v1/autenticacion/sesion", headers=encabezado(cambio.json()["token_acceso"])).status_code == 200
    assert cliente.post(RESTABLECER, json={"token": token, "contrasena_nueva": "OtraSenda2026"}).status_code == 400


def test_cuenta_desactivada_no_recibe_correo(cliente, token_usuario, fabrica_sesiones, correo_ficticio):
    with fabrica_sesiones() as sesion:
        sesion.scalar(select(Usuario).where(Usuario.correo == CORREO_DEPORTISTA)).activo = False
        sesion.commit()
    assert cliente.post(SOLICITAR, json={"correo": CORREO_DEPORTISTA}).status_code == 202
    assert correo_ficticio == []


def test_smtp_fallido_no_filtra_datos_y_retira_el_enlace(cliente, token_usuario, fabrica_sesiones, monkeypatch, caplog):
    def fallar(*args):
        raise RuntimeError("secreto-no-debe-aparecer@example.com")
    monkeypatch.setattr(recuperacion, "enviar_correo", fallar)
    assert cliente.post(SOLICITAR, json={"correo": CORREO_DEPORTISTA}).status_code == 202
    assert "secreto-no-debe-aparecer" not in caplog.text
    with fabrica_sesiones() as sesion:
        assert sesion.scalar(select(RecuperacionAcceso)) is None


def test_sin_smtp_no_simula_envio(cliente, monkeypatch):
    monkeypatch.setattr(configuracion, "smtp_servidor", "")
    assert cliente.get("/api/v1/autenticacion/opciones-publicas").json()["recuperacion_habilitada"] is False
    assert cliente.post(SOLICITAR, json={"correo": "cualquiera@example.com"}).status_code == 503


def test_limita_solicitudes_sin_depender_de_existencia(cliente):
    respuestas = [cliente.post(SOLICITAR, json={"correo": f"inexistente{i}@example.com"}) for i in range(6)]
    assert respuestas[-1].status_code == 429
    assert "Retry-After" in respuestas[-1].headers


def test_limita_intentos_de_canje(cliente):
    respuestas = [cliente.post(RESTABLECER, json={"token": "a" * 43, "contrasena_nueva": "NuevaSenda2026"}) for _ in range(9)]
    assert respuestas[0].status_code == 400 and respuestas[-1].status_code == 429


@pytest.mark.parametrize("clave", ["corta1", "sinnumeros", "12345678", "á" * 40 + "1", " claveSegura1"])
def test_reglas_de_contrasena_en_canje(cliente, clave):
    assert cliente.post(RESTABLECER, json={"token": "a" * 43, "contrasena_nueva": clave}).status_code == 422


def test_produccion_exige_https_y_smtp_cifrado():
    config = Configuracion(_env_file=None, entorno="produccion", correo_transporte="smtp", smtp_servidor="smtp.example.com", smtp_remitente="senda@example.com")
    assert not config.recuperacion_habilitada
    config.url_publica_frontend = "https://senda.example.com"
    assert config.recuperacion_habilitada
    config.smtp_seguridad = "ninguna"
    assert not config.recuperacion_habilitada


def test_gmail_sin_clave_no_se_anuncia_disponible():
    config = Configuracion(_env_file=None, correo_transporte="smtp", smtp_servidor="smtp.gmail.com", smtp_remitente="senda1986.gt@gmail.com", smtp_usuario="senda1986.gt@gmail.com")
    assert not config.recuperacion_habilitada
    config.smtp_contrasena = SecretStr("secreto-ficticio-de-prueba")
    assert config.recuperacion_habilitada
    config.smtp_seguridad = "ninguna"
    assert not config.recuperacion_habilitada


def test_gmail_api_usa_https_y_mime_sin_secretos_en_la_url(monkeypatch):
    monkeypatch.setattr(configuracion, "gmail_cliente_id", "cliente-ficticio")
    monkeypatch.setattr(configuracion, "gmail_cliente_secreto", SecretStr("secreto-ficticio"))
    monkeypatch.setattr(configuracion, "gmail_refresh_token", SecretStr("refresh-ficticio"))
    peticiones = []
    def proveedor(peticion, timeout):
        peticiones.append(peticion)
        return BytesIO(json.dumps({"access_token": "acceso-ficticio"} if len(peticiones) == 1 else {"id": "mensaje-ficticio"}).encode())
    monkeypatch.setattr(recuperacion, "urlopen", proveedor)
    mensaje = EmailMessage()
    mensaje["To"] = "persona@example.com"
    mensaje["From"] = "senda1986.gt@gmail.com"
    mensaje.set_content("Mensaje ficticio de recuperación")
    recuperacion.enviar_por_gmail(mensaje)
    assert [p.full_url for p in peticiones] == ["https://oauth2.googleapis.com/token", "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"]
    assert all("ficticio" not in p.full_url for p in peticiones)
    assert peticiones[1].get_header("Authorization") == "Bearer acceso-ficticio"
    contenido = base64.urlsafe_b64decode(json.loads(peticiones[1].data)["raw"])
    assert b"persona@example.com" in contenido


def test_canje_concurrente_solo_permite_un_ganador(tmp_path):
    motor = create_engine(f"sqlite:///{tmp_path / 'concurrencia.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(motor)
    fabrica = sessionmaker(bind=motor)
    with fabrica() as sesion:
        usuario = Usuario(correo="prueba@example.com", nombre="Prueba", contrasena_cifrada="hash-ficticio")
        sesion.add(usuario)
        sesion.flush()
        sesion.add(RecuperacionAcceso(usuario_id=usuario.id, resumen_token=recuperacion.resumen("a" * 43), vence_en=recuperacion.ahora_utc() + timedelta(minutes=15)))
        sesion.commit()
    def intentar(_):
        with fabrica() as sesion:
            try:
                recuperacion.restablecer(sesion, "a" * 43, "NuevaSenda2026")
                return "correcto"
            except recuperacion.EnlaceNoValido:
                return "rechazado"
    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        assert sorted(ejecutor.map(intentar, range(2))) == ["correcto", "rechazado"]
    motor.dispose()
