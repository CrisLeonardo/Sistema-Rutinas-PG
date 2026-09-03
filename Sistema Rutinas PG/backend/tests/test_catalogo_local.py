"""Pruebas funcionales del catálogo local (historias HU-08 y HU-11).

Verifican la administración reservada al administrador, la selección de
alimentos y ejercicios del catálogo local, el sustituto de aporte equivalente y
la presentación de las cantidades en medidas caseras.
"""

import pytest

from app.esquemas.catalogo import NOMBRES_CATEGORIA
from app.esquemas.menu import PorcionPublica, pluralizar
from app.modelos.enumeraciones import CategoriaAlimento
from app.motor.menu import (
    MINIMO_ALIMENTOS_PARA_MENU,
    AlimentoDisponible,
    CatalogoDeAlimentosInsuficiente,
    buscar_sustituto,
    generar_menu,
)
from app.nucleo.alimentos_iniciales import ALIMENTOS_INICIALES
from tests.conftest import encabezado

RUTA_PERFIL = "/api/v1/perfil-biometrico"
RUTA_PLAN = "/api/v1/plan-nutricional"
RUTA_MENU = "/api/v1/plan-nutricional/menu"
RUTA_ALIMENTOS = "/api/v1/catalogos/alimentos"
RUTA_EJERCICIOS = "/api/v1/catalogos/ejercicios"

PERFIL_VALIDO = {
    "peso_kg": 80.0,
    "estatura_cm": 174.0,
    "edad": 28,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "mantenimiento",
    "nivel_experiencia": "intermedio",
    "dias_entrenamiento_semana": 4,
}

ALIMENTO_NUEVO = {
    "nombre": "Chipilín",
    "categoria": "verdura",
    "energia_kcal_100g": 45.0,
    "proteina_g_100g": 4.5,
    "carbohidrato_g_100g": 6.0,
    "grasa_g_100g": 0.8,
    "costo_aproximado_quetzales": 3.0,
    "medida_casera": "1 manojo ≈ 100 g",
    "disponible_localmente": True,
}

EJERCICIO_NUEVO = {
    "nombre": "Remo en máquina sentado",
    "grupo_muscular": "espalda",
    "nivel_minimo": "principiante",
    "equipamiento": "Máquina",
    "descripcion": "Sentado, jale el agarre hacia el abdomen.",
    "es_compuesto": True,
    "disponible_localmente": True,
}

CATALOGO = [
    AlimentoDisponible(
        id=posicion + 1,
        nombre=nombre,
        categoria=categoria,
        energia_kcal_100g=energia,
        proteina_g_100g=proteina,
        carbohidrato_g_100g=carbohidrato,
        grasa_g_100g=grasa,
        medida_casera=medida,
    )
    for posicion, (
        nombre,
        categoria,
        energia,
        proteina,
        carbohidrato,
        grasa,
        _costo,
        medida,
    ) in enumerate(ALIMENTOS_INICIALES)
]


@pytest.fixture(name="con_plan")
def fixture_con_plan(cliente, token_usuario):
    """Deja al usuario con perfil y plan, que arrastra consigo el menú."""
    cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario))
    assert cliente.post(RUTA_PLAN, headers=encabezado(token_usuario)).status_code == 201
    return token_usuario


# --------------------------------------------------------------------------
# HU-11. Administración de catálogos maestros
# --------------------------------------------------------------------------


def test_el_catalogo_inicial_se_carga_al_arrancar(cliente, token_usuario):
    """Sin catálogo poblado no se podrían generar planes ni rutinas."""
    alimentos = cliente.get(RUTA_ALIMENTOS, headers=encabezado(token_usuario)).json()
    ejercicios = cliente.get(RUTA_EJERCICIOS, headers=encabezado(token_usuario)).json()

    assert len(alimentos) >= MINIMO_ALIMENTOS_PARA_MENU
    assert len(ejercicios) >= 20


def test_el_catalogo_cubre_todas_las_categorias_de_alimento(cliente, token_usuario):
    """Un catálogo sin alguna categoría produciría menús incompletos."""
    alimentos = cliente.get(RUTA_ALIMENTOS, headers=encabezado(token_usuario)).json()
    categorias = {alimento["categoria"] for alimento in alimentos}

    assert categorias == {categoria.value for categoria in CategoriaAlimento}


