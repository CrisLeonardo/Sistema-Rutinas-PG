"""Controlador de los catalogos maestros (historia HU-11).

La consulta esta abierta a cualquier cuenta autenticada, porque el usuario
deportista necesita ver los alimentos y ejercicios que su plan le propone. El
alta, la modificacion y la baja quedan reservadas al administrador, conforme al
criterio de aceptacion de la historia.
"""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencias import Administrador, SesionBD, UsuarioAutenticado
from app.esquemas.catalogo import (
    AlimentoEntrada,
    AlimentoPublico,
    EjercicioEntrada,
    EjercicioPublico,
)
from app.esquemas.usuario import CambioEstado
from app.modelos.enumeraciones import CategoriaAlimento, GrupoMuscular
from app.servicios import catalogo as servicio_catalogo

enrutador = APIRouter(prefix="/catalogos", tags=["Catalogos maestros"])

_NO_ENCONTRADO = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="El elemento del catálogo indicado no existe.",
)


def _conflicto_nombre(nombre: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Ya existe un elemento del catálogo con el nombre «{nombre}».",
    )


# --------------------------------------------------------------------------
# Alimentos
# --------------------------------------------------------------------------


@enrutador.get(
    "/alimentos",
    response_model=list[AlimentoPublico],
    summary="Consultar el catálogo de alimentos",
)
def listar_alimentos(
    sesion: SesionBD,
    usuario: UsuarioAutenticado,
    categoria: CategoriaAlimento | None = None,
    solo_disponibles: bool = False,
) -> list[AlimentoPublico]:
    """Devuelve los alimentos del catálogo local."""
    return [
        AlimentoPublico.model_validate(alimento)
        for alimento in servicio_catalogo.listar_alimentos(sesion, categoria, solo_disponibles)
    ]


@enrutador.post(
    "/alimentos",
    response_model=AlimentoPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Dar de alta un alimento",
)
def crear_alimento(
    datos: AlimentoEntrada, sesion: SesionBD, administrador: Administrador
) -> AlimentoPublico:
    """Registra un alimento nuevo. Reservado al administrador."""
    try:
        alimento = servicio_catalogo.crear_alimento(sesion, datos)
    except servicio_catalogo.NombreDuplicado:
        raise _conflicto_nombre(datos.nombre) from None
    return AlimentoPublico.model_validate(alimento)


@enrutador.put(
    "/alimentos/{alimento_id}",
    response_model=AlimentoPublico,
    summary="Modificar un alimento",
)
def modificar_alimento(
    alimento_id: int,
    datos: AlimentoEntrada,
    sesion: SesionBD,
    administrador: Administrador,
) -> AlimentoPublico:
    """Actualiza los datos de un alimento. Reservado al administrador."""
    try:
        alimento = servicio_catalogo.modificar_alimento(sesion, alimento_id, datos)
    except servicio_catalogo.ElementoNoEncontrado:
        raise _NO_ENCONTRADO from None
    except servicio_catalogo.NombreDuplicado:
        raise _conflicto_nombre(datos.nombre) from None
    return AlimentoPublico.model_validate(alimento)


@enrutador.put(
    "/alimentos/{alimento_id}/disponibilidad",
    response_model=AlimentoPublico,
    summary="Dar de baja o habilitar un alimento",
)
def cambiar_disponibilidad_alimento(
    alimento_id: int,
    datos: CambioEstado,
    sesion: SesionBD,
    administrador: Administrador,
) -> AlimentoPublico:
    """Marca un alimento como disponible o no disponible.

    La baja es lógica: los planes ya generados conservan la referencia, pero el
    alimento deja de proponerse en los planes nuevos.
    """
    try:
        alimento = servicio_catalogo.cambiar_disponibilidad_alimento(
            sesion, alimento_id, datos.activo
        )
    except servicio_catalogo.ElementoNoEncontrado:
        raise _NO_ENCONTRADO from None
    return AlimentoPublico.model_validate(alimento)


# --------------------------------------------------------------------------
# Ejercicios
# --------------------------------------------------------------------------


@enrutador.get(
    "/ejercicios",
    response_model=list[EjercicioPublico],
    summary="Consultar el catálogo de ejercicios",
)
def listar_ejercicios(
    sesion: SesionBD,
    usuario: UsuarioAutenticado,
    grupo_muscular: GrupoMuscular | None = None,
    solo_disponibles: bool = False,
) -> list[EjercicioPublico]:
    """Devuelve los ejercicios registrados para la institución."""
    return [
        EjercicioPublico.model_validate(ejercicio)
        for ejercicio in servicio_catalogo.listar_ejercicios(
            sesion, grupo_muscular, solo_disponibles
        )
    ]


@enrutador.post(
    "/ejercicios",
    response_model=EjercicioPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Dar de alta un ejercicio",
)
def crear_ejercicio(
    datos: EjercicioEntrada, sesion: SesionBD, administrador: Administrador
) -> EjercicioPublico:
    """Registra un ejercicio nuevo. Reservado al administrador."""
    try:
        ejercicio = servicio_catalogo.crear_ejercicio(sesion, datos)
    except servicio_catalogo.NombreDuplicado:
        raise _conflicto_nombre(datos.nombre) from None
    return EjercicioPublico.model_validate(ejercicio)


@enrutador.put(
    "/ejercicios/{ejercicio_id}",
    response_model=EjercicioPublico,
    summary="Modificar un ejercicio",
)
def modificar_ejercicio(
    ejercicio_id: int,
    datos: EjercicioEntrada,
    sesion: SesionBD,
    administrador: Administrador,
) -> EjercicioPublico:
    """Actualiza los datos de un ejercicio. Reservado al administrador."""
    try:
        ejercicio = servicio_catalogo.modificar_ejercicio(sesion, ejercicio_id, datos)
    except servicio_catalogo.ElementoNoEncontrado:
        raise _NO_ENCONTRADO from None
    except servicio_catalogo.NombreDuplicado:
        raise _conflicto_nombre(datos.nombre) from None
    return EjercicioPublico.model_validate(ejercicio)


@enrutador.put(
    "/ejercicios/{ejercicio_id}/disponibilidad",
    response_model=EjercicioPublico,
    summary="Dar de baja o habilitar un ejercicio",
)
def cambiar_disponibilidad_ejercicio(
    ejercicio_id: int,
    datos: CambioEstado,
    sesion: SesionBD,
    administrador: Administrador,
) -> EjercicioPublico:
    """Marca un ejercicio como disponible o no disponible."""
    try:
        ejercicio = servicio_catalogo.cambiar_disponibilidad_ejercicio(
            sesion, ejercicio_id, datos.activo
        )
    except servicio_catalogo.ElementoNoEncontrado:
        raise _NO_ENCONTRADO from None
    return EjercicioPublico.model_validate(ejercicio)
