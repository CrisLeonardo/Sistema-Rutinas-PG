"""Configuracion comun de las pruebas funcionales.

Las pruebas se ejecutan sobre una base de datos independiente y temporal, de modo
que puedan correrse sin afectar los datos del entorno de desarrollo.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.modelos  # noqa: F401  registra las entidades en los metadatos
from app.api.dependencias import obtener_sesion
from app.esquemas.usuario import RegistroUsuario
from app.main import aplicacion
from app.modelos.enumeraciones import RolUsuario
from app.nucleo.base_datos import Base
from app.nucleo.alimentos_iniciales import cargar_alimentos
from app.nucleo.catalogo_inicial import cargar_ejercicios
from app.servicios import autenticacion

CORREO_ADMINISTRADOR = "admin.pruebas@sistemarutinas.gt"
CONTRASENA_ADMINISTRADOR = "Administra2026"


@pytest.fixture(name="fabrica_sesiones")
def fixture_fabrica_sesiones():
    """Crea un esquema limpio en memoria para cada prueba."""
    motor = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=motor)
    fabrica = sessionmaker(bind=motor, autocommit=False, autoflush=False)
    # El catalogo de ejercicios se carga igual que en el arranque real, porque la
    # generacion de rutinas de la historia HU-07 depende de el.
    with fabrica() as sesion:
        cargar_ejercicios(sesion)
        cargar_alimentos(sesion)
    try:
        yield fabrica
    finally:
        Base.metadata.drop_all(bind=motor)
        motor.dispose()


@pytest.fixture(name="cliente")
def fixture_cliente(fabrica_sesiones):
    """Cliente de pruebas con la sesion de base de datos sustituida."""

    def sesion_de_prueba():
        sesion = fabrica_sesiones()
        try:
            yield sesion
        finally:
            sesion.close()

    aplicacion.dependency_overrides[obtener_sesion] = sesion_de_prueba
    # El cliente se construye sin gestor de contexto a proposito: asi no se
    # ejecuta el ciclo de vida de la aplicacion y las pruebas no dependen de
    # que MySQL este levantado.
    try:
        yield TestClient(aplicacion)
    finally:
        aplicacion.dependency_overrides.clear()


@pytest.fixture(name="token_administrador")
def fixture_token_administrador(cliente, fabrica_sesiones) -> str:
    """Crea una cuenta de administrador y devuelve su token de sesion."""
    with fabrica_sesiones() as sesion:
        autenticacion.registrar_usuario(
            sesion,
            RegistroUsuario(
                correo=CORREO_ADMINISTRADOR,
                nombre="Administrador de pruebas",
                contrasena=CONTRASENA_ADMINISTRADOR,
            ),
            rol=RolUsuario.ADMINISTRADOR,
        )

    respuesta = cliente.post(
        "/api/v1/autenticacion/acceso",
        json={"correo": CORREO_ADMINISTRADOR, "contrasena": CONTRASENA_ADMINISTRADOR},
    )
    assert respuesta.status_code == 200
    return respuesta.json()["token_acceso"]


def encabezado(token: str) -> dict[str, str]:
    """Arma el encabezado de autorizacion con el token indicado."""
    return {"Authorization": f"Bearer {token}"}


CORREO_DEPORTISTA = "deportista.pruebas@sistemarutinas.gt"
CONTRASENA_DEPORTISTA = "Entrenamiento2026"


@pytest.fixture(name="token_usuario")
def fixture_token_usuario(cliente) -> str:
    """Crea una cuenta con rol de usuario deportista y devuelve su token de sesion."""
    cliente.post(
        "/api/v1/autenticacion/registro",
        json={
            "correo": CORREO_DEPORTISTA,
            "nombre": "Deportista de pruebas",
            "contrasena": CONTRASENA_DEPORTISTA,
        },
    )
    respuesta = cliente.post(
        "/api/v1/autenticacion/acceso",
        json={"correo": CORREO_DEPORTISTA, "contrasena": CONTRASENA_DEPORTISTA},
    )
    assert respuesta.status_code == 200
    return respuesta.json()["token_acceso"]


@pytest.fixture(name="token_segundo_usuario")
def fixture_token_segundo_usuario(cliente) -> str:
    """Segunda cuenta de deportista, para verificar el aislamiento de los datos."""
    correo = "otro.deportista@sistemarutinas.gt"
    contrasena = "Entrenamiento2027"
    cliente.post(
        "/api/v1/autenticacion/registro",
        json={"correo": correo, "nombre": "Otro deportista", "contrasena": contrasena},
    )
    respuesta = cliente.post(
        "/api/v1/autenticacion/acceso",
        json={"correo": correo, "contrasena": contrasena},
    )
    assert respuesta.status_code == 200
    return respuesta.json()["token_acceso"]
