"""Conexion a la base de datos PostgreSQL y sesion de trabajo por peticion."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.nucleo.configuracion import configuracion


def _argumentos_de_conexion(url: str) -> dict:
    """Ajusta el controlador a las condiciones del proveedor administrado.

    Supabase no expone la base de datos de forma directa a los servicios que
    salen a internet por IPv4: las conexiones pasan por su repartidor, que en
    modo de transaccion entrega una conexion distinta a cada instruccion. Las
    sentencias preparadas del lado del servidor, que psycopg activa por su
    cuenta a partir de la quinta ejecucion, quedan entonces registradas en una
    conexion y se invocan en otra, y el resultado es un fallo intermitente que
    solo aparece con el sistema en uso.

    Desactivarlas cuesta poco: las consultas del sistema son simples y el
    tiempo de un plan lo domina el computo del modelo, no el analisis de la
    consulta.
    """
    if not url.startswith("postgresql"):
        return {}
    return {"prepare_threshold": None}


motor = create_engine(
    configuracion.url_base_datos,
    # Comprueba la conexion antes de entregarla: el repartidor de Supabase
    # cierra las que llevan tiempo ociosas, y sin esta verificacion la primera
    # peticion despues de un rato tranquilo fallaria.
    pool_pre_ping=True,
    # Cinco minutos, no una hora: el repartidor recicla antes que eso.
    pool_recycle=300,
    pool_size=5,
    max_overflow=5,
    connect_args=_argumentos_de_conexion(configuracion.url_base_datos),
    echo=False,
)

FabricaSesiones = sessionmaker(bind=motor, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Clase base de la que heredan todas las entidades del modelo de datos."""


def obtener_sesion() -> Generator[Session, None, None]:
    """Entrega una sesion de base de datos y garantiza su cierre al terminar."""
    sesion = FabricaSesiones()
    try:
        yield sesion
    finally:
        sesion.close()
