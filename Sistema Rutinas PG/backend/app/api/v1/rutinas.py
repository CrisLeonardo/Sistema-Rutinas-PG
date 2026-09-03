"""Controlador de la rutina de entrenamiento (historia HU-07).

La rutina se genera junto con el plan nutricional, de modo que aqui solo se
consulta. Como el resto de las rutas del usuario deportista, opera siempre sobre
la cuenta que inicio sesion.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.rutina import (
    EjercicioRutinaPublico,
    RutinaPublica,
    SesionRutinaPublica,
)
from app.modelos.perfil import PerfilBiometrico
from app.modelos.plan import Plan, SesionEntrenamiento
from app.servicios import plan as servicio_plan

enrutador = APIRouter(prefix="/rutina", tags=["Rutina de entrenamiento"])

_SIN_RUTINA = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Todavía no tiene una rutina. Genere su plan para obtenerla.",
)


def _componer(sesion: SesionBD, plan: Plan) -> RutinaPublica:
    """Arma la respuesta a partir de las sesiones almacenadas con el plan."""
    sentencia = (
        select(SesionEntrenamiento)
        .where(SesionEntrenamiento.plan_id == plan.id)
        .options(selectinload(SesionEntrenamiento.ejercicios))
        .order_by(SesionEntrenamiento.dia)
    )
    almacenadas = list(sesion.execute(sentencia).scalars())
    if not almacenadas:
        raise _SIN_RUTINA

    perfil = sesion.get(PerfilBiometrico, plan.perfil_id)

    sesiones = []
    for entidad in almacenadas:
        ejercicios = [
            EjercicioRutinaPublico(
                ejercicio_id=prescrito.ejercicio_id,
                nombre=prescrito.ejercicio.nombre,
                grupo_muscular=prescrito.ejercicio.grupo_muscular,
                equipamiento=prescrito.ejercicio.equipamiento,
                descripcion=prescrito.ejercicio.descripcion,
                orden=prescrito.orden,
                series=prescrito.series,
                repeticiones_min=prescrito.repeticiones_min,
                repeticiones_max=prescrito.repeticiones_max,
                repeticiones_en_reserva=prescrito.repeticiones_en_reserva,
                descanso_segundos=prescrito.descanso_segundos,
            )
            for prescrito in sorted(entidad.ejercicios, key=lambda e: e.orden)
        ]
        sesiones.append(
            SesionRutinaPublica(
                id=entidad.id,
                dia=entidad.dia,
                grupo_muscular=entidad.grupo_muscular,
                ejercicios=ejercicios,
            )
        )

    return RutinaPublica(
        plan_id=plan.id,
        fecha_generacion=plan.fecha_generacion,
        activo=plan.activo,
        dias_entrenamiento_semana=perfil.dias_entrenamiento_semana,
        series_objetivo_por_grupo=servicio_plan.volumen_de_referencia(perfil),
        nivel_experiencia=perfil.nivel_experiencia.value,
        objetivo=perfil.objetivo.value,
        sesiones=sesiones,
    )


@enrutador.get(
    "",
    response_model=RutinaPublica,
    summary="Consultar la rutina semanal vigente",
)
def consultar_vigente(sesion: SesionBD, usuario: UsuarioAutenticado) -> RutinaPublica:
    """Devuelve la rutina asociada al plan vigente (historia HU-07)."""
    plan = servicio_plan.obtener_plan_vigente(sesion, usuario)
    if plan is None:
        raise _SIN_RUTINA
    return _componer(sesion, plan)
