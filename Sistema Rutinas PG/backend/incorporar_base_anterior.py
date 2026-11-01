"""Incorpora a Alembic una base creada con `create_all` antes de las migraciones.

Caso que resuelve (auditoría final del 31-10-2026): la base de producción se
creó en septiembre con las quince tablas de entonces y sin `alembic_version`.
Al publicar el código nuevo, el arranque ejecutó `create_all`, que añadió las
tablas nuevas —vacías— pero no las columnas nuevas de tablas existentes. Desde
ese momento el acceso falla: `usuarios.version_sesion` no existe.

`adoptar` no sirve, porque la estructura no coincide, y `actualizar` se niega a
tocar tablas sin versión. Este guion comprueba que la base está exactamente en
esa situación y, solo entonces, retira las tablas nuevas vacías, registra la
revisión inicial y aplica las migraciones. Todo ocurre en una transacción.

Uso, desde backend, con la conexión de la base que se va a incorporar:

    uv run python incorporar_base_anterior.py              # solo diagnostica
    uv run python incorporar_base_anterior.py --confirmar  # aplica

Antes de confirmar: respaldar la base, restaurar el respaldo en otra base y
ensayar ahí. No borra datos: se detiene si alguna tabla nueva tiene filas.
"""

import argparse
import sys

from alembic import command
from sqlalchemy import create_engine, inspect, text

import app.modelos  # noqa: F401  registra las entidades
from app.nucleo import migraciones
from app.nucleo.base_datos import Base
from app.nucleo.configuracion import configuracion

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


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--confirmar", action="store_true", help="aplica los cambios; sin esto solo diagnostica")
    opciones = argumentos.parse_args()
    motor = create_engine(configuracion.url_base_datos)
    try:
        with motor.begin() as conexion:
            for paso in incorporar(conexion, opciones.confirmar):
                print(paso)
        if not opciones.confirmar:
            print("Diagnóstico sin cambios. Respalde, ensaye en una copia y repita con --confirmar.")
        return 0
    except BaseNoReconocida as error:
        print(f"No se hizo ningún cambio: {error}", file=sys.stderr)
        return 1
    finally:
        motor.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
