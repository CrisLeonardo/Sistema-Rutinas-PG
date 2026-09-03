"""Version 1 de la interfaz de programacion de aplicaciones."""

from fastapi import APIRouter

from app.api.v1 import (
    administracion,
    autenticacion,
    catalogos,
    perfiles,
    planes,
    progreso,
    rutinas,
    usuarios,
)

enrutador_v1 = APIRouter(prefix="/api/v1")
enrutador_v1.include_router(autenticacion.enrutador)
enrutador_v1.include_router(usuarios.enrutador)
enrutador_v1.include_router(perfiles.enrutador)
enrutador_v1.include_router(planes.enrutador)
enrutador_v1.include_router(rutinas.enrutador)
enrutador_v1.include_router(progreso.enrutador)
enrutador_v1.include_router(catalogos.enrutador)
enrutador_v1.include_router(administracion.enrutador)

__all__ = ["enrutador_v1"]
