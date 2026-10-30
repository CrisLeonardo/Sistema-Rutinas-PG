"""Control explicito del esquema; nunca migra durante una peticion web.

La adopcion inicial solo registra una base cuyo esquema coincide con los modelos.
No crea, borra ni altera sus tablas de negocio. Alembic registra la revision en
su propia tabla. Una base no versionada con datos no pasa por upgrade a ciegas.
"""

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Enum, inspect

import app.modelos  # noqa: F401
from app.nucleo.base_datos import Base
from app.nucleo.configuracion import RAIZ_BACKEND

REVISION_INICIAL = "0001_esquema_inicial"
REVISION_ACTUAL = "0005_comunidad_privada"


class EsquemaNoCompatible(RuntimeError):
    """La base requiere revision antes de adoptar o actualizar su esquema."""


def configurar(conexion) -> Config:
    configuracion = Config(str(RAIZ_BACKEND / "alembic.ini"))
    configuracion.attributes["connection"] = conexion
    return configuracion


def revision_actual(conexion) -> str | None:
    contexto = MigrationContext.configure(conexion)
    revisiones = contexto.get_current_heads()
    if len(revisiones) > 1:
        raise EsquemaNoCompatible("La base tiene varias revisiones activas; revise sus ramas.")
    return revisiones[0] if revisiones else None


def diferencias(conexion) -> list:
    """Compara estructura, valores por defecto, claves y enumeraciones nativas."""
    contexto = MigrationContext.configure(
        conexion, opts={"compare_type": True, "compare_server_default": True}
    )
    cambios = list(compare_metadata(contexto, Base.metadata))
    inspector = inspect(conexion)
    existentes = set(inspector.get_table_names())
    for tabla in Base.metadata.sorted_tables:
        if tabla.name not in existentes:
            continue
        primaria = inspector.get_pk_constraint(tabla.name)["constrained_columns"]
        esperada = [columna.name for columna in tabla.primary_key.columns]
        if primaria != esperada:
            cambios.append(("clave_primaria", tabla.name, primaria, esperada))

    # Alembic no detecta por si solo cambios de valores de un ENUM PostgreSQL.
    if conexion.dialect.name == "postgresql":
        enumeraciones = {tipo["name"]: tipo["labels"] for tipo in inspector.get_enums()}
        esperadas = {
            columna.type.name: columna.type.enums
            for tabla in Base.metadata.tables.values()
            for columna in tabla.columns
            if isinstance(columna.type, Enum) and columna.type.native_enum
        }
        for nombre, valores in esperadas.items():
            if nombre in enumeraciones and enumeraciones[nombre] != valores:
                cambios.append(("valores_enumerados", nombre, enumeraciones[nombre], valores))
    return cambios


def adoptar(conexion) -> str:
    """Incorpora solo una base que ya coincide exactamente con esta versión.

    Para una base antigua sin versión se usa primero el código de fase 0 para
    adoptar 0001; después se aplica actualizar con el código nuevo.
    """
    configuracion = configurar(conexion)
    if ScriptDirectory.from_config(configuracion).get_current_head() != REVISION_ACTUAL:
        raise EsquemaNoCompatible(
            "El historial no corresponde a la versión de adopción. "
            "Use el codigo de esa version para incorporar una base antigua."
        )
    actual = revision_actual(conexion)
    if actual not in (None, REVISION_ACTUAL):
        raise EsquemaNoCompatible("La revision registrada no corresponde a esta version.")
    cambios = diferencias(conexion)
    if cambios:
        raise EsquemaNoCompatible(
            f"No se adopto la base: hay {len(cambios)} diferencias de estructura. "
            "Ejecute gestionar_esquema.py comprobar y revise las diferencias."
        )
    if actual is None:
        command.stamp(configuracion, REVISION_ACTUAL)
    return REVISION_ACTUAL


def actualizar(conexion) -> str:
    """Crea una base vacia o aplica revisiones pendientes a una ya versionada."""
    actual = revision_actual(conexion)
    tablas = set(inspect(conexion).get_table_names()) - {"alembic_version"}
    if actual is None and tablas:
        raise EsquemaNoCompatible(
            "La base tiene tablas sin revision. Respalde y use adoptar antes de actualizar."
        )
    configuracion = configurar(conexion)
    command.upgrade(configuracion, "head")
    return revision_actual(conexion)
