"""Punto de entrada de la interfaz de programacion de aplicaciones.

Expone los servicios del sistema de generacion de planes nutricionales y
rutinas de entrenamiento descrito en el Capitulo IV del proyecto de graduacion.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import enrutador_v1
from app.nucleo.arranque import inicializar
from app.nucleo.configuracion import configuracion

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)


@asynccontextmanager
async def ciclo_de_vida(aplicacion: FastAPI) -> AsyncIterator[None]:
    """Prepara la base de datos antes de atender la primera peticion."""
    inicializar()
    yield


aplicacion = FastAPI(
    title=configuracion.nombre_sistema,
    version=configuracion.version,
    description=(
        "Servicios para el registro de usuarios, la captura del perfil biometrico "
        "y la generacion automatica de planes de nutricion y entrenamiento."
    ),
    lifespan=ciclo_de_vida,
    docs_url="/documentacion",
    redoc_url=None,
    openapi_url="/openapi.json",
)

aplicacion.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.lista_origenes,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

aplicacion.include_router(enrutador_v1)


@aplicacion.get("/api/v1/estado", tags=["Estado"], summary="Verificar disponibilidad")
def estado() -> dict[str, str]:
    """Comprueba que el servicio responde. Util para el monitoreo del despliegue."""
    return {
        "estado": "disponible",
        "sistema": configuracion.nombre_sistema,
        "version": configuracion.version,
    }
