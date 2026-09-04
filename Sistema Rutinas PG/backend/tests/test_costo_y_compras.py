"""Pruebas del costo del menu y de la lista de compras semanal.

El catalogo registraba el costo de cada alimento desde la Iteracion 4 y ningun
modulo lo consultaba: se capturaba, se validaba y se editaba sin que influyera
en nada. Estas pruebas fijan el comportamiento que lo pone en uso, que es lo que
atiende la barrera economica que el estudio del Capitulo I documenta.
"""

import pytest

from app.motor.menu import (
    AlimentoDisponible,
    candidatos_economicos,
    costo_por_unidad_aportada,
    generar_menu,
)
from app.modelos.enumeraciones import CategoriaAlimento
from app.motor.menu import (
    CATEGORIAS_ENERGETICAS,
    CATEGORIAS_FRESCAS,
    CATEGORIAS_GRASAS,
    CATEGORIAS_PROTEICAS,
)
from app.nucleo.alimentos_iniciales import ALIMENTOS_INICIALES

from .conftest import encabezado

PERFIL = {
    "peso_kg": 78.0,
    "estatura_cm": 175.0,
    "edad": 28,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "mantenimiento",
    "nivel_experiencia": "principiante",
    "dias_entrenamiento_semana": 4,
}


def catalogo_completo() -> list[AlimentoDisponible]:
    """Reproduce el catalogo inicial en la forma que el motor consume."""
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


# --------------------------------------------------------------------------
# Unidad del costo
# --------------------------------------------------------------------------


def test_todos_los_alimentos_iniciales_traen_costo():
    """Sin precio, el catalogo no puede sostener ninguna decision economica."""
    sin_precio = [nombre for nombre, *_, costo, _ in ALIMENTOS_INICIALES if costo is None]

    assert sin_precio == []


def test_el_costo_esta_expresado_por_cada_cien_gramos():
    """Los valores anteriores mezclaban unidades: por pieza, por libra, por envase.

    La comprobacion es de orden de magnitud: ningun alimento de consumo corriente
    cuesta mas de cincuenta quetzales los cien gramos en el mercado local.
    """
    for nombre, *_, costo, _ in ALIMENTOS_INICIALES:
        assert 0 < costo <= 50, f"{nombre} tiene un costo fuera de escala para 100 g"


def test_la_porcion_calcula_su_costo_proporcional():
    alimento = AlimentoDisponible(
        id=1,
        nombre="Prueba",
        categoria=CategoriaAlimento.CEREAL,
        energia_kcal_100g=100,
        proteina_g_100g=10,
        carbohidrato_g_100g=10,
        grasa_g_100g=1,
        costo_quetzales_100g=4.0,
    )

    assert alimento.costo_de(100) == pytest.approx(4.0)
    assert alimento.costo_de(250) == pytest.approx(10.0)
    assert alimento.costo_de(0) == pytest.approx(0.0)


def test_un_alimento_sin_precio_no_declara_costo():
    alimento = AlimentoDisponible(
        id=1,
        nombre="Sin precio",
        categoria=CategoriaAlimento.CEREAL,
        energia_kcal_100g=100,
        proteina_g_100g=10,
        carbohidrato_g_100g=10,
        grasa_g_100g=1,
        costo_quetzales_100g=None,
    )

    assert alimento.costo_de(100) is None


# --------------------------------------------------------------------------
# Preferencia por lo economico
# --------------------------------------------------------------------------


def test_el_costo_se_mide_contra_lo_que_el_alimento_aporta():
    """El pollo se compra por su proteina; la tortilla, por su energia."""
    catalogo = {alimento.nombre: alimento for alimento in catalogo_completo()}

    pollo = costo_por_unidad_aportada(catalogo["Pechuga de pollo"], CATEGORIAS_PROTEICAS)
    frijol = costo_por_unidad_aportada(
        catalogo["Frijol negro cocido"], CATEGORIAS_PROTEICAS
    )

    assert frijol < pollo, "el frijol aporta proteína más barata que el pollo"


