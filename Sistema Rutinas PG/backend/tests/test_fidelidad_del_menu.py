"""El menu debe entregar la energia que el plan pide (historia HU-08).

El generador dimensionaba el alimento proteico solo por su contenido de
proteina, sin considerar la energia que arrastra. El garbanzo cocido aporta
8.9 gramos de proteina por cada 100 y 164 kilocalorias: cubrir 35 gramos de
proteina exigia 395 gramos de garbanzo, que traen 648 kilocalorias, cuando el
almuerzo disponia de 631.

El efecto se concentraba justamente donde mas dano hace. Los planes de perdida
de grasa son los que combinan poca energia con mucha proteina, y son los que
declara la mayoria de los usuarios: el menu de un plan de 1 200 kilocalorias
entregaba 1 783, un 48 % por encima de lo prescrito. Un plan asi no reduce peso,
y el usuario no tiene como saber por que.

Estas pruebas fijan la fidelidad del menu en todo el dominio que el sistema
admite, para que la correccion no se pierda en un cambio posterior.
"""

import pytest

from app.modelos.enumeraciones import CategoriaAlimento
from app.motor.menu import (
    PROPORCION_MAXIMA_PROTEICA_POR_TIEMPO,
    AlimentoDisponible,
    energia_por_gramo_de_proteina,
    generar_menu,
)
from app.nucleo.alimentos_iniciales import ALIMENTOS_INICIALES

# Margen con que se acepta el menu frente a la energia del plan. Es holgado a
# proposito: las porciones se redondean a multiplos de cinco gramos y las
# verduras van en porcion fija, de modo que la coincidencia exacta no es
# alcanzable ni deseable. Lo que no cabe es un desvio que cambie el resultado
# del plan.
DESVIACION_ADMITIDA = 0.06


def catalogo() -> list[AlimentoDisponible]:
    return [
        AlimentoDisponible(
            id=indice,
            nombre=nombre,
            categoria=categoria,
            energia_kcal_100g=energia,
            proteina_g_100g=proteina,
            carbohidrato_g_100g=carbohidrato,
            grasa_g_100g=grasa,
            medida_casera=medida,
            costo_quetzales_100g=costo,
        )
        for indice, (
            nombre,
            categoria,
            energia,
            proteina,
            carbohidrato,
            grasa,
            costo,
            medida,
        ) in enumerate(ALIMENTOS_INICIALES, start=1)
    ]


# Pares de energia y proteina que el sistema produce de verdad: la proteina sale
# de la regla del negocio *c*, entre 1.6 y 2.2 gramos por kilogramo de peso.
PLANES_REALES = [
    (1200, 100),  # mujer pequeña en pérdida de grasa, sobre el piso energético
    (1500, 120),  # hombre pequeño en pérdida de grasa
    (1800, 158),  # el caso que motivó la corrección
    (2000, 140),
    (2500, 150),
    (3000, 160),
    (3500, 180),  # hombre grande en ganancia muscular
]


@pytest.mark.parametrize(("energia", "proteina"), PLANES_REALES)
def test_el_menu_entrega_la_energia_que_el_plan_pide(energia, proteina):
    menu = generar_menu(energia, proteina, catalogo())

    assert menu.desviacion_energia <= DESVIACION_ADMITIDA, (
        f"el menú entregó {menu.energia_kcal} kcal para un plan de {energia}"
    )


@pytest.mark.parametrize("energia", range(1200, 4001, 200))
def test_la_fidelidad_se_sostiene_en_todo_el_dominio(energia):
    """Recorre el rango completo que los guardarrailes clinicos admiten."""
    menu = generar_menu(energia, round(energia * 0.09), catalogo())

    assert menu.desviacion_energia <= DESVIACION_ADMITIDA


def test_el_alimento_proteico_no_se_come_el_tiempo_de_comida():
    """Es la causa del desvio: la proteina desplazaba a todo lo demas."""
    menu = generar_menu(1200, 100, catalogo())

    for tiempo in menu.tiempos:
        proteicas = [
            porcion
            for porcion in tiempo.porciones
            if porcion.categoria
            in (
                CategoriaAlimento.PROTEINA_ANIMAL,
                CategoriaAlimento.LEGUMINOSA,
                CategoriaAlimento.LACTEO,
            )
        ]
        if not proteicas or not tiempo.energia_kcal:
            continue

        energia_proteica = sum(porcion.energia_kcal for porcion in proteicas)
        proporcion = energia_proteica / tiempo.energia_kcal
        assert proporcion <= PROPORCION_MAXIMA_PROTEICA_POR_TIEMPO + 0.20, (
            f"{tiempo.nombre}: la proteína ocupa el {proporcion:.0%} del tiempo"
        )


def test_la_energia_por_gramo_de_proteina_distingue_las_fuentes():
    """Es la medida con que el generador decide si un alimento cabe."""
    por_nombre = {alimento.nombre: alimento for alimento in catalogo()}

    pollo = energia_por_gramo_de_proteina(por_nombre["Pechuga de pollo"])
    garbanzo = energia_por_gramo_de_proteina(por_nombre["Garbanzo cocido"])

    assert pollo < garbanzo
    assert pollo == pytest.approx(165 / 31, rel=0.01)


def test_un_alimento_sin_proteina_nunca_se_elige_como_fuente_proteica():
    alimento = AlimentoDisponible(
        id=1,
        nombre="Aceite",
        categoria=CategoriaAlimento.GRASA,
        energia_kcal_100g=884,
        proteina_g_100g=0,
        carbohidrato_g_100g=0,
        grasa_g_100g=100,
    )

    assert energia_por_gramo_de_proteina(alimento) == float("inf")


def test_las_refacciones_llevan_algo_mas_que_fruta():
    """Una refaccion de solo fruta no es la que se come en el municipio.

    Ademas dejaba a cada refaccion en la mitad de la energia que le tocaba, y
    las comidas principales no podian absorber ese faltante sin llegar a su
    porcion maxima.
    """
    menu = generar_menu(2500, 150, catalogo())
    refacciones = [
        tiempo for tiempo in menu.tiempos if tiempo.nombre.startswith("Refacción")
    ]

    assert refacciones
    for refaccion in refacciones:
        assert len(refaccion.porciones) >= 2
        energia_esperada = 2500 * refaccion.proporcion
        # La refacción ya no queda a menos de la mitad de lo que le toca.
        assert refaccion.energia_kcal >= energia_esperada * 0.5


def test_el_menu_sigue_siendo_el_mismo_para_el_mismo_plan():
    """El plan debe ser auditable: mismo perfil, mismo menu."""
    primero = generar_menu(2200, 145, catalogo())
    segundo = generar_menu(2200, 145, catalogo())

    assert [
        (porcion.nombre, porcion.gramos)
        for tiempo in primero.tiempos
        for porcion in tiempo.porciones
    ] == [
        (porcion.nombre, porcion.gramos)
        for tiempo in segundo.tiempos
        for porcion in tiempo.porciones
    ]


def test_ninguna_porcion_resulta_impracticable():
    """Ni veinte gramos de tortilla ni un kilo de pollo."""
    for energia, proteina in PLANES_REALES:
        menu = generar_menu(energia, proteina, catalogo())
        for tiempo in menu.tiempos:
            for porcion in tiempo.porciones:
                assert 20 <= porcion.gramos <= 400, (
                    f"{porcion.nombre}: {porcion.gramos} g en {tiempo.nombre}"
                )
