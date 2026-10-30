"""Consulta y administra migraciones con la URL configurada en el entorno.

Ejecutar desde backend: python gestionar_esquema.py estado|comprobar|adoptar|actualizar
Estado y comprobar son de lectura. Las escrituras requieren una accion explicita.
"""

import argparse
import sys

from sqlalchemy.exc import SQLAlchemyError

from app.nucleo.base_datos import motor
from app.nucleo.migraciones import (
    EsquemaNoCompatible,
    actualizar,
    adoptar,
    diferencias,
    revision_actual,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accion", choices=("estado", "comprobar", "adoptar", "actualizar"))
    argumentos = parser.parse_args()
    try:
        with motor.begin() as conexion:
            if argumentos.accion == "estado":
                print(f"Revision actual: {revision_actual(conexion) or 'sin versionar'}")
            elif argumentos.accion == "comprobar":
                cambios = diferencias(conexion)
                for cambio in cambios:
                    print(repr(cambio))
                print(f"Diferencias de estructura: {len(cambios)}")
                return 1 if cambios else 0
            elif argumentos.accion == "adoptar":
                print(f"Revision adoptada: {adoptar(conexion)}")
            else:
                print(f"Revision aplicada: {actualizar(conexion)}")
    except EsquemaNoCompatible as error:
        print(str(error), file=sys.stderr)
        return 1
    except SQLAlchemyError as error:
        # No mostrar una URL ni parametros de consulta que puedan incluir secretos.
        print(f"No se completo la operacion ({type(error).__name__}). Revise la conexion y el esquema.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
