"""MEJ-08/09: exclusiones, coherencia de semana, compras y aislamiento."""
from collections import defaultdict
from dataclasses import replace
from copy import deepcopy

import pytest
from sqlalchemy import select

from app.esquemas.alimentacion import PreferenciasEntrada
from app.modelos.alimentacion import SemanaAlimentaria
from app.modelos.catalogo import Alimento
from app.motor import semana_alimentaria as motor
from app.nucleo.recetas import RECETAS
from app.servicios.restricciones_alimentarias import compatible, filtrar
from tests.conftest import encabezado
from tests.test_fidelidad_del_menu import catalogo
from tests.test_plan_nutricional import PERFIL_VALIDO

RUTA = "/api/v1/alimentacion"
OBJETIVO = dict(energia_kcal=2500, proteina_g=150, carbohidrato_g=300, grasa_g=78)


@pytest.fixture
def alimentado(cliente, token_usuario, monkeypatch):
    monkeypatch.setattr("app.servicios.plan.obtener_motor", lambda: None)
    headers = encabezado(token_usuario)
    assert cliente.post("/api/v1/perfil-biometrico", json=PERFIL_VALIDO, headers=headers).status_code == 201
    assert cliente.post("/api/v1/plan-nutricional", headers=headers).status_code == 201
    return headers


def preparar(cliente, headers):
    respuesta = cliente.post(f"{RUTA}/semana", headers=headers)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


@pytest.mark.parametrize("clave", ["leche", "huevo", "pescado", "mani", "frutos_secos", "trigo", "soya", "sesamo", "crustaceos"])
def test_exclusion_alergenos_en_ingredientes_y_recetas(clave):
    alimentos = filtrar(catalogo(), PreferenciasEntrada(alergias=[clave]))
    recetas, por_nombre = motor.disponibles_para_recetas(alimentos)
    assert recetas
    for receta in recetas:
        for nombre, _ in receta.ingredientes:
            assert compatible(por_nombre[nombre], PreferenciasEntrada(alergias=[clave]))
    if clave == "leche":
        assert not any(a.nombre in {"Leche entera", "Queso fresco", "Yogur natural"} for a in alimentos)


@pytest.mark.parametrize("clave", ["lactosa", "gluten"])
def test_exclusion_intolerancias(clave):
    opciones = PreferenciasEntrada(intolerancias=[clave])
    alimentos = filtrar(catalogo(), opciones)
    assert alimentos
    prohibidos = {"Leche entera", "Queso fresco", "Yogur natural"} if clave == "lactosa" else {"Pan francés", "Avena en hojuelas", "Pasta cocida", "Incaparina en polvo"}
    assert not prohibidos.intersection(a.nombre for a in alimentos)


def test_desconocido_y_nombre_parecido_no_heredan_composicion():
    original = catalogo()[0]
    desconocidos = [replace(original, nombre="Tortilla de maíz con queso"), replace(original, proteina_g_100g=99)]
    for alimento in desconocidos:
        assert not compatible(alimento, PreferenciasEntrada(alergias=["leche"]))
        assert not compatible(alimento, PreferenciasEntrada(patron="vegano"))


def test_vegano_vegetariano_y_gusto_no_se_equiparan_a_alergia():
    todos = catalogo()
    veganos = filtrar(todos, PreferenciasEntrada(patron="vegano"))
    vegetarianos = filtrar(todos, PreferenciasEntrada(patron="vegetariano"))
    assert "Huevo de gallina" not in {a.nombre for a in veganos}
    assert "Huevo de gallina" in {a.nombre for a in vegetarianos}
    assert "Pechuga de pollo" not in {a.nombre for a in vegetarianos}
    assert not compatible(todos[0], PreferenciasEntrada(alimentos_excluidos=[todos[0].id]))


@pytest.mark.parametrize("energia,proteina,carbohidrato,grasa", [(2000, 140, 225, 60), (2500, 150, 300, 78), (3500, 180, 450, 110)])
def test_siete_dias_con_aportes_reparto_variedad_y_compras(energia, proteina, carbohidrato, grasa):
    objetivo = dict(energia_kcal=energia, proteina_g=proteina, carbohidrato_g=carbohidrato, grasa_g=grasa)
    semana = motor.generar(objetivo, catalogo())
    assert len(semana["dias"]) == 7
    gramos = defaultdict(int)
    menus = set()
    for dia in semana["dias"]:
        assert len(dia["tiempos"]) == 5
        assert motor.dentro(motor.totales(dia["tiempos"]), objetivo)
        menus.add(tuple(t["receta_id"] for t in dia["tiempos"]))
        for i, t in enumerate(dia["tiempos"]):
            esperado = energia * motor.TIEMPOS_DE_COMIDA[i][1]
            assert abs(t["energia_kcal"] / esperado - 1) <= motor.TOLERANCIA
            for p in t["porciones"]:
                gramos[p["alimento_id"]] += p["gramos"]
                assert p["estado"] and p["gramos"] > 0
    assert len(menus) >= 5
    assert {r["alimento_id"]: r["gramos_semana"] for r in motor.compras(semana)["renglones"]} == gramos
    assert motor.generar(objetivo, catalogo()) == semana


