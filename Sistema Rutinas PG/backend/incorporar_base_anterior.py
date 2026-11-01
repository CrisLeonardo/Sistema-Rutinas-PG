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

from sqlalchemy import create_engine

from app.nucleo.configuracion import configuracion
from app.nucleo.incorporacion import (  # noqa: F401  se reexportan para las pruebas
    COLUMNAS_NUEVAS,
    TABLAS_NUEVAS,
    BaseNoReconocida,
    incorporar,
)


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
