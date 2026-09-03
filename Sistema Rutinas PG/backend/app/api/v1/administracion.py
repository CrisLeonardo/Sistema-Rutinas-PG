"""Operaciones de administracion del sistema (apartado 3.8).

Reservadas al administrador. Permiten recargar el modelo neuronal sin detener el
servicio, que es lo que exige el requerimiento no funcional 4.5.6, y consultar
las metricas del modelo en operacion.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.dependencias import Administrador, SesionBD
from app.nucleo.configuracion import configuracion
from app.servicios import catalogo as servicio_catalogo
from app.servicios import plan as servicio_plan

enrutador = APIRouter(prefix="/administracion", tags=["Administracion del sistema"])


class EstadoModelo(BaseModel):
    """Situacion del modelo neuronal en el proceso que atiende las peticiones."""

    modelo_cargado: bool
    origen_de_los_planes: str
    metricas: dict | None = None


class EstadoSistema(BaseModel):
    """Resumen operativo para el administrador."""

    entorno: str
    version: str
    credenciales_pendientes: list[str]
    alimentos_disponibles: int
    ejercicios_disponibles: int
    modelo: EstadoModelo


@enrutador.get(
    "/estado",
    response_model=EstadoSistema,
    summary="Consultar el estado operativo del sistema",
)
def consultar_estado(sesion: SesionBD, administrador: Administrador) -> EstadoSistema:
    """Reune lo que el administrador necesita revisar antes y despues de desplegar."""
    motor = servicio_plan.obtener_motor()
    ejercicios = servicio_catalogo.contar_ejercicios_por_grupo(sesion)

    return EstadoSistema(
        entorno=configuracion.entorno,
        version=configuracion.version,
        credenciales_pendientes=configuracion.credenciales_predeterminadas(),
        alimentos_disponibles=servicio_catalogo.contar_alimentos_disponibles(sesion),
        ejercicios_disponibles=sum(ejercicios.values()),
        modelo=EstadoModelo(
            modelo_cargado=motor is not None,
            origen_de_los_planes=(
                servicio_plan.ORIGEN_RED_NEURONAL
                if motor is not None
                else servicio_plan.ORIGEN_FORMULA
            ),
            metricas=motor.metricas if motor is not None else None,
        ),
    )


@enrutador.post(
    "/modelo/recargar",
    response_model=EstadoModelo,
    summary="Recargar el modelo neuronal sin detener el servicio",
)
def recargar_modelo(administrador: Administrador) -> EstadoModelo:
    """Vuelve a leer del disco el modelo entrenado (requerimiento 4.5.6).

    Permite poner en operacion un reentrenamiento sin interrumpir el servicio:
    se ejecuta `entrenar_modelo.py`, que sobrescribe el archivo, y despues se
    invoca esta ruta para que el proceso tome la version nueva.
    """
    servicio_plan.reiniciar_motor()
    motor = servicio_plan.obtener_motor()

    if motor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "No fue posible cargar el modelo. Verifique que se haya entrenado con "
                "«uv run python entrenar_modelo.py». Mientras tanto, los planes se "
                "calculan con las fórmulas de referencia."
            ),
        )

    return EstadoModelo(
        modelo_cargado=True,
        origen_de_los_planes=servicio_plan.ORIGEN_RED_NEURONAL,
        metricas=motor.metricas,
    )