def test_solo_el_administrador_da_de_alta_alimentos(cliente, token_usuario):
    """El alta está reservada al administrador (criterio de HU-11)."""
    respuesta = cliente.post(
        RUTA_ALIMENTOS, json=ALIMENTO_NUEVO, headers=encabezado(token_usuario)
    )

    assert respuesta.status_code == 403


def test_solo_el_administrador_da_de_alta_ejercicios(cliente, token_usuario):
    """La misma restricción aplica al catálogo de ejercicios."""
    respuesta = cliente.post(
        RUTA_EJERCICIOS, json=EJERCICIO_NUEVO, headers=encabezado(token_usuario)
    )

    assert respuesta.status_code == 403


def test_el_administrador_da_de_alta_un_alimento(cliente, token_administrador):
    """Alta de alimentos, reservada al administrador."""
    respuesta = cliente.post(
        RUTA_ALIMENTOS, json=ALIMENTO_NUEVO, headers=encabezado(token_administrador)
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == ALIMENTO_NUEVO["nombre"]
    assert cuerpo["nombre_categoria"] == NOMBRES_CATEGORIA[CategoriaAlimento.VERDURA]


def test_el_administrador_modifica_un_alimento(cliente, token_administrador):
    """Modificación de alimentos."""
    creado = cliente.post(
        RUTA_ALIMENTOS, json=ALIMENTO_NUEVO, headers=encabezado(token_administrador)
    ).json()

    respuesta = cliente.put(
        f"{RUTA_ALIMENTOS}/{creado['id']}",
        json={**ALIMENTO_NUEVO, "costo_aproximado_quetzales": 5.0},
        headers=encabezado(token_administrador),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["costo_aproximado_quetzales"] == 5.0


def test_la_baja_de_un_alimento_es_logica(cliente, token_administrador):
    """El alimento se marca como no disponible en lugar de borrarse.

    Los planes ya generados lo referencian: borrarlo los dejaría incompletos.
    """
    creado = cliente.post(
        RUTA_ALIMENTOS, json=ALIMENTO_NUEVO, headers=encabezado(token_administrador)
    ).json()

    respuesta = cliente.put(
        f"{RUTA_ALIMENTOS}/{creado['id']}/disponibilidad",
        json={"activo": False},
        headers=encabezado(token_administrador),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["disponible_localmente"] is False

    todos = cliente.get(RUTA_ALIMENTOS, headers=encabezado(token_administrador)).json()
    disponibles = cliente.get(
        f"{RUTA_ALIMENTOS}?solo_disponibles=true", headers=encabezado(token_administrador)
    ).json()

    assert creado["id"] in {alimento["id"] for alimento in todos}
    assert creado["id"] not in {alimento["id"] for alimento in disponibles}


def test_no_se_admiten_dos_alimentos_con_el_mismo_nombre(cliente, token_administrador):
    """El nombre identifica al alimento en el catálogo."""
    cliente.post(RUTA_ALIMENTOS, json=ALIMENTO_NUEVO, headers=encabezado(token_administrador))

    repetido = cliente.post(
        RUTA_ALIMENTOS, json=ALIMENTO_NUEVO, headers=encabezado(token_administrador)
    )

    assert repetido.status_code == 409


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("energia_kcal_100g", -1),
        ("energia_kcal_100g", 950),
        ("proteina_g_100g", 101),
        ("grasa_g_100g", -5),
        ("costo_aproximado_quetzales", -2),
        ("nombre", "x"),
    ],
)
def test_el_alta_de_alimentos_valida_sus_campos(cliente, token_administrador, campo, valor):
    """Un dato fuera de rango produciría planes con cifras imposibles."""
    respuesta = cliente.post(
        RUTA_ALIMENTOS,
        json={**ALIMENTO_NUEVO, campo: valor},
        headers=encabezado(token_administrador),
    )

    assert respuesta.status_code == 422


def test_el_administrador_da_de_alta_y_modifica_un_ejercicio(cliente, token_administrador):
    """Alta y modificación de ejercicios, reservadas al administrador."""
    creado = cliente.post(
        RUTA_EJERCICIOS, json=EJERCICIO_NUEVO, headers=encabezado(token_administrador)
    )
    assert creado.status_code == 201

    modificado = cliente.put(
        f"{RUTA_EJERCICIOS}/{creado.json()['id']}",
        json={**EJERCICIO_NUEVO, "equipamiento": "Polea"},
        headers=encabezado(token_administrador),
    )

    assert modificado.status_code == 200
    assert modificado.json()["equipamiento"] == "Polea"


def test_la_baja_de_un_ejercicio_lo_retira_de_las_rutinas_nuevas(
    cliente, token_administrador, token_usuario
):
    """Un ejercicio dado de baja deja de proponerse en los planes nuevos."""
    ejercicios = cliente.get(
        f"{RUTA_EJERCICIOS}?grupo_muscular=pecho", headers=encabezado(token_administrador)
    ).json()
    a_retirar = ejercicios[0]

    cliente.put(
        f"{RUTA_EJERCICIOS}/{a_retirar['id']}/disponibilidad",
        json={"activo": False},
        headers=encabezado(token_administrador),
    )

    cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario))
    cliente.post(RUTA_PLAN, headers=encabezado(token_usuario))
    rutina = cliente.get("/api/v1/rutina", headers=encabezado(token_usuario)).json()

    prescritos = {
        ejercicio["nombre"] for sesion in rutina["sesiones"] for ejercicio in sesion["ejercicios"]
    }
    assert a_retirar["nombre"] not in prescritos


