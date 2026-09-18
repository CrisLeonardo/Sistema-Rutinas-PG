"""Controlador de la senda: nivel, puntos, insignias y camino recorrido.

Solo hay ruta de lectura. Los puntos se otorgan como consecuencia de registrar
una sesion de gimnasio o de anotar el peso de la semana, dentro de esas mismas
operaciones: una ruta que sumara puntos por si sola convertiria el sistema de
recompensas en un formulario, y lo que el usuario declara sin haberlo hecho no
es progreso.

Como el resto de la bitacora, opera unicamente sobre la cuenta que inicio sesion,
en cumplimiento de la regla del negocio *f* del apartado 4.3.4.
"""

from datetime import date

from fastapi import APIRouter
from sqlalchemy import select

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.juego import EstadoJuego
from app.modelos.plan import SesionEntrenamiento
from app.servicios import juego as servicio
from app.servicios import plan as servicio_plan

enrutador = APIRouter(prefix="/juego", tags=["Senda y recompensas"])


@enrutador.get(
    "",
    response_model=EstadoJuego,
    summary="Consultar la senda del usuario",
)
def consultar_estado(sesion: SesionBD, usuario: UsuarioAutenticado) -> EstadoJuego:
    """Nivel, puntos, insignias y camino recorrido de la cuenta en sesión.

    Lleva también el ánimo con que debe dibujarse la mascota. Se decide aquí y no
    en la interfaz porque depende de la bitácora completa —cuándo fue la última
    sesión, si la racha está en riesgo, si hoy toca entrenar—, que la interfaz no
    tiene.
    """
    return EstadoJuego(
        **servicio.estado(sesion, usuario, toca_sesion_hoy=_toca_sesion_hoy(sesion, usuario))
    )


def _toca_sesion_hoy(sesion: SesionBD, usuario: UsuarioAutenticado) -> bool:
    """Indica si la rutina vigente prescribe una sesión para el día de hoy."""
    plan = servicio_plan.obtener_plan_vigente(sesion, usuario)
    if plan is None:
        return False

    prescrita = sesion.execute(
        select(SesionEntrenamiento.id).where(
            SesionEntrenamiento.plan_id == plan.id,
            SesionEntrenamiento.dia == date.today().isoweekday(),
        )
    ).first()
    return prescrita is not None
