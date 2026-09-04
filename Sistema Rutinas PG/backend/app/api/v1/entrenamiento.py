"""Controlador de la bitacora de entrenamiento.

Todas las rutas operan sobre la cuenta que inicio sesion. No existe ninguna que
permita consultar la bitacora de otra persona, ni siquiera para el administrador,
en cumplimiento de la regla del negocio *f* del apartado 4.3.4.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.entrenamiento import (
    EjercicioParaEntrenar,
    HistorialDeEjercicio,
    MarcaPersonal,
    PuntoDeCarga,
    RecomendacionPublica,
    ResumenEntrenamiento,
    RespuestaSesionRegistrada,
    SeriePrevia,
    SesionEjecutadaEntrada,
    SesionParaEntrenar,
    SesionRealizadaPublica,
)
from app.esquemas.rutina import NOMBRES_GRUPO
from app.modelos.catalogo import Ejercicio
from app.modelos.plan import EjercicioSesion, Plan, SesionEntrenamiento
from app.motor.progresion import Decision
from app.motor.rutina import NOMBRES_DIAS
from app.servicios import entrenamiento as servicio

enrutador = APIRouter(prefix="/entrenamiento", tags=["Bitacora de entrenamiento"])

_SESION_NO_ENCONTRADA = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="La sesión indicada no existe o no pertenece a su rutina.",
)


@enrutador.get(
    "/sesiones/{sesion_id}",
    response_model=SesionParaEntrenar,
    summary="Abrir una sesion para entrenarla",
)
def abrir_sesion(
    sesion_id: int, sesion: SesionBD, usuario: UsuarioAutenticado
) -> SesionParaEntrenar:
    """Entrega la sesión prescrita con la carga sugerida para cada ejercicio.

    Es la pantalla que se usa dentro del gimnasio: además de la prescripción,
    lleva lo que el usuario hizo la última vez y con cuánto peso conviene
    entrenar hoy, calculado con la regla del negocio *d*.
    """
    sentencia = (
        select(SesionEntrenamiento)
        .join(Plan, Plan.id == SesionEntrenamiento.plan_id)
        .where(SesionEntrenamiento.id == sesion_id, Plan.usuario_id == usuario.id)
        .options(
            selectinload(SesionEntrenamiento.ejercicios).selectinload(
                EjercicioSesion.ejercicio
            )
        )
    )
    prescrita = sesion.execute(sentencia).scalar_one_or_none()
    if prescrita is None:
        raise _SESION_NO_ENCONTRADA

    ejercicios = []
    for prescrito in sorted(prescrita.ejercicios, key=lambda e: e.orden):
        recomendacion, ultima_vez, fecha = servicio.recomendar_carga(
            sesion,
            usuario,
            prescrito.ejercicio,
            prescrito.repeticiones_min,
            prescrito.repeticiones_max,
        )
        ejercicios.append(
            EjercicioParaEntrenar(
                ejercicio_id=prescrito.ejercicio_id,
                nombre=prescrito.ejercicio.nombre,
                equipamiento=prescrito.ejercicio.equipamiento,
                descripcion=prescrito.ejercicio.descripcion,
                grupo_muscular=NOMBRES_GRUPO[prescrito.ejercicio.grupo_muscular],
                orden=prescrito.orden,
                series=prescrito.series,
                repeticiones_min=prescrito.repeticiones_min,
                repeticiones_max=prescrito.repeticiones_max,
                repeticiones_en_reserva=prescrito.repeticiones_en_reserva,
                descanso_segundos=prescrito.descanso_segundos,
                recomendacion=RecomendacionPublica(**vars(recomendacion)),
                ultima_vez=[
                    SeriePrevia(
                        numero_serie=serie.numero_serie,
                        repeticiones=serie.repeticiones,
                        peso_kg=float(serie.peso_kg) if serie.peso_kg is not None else None,
                    )
                    for serie in ultima_vez
                ],
                fecha_ultima_vez=fecha,
            )
        )

    segundos = sum(
        prescrito.series * (40 + prescrito.descanso_segundos)
        for prescrito in prescrita.ejercicios
    )

    return SesionParaEntrenar(
        sesion_id=prescrita.id,
        dia=prescrita.dia,
        nombre_dia=NOMBRES_DIAS[prescrita.dia],
        nombre_grupo=NOMBRES_GRUPO[prescrita.grupo_muscular],
        plan_id=prescrita.plan_id,
        duracion_estimada_minutos=max(round(segundos / 60), 1),
        ya_registrada_hoy=servicio.hay_sesion_registrada(sesion, usuario, prescrita.id),
        ejercicios=ejercicios,
    )


@enrutador.post(
    "/sesiones",
    response_model=RespuestaSesionRegistrada,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una sesion completada",
)
def registrar_sesion(
    datos: SesionEjecutadaEntrada, sesion: SesionBD, usuario: UsuarioAutenticado
) -> RespuestaSesionRegistrada:
    """Guarda lo que el usuario hizo y le dice qué hará el sistema la próxima vez.

    La respuesta incluye la progresión de cada ejercicio para que el usuario vea
    de inmediato el efecto de lo que acaba de registrar: sin eso, la bitácora
    sería un formulario que no devuelve nada.
    """
    try:
        realizada = servicio.registrar_sesion(sesion, usuario, datos)
    except servicio.SesionNoEncontrada:
        raise _SESION_NO_ENCONTRADA from None
    except servicio.EjercicioNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alguno de los ejercicios registrados no existe en el catálogo.",
        ) from None

    progresiones = servicio.progresiones_de_la_sesion(sesion, usuario, realizada)
    subidas = sum(1 for p in progresiones if p.decision == Decision.SUBIR_CARGA)

    if subidas:
        mensaje = (
            f"Sesión registrada. En la próxima le toca subir la carga en {subidas} "
            f"{'ejercicio' if subidas == 1 else 'ejercicios'}."
        )
    else:
        mensaje = (
            "Sesión registrada. Repita estas cargas la próxima vez y busque completar "
            "el rango de repeticiones en todas las series."
        )

    return RespuestaSesionRegistrada(
        sesion=_a_publica(sesion, realizada),
        progresiones=[RecomendacionPublica(**vars(p)) for p in progresiones],
        mensaje=mensaje,
    )


@enrutador.get(
    "/sesiones",
    response_model=list[SesionRealizadaPublica],
    summary="Consultar la bitacora de entrenamientos",
)
def listar_sesiones(
    sesion: SesionBD, usuario: UsuarioAutenticado
) -> list[SesionRealizadaPublica]:
    """Devuelve las sesiones registradas, de la más reciente a la más antigua."""
    return [
        _a_publica(sesion, realizada)
        for realizada in servicio.listar_sesiones(sesion, usuario)
    ]


@enrutador.get(
    "/ejercicios/{ejercicio_id}",
    response_model=HistorialDeEjercicio,
    summary="Consultar la evolucion de un ejercicio",
)
def historial_de_ejercicio(
    ejercicio_id: int, sesion: SesionBD, usuario: UsuarioAutenticado
) -> HistorialDeEjercicio:
    """Cómo ha evolucionado la carga de un ejercicio a lo largo de las sesiones."""
    ejercicio = sesion.get(Ejercicio, ejercicio_id)
    if ejercicio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El ejercicio indicado no existe en el catálogo.",
        )

    historial = servicio.ejecuciones_de_ejercicio(
        sesion, usuario, ejercicio_id, limite=52
    )
    puntos = [
        PuntoDeCarga(
            fecha=fecha,
            carga_maxima_kg=max(
                (float(s.peso_kg) for s in series if s.peso_kg is not None), default=None
            ),
            volumen_kg=round(
                sum(
                    float(s.peso_kg) * s.repeticiones
                    for s in series
                    if s.peso_kg is not None
                ),
                1,
            ),
            repeticiones_totales=sum(s.repeticiones for s in series),
        )
        # La lectura de una evolución va de izquierda a derecha en el tiempo.
        for fecha, series, _ in reversed(historial)
    ]

    carga, repeticiones, fecha_marca = servicio.marca_personal(
        sesion, usuario, ejercicio_id
    )

    return HistorialDeEjercicio(
        ejercicio_id=ejercicio.id,
        nombre=ejercicio.nombre,
        grupo_muscular=NOMBRES_GRUPO[ejercicio.grupo_muscular],
        marca=MarcaPersonal(
            ejercicio_id=ejercicio.id,
            nombre=ejercicio.nombre,
            carga_maxima_kg=carga,
            repeticiones_en_la_maxima=repeticiones,
            fecha=fecha_marca,
        ),
        puntos=puntos,
    )


@enrutador.get(
    "/resumen",
    response_model=ResumenEntrenamiento,
    summary="Consultar el resumen de la bitacora",
)
def consultar_resumen(
    sesion: SesionBD, usuario: UsuarioAutenticado
) -> ResumenEntrenamiento:
    """Cifras de constancia y volumen, con las marcas personales del usuario."""
    cifras = servicio.resumen(sesion, usuario)

    # Las marcas se limitan a los ejercicios que el usuario efectivamente
    # registró: listar el catálogo entero con marcas vacías no dice nada.
    registrados = servicio.listar_sesiones(sesion, usuario, limite=200)
    ejercicios_vistos: list[int] = []
    for realizada in registrados:
        for serie in realizada.series:
            if serie.ejercicio_id not in ejercicios_vistos:
                ejercicios_vistos.append(serie.ejercicio_id)

    marcas = []
    for ejercicio_id in ejercicios_vistos:
        ejercicio = sesion.get(Ejercicio, ejercicio_id)
        if ejercicio is None:
            continue
        carga, repeticiones, fecha = servicio.marca_personal(sesion, usuario, ejercicio_id)
        if carga is None:
            continue
        marcas.append(
            MarcaPersonal(
                ejercicio_id=ejercicio_id,
                nombre=ejercicio.nombre,
                carga_maxima_kg=carga,
                repeticiones_en_la_maxima=repeticiones,
                fecha=fecha,
            )
        )

    return ResumenEntrenamiento(**cifras, marcas=marcas)


def _a_publica(sesion: SesionBD, realizada) -> SesionRealizadaPublica:
    """Arma la respuesta de una sesion registrada, con el nombre de su grupo."""
    nombre_grupo = None
    if realizada.sesion_id is not None:
        prescrita = sesion.get(SesionEntrenamiento, realizada.sesion_id)
        if prescrita is not None:
            nombre_grupo = NOMBRES_GRUPO[prescrita.grupo_muscular]

    publica = SesionRealizadaPublica.model_validate(realizada)
    return publica.model_copy(update={"nombre_grupo": nombre_grupo})