def test_modificar_un_elemento_inexistente_devuelve_no_encontrado(cliente, token_administrador):
    """El sistema lo dice en lugar de fallar de forma opaca."""
    respuesta = cliente.put(
        f"{RUTA_ALIMENTOS}/9999", json=ALIMENTO_NUEVO, headers=encabezado(token_administrador)
    )

    assert respuesta.status_code == 404


def test_el_catalogo_se_puede_filtrar_por_categoria(cliente, token_usuario):
    """El filtro permite al usuario buscar alternativas de un mismo grupo."""
    frutas = cliente.get(
        f"{RUTA_ALIMENTOS}?categoria=fruta", headers=encabezado(token_usuario)
    ).json()

    assert frutas
    assert all(alimento["categoria"] == "fruta" for alimento in frutas)


def test_sin_sesion_no_se_consulta_el_catalogo(cliente):
    """La consulta requiere cuenta, aunque no rol de administrador."""
    assert cliente.get(RUTA_ALIMENTOS).status_code == 401
    assert cliente.get(RUTA_EJERCICIOS).status_code == 401


# --------------------------------------------------------------------------
# HU-08. Selección de alimentos del catálogo local
# --------------------------------------------------------------------------


def test_generar_el_plan_produce_tambien_el_menu(cliente, con_plan):
    """El plan que el usuario pidió incluye qué comer, no solo cuánta energía."""
    respuesta = cliente.get(RUTA_MENU, headers=encabezado(con_plan))

    assert respuesta.status_code == 200
    menu = respuesta.json()
    assert len(menu["tiempos"]) == 5


def test_todos_los_alimentos_propuestos_existen_en_el_catalogo(cliente, con_plan):
    """Criterio de aceptación: todo alimento propuesto está en el catálogo local."""
    menu = cliente.get(RUTA_MENU, headers=encabezado(con_plan)).json()
    catalogo = cliente.get(RUTA_ALIMENTOS, headers=encabezado(con_plan)).json()
    identificadores = {alimento["id"] for alimento in catalogo}

    propuestos = {
        porcion["alimento_id"] for tiempo in menu["tiempos"] for porcion in tiempo["porciones"]
    }
    assert propuestos
    assert propuestos <= identificadores


def test_cada_porcion_ofrece_un_sustituto_equivalente(cliente, con_plan):
    """Criterio de aceptación: sustituto con aporte nutricional equivalente."""
    menu = cliente.get(RUTA_MENU, headers=encabezado(con_plan)).json()

    for tiempo in menu["tiempos"]:
        for porcion in tiempo["porciones"]:
            assert porcion["sustituto"] is not None
            assert porcion["sustituto"]["alimento_id"] != porcion["alimento_id"]
            assert porcion["sustituto"]["gramos"] > 0


