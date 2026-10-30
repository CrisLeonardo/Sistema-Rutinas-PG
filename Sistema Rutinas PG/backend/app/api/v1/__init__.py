"""Version 1 de la interfaz de programacion de aplicaciones."""

from fastapi import APIRouter

from app.api.v1 import (
    administracion,
    comunidad,
    alimentacion,
    autenticacion,
    catalogos,
    entrenamiento,
    informes,
    juego,
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
enrutador_v1.include_router(alimentacion.enrutador)
enrutador_v1.include_router(rutinas.enrutador)
enrutador_v1.include_router(progreso.enrutador)
enrutador_v1.include_router(entrenamiento.enrutador)
enrutador_v1.include_router(juego.enrutador)
enrutador_v1.include_router(informes.enrutador)
enrutador_v1.include_router(catalogos.enrutador)
enrutador_v1.include_router(administracion.enrutador)

from app.nucleo.configuracion import configuracion
enrutador_v1.include_router(comunidad.enrutador, include_in_schema=configuracion.comunidad_habilitada)

__all__ = ["enrutador_v1"]
