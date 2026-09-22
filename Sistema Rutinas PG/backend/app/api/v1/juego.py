"""Controlador de la senda: nivel, puntos, insignias y camino recorrido.

Solo hay ruta de lectura. Los puntos se otorgan como consecuencia de registrar
una sesion de gimnasio o de anotar el peso de la semana, dentro de esas mismas
operaciones: una ruta que sumara puntos por si sola convertiria el sistema de
recompensas en un formulario, y lo que el usuario declara sin haberlo hecho no
es progreso.

Como el resto de la bitacora, opera unicamente sobre la cuenta que inicio sesion,
en cumplimiento de la regla del negocio RN-06 del apartado 4.3.4.
"""

from fastapi import APIRouter

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.juego import EstadoJuego
from app.servicios import juego as servicio

enrutador = APIRouter(prefix="/juego", tags=["Senda y recompensas"])


@enrutador.get(
    "",
    response_model=EstadoJuego,
    summary="Consultar la senda del usuario",
)
def consultar_estado(sesion: SesionBD, usuario: UsuarioAutenticado) -> EstadoJuego:
    """Nivel, puntos, insignias y camino recorrido de la cuenta en sesión."""
    return EstadoJuego(**servicio.estado(sesion, usuario))