def test_precios_desconocidos_no_se_convierten_en_cero():
    alimentos = [replace(a, costo_quetzales_100g=None) for a in catalogo()]
    semana = motor.generar(OBJETIVO, alimentos)
    compras = motor.compras(semana)
    assert compras["costo_quetzales"] is None
    assert all(r["costo_quetzales"] is None for r in compras["renglones"])


def test_el_margen_no_permite_un_gramo_extra_en_aportes_pequenos():
    objetivo = dict(energia_kcal=200, proteina_g=4, carbohidrato_g=30, grasa_g=6)
    assert not motor.dentro({**objetivo, "proteina_g": 4.8}, objetivo)
    assert motor.dentro({**objetivo, "proteina_g": 4.2}, objetivo)


def test_recetas_editoriales_tienen_ingredientes_y_estado_sin_revision_inventada():
    assert len(RECETAS) == 18
    assert len({r.id for r in RECETAS}) == 18
    recetas, _ = motor.disponibles_para_recetas(catalogo())
    assert len(recetas) == 18
    assert all(r.estado_revision == "revisada" and r.rendimiento_porciones == 1 and r.pasos for r in recetas)


@pytest.mark.parametrize("ruta", ["/preferencias", "/recetas", "/semana", "/alternativas?dia=1&tiempo=0"])
def test_lecturas_requieren_cuenta(cliente, ruta):
    assert cliente.get(RUTA + ruta).status_code == 401


def test_mutaciones_requieren_cuenta(cliente):
    assert cliente.post(f"{RUTA}/semana").status_code == 401
    assert cliente.put(f"{RUTA}/preferencias", json={}).status_code == 401
    assert cliente.put(f"{RUTA}/semana/comida", json=dict(revision=1, dia=1, tiempo=0, receta_id="huevo-frijol")).status_code == 401


@pytest.mark.parametrize("datos", [{"alergias": ["inventada"]}, {"intolerancias": ["leche"]}, {"patron": "libre"}, {"alimentos_excluidos": [-1]}, {"alimentos_excluidos": [999999]}, {"usuario_id": 2}])
def test_rechaza_restricciones_no_estructuradas(cliente, token_usuario, datos):
    assert cliente.put(f"{RUTA}/preferencias", json=datos, headers=encabezado(token_usuario)).status_code == 422


def test_preferencias_privadas_y_normalizadas(cliente, token_usuario, token_segundo_usuario):
    h1, h2 = encabezado(token_usuario), encabezado(token_segundo_usuario)
    respuesta = cliente.put(f"{RUTA}/preferencias", json={"alergias": ["leche", "leche"]}, headers=h1)
    assert respuesta.status_code == 200
    assert cliente.get(f"{RUTA}/preferencias", headers=h1).json()["preferencias"]["alergias"] == ["leche"]
    assert cliente.get(f"{RUTA}/preferencias", headers=h2).json()["preferencias"]["alergias"] == []


def test_semana_persistente_cambio_recalcula_y_rechaza_revision_antigua(cliente, alimentado):
    original = preparar(cliente, alimentado)
    assert cliente.get(f"{RUTA}/semana", headers=alimentado).json() == original
    opciones = cliente.get(f"{RUTA}/alternativas?dia=1&tiempo=2", headers=alimentado).json()
    assert opciones["opciones"]
    cambio = dict(revision=original["revision"], dia=1, tiempo=2, receta_id=opciones["opciones"][0]["receta_id"])
    respuesta = cliente.put(f"{RUTA}/semana/comida", json=cambio, headers=alimentado)
    assert respuesta.status_code == 200, respuesta.text
    nueva = respuesta.json()
    assert nueva["revision"] == original["revision"] + 1
    assert nueva["dias"][1:] == original["dias"][1:]
    assert nueva["compras"] != original["compras"]
    assert motor.dentro(nueva["dias"][0], nueva["objetivo"])
    assert cliente.put(f"{RUTA}/semana/comida", json=cambio, headers=alimentado).status_code == 409
    assert cliente.get(f"{RUTA}/semana", headers=alimentado).json() == nueva
    # El cliente antiguo de compras obtiene los mismos gramos, sin multiplicar día 1 por 7.
    antigua = cliente.get("/api/v1/plan-nutricional/lista-de-compras", headers=alimentado)
    assert antigua.status_code == 200, antigua.text
    filas = [r for g in antigua.json()["grupos"] for r in g["renglones"]]
    assert {r["alimento_id"]: r["gramos_semana"] for r in filas} == {r["alimento_id"]: r["gramos_semana"] for r in nueva["compras"]["renglones"]}
    assert cliente.get("/api/v1/plan-nutricional/menu", headers=alimentado).status_code == 200