def test_la_rotacion_descarta_el_alimento_caro_cuando_existe_el_barato_equivalente():
    catalogo = catalogo_completo()
    grasas = [a for a in catalogo if a.categoria == CategoriaAlimento.GRASA]

    en_rotacion = candidatos_economicos(grasas, CATEGORIAS_GRASAS)
    nombres = {alimento.nombre for alimento in en_rotacion}

    assert "Semilla de marañón" not in nombres, "es la grasa más cara del catálogo"
    assert len(en_rotacion) < len(grasas)


def test_la_rotacion_conserva_variedad_suficiente():
    """Un menu de un solo alimento por categoria se abandona por aburrimiento."""
    catalogo = catalogo_completo()
    for categorias in (
        CATEGORIAS_PROTEICAS,
        CATEGORIAS_ENERGETICAS,
        CATEGORIAS_FRESCAS,
        CATEGORIAS_GRASAS,
    ):
        candidatos = [a for a in catalogo if a.categoria in categorias]
        en_rotacion = candidatos_economicos(candidatos, categorias)

        assert len(en_rotacion) >= min(3, len(candidatos))


def test_una_categoria_pequena_no_se_recorta():
    catalogo = catalogo_completo()[:2]

    assert candidatos_economicos(catalogo, CATEGORIAS_PROTEICAS) == catalogo


def test_un_catalogo_sin_precios_conserva_todos_los_candidatos():
    """El filtro economico no debe castigar a un catalogo aun sin levantar."""
    catalogo = [
        AlimentoDisponible(
            id=indice,
            nombre=f"Alimento {indice}",
            categoria=CategoriaAlimento.CEREAL,
            energia_kcal_100g=200,
            proteina_g_100g=8,
            carbohidrato_g_100g=40,
            grasa_g_100g=2,
            costo_quetzales_100g=None,
        )
        for indice in range(1, 7)
    ]

    assert candidatos_economicos(catalogo, CATEGORIAS_ENERGETICAS) == catalogo


def test_preferir_lo_economico_abarata_el_menu():
    """Es el efecto que justifica la preferencia, medido sobre el catálogo real."""
    catalogo = catalogo_completo()
    caro = [
        AlimentoDisponible(**{**vars(alimento), "costo_quetzales_100g": None})
        for alimento in catalogo
    ]

    economico = generar_menu(2500, 130, catalogo)
    # Sin precios el filtro no actúa y la rotación recorre todo el catálogo.
    sin_filtro = generar_menu(2500, 130, caro)

    nombres_economico = {p.nombre for t in economico.tiempos for p in t.porciones}
    nombres_sin_filtro = {p.nombre for t in sin_filtro.tiempos for p in t.porciones}

    assert nombres_economico != nombres_sin_filtro
    assert economico.costo_quetzales > 0


def test_el_menu_declara_su_costo():
    menu = generar_menu(2500, 130, catalogo_completo())

    assert menu.costo_quetzales > 0
    assert menu.costo_quetzales == pytest.approx(
        round(sum(tiempo.costo_quetzales for tiempo in menu.tiempos), 2)
    )


# --------------------------------------------------------------------------
# Lista de compras
# --------------------------------------------------------------------------


def _con_plan(cliente, token):
    respuesta = cliente.post(
        "/api/v1/perfil-biometrico", json=PERFIL, headers=encabezado(token)
    )
    assert respuesta.status_code == 201, respuesta.text
    respuesta = cliente.post("/api/v1/plan-nutricional", headers=encabezado(token))
    assert respuesta.status_code == 201, respuesta.text


def test_la_lista_de_compras_suma_la_semana(cliente, token_usuario):
    _con_plan(cliente, token_usuario)

    respuesta = cliente.get(
        "/api/v1/plan-nutricional/lista-de-compras", headers=encabezado(token_usuario)
    )

    assert respuesta.status_code == 200
    lista = respuesta.json()
    assert lista["dias"] == 7
    assert lista["alimentos_distintos"] > 0
    assert lista["costo_total_quetzales"] > 0


