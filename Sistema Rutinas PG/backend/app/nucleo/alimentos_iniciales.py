"""Carga inicial del catalogo de alimentos (historia HU-11, parcial).

Los alimentos listados son los de consumo habitual en el municipio de El
Progreso, Jutiapa, con su aporte nutricional por cada 100 gramos y una medida
casera que permita servirlos sin bascula, como exige el criterio de aceptacion de
la historia HU-08.

**Este catalogo es provisional.** La historia HU-11 exige levantarlo mediante
visita directa a los mercados del municipio, tanto para confirmar la
disponibilidad real como para registrar el costo vigente. Los aportes
nutricionales provienen de tablas de composicion de alimentos para Centroamerica
y los costos son estimaciones que deben verificarse en el mercado. Mientras esa
visita no se realice, el catalogo sirve para que la generacion de planes de la
historia HU-08 tenga de donde elegir.

La carga es idempotente: solo se insertan los alimentos que aun no existen, de
modo que los cambios del administrador no se deshagan en cada arranque.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modelos.catalogo import Alimento
from app.modelos.enumeraciones import CategoriaAlimento

bitacora = logging.getLogger(__name__)

# (nombre, categoria, kcal, proteina, carbohidrato, grasa, costo aproximado, medida casera)
ALIMENTOS_INICIALES: list[
    tuple[str, CategoriaAlimento, float, float, float, float, float | None, str]
] = [
    # Cereales
    ("Tortilla de maíz", CategoriaAlimento.CEREAL, 218, 5.7, 44.6, 2.5, 1.0, "1 tortilla ≈ 30 g"),
    ("Arroz blanco cocido", CategoriaAlimento.CEREAL, 130, 2.7, 28.0, 0.3, 3.0, "1 taza ≈ 160 g"),
    ("Pan francés", CategoriaAlimento.CEREAL, 277, 8.5, 53.0, 2.7, 1.5, "1 pan ≈ 50 g"),
    ("Avena en hojuelas", CategoriaAlimento.CEREAL, 389, 16.9, 66.0, 6.9, 12.0, "1/2 taza ≈ 40 g"),
    ("Incaparina en polvo", CategoriaAlimento.CEREAL, 380, 18.0, 65.0, 3.5, 14.0, "3 cucharadas ≈ 30 g"),
    ("Pasta cocida", CategoriaAlimento.CEREAL, 158, 5.8, 31.0, 0.9, 6.0, "1 taza ≈ 140 g"),
    # Proteína animal
    ("Pechuga de pollo", CategoriaAlimento.PROTEINA_ANIMAL, 165, 31.0, 0.0, 3.6, 28.0, "1 pieza mediana ≈ 120 g"),
    ("Huevo de gallina", CategoriaAlimento.PROTEINA_ANIMAL, 143, 12.6, 0.7, 9.5, 1.5, "1 huevo ≈ 50 g"),
    ("Carne de res molida magra", CategoriaAlimento.PROTEINA_ANIMAL, 176, 20.0, 0.0, 10.0, 45.0, "1 porción ≈ 100 g"),
    ("Tilapia", CategoriaAlimento.PROTEINA_ANIMAL, 96, 20.0, 0.0, 1.7, 30.0, "1 filete ≈ 120 g"),
    ("Hígado de res", CategoriaAlimento.PROTEINA_ANIMAL, 135, 20.4, 3.9, 3.6, 25.0, "1 porción ≈ 100 g"),
    # Leguminosas
    ("Frijol negro cocido", CategoriaAlimento.LEGUMINOSA, 132, 8.9, 23.7, 0.5, 4.0, "1/2 taza ≈ 90 g"),
    ("Lenteja cocida", CategoriaAlimento.LEGUMINOSA, 116, 9.0, 20.0, 0.4, 8.0, "1/2 taza ≈ 100 g"),
    ("Garbanzo cocido", CategoriaAlimento.LEGUMINOSA, 164, 8.9, 27.4, 2.6, 10.0, "1/2 taza ≈ 82 g"),
    # Lácteos
    ("Leche entera", CategoriaAlimento.LACTEO, 61, 3.2, 4.8, 3.3, 8.0, "1 vaso ≈ 240 ml"),
    ("Queso fresco", CategoriaAlimento.LACTEO, 264, 17.0, 3.0, 21.0, 35.0, "1 rebanada ≈ 30 g"),
    ("Yogur natural", CategoriaAlimento.LACTEO, 61, 3.5, 4.7, 3.3, 12.0, "1 vaso ≈ 200 g"),
    # Frutas
    ("Banano", CategoriaAlimento.FRUTA, 89, 1.1, 22.8, 0.3, 1.5, "1 unidad mediana ≈ 120 g"),
    ("Papaya", CategoriaAlimento.FRUTA, 43, 0.5, 10.8, 0.3, 5.0, "1 taza en cubos ≈ 145 g"),
    ("Mango", CategoriaAlimento.FRUTA, 60, 0.8, 15.0, 0.4, 3.0, "1 unidad mediana ≈ 200 g"),
    ("Naranja", CategoriaAlimento.FRUTA, 47, 0.9, 11.8, 0.1, 1.5, "1 unidad mediana ≈ 130 g"),
    ("Sandía", CategoriaAlimento.FRUTA, 30, 0.6, 7.6, 0.2, 4.0, "1 taza en cubos ≈ 150 g"),
    # Verduras
    ("Güisquil", CategoriaAlimento.VERDURA, 19, 0.8, 4.5, 0.1, 2.0, "1 unidad ≈ 200 g"),
    ("Tomate", CategoriaAlimento.VERDURA, 18, 0.9, 3.9, 0.2, 2.0, "1 unidad mediana ≈ 120 g"),
    ("Repollo", CategoriaAlimento.VERDURA, 25, 1.3, 5.8, 0.1, 3.0, "1 taza de repollo picado ≈ 90 g"),
    ("Zanahoria", CategoriaAlimento.VERDURA, 41, 0.9, 9.6, 0.2, 2.0, "1 unidad mediana ≈ 60 g"),
    ("Ejote", CategoriaAlimento.VERDURA, 31, 1.8, 7.0, 0.1, 5.0, "1 taza ≈ 100 g"),
    ("Espinaca", CategoriaAlimento.VERDURA, 23, 2.9, 3.6, 0.4, 6.0, "1 taza cruda ≈ 30 g"),
    # Grasas
    ("Aceite vegetal", CategoriaAlimento.GRASA, 884, 0.0, 0.0, 100.0, 2.0, "1 cucharada ≈ 14 g"),
    ("Aguacate", CategoriaAlimento.GRASA, 160, 2.0, 8.5, 14.7, 6.0, "1/2 unidad ≈ 100 g"),
    ("Maní tostado", CategoriaAlimento.GRASA, 567, 25.8, 16.1, 49.2, 10.0, "1 puño ≈ 30 g"),
    ("Semilla de marañón", CategoriaAlimento.GRASA, 553, 18.2, 30.2, 43.9, 25.0, "1 puño ≈ 30 g"),
    # Tubérculos
    ("Papa cocida", CategoriaAlimento.TUBERCULO, 77, 2.0, 17.0, 0.1, 3.0, "1 unidad mediana ≈ 150 g"),
    ("Camote cocido", CategoriaAlimento.TUBERCULO, 86, 1.6, 20.0, 0.1, 3.0, "1 unidad mediana ≈ 130 g"),
    ("Yuca cocida", CategoriaAlimento.TUBERCULO, 160, 1.4, 38.0, 0.3, 4.0, "1 porción ≈ 100 g"),
    ("Plátano macho cocido", CategoriaAlimento.TUBERCULO, 122, 1.3, 32.0, 0.4, 2.5, "1 unidad ≈ 150 g"),
]


def cargar_alimentos(sesion: Session) -> int:
    """Inserta los alimentos que aun no existan y devuelve cuantos agrego."""
    existentes = {nombre for (nombre,) in sesion.execute(select(Alimento.nombre)).all()}

    agregados = 0
    for (
        nombre,
        categoria,
        energia,
        proteina,
        carbohidrato,
        grasa,
        costo,
        medida,
    ) in ALIMENTOS_INICIALES:
        if nombre in existentes:
            continue
        sesion.add(
            Alimento(
                nombre=nombre,
                categoria=categoria,
                energia_kcal_100g=energia,
                proteina_g_100g=proteina,
                carbohidrato_g_100g=carbohidrato,
                grasa_g_100g=grasa,
                costo_aproximado_quetzales=costo,
                medida_casera=medida,
                disponible_localmente=True,
            )
        )
        agregados += 1

    if agregados:
        sesion.commit()
    return agregados


def contar_alimentos(sesion: Session) -> int:
    """Cuenta los alimentos registrados en el catalogo."""
    return sesion.execute(select(func.count()).select_from(Alimento)).scalar_one()