def test_las_cantidades_se_presentan_en_medidas_caseras(cliente, con_plan):
    """Criterio de aceptación: las cantidades también en medidas caseras."""
    menu = cliente.get(RUTA_MENU, headers=encabezado(con_plan)).json()

    con_medida = [
        porcion
        for tiempo in menu["tiempos"]
        for porcion in tiempo["porciones"]
        if porcion["cantidad_en_medida_casera"]
    ]
    assert con_medida
    for porcion in con_medida:
        assert porcion["gramos"] > 0
        assert porcion["cantidad_en_medida_casera"]


def test_el_menu_se_aproxima_a_la_energia_del_plan(cliente, con_plan):
    """El menú debe entregar la energía que el plan prescribe."""
    menu = cliente.get(RUTA_MENU, headers=encabezado(con_plan)).json()

    assert menu["desviacion_energia_porcentaje"] < 10


def test_el_menu_propone_variedad_de_alimentos(cliente, con_plan):
    """Un menú que repitiera el mismo alimento sería impracticable."""
    menu = cliente.get(RUTA_MENU, headers=encabezado(con_plan)).json()

    assert menu["alimentos_distintos"] >= 5


def test_el_menu_solo_es_visible_para_su_titular(cliente, con_plan, token_segundo_usuario):
    """Regla del negocio f, verificada también sobre el menú."""
    ajeno = cliente.get(RUTA_MENU, headers=encabezado(token_segundo_usuario))

    assert ajeno.status_code == 404


def test_sin_sesion_no_se_consulta_el_menu(cliente):
    """La validación de acceso ocurre en el servidor."""
    assert cliente.get(RUTA_MENU).status_code == 401


# --------------------------------------------------------------------------
# Generador de menú, verificado sin base de datos
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("energia", "proteina"), [(1800, 140), (2300, 180), (2800, 190), (3200, 200)]
)
def test_el_menu_generado_se_acerca_a_los_objetivos(energia, proteina):
    """El reparto debe entregar la energía y la proteína que el plan prescribe."""
    menu = generar_menu(energia, proteina, CATALOGO)

    assert menu.desviacion_energia < 0.10
    assert menu.proteina_g >= proteina * 0.85


def test_el_menu_reparte_en_los_cinco_tiempos_de_comida():
    """Sigue la estructura de comidas habitual del municipio."""
    menu = generar_menu(2300, 180, CATALOGO)

    assert [tiempo.nombre for tiempo in menu.tiempos] == [
        "Desayuno",
        "Refacción de la mañana",
        "Almuerzo",
        "Refacción de la tarde",
        "Cena",
    ]
    assert all(tiempo.porciones for tiempo in menu.tiempos)


def test_las_porciones_de_verdura_y_fruta_son_practicables():
    """Dimensionarlas por energía produciría porciones absurdas."""
    menu = generar_menu(2300, 180, CATALOGO)

    frescos = [
        porcion
        for tiempo in menu.tiempos
        for porcion in tiempo.porciones
        if porcion.categoria in (CategoriaAlimento.VERDURA, CategoriaAlimento.FRUTA)
    ]
    assert frescos
    assert all(porcion.gramos <= 200 for porcion in frescos)


def test_las_porciones_de_grasa_estan_acotadas():
    """El aceite es muy denso: una porción grande desbalancearía el plan."""
    menu = generar_menu(2300, 180, CATALOGO)

    grasas = [
        porcion
        for tiempo in menu.tiempos
        for porcion in tiempo.porciones
        if porcion.categoria == CategoriaAlimento.GRASA
    ]
    assert all(porcion.gramos <= 30 for porcion in grasas)


def test_el_menu_es_reproducible():
    """El mismo perfil produce el mismo menú, lo que hace el plan auditable."""
    primero = generar_menu(2300, 180, CATALOGO)
    segundo = generar_menu(2300, 180, CATALOGO)

    assert [
        (porcion.nombre, porcion.gramos)
        for tiempo in primero.tiempos
        for porcion in tiempo.porciones
    ] == [
        (porcion.nombre, porcion.gramos)
        for tiempo in segundo.tiempos
        for porcion in tiempo.porciones
    ]


