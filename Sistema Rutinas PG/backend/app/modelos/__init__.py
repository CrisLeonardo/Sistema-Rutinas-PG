"""Entidades del modelo de datos.

Se importan todas aqui para que SQLAlchemy resuelva las relaciones declaradas
por nombre y para que la creacion del esquema incluya la totalidad de las tablas.
"""

from app.modelos.catalogo import Alimento, Ejercicio
from app.modelos.entrenamiento import SerieRealizada, SesionRealizada
from app.modelos.enumeraciones import (
    CategoriaAlimento,
    CondicionMedica,
    GrupoMuscular,
    NivelActividad,
    NivelExperiencia,
    Objetivo,
    RolUsuario,
    Sexo,
    ZonaLesion,
)
from app.modelos.juego import EventoJuego, LogroObtenido
from app.modelos.perfil import (
    CondicionPerfil,
    LesionPerfil,
    PerfilBiometrico,
    RegistroProgreso,
)
from app.modelos.plan import ComidaPlan, EjercicioSesion, Plan, SesionEntrenamiento
from app.modelos.usuario import Usuario

__all__ = [
    "Alimento",
    "CategoriaAlimento",
    "ComidaPlan",
    "CondicionMedica",
    "CondicionPerfil",
    "Ejercicio",
    "EjercicioSesion",
    "EventoJuego",
    "GrupoMuscular",
    "LesionPerfil",
    "LogroObtenido",
    "NivelActividad",
    "NivelExperiencia",
    "Objetivo",
    "PerfilBiometrico",
    "Plan",
    "RegistroProgreso",
    "SerieRealizada",
    "SesionRealizada",
    "RolUsuario",
    "SesionEntrenamiento",
    "Sexo",
    "Usuario",
    "ZonaLesion",
]
