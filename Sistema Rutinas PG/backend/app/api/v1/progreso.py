"""Controlador del seguimiento y los reportes (historias HU-09 y HU-10).

Todas las rutas operan sobre la cuenta que inicio sesion: el progreso es un dato
biometrico y, por la regla del negocio *f* del apartado 4.3.4, solo es visible
para su titular.
"""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.progreso import (
    ComparacionPlanes,
    PuntoEvolucion,
    RegistroProgresoEntrada,
    RegistroProgresoPublico,
    ReporteEvolucion,
    RespuestaProgreso,
)
from app.servicios import perfil as servicio_perfil
from app.servicios import plan as servicio_plan
from app.servicios import progreso as servicio_progreso

enrutador = APIRouter(prefix="/progreso", tags=["Seguimiento y reportes"])

_SIN_PLAN = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail=(
        "Para registrar su avance primero necesita un plan. Genere su plan de "
        "alimentación y entrenamiento."
    ),
)


@enrutador.post(
    "",
    response_model=RespuestaProgreso,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar el avance de la semana",
)
def registrar(
    datos: RegistroProgresoEntrada,
    sesion: SesionBD,
    usuario: UsuarioAutenticado,
) -> RespuestaProgreso:
    """Guarda el avance y reajusta el plan cuando corresponde (historia HU-09).

    La respuesta explica siempre qué hizo el sistema, para que el reajuste no
    ocurra en silencio.
    """
    try:
        registro, reajuste = servicio_progreso.registrar_progreso(sesion, usuario, datos)
    except servicio_progreso.SinPlanVigente:
        raise _SIN_PLAN from None
    except servicio_perfil.PerfilNoRegistrado:
        raise _SIN_PLAN from None

    return RespuestaProgreso(
        registro=RegistroProgresoPublico.model_validate(registro),
        reajuste=reajuste,
    )


@enrutador.get(
    "",
    response_model=list[RegistroProgresoPublico],
    summary="Consultar el historial de avance",
)
def consultar_historial(
    sesion: SesionBD, usuario: UsuarioAutenticado
) -> list[RegistroProgresoPublico]:
    """Devuelve los registros del usuario, del más antiguo al más reciente."""
    return [
        RegistroProgresoPublico.model_validate(registro)
        for registro in servicio_progreso.listar_progreso(sesion, usuario)
    ]


@enrutador.get(
    "/reporte",
    response_model=ReporteEvolucion,
    summary="Consultar el reporte de evolución",
)
def consultar_reporte(sesion: SesionBD, usuario: UsuarioAutenticado) -> ReporteEvolucion:
    """Entrega los datos con que la interfaz dibuja las gráficas (historia HU-10).

    El cálculo de los agregados se hace en el servidor para que la interfaz solo
    tenga que dibujar, y para que las cifras del reporte sean las mismas
    cualquiera que sea el dispositivo desde el que se consulten.
    """
    registros = servicio_progreso.listar_progreso(sesion, usuario)
    puntos = [
        PuntoEvolucion(
            fecha=registro.fecha_registro,
            peso_kg=float(registro.peso_kg),
            perimetro_cintura_cm=(
                float(registro.perimetro_cintura_cm)
                if registro.perimetro_cintura_cm is not None
                else None
            ),
            sesiones_cumplidas=registro.sesiones_cumplidas,
            adherencia_nutricional=registro.adherencia_nutricional,
        )
        for registro in registros
    ]

    inicial = servicio_progreso.obtener_plan_inicial(sesion, usuario)
    vigente = servicio_plan.obtener_plan_vigente(sesion, usuario)
    comparacion = None
    if inicial is not None and vigente is not None:
        comparacion = ComparacionPlanes(
            plan_id_inicial=inicial.id,
            plan_id_vigente=vigente.id,
            calorias_inicial=float(inicial.calorias_objetivo),
            calorias_vigente=float(vigente.calorias_objetivo),
            proteina_inicial=float(inicial.proteina_g),
            proteina_vigente=float(vigente.proteina_g),
            carbohidrato_inicial=float(inicial.carbohidrato_g),
            carbohidrato_vigente=float(vigente.carbohidrato_g),
            grasa_inicial=float(inicial.grasa_g),
            grasa_vigente=float(vigente.grasa_g),
            fecha_inicial=inicial.fecha_generacion,
            fecha_vigente=vigente.fecha_generacion,
        )

    return ReporteEvolucion(puntos=puntos, comparacion_planes=comparacion)
