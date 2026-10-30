"""Entorno de Alembic; reutiliza la configuracion y los modelos del sistema."""

from alembic import context

import app.modelos  # noqa: F401
from app.nucleo.base_datos import Base, motor

configuracion = context.config


def ejecutar(conexion):
    context.configure(
        connection=conexion,
        target_metadata=Base.metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(
        url=str(motor.url),
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    conexion = configuracion.attributes.get("connection")
    if conexion is not None:
        ejecutar(conexion)
    else:
        with motor.connect() as conexion:
            ejecutar(conexion)
