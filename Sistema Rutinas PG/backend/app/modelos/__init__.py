"""Entidades del modelo de datos.

Se importan todas aqui para que SQLAlchemy resuelva las relaciones declaradas
por nombre y para que la creacion del esquema incluya la totalidad de las tablas.
"""

from app.modelos.catalogo import Alimento, Ejercicio
from app.modelos.enumeraciones import (
    CategoriaAlimento,
    GrupoMuscular,
    NivelActividad,
    NivelExperiencia,
    Objetivo,
    RolUsuario,
    Sexo,
)
from app.modelos.perfil import PerfilBiometrico, RegistroProgreso
from app.modelos.plan import ComidaPlan, EjercicioSesion, Plan, SesionEntrenamiento
from app.modelos.usuario import Usuario

__all__ = [
    "Alimento",
    "CategoriaAlimento",
    "ComidaPlan",
    "Ejercicio",
    "EjercicioSesion",
    "GrupoMuscular",
    "NivelActividad",
    "NivelExperiencia",
    "Objetivo",
    "PerfilBiometrico",
    "Plan",
    "RegistroProgreso",
    "RolUsuario",
    "SesionEntrenamiento",
    "Sexo",
    "Usuario",
]