def test_restriccion_nueva_invalida_semana_y_lecturas_antiguas(cliente, alimentado):
    original = preparar(cliente, alimentado)
    assert cliente.put(f"{RUTA}/preferencias", json={"alergias": ["leche"]}, headers=alimentado).status_code == 200
    for ruta in [f"{RUTA}/semana", "/api/v1/plan-nutricional/menu", "/api/v1/plan-nutricional/lista-de-compras"]:
        assert cliente.get(ruta, headers=alimentado).status_code == 409
    nueva = preparar(cliente, alimentado)
    assert nueva["revision"] > original["revision"]
    assert not any(p["nombre"] in {"Leche entera", "Queso fresco", "Yogur natural"} for d in nueva["dias"] for t in d["tiempos"] for p in t["porciones"])
    alternativas = cliente.get(f"{RUTA}/alternativas?dia=1&tiempo=2", headers=alimentado).json()
    assert not any(p["nombre"] in {"Leche entera", "Queso fresco", "Yogur natural"} for t in alternativas["opciones"] for p in t["porciones"])


def test_sin_semana_bloquea_ingrediente_antiguo_excluido(cliente, alimentado):
    menu = cliente.get("/api/v1/plan-nutricional/menu", headers=alimentado).json()
    excluido = menu["tiempos"][0]["porciones"][0]["alimento_id"]
    cliente.put(f"{RUTA}/preferencias", json={"alimentos_excluidos": [excluido]}, headers=alimentado)
    for ruta in ["menu", "lista-de-compras"]:
        assert cliente.get(f"/api/v1/plan-nutricional/{ruta}", headers=alimentado).status_code == 409


def test_catalogo_modificado_requiere_recalculo(cliente, alimentado, fabrica_sesiones):
    semana = preparar(cliente, alimentado)
    id_alimento = semana["dias"][0]["tiempos"][0]["porciones"][0]["alimento_id"]
    with fabrica_sesiones() as sesion:
        alimento = sesion.get(Alimento, id_alimento)
        alimento.disponible_localmente = False
        sesion.commit()
    assert cliente.get(f"{RUTA}/semana", headers=alimentado).status_code == 409
    assert cliente.get(f"{RUTA}/alternativas?dia=1&tiempo=0", headers=alimentado).status_code == 409


def test_semana_de_otra_cuenta_no_se_expone(cliente, alimentado, token_segundo_usuario):
    preparar(cliente, alimentado)
    respuesta = cliente.get(f"{RUTA}/semana", headers=encabezado(token_segundo_usuario))
    assert respuesta.status_code in {404, 409}
    assert "dias" not in respuesta.json()


@pytest.mark.parametrize("ruta", ["/semana", "/recetas", "/alternativas?dia=1&tiempo=0"])
def test_otra_restriccion_deriva_en_servidor(cliente, alimentado, ruta):
    preparar(cliente, alimentado)
    cliente.put(f"{RUTA}/preferencias", json={"otra_restriccion": True}, headers=alimentado)
    assert cliente.get(RUTA + ruta, headers=alimentado).status_code == 403
    assert cliente.post(f"{RUTA}/semana", headers=alimentado).status_code == 403


def test_condicion_medica_vigente_bloquea_aun_con_semana_previa(cliente, alimentado):
    preparar(cliente, alimentado)
    respuesta = cliente.post("/api/v1/perfil-biometrico", json={**PERFIL_VALIDO, "condiciones": ["diabetes"]}, headers=alimentado)
    assert respuesta.status_code == 201, respuesta.text
    assert cliente.post(f"{RUTA}/semana", headers=alimentado).status_code == 403
    assert cliente.get(f"{RUTA}/recetas", headers=alimentado).status_code == 403


def test_catalogo_insuficiente_no_guarda_semana_parcial(cliente, alimentado, fabrica_sesiones):
    cliente.put(f"{RUTA}/preferencias", json={"alimentos_excluidos": [a.id for a in catalogo() if a.nombre != "Banano"]}, headers=alimentado)
    assert cliente.post(f"{RUTA}/semana", headers=alimentado).status_code == 409
    with fabrica_sesiones() as sesion:
        assert sesion.scalars(select(SemanaAlimentaria)).all() == []


@pytest.mark.parametrize("dia,tiempo", [(0, 0), (8, 0), (1, -1), (1, 5)])
def test_limites_de_indices_en_servidor(cliente, token_usuario, dia, tiempo):
    assert cliente.get(f"{RUTA}/alternativas?dia={dia}&tiempo={tiempo}", headers=encabezado(token_usuario)).status_code == 422


def test_no_permite_receta_arbitraria_ni_editar_aportes(cliente, alimentado):
    semana = preparar(cliente, alimentado)
    datos = dict(revision=semana["revision"], dia=1, tiempo=2, receta_id="inexistente")
    assert cliente.put(f"{RUTA}/semana/comida", json=datos, headers=alimentado).status_code == 409
    assert cliente.put(f"{RUTA}/semana/comida", json={**datos, "energia_kcal": 1}, headers=alimentado).status_code == 422
    assert cliente.get(f"{RUTA}/semana", headers=alimentado).json() == semana
