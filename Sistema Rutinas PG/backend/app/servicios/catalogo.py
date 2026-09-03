"""Administracion de los catalogos maestros (historia HU-11).

Concentra el alta, la modificacion y la baja de alimentos y ejercicios. La baja
es logica y no fisica: un alimento que deja de conseguirse en el mercado se marca
como no disponible en lugar de borrarse, porque los planes ya generados lo
referencian y borrarlo dejaria esos planes incompletos.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.esquemas.catalogo import AlimentoEntrada, EjercicioEntrada
from app.modelos.catalogo import Alimento, Ejercicio
from app.modelos.enumeraciones import CategoriaAlimento, GrupoMuscular

bitacora = logging.getLogger(__name__)


class NombreDuplicado(Exception):
    """Ya existe un elemento del catalogo con ese nombre."""


class ElementoNoEncontrado(Exception):
    """El elemento del catalogo indicado no existe."""


# --------------------------------------------------------------------------
# Alimentos
# --------------------------------------------------------------------------


def listar_alimentos(
    sesion: Session,
    categoria: CategoriaAlimento | None = None,
    solo_disponibles: bool = False,
) -> list[Alimento]:
    """Devuelve los alimentos del catalogo, con filtros opcionales."""
    sentencia = select(Alimento)
    if categoria is not None:
        sentencia = sentencia.where(Alimento.categoria == categoria)
    if solo_disponibles:
        sentencia = sentencia.where(Alimento.disponible_localmente.is_(True))
    sentencia = sentencia.order_by(Alimento.categoria, Alimento.nombre)
    return list(sesion.execute(sentencia).scalars())


def obtener_alimento(sesion: Session, alimento_id: int) -> Alimento:
    """Recupera un alimento por su identificador."""
    alimento = sesion.get(Alimento, alimento_id)
    if alimento is None:
        raise ElementoNoEncontrado(alimento_id)
    return alimento


def crear_alimento(sesion: Session, datos: AlimentoEntrada) -> Alimento:
    """Da de alta un alimento en el catalogo."""
    alimento = Alimento(**datos.model_dump())
    sesion.add(alimento)
    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        raise NombreDuplicado(datos.nombre) from error
    sesion.refresh(alimento)
    return alimento


def modificar_alimento(sesion: Session, alimento_id: int, datos: AlimentoEntrada) -> Alimento:
    """Actualiza los datos de un alimento existente."""
    alimento = obtener_alimento(sesion, alimento_id)
    for campo, valor in datos.model_dump().items():
        setattr(alimento, campo, valor)
    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        raise NombreDuplicado(datos.nombre) from error
    sesion.refresh(alimento)
    return alimento


def cambiar_disponibilidad_alimento(
    sesion: Session, alimento_id: int, disponible: bool
) -> Alimento:
    """Da de baja o vuelve a habilitar un alimento.

    La baja es logica: los planes ya generados conservan la referencia y siguen
    siendo consultables, pero el alimento deja de proponerse en planes nuevos.
    """
    alimento = obtener_alimento(sesion, alimento_id)
    alimento.disponible_localmente = disponible
    sesion.commit()
    sesion.refresh(alimento)
    return alimento


def contar_alimentos_disponibles(sesion: Session) -> int:
    """Cuenta los alimentos que pueden proponerse en un plan."""
    sentencia = (
        select(func.count())
        .select_from(Alimento)
        .where(Alimento.disponible_localmente.is_(True))
    )
    return sesion.execute(sentencia).scalar_one()


# --------------------------------------------------------------------------
# Ejercicios
# --------------------------------------------------------------------------


def listar_ejercicios(
    sesion: Session,
    grupo_muscular: GrupoMuscular | None = None,
    solo_disponibles: bool = False,
) -> list[Ejercicio]:
    """Devuelve los ejercicios del catalogo, con filtros opcionales."""
    sentencia = select(Ejercicio)
    if grupo_muscular is not None:
        sentencia = sentencia.where(Ejercicio.grupo_muscular == grupo_muscular)
    if solo_disponibles:
        sentencia = sentencia.where(Ejercicio.disponible_localmente.is_(True))
    sentencia = sentencia.order_by(Ejercicio.grupo_muscular, Ejercicio.nombre)
    return list(sesion.execute(sentencia).scalars())


def obtener_ejercicio(sesion: Session, ejercicio_id: int) -> Ejercicio:
    """Recupera un ejercicio por su identificador."""
    ejercicio = sesion.get(Ejercicio, ejercicio_id)
    if ejercicio is None:
        raise ElementoNoEncontrado(ejercicio_id)
    return ejercicio


def crear_ejercicio(sesion: Session, datos: EjercicioEntrada) -> Ejercicio:
    """Da de alta un ejercicio en el catalogo."""
    ejercicio = Ejercicio(**datos.model_dump())
    sesion.add(ejercicio)
    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        raise NombreDuplicado(datos.nombre) from error
    sesion.refresh(ejercicio)
    return ejercicio


def modificar_ejercicio(sesion: Session, ejercicio_id: int, datos: EjercicioEntrada) -> Ejercicio:
    """Actualiza los datos de un ejercicio existente."""
    ejercicio = obtener_ejercicio(sesion, ejercicio_id)
    for campo, valor in datos.model_dump().items():
        setattr(ejercicio, campo, valor)
    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        raise NombreDuplicado(datos.nombre) from error
    sesion.refresh(ejercicio)
    return ejercicio


def cambiar_disponibilidad_ejercicio(
    sesion: Session, ejercicio_id: int, disponible: bool
) -> Ejercicio:
    """Da de baja o vuelve a habilitar un ejercicio.

    Igual que con los alimentos, la baja es logica para no romper las rutinas
    que ya lo referencian.
    """
    ejercicio = obtener_ejercicio(sesion, ejercicio_id)
    ejercicio.disponible_localmente = disponible
    sesion.commit()
    sesion.refresh(ejercicio)
    return ejercicio


def contar_ejercicios_por_grupo(sesion: Session) -> dict[GrupoMuscular, int]:
    """Cuenta los ejercicios disponibles de cada grupo muscular.

    Permite al administrador detectar los grupos que se quedaron sin opciones
    suficientes para armar una rutina.
    """
    sentencia = (
        select(Ejercicio.grupo_muscular, func.count())
        .where(Ejercicio.disponible_localmente.is_(True))
        .group_by(Ejercicio.grupo_muscular)
    )
    return {grupo: cantidad for grupo, cantidad in sesion.execute(sentencia).all()}
