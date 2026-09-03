"""Conexion a la base de datos MySQL y sesion de trabajo por peticion."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.nucleo.configuracion import configuracion

motor = create_engine(
    configuracion.url_base_datos,
    pool_pre_ping=True,
    pool_recycle=3600,
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
