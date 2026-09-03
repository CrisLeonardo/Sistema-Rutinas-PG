"""Carga inicial del catalogo de ejercicios (historia HU-11, parcial).

Los ejercicios listados aqui son los ejecutables con el equipamiento basico de un
gimnasio del municipio: barra, discos, mancuernas, banca, polea y peso corporal.
Sirven para que la generacion de rutinas de la historia HU-07 tenga de donde
elegir desde el primer arranque del sistema.

**Este catalogo es provisional.** La historia HU-11 exige registrar el
equipamiento efectivamente disponible en el Gimnasio FAMAS mediante visita
directa, y esa verificacion sustituira o depurara esta lista. Hasta entonces, el
administrador puede dar de alta y de baja ejercicios desde el sistema.

La carga es idempotente: solo se insertan los ejercicios que aun no existen, de
modo que los cambios que haga el administrador no se deshagan en cada arranque.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modelos.catalogo import Ejercicio
from app.modelos.enumeraciones import GrupoMuscular, NivelExperiencia

bitacora = logging.getLogger(__name__)

EQUIPAMIENTO_BARRA = "Barra y discos"
EQUIPAMIENTO_MANCUERNAS = "Mancuernas"
EQUIPAMIENTO_BANCA = "Banca y mancuernas"
EQUIPAMIENTO_POLEA = "Polea"
EQUIPAMIENTO_PESO_CORPORAL = "Peso corporal"
EQUIPAMIENTO_MAQUINA = "Máquina"

# (nombre, grupo, nivel minimo, equipamiento, es compuesto, descripcion)
EJERCICIOS_INICIALES: list[tuple[str, GrupoMuscular, NivelExperiencia, str, bool, str]] = [
    # Pecho
    (
        "Press de banca con barra",
        GrupoMuscular.PECHO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_BARRA,
        True,
        "Acostado en la banca, baje la barra hasta el pecho y empuje hacia arriba.",
    ),
    (
        "Press inclinado con mancuernas",
        GrupoMuscular.PECHO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_BANCA,
        True,
        "Con la banca inclinada, empuje las mancuernas desde el pecho hacia arriba.",
    ),
    (
        "Aperturas con mancuernas",
        GrupoMuscular.PECHO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_BANCA,
        False,
        "Con los brazos casi extendidos, abra y cierre describiendo un arco amplio.",
    ),
    (
        "Lagartijas",
        GrupoMuscular.PECHO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_PESO_CORPORAL,
        True,
        "Con el cuerpo recto, baje hasta que el pecho casi toque el suelo.",
    ),
    # Espalda
    (
        "Remo con barra",
        GrupoMuscular.ESPALDA,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_BARRA,
        True,
        "Con el torso inclinado y la espalda recta, lleve la barra hacia el abdomen.",
    ),
    (
        "Jalón al pecho en polea",
        GrupoMuscular.ESPALDA,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_POLEA,
        True,
        "Sentado, jale la barra hasta la parte alta del pecho sin balancear el torso.",
    ),
    (
        "Remo con mancuerna a una mano",
        GrupoMuscular.ESPALDA,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_BANCA,
        True,
        "Apoyado en la banca, jale la mancuerna hacia la cadera.",
    ),
    (
        "Dominadas",
        GrupoMuscular.ESPALDA,
        NivelExperiencia.INTERMEDIO,
        EQUIPAMIENTO_PESO_CORPORAL,
        True,
        "Colgado de la barra, súbase hasta pasar la barbilla por encima.",
    ),
    # Pierna
    (
        "Sentadilla con barra",
        GrupoMuscular.PIERNA,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_BARRA,
        True,
        "Con la barra sobre la espalda alta, baje hasta que el muslo quede paralelo al suelo.",
    ),
    (
        "Prensa de piernas",
        GrupoMuscular.PIERNA,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_MAQUINA,
        True,
        "Empuje la plataforma sin llegar a bloquear por completo la rodilla.",
    ),
    (
        "Peso muerto rumano",
        GrupoMuscular.PIERNA,
        NivelExperiencia.INTERMEDIO,
        EQUIPAMIENTO_BARRA,
        True,
        "Con la espalda recta, baje la barra pegada a la pierna hasta sentir tensión atrás.",
    ),
    (
        "Zancadas con mancuernas",
        GrupoMuscular.PIERNA,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_MANCUERNAS,
        True,
        "Dé un paso al frente y baje la rodilla de atrás sin tocar el suelo.",
    ),
    (
        "Elevación de talones de pie",
        GrupoMuscular.PIERNA,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_PESO_CORPORAL,
        False,
        "Suba sobre la punta de los pies y baje despacio.",
    ),
    # Hombro
    (
        "Press militar con barra",
        GrupoMuscular.HOMBRO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_BARRA,
        True,
        "De pie, empuje la barra desde los hombros hasta arriba de la cabeza.",
    ),
    (
        "Elevaciones laterales con mancuernas",
        GrupoMuscular.HOMBRO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_MANCUERNAS,
        False,
        "Suba las mancuernas a los lados hasta la altura del hombro.",
    ),
    (
        "Pájaros con mancuernas",
        GrupoMuscular.HOMBRO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_MANCUERNAS,
        False,
        "Con el torso inclinado, abra los brazos hacia atrás.",
    ),
    (
        "Press Arnold con mancuernas",
        GrupoMuscular.HOMBRO,
        NivelExperiencia.INTERMEDIO,
        EQUIPAMIENTO_MANCUERNAS,
        True,
        "Empuje las mancuernas girando las muñecas desde el pecho hacia afuera.",
    ),
    # Brazo
    (
        "Curl de bíceps con barra",
        GrupoMuscular.BRAZO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_BARRA,
        False,
        "Con los codos pegados al cuerpo, suba la barra hasta el pecho.",
    ),
    (
        "Curl alterno con mancuernas",
        GrupoMuscular.BRAZO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_MANCUERNAS,
        False,
        "Suba una mancuerna a la vez, girando la muñeca hacia arriba.",
    ),
    (
        "Extensión de tríceps en polea",
        GrupoMuscular.BRAZO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_POLEA,
        False,
        "Con los codos fijos, extienda los brazos hacia abajo.",
    ),
    (
        "Fondos entre bancas",
        GrupoMuscular.BRAZO,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_PESO_CORPORAL,
        True,
        "Apoyado con las manos atrás, baje y suba el cuerpo doblando los codos.",
    ),
    # Abdomen
    (
        "Plancha frontal",
        GrupoMuscular.ABDOMEN,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_PESO_CORPORAL,
        False,
        "Apoyado en antebrazos y punta de pies, sostenga el cuerpo recto.",
    ),
    (
        "Abdominales en el suelo",
        GrupoMuscular.ABDOMEN,
        NivelExperiencia.PRINCIPIANTE,
        EQUIPAMIENTO_PESO_CORPORAL,
        False,
        "Con las rodillas dobladas, despegue los hombros del suelo.",
    ),
    (
        "Rueda abdominal o rodillo",
        GrupoMuscular.ABDOMEN,
        NivelExperiencia.INTERMEDIO,
        EQUIPAMIENTO_PESO_CORPORAL,
        False,
        "De rodillas, ruede hacia adelante sin arquear la espalda baja.",
    ),
    (
        "Elevación de piernas colgado",
        GrupoMuscular.ABDOMEN,
        NivelExperiencia.INTERMEDIO,
        EQUIPAMIENTO_PESO_CORPORAL,
        False,
        "Colgado de la barra, suba las piernas rectas hasta la altura de la cadera.",
    ),
]


def cargar_ejercicios(sesion: Session) -> int:
    """Inserta los ejercicios que aun no existan y devuelve cuantos agrego."""
    existentes = {
        nombre for (nombre,) in sesion.execute(select(Ejercicio.nombre)).all()
    }

    agregados = 0
    for nombre, grupo, nivel, equipamiento, compuesto, descripcion in EJERCICIOS_INICIALES:
        if nombre in existentes:
            continue
        sesion.add(
            Ejercicio(
                nombre=nombre,
                grupo_muscular=grupo,
                nivel_minimo=nivel,
                equipamiento=equipamiento,
                descripcion=descripcion,
                es_compuesto=compuesto,
                disponible_localmente=True,
            )
        )
        agregados += 1

    if agregados:
        sesion.commit()
    return agregados


def contar_ejercicios(sesion: Session) -> int:
    """Cuenta los ejercicios registrados en el catalogo."""
    return sesion.execute(select(func.count()).select_from(Ejercicio)).scalar_one()
