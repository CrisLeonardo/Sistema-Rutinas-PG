"""Migraciones y adopcion sin perdida de datos, con SQLite y PostgreSQL opcional.

URL_POSTGRESQL_PRUEBAS solo admite un PostgreSQL local de fase 0. Cada prueba
usa su propio esquema y nunca comparte las tablas de una base real del sistema.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4

import pytest
from alembic import command
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

from app.nucleo.base_datos import Base
from app.modelos.recuperacion import RecuperacionAcceso
from app.modelos.usuario import Usuario
from app.servicios import recuperacion
from app.nucleo.migraciones import (
    REVISION_ACTUAL,
    REVISION_INICIAL,
    EsquemaNoCompatible,
    actualizar,
    adoptar,
    configurar,
    diferencias,
    revision_actual,
)


@pytest.fixture(params=["sqlite", "postgresql"])
def conexion_migraciones(request):
    if request.param == "sqlite":
        motor = create_engine("sqlite:///:memory:")
        with motor.begin() as conexion:
            yield conexion
        motor.dispose()
        return

    url = os.getenv("URL_POSTGRESQL_PRUEBAS")
    if not url:
        pytest.skip("Defina URL_POSTGRESQL_PRUEBAS para comprobar PostgreSQL local.")
    destino = make_url(url)
    if destino.host not in {"127.0.0.1", "localhost"} or not (destino.database or "").startswith("senda_fase0"):
        pytest.fail("Las pruebas de migracion solo admiten la base local senda_fase0.")
    esquema = f"fase0_test_{uuid4().hex}"
    administrador = create_engine(url, poolclass=NullPool)
    with administrador.begin() as conexion:
        conexion.exec_driver_sql(f'CREATE SCHEMA "{esquema}"')
    motor = create_engine(
        url, poolclass=NullPool,
        connect_args={"options": f"-csearch_path={esquema}", "prepare_threshold": None},
    )
    try:
        with motor.begin() as conexion:
            yield conexion
    finally:
        motor.dispose()
        # El nombre se genera aqui y nunca proviene de argumentos del usuario.
        assert esquema.startswith("fase0_test_") and esquema.removeprefix("fase0_test_").isalnum()
        with administrador.begin() as conexion:
            conexion.exec_driver_sql(f'DROP SCHEMA "{esquema}" CASCADE')
        administrador.dispose()


def test_crea_el_esquema_completo_desde_cero(conexion_migraciones):
    conexion = conexion_migraciones
    assert actualizar(conexion) == REVISION_ACTUAL
    assert set(inspect(conexion).get_table_names()) == set(Base.metadata.tables) | {"alembic_version"}
    assert diferencias(conexion) == []


def test_adopta_una_base_existente_sin_modificar_sus_datos(conexion_migraciones):
    conexion = conexion_migraciones
    Base.metadata.create_all(conexion)
    usuarios = Base.metadata.tables["usuarios"]
    conexion.execute(usuarios.insert().values(
        correo="ficticio@example.com", nombre="Persona de prueba", contrasena_cifrada="hash-ficticio"
    ))
    antes = conexion.execute(usuarios.select()).all()
    assert adoptar(conexion) == REVISION_ACTUAL
    assert conexion.execute(usuarios.select()).all() == antes
    assert diferencias(conexion) == []


def test_repetir_la_actualizacion_no_cambia_la_revision(conexion_migraciones):
    conexion = conexion_migraciones
    actualizar(conexion)
    assert actualizar(conexion) == REVISION_ACTUAL
    assert conexion.execute(text("SELECT count(*) FROM alembic_version")).scalar_one() == 1


def test_repetir_la_adopcion_es_idempotente(conexion_migraciones):
    conexion = conexion_migraciones
    Base.metadata.create_all(conexion)
    adoptar(conexion)
    assert adoptar(conexion) == REVISION_ACTUAL


def test_no_actualiza_a_ciegas_una_base_existente_sin_version(conexion_migraciones):
    conexion = conexion_migraciones
    Base.metadata.create_all(conexion)
    with pytest.raises(EsquemaNoCompatible, match="sin revision"):
        actualizar(conexion)
    assert revision_actual(conexion) is None


def test_rechaza_adoptar_una_base_vacia(conexion_migraciones):
    conexion = conexion_migraciones
    with pytest.raises(EsquemaNoCompatible, match="diferencias"):
        adoptar(conexion)
    assert "alembic_version" not in inspect(conexion).get_table_names()


def test_rechaza_adoptar_si_falta_una_columna(conexion_migraciones):
    conexion = conexion_migraciones
    Base.metadata.create_all(conexion)
    conexion.exec_driver_sql("ALTER TABLE usuarios DROP COLUMN nombre")
    with pytest.raises(EsquemaNoCompatible, match="diferencias"):
        adoptar(conexion)
    assert revision_actual(conexion) is None


def test_rechaza_adoptar_si_falta_el_indice_unico_del_correo(conexion_migraciones):
    conexion = conexion_migraciones
    Base.metadata.create_all(conexion)
    conexion.exec_driver_sql("DROP INDEX ix_usuarios_correo")
    with pytest.raises(EsquemaNoCompatible, match="diferencias"):
        adoptar(conexion)
    assert revision_actual(conexion) is None


def test_rechaza_adoptar_si_cambia_un_tipo_enumerado(conexion_migraciones):
    conexion = conexion_migraciones
    if conexion.dialect.name != "postgresql":
        pytest.skip("SQLite no tiene tipos enumerados nativos.")
    Base.metadata.create_all(conexion)
    conexion.exec_driver_sql("ALTER TYPE rolusuario ADD VALUE 'rol_ajeno'")
    with pytest.raises(EsquemaNoCompatible, match="diferencias"):
        adoptar(conexion)


def test_reversion_y_recreacion_de_una_base_desechable(conexion_migraciones):
    conexion = conexion_migraciones
    actualizar(conexion)
    command.downgrade(configurar(conexion), "base")
    assert set(inspect(conexion).get_table_names()) == {"alembic_version"}
    assert actualizar(conexion) == REVISION_ACTUAL
    assert diferencias(conexion) == []


def test_actualiza_una_base_fase0_poblada_sin_perder_cuentas(conexion_migraciones):
    conexion = conexion_migraciones
    command.upgrade(configurar(conexion), REVISION_INICIAL)
    conexion.execute(text("INSERT INTO usuarios (correo, nombre, contrasena_cifrada, rol, activo) VALUES (:correo, :nombre, :clave, :rol, :activo)"), {
        "correo": "ficticio@example.com", "nombre": "Persona ficticia",
        "clave": "hash-conservado", "rol": "usuario", "activo": True,
    })
    assert actualizar(conexion) == REVISION_ACTUAL
    cuenta = conexion.execute(text("SELECT nombre, contrasena_cifrada, version_sesion FROM usuarios WHERE correo='ficticio@example.com'")).one()
    assert tuple(cuenta) == ("Persona ficticia", "hash-conservado", 0)
    assert diferencias(conexion) == []


def test_canje_concurrente_postgresql_en_esquema_aislado(conexion_migraciones):
    conexion = conexion_migraciones
    if conexion.dialect.name != "postgresql":
        pytest.skip("El canje concurrente SQLite se comprueba con una base de archivo independiente.")
    actualizar(conexion)
    tabla = Base.metadata.tables["usuarios"]
    identificador = conexion.execute(tabla.insert().values(correo="ficticio@example.com", nombre="Prueba", contrasena_cifrada="hash-ficticio").returning(tabla.c.id)).scalar_one()
    conexion.execute(RecuperacionAcceso.__table__.insert().values(usuario_id=identificador, resumen_token=recuperacion.resumen("a" * 43), vence_en=recuperacion.ahora_utc() + timedelta(minutes=15)))
    conexion.commit()
    fabrica = sessionmaker(bind=conexion.engine)
    def intentar(_):
        with fabrica() as sesion:
            try:
                recuperacion.restablecer(sesion, "a" * 43, "NuevaSenda2026")
                return "correcto"
            except recuperacion.EnlaceNoValido:
                return "rechazado"
    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        assert sorted(ejecutor.map(intentar, range(2))) == ["correcto", "rechazado"]
    with fabrica() as sesion:
        assert sesion.get(Usuario, identificador).version_sesion == 1