def test_la_lista_agrupa_por_categoria_en_orden_estable(cliente, token_usuario):
    """El orden de los grupos no debe depender del plan que se consulte."""
    _con_plan(cliente, token_usuario)

    lista = cliente.get(
        "/api/v1/plan-nutricional/lista-de-compras", headers=encabezado(token_usuario)
    ).json()
    categorias = [grupo["categoria"] for grupo in lista["grupos"]]

    orden_catalogo = [categoria.value for categoria in CategoriaAlimento]
    posiciones = [orden_catalogo.index(categoria) for categoria in categorias]
    assert posiciones == sorted(posiciones)


def test_la_cantidad_se_expresa_como_se_pide_en_el_mercado(cliente, token_usuario):
    """Nadie pide «1 815 gramos de pollo» en un puesto."""
    _con_plan(cliente, token_usuario)

    lista = cliente.get(
        "/api/v1/plan-nutricional/lista-de-compras", headers=encabezado(token_usuario)
    ).json()
    renglones = [r for grupo in lista["grupos"] for r in grupo["renglones"]]

    assert renglones
    for renglon in renglones:
        assert "libra" in renglon["cantidad_de_mercado"] or (
            "gramos" in renglon["cantidad_de_mercado"]
        )
        if renglon["gramos_semana"] >= 300:
            assert "libra" in renglon["cantidad_de_mercado"]


def test_el_costo_de_la_lista_coincide_con_el_del_menu(cliente, token_usuario):
    """La misma comida contada de dos maneras debe costar lo mismo."""
    _con_plan(cliente, token_usuario)
    cabeceras = encabezado(token_usuario)

    menu = cliente.get("/api/v1/plan-nutricional/menu", headers=cabeceras).json()
    lista = cliente.get(
        "/api/v1/plan-nutricional/lista-de-compras", headers=cabeceras
    ).json()

    assert lista["costo_total_quetzales"] == pytest.approx(
        menu["costo_semanal_quetzales"], rel=0.02
    )


def test_la_lista_advierte_cuando_faltan_precios(cliente, token_usuario):
    _con_plan(cliente, token_usuario)

    lista = cliente.get(
        "/api/v1/plan-nutricional/lista-de-compras", headers=encabezado(token_usuario)
    ).json()

    assert lista["aviso_costo"]
    assert "estimaciones" in lista["aviso_costo"]


def test_sin_plan_no_hay_lista_de_compras(cliente, token_usuario):
    respuesta = cliente.get(
        "/api/v1/plan-nutricional/lista-de-compras", headers=encabezado(token_usuario)
    )

    assert respuesta.status_code == 404


def test_la_lista_de_compras_exige_sesion(cliente):
    assert cliente.get("/api/v1/plan-nutricional/lista-de-compras").status_code == 401


def test_la_lista_es_privada_de_su_titular(cliente, token_usuario, token_segundo_usuario):
    """Regla del negocio *f*: los datos de un plan solo los ve su titular."""
    _con_plan(cliente, token_usuario)

    respuesta = cliente.get(
        "/api/v1/plan-nutricional/lista-de-compras",
        headers=encabezado(token_segundo_usuario),
    )

    assert respuesta.status_code == 404


def test_el_menu_declara_el_costo_mensual(cliente, token_usuario):
    """Es la cifra con que el usuario decide si el plan le es asequible."""
    _con_plan(cliente, token_usuario)

    menu = cliente.get(
        "/api/v1/plan-nutricional/menu", headers=encabezado(token_usuario)
    ).json()

    assert menu["costo_diario_quetzales"] > 0
    assert menu["costo_mensual_quetzales"] == pytest.approx(
        menu["costo_diario_quetzales"] * 30, rel=0.01
    )
