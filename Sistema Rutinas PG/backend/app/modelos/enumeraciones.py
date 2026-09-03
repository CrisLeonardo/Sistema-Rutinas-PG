"""Valores controlados que comparten el modelo de datos y los contratos de la API."""

from enum import StrEnum


class RolUsuario(StrEnum):
    """Roles de acceso definidos en la historia de usuario HU-03."""

    USUARIO = "usuario"
    ADMINISTRADOR = "administrador"


class Sexo(StrEnum):
    """Sexo biologico, requerido por las formulas de Mifflin-St Jeor y Harris-Benedict."""

    MASCULINO = "masculino"
    FEMENINO = "femenino"


class NivelActividad(StrEnum):
    """Nivel de actividad fisica que multiplica la tasa metabolica basal."""

    SEDENTARIO = "sedentario"
    LIGERO = "ligero"
    MODERADO = "moderado"
    ALTO = "alto"
    MUY_ALTO = "muy_alto"


class Objetivo(StrEnum):
    """Objetivo declarado por el usuario, que determina el ajuste calorico."""

    PERDIDA_GRASA = "perdida_grasa"
    MANTENIMIENTO = "mantenimiento"
    GANANCIA_MUSCULAR = "ganancia_muscular"


class GrupoMuscular(StrEnum):
    """Grupos musculares empleados para distribuir el estimulo semanal."""

    PECHO = "pecho"
    ESPALDA = "espalda"
    PIERNA = "pierna"
    HOMBRO = "hombro"
    BRAZO = "brazo"
    ABDOMEN = "abdomen"
    CUERPO_COMPLETO = "cuerpo_completo"


class NivelExperiencia(StrEnum):
    """Nivel de experiencia que condiciona el volumen e intensidad prescritos."""

    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"


class CategoriaAlimento(StrEnum):
    """Categorias del catalogo local de alimentos."""

    CEREAL = "cereal"
    PROTEINA_ANIMAL = "proteina_animal"
    LEGUMINOSA = "leguminosa"
    LACTEO = "lacteo"
    FRUTA = "fruta"
    VERDURA = "verdura"
    GRASA = "grasa"
    TUBERCULO = "tuberculo"
