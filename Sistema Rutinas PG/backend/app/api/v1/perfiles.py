"""Controlador del perfil biometrico (historias HU-04 y HU-05).

Todas las rutas operan sobre la cuenta que inicio sesion. No existe ninguna
ruta que permita consultar el perfil de otra persona, ni siquiera al
administrador, en cumplimiento de la regla del negocio *f* del apartado 4.3.4.
"""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.perfil import PerfilBiometricoPublico, RegistroPerfilBiometrico
from app.servicios import perfil as servicio_perfil

enrutador = APIRouter(prefix="/perfil-biometrico", tags=["Perfil biometrico"])

_SIN_PERFIL = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Todavía no ha registrado sus medidas. Complete su perfil biométrico.",
)


@enrutador.post(
    "",
    response_model=PerfilBiometricoPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar o actualizar las medidas del perfil biometrico",
)
def registrar(
    datos: RegistroPerfilBiometrico,
    sesion: SesionBD,
    usuario: UsuarioAutenticado,
) -> PerfilBiometricoPublico:
    """Guarda una medicion nueva del usuario en sesion (historias HU-04 y HU-05).

    Actualizar las medidas no reemplaza la medicion anterior: se agrega un
    registro con su propia fecha, con lo que el historial queda completo.
    """
    guardado = servicio_perfil.registrar_perfil(sesion, usuario, datos)
    return PerfilBiometricoPublico.model_validate(guardado)


@enrutador.get(
    "",
    response_model=PerfilBiometricoPublico,
    summary="Consultar el perfil biometrico vigente",
)
def consultar_vigente(sesion: SesionBD, usuario: UsuarioAutenticado) -> PerfilBiometricoPublico:
    """Devuelve la medicion mas reciente de la cuenta en sesion."""
    try:
        vigente = servicio_perfil.obtener_perfil_vigente(sesion, usuario)
    except servicio_perfil.PerfilNoRegistrado:
        raise _SIN_PERFIL from None
    return PerfilBiometricoPublico.model_validate(vigente)


@enrutador.get(
    "/historial",
    response_model=list[PerfilBiometricoPublico],
    summary="Consultar el historial de medidas",
)
def consultar_historial(
    sesion: SesionBD, usuario: UsuarioAutenticado
) -> list[PerfilBiometricoPublico]:
    """Devuelve las mediciones del usuario ordenadas de la mas reciente a la mas antigua."""
    return [
        PerfilBiometricoPublico.model_validate(medicion)
        for medicion in servicio_perfil.listar_historial(sesion, usuario)
    ]
