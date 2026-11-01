"""Incorporación de una base creada con `create_all` antes de Alembic (auditoría final)."""

import os
from uuid import uuid4

import pytest
from alembic import command
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

import incorporar_base_anterior as guion
from app.nucleo import migraciones
from app.nucleo.base_datos import Base


@pytest.fixture(params=["sqlite", "postgresql"])
def base_de_septiembre(request):
    """Quince tablas sin versión y luego el arranque del código nuevo, como producción."""
    if request.param == "sqlite":
        motor = create_engine("sqlite:///:memory:", poolclass=None)
        esquema = None
    else:
        url = os.getenv("URL_POSTGRESQL_PRUEBAS")
        if not url:
            pytest.skip("Defina URL_POSTGRESQL_PRUEBAS para comprobar PostgreSQL local.")
        destino = make_url(url)
        if destino.host not in {"127.0.0.1", "localhost"} or not (destino.database or "").startswith("senda_fase0"):
            pytest.fail("Solo se admite la base local senda_fase0.")
        esquema = f"fase0_test_{uuid4().hex}"
        administrador = create_engine(url, poolclass=NullPool)
        with administrador.begin() as conexion:
            conexion.exec_driver_sql(f'CREATE SCHEMA "{esquema}"')
        motor = create_engine(url, poolclass=NullPool,
                              connect_args={"options": f"-csearch_path={esquema}", "prepare_threshold": None})
    with motor.connect() as conexion:
        with conexion.begin():
            command.upgrade(migraciones.configurar(conexion), migraciones.REVISION_INICIAL)
            conexion.exec_driver_sql("DROP TABLE alembic_version")
            conexion.execute(text("INSERT INTO usuarios (correo, contrasena_cifrada, nombre, rol, activo) "
                                  "VALUES ('persona@ejemplo.gt', 'x', 'Persona', 'usuario', true)"))
        with conexion.begin():
            Base.metadata.create_all(bind=conexion)
        yield conexion
    motor.dispose()
    if esquema:
        assert esquema.startswith("fase0_test_") and esquema.removeprefix("fase0_test_").isalnum()
        with administrador.begin() as conexion:
            conexion.exec_driver_sql(f'DROP SCHEMA "{esquema}" CASCADE')
        administrador.dispose()


def test_diagnostica_sin_cambiar_nada(base_de_septiembre):
    conexion = base_de_septiembre
    with conexion.begin():
        pasos = guion.incorporar(conexion, confirmar=False)
    assert "usuarios.version_sesion" in pasos[0]
    with conexion.begin():
        assert migraciones.revision_actual(conexion) is None
        assert "version_sesion" not in {c["name"] for c in inspect(conexion).get_columns("usuarios")}


def test_incorpora_la_base_y_conserva_las_cuentas(base_de_septiembre):
    conexion = base_de_septiembre
    with conexion.begin():
        guion.incorporar(conexion, confirmar=True)
    with conexion.begin():
        assert migraciones.revision_actual(conexion) == migraciones.REVISION_ACTUAL
        assert migraciones.diferencias(conexion) == []
        assert conexion.execute(text("SELECT correo, version_sesion FROM usuarios")).one() == ("persona@ejemplo.gt", 0)


def test_no_retira_una_tabla_nueva_con_filas(base_de_septiembre):
    conexion = base_de_septiembre
    with conexion.begin():
        conexion.execute(text("INSERT INTO preferencias_alimentarias (usuario_id, datos) VALUES (1, '{}')"))
    with pytest.raises(guion.BaseNoReconocida, match="preferencias_alimentarias"):
        with conexion.begin():
            guion.incorporar(conexion, confirmar=True)
    with conexion.begin():
        assert migraciones.revision_actual(conexion) is None
