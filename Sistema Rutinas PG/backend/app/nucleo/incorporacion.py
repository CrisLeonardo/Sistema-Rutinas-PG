"""Incorporación a Alembic de una base creada con `create_all` (auditoría final).

La base de producción se creó en septiembre de 2026 con las quince tablas de
entonces y sin `alembic_version`. Al publicar el código nuevo, `create_all` le
añadió las tablas nuevas —vacías— pero no las columnas nuevas de tablas
existentes, y el acceso falla porque `usuarios.version_sesion` no existe. Este
módulo reconoce exactamente esa situación y la resuelve en una transacción:
retira las tablas nuevas vacías, registra la revisión inicial y aplica las
migraciones. Ante cualquier otra diferencia se detiene sin cambiar nada.
"""

from alembic import command
from sqlalchemy import inspect, text

import app.modelos  # noqa: F401  registra las entidades
from app.nucleo import migraciones
from app.nucleo.base_datos import Base

# Tablas que las revisiones 0002, 0003 y 0005 crean, en orden de dependencias.
TABLAS_NUEVAS = (
    "recuperaciones_acceso",
    "preferencias_alimentarias",
    "semanas_alimentarias",
    "grupos_privados",
    "miembros_privados",
    "invitaciones_privadas",
    "semanas_privadas",
    "eventos_constancia",
    "bloqueos_privados",
    "denuncias_privadas",
)
# Columnas que las revisiones 0002 y 0004 agregan a tablas existentes.
COLUMNAS_NUEVAS = {
    ("usuarios", "version_sesion"),
    ("ejercicios_sesion", "duracion_segundos_min"),
    ("ejercicios_sesion", "duracion_segundos_max"),
    ("series_realizadas", "duracion_segundos"),
}


class BaseNoReconocida(RuntimeError):
    """La base no está en la situación que este guion sabe resolver."""


def _columnas_faltantes(conexion) -> set[tuple[str, str]]:
    faltantes = set()
    for cambio in migraciones.diferencias(conexion):
        if isinstance(cambio, tuple) and cambio[0] == "add_column":
            faltantes.add((cambio[2], cambio[3].name))
        else:
            raise BaseNoReconocida(f"Diferencia no prevista: {cambio!r}. Revise con gestionar_esquema.py comprobar.")
    return faltantes


def incorporar(conexion, confirmar: bool) -> list[str]:
    """Diagnostica y, si `confirmar`, incorpora. Devuelve lo que hizo o haría."""
    if migraciones.revision_actual(conexion) is not None:
        raise BaseNoReconocida("La base ya tiene revisión. Use gestionar_esquema.py actualizar.")
    existentes = set(inspect(conexion).get_table_names())
    faltan_tablas = set(Base.metadata.tables) - set(TABLAS_NUEVAS) - existentes
    if faltan_tablas:
        raise BaseNoReconocida(f"Faltan tablas originales: {sorted(faltan_tablas)}.")
    faltantes = _columnas_faltantes(conexion)
    if not faltantes:
        raise BaseNoReconocida("No faltan columnas: use gestionar_esquema.py adoptar.")
    if not faltantes <= COLUMNAS_NUEVAS:
        raise BaseNoReconocida(f"Faltan columnas no previstas: {sorted(faltantes - COLUMNAS_NUEVAS)}.")

    pasos = [f"Faltan {len(faltantes)} columnas: {', '.join(f'{t}.{c}' for t, c in sorted(faltantes))}."]
    for tabla in TABLAS_NUEVAS:
        if tabla in existentes:
            filas = conexion.execute(text(f'SELECT count(*) FROM "{tabla}"')).scalar_one()
            if filas:
                raise BaseNoReconocida(f"La tabla {tabla} tiene {filas} filas; no se retira. Revise a mano.")
            pasos.append(f"Retirar la tabla vacía {tabla}.")
    pasos.append(f"Registrar {migraciones.REVISION_INICIAL} y actualizar hasta {migraciones.REVISION_ACTUAL}.")
    if not confirmar:
        return pasos

    for tabla in reversed(TABLAS_NUEVAS):
        if tabla in existentes:
            conexion.exec_driver_sql(f'DROP TABLE "{tabla}"')
    command.stamp(migraciones.configurar(conexion), migraciones.REVISION_INICIAL)
    revision = migraciones.actualizar(conexion)
    restantes = migraciones.diferencias(conexion)
    if restantes:
        raise BaseNoReconocida(f"Quedaron {len(restantes)} diferencias; se revierte la transacción.")
    pasos.append(f"Revisión aplicada: {revision}. Diferencias de estructura: 0.")
    return pasos


def es_base_anterior(conexion) -> bool:
    """Comprobación rápida, sin escribir: base sin versión a la que le faltan columnas nuevas."""
    inspector = inspect(conexion)
    tablas = set(inspector.get_table_names())
    if "alembic_version" in tablas or "usuarios" not in tablas:
        return False
    return any(
        tabla in tablas and columna not in {c["name"] for c in inspector.get_columns(tabla)}
        for tabla, columna in COLUMNAS_NUEVAS
    )
