"""Punto de entrada de la interfaz de programacion de aplicaciones.

Expone los servicios del sistema de generacion de planes nutricionales y
rutinas de entrenamiento descrito en el Capitulo IV del proyecto de graduacion.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
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


# La documentacion interactiva describe todas las rutas, sus contratos y sus
# reglas de validacion. Es una herramienta de desarrollo: publicarla en
# produccion le entrega a cualquiera el mapa completo de la interfaz, incluidas
# las rutas reservadas al administrador. Se sirve fuera de produccion.
_EXPONE_DOCUMENTACION = not configuracion.es_produccion

aplicacion = FastAPI(
    title=configuracion.nombre_sistema,
    version=configuracion.version,
    description=(
        "Servicios para el registro de usuarios, la captura del perfil biometrico "
        "y la generacion automatica de planes de nutricion y entrenamiento."
    ),
    lifespan=ciclo_de_vida,
    docs_url="/documentacion" if _EXPONE_DOCUMENTACION else None,
    redoc_url=None,
    openapi_url="/openapi.json" if _EXPONE_DOCUMENTACION else None,
)

# Encabezados de seguridad de las respuestas de la interfaz de programacion.
#
# El sitio estatico ya declara los suyos en `render.yaml` y en `nginx.conf`,
# pero esos no alcanzan a las respuestas del backend: el reenvio las entrega tal
# como el servicio las produce. Sin estos encabezados, una respuesta JSON puede
# interpretarse como HTML si el navegador adivina el tipo, y el servicio puede
# incrustarse en un marco ajeno.
_ENCABEZADOS_DE_SEGURIDAD = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    # La interfaz de programacion solo devuelve JSON: no carga recursos, no
    # ejecuta guiones y no debe poder incrustarse.
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    # Las respuestas llevan datos biometricos: no deben quedar en la memoria
    # intermedia de ningun proxy ni del navegador.
    "Cache-Control": "no-store",
}

# Un ano de HSTS. Solo se declara en produccion, donde el trafico va cifrado:
# en desarrollo obligaria al navegador a insistir con HTTPS contra un servidor
# que responde en texto plano, y la aplicacion dejaria de cargar.
if configuracion.es_produccion:
    _ENCABEZADOS_DE_SEGURIDAD["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )


@aplicacion.middleware("http")
async def anadir_encabezados_de_seguridad(peticion: Request, siguiente) -> Response:
    """Anade a cada respuesta los encabezados de seguridad del servicio."""
    respuesta = await siguiente(peticion)
    for nombre, valor in _ENCABEZADOS_DE_SEGURIDAD.items():
        respuesta.headers.setdefault(nombre, valor)
    return respuesta

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