def test_el_sustituto_pertenece_a_la_misma_categoria_cuando_la_hay():
    """Un sustituto de otra categoría desbalancearía el tiempo de comida."""
    pollo = next(
        alimento for alimento in CATALOGO if alimento.nombre == "Pechuga de pollo"
    )

    sustituto = buscar_sustituto(pollo, 150, CATALOGO)

    assert sustituto is not None
    reemplazo = next(
        alimento for alimento in CATALOGO if alimento.id == sustituto.alimento_id
    )
    assert reemplazo.categoria == pollo.categoria


def test_el_sustituto_aporta_una_energia_parecida():
    """Aporte nutricional equivalente, no un alimento cualquiera."""
    arroz = next(
        alimento for alimento in CATALOGO if alimento.nombre == "Arroz blanco cocido"
    )

    sustituto = buscar_sustituto(arroz, 150, CATALOGO)
    energia_original = arroz.energia_de(150)

    assert sustituto is not None
    assert abs(sustituto.energia_kcal - energia_original) / energia_original < 0.30


def test_un_catalogo_demasiado_pequeno_no_produce_menu():
    """El sistema lo dice en lugar de proponer un menú incompleto."""
    with pytest.raises(CatalogoDeAlimentosInsuficiente):
        generar_menu(2300, 180, CATALOGO[:3])


# --------------------------------------------------------------------------
# Presentacion de las cantidades en medidas caseras
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("medida", "gramos", "esperado"),
    [
        ("1 pan ≈ 50 g", 195, "4 panes"),
        ("1 pan ≈ 50 g", 50, "1 pan"),
        ("1 filete ≈ 120 g", 60, "medio filete"),
        ("1/2 taza ≈ 90 g", 400, "2 tazas"),
        ("1 unidad mediana ≈ 120 g", 150, "1 unidad mediana"),
        ("1 unidad mediana ≈ 120 g", 240, "2 unidades medianas"),
        ("1 taza en cubos ≈ 145 g", 300, "2 tazas en cubos"),
        ("1 puño ≈ 30 g", 20, "medio puño"),
        ("1 porción ≈ 100 g", 250, "2.5 porciones"),
        ("1 tortilla ≈ 30 g", 90, "3 tortillas"),
    ],
)
def test_la_medida_casera_concuerda_en_numero_y_genero(medida, gramos, esperado):
    """La cantidad se presenta con el plural y el género que corresponden.

    «4 pan» o «media filete» delatarían que el texto se arma concatenando, y el
    requerimiento 4.5.3 exige que la interfaz se lea con naturalidad.
    """
    porcion = PorcionPublica(
        alimento_id=1,
        nombre="Alimento de prueba",
        categoria=CategoriaAlimento.CEREAL,
        gramos=gramos,
        energia_kcal=100,
        proteina_g=5,
        carbohidrato_g=20,
        grasa_g=1,
        medida_casera=medida,
    )

    assert porcion.cantidad_en_medida_casera == esperado


def test_sin_medida_casera_registrada_no_se_inventa_una():
    """Un alimento sin medida casera se presenta solo en gramos."""
    porcion = PorcionPublica(
        alimento_id=1,
        nombre="Alimento sin medida",
        categoria=CategoriaAlimento.CEREAL,
        gramos=100,
        energia_kcal=100,
        proteina_g=5,
        carbohidrato_g=20,
        grasa_g=1,
        medida_casera=None,
    )

    assert porcion.cantidad_en_medida_casera is None


@pytest.mark.parametrize(
    ("palabra", "plural"),
    [
        ("porción", "porciones"),
        ("taza", "tazas"),
        ("pan", "panes"),
        ("unidad", "unidades"),
        ("vez", "veces"),
    ],
)
def test_la_pluralizacion_cubre_los_casos_del_catalogo(palabra, plural):
    """Las unidades del catálogo se pluralizan según las reglas del español."""
    assert pluralizar(palabra) == plural
