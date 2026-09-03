"""Pruebas funcionales de la epica E2, Perfil biometrico.

Cada prueba corresponde a un criterio de aceptacion de la Tabla 9 del Capitulo IV,
a una regla del negocio del apartado 4.3.4 o a una validacion del apartado 4.8.3.
"""

import pytest

from app.esquemas.perfil import clasificar_indice_masa_corporal
from tests.conftest import encabezado

RUTA_PERFIL = "/api/v1/perfil-biometrico"
RUTA_HISTORIAL = "/api/v1/perfil-biometrico/historial"
RUTA_SESION = "/api/v1/autenticacion/sesion"

PERFIL_VALIDO = {
    "peso_kg": 78.5,
    "estatura_cm": 172,
    "edad": 27,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "perdida_grasa",
    "nivel_experiencia": "principiante",
    "dias_entrenamiento_semana": 4,
}

CAMPOS_OBLIGATORIOS = [
    "peso_kg",
    "estatura_cm",
    "edad",
    "sexo",
    "nivel_actividad",
    "objetivo",
]


# --------------------------------------------------------------------------
# HU-04. Captura y validacion del perfil biometrico
# --------------------------------------------------------------------------


def test_registro_guarda_el_perfil_asociado_a_la_cuenta_en_sesion(cliente, token_usuario):
    """Los datos quedan almacenados y asociados al usuario que inicio sesion."""
    respuesta = cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario))

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["peso_kg"] == PERFIL_VALIDO["peso_kg"]
    assert cuerpo["estatura_cm"] == PERFIL_VALIDO["estatura_cm"]
    assert cuerpo["objetivo"] == PERFIL_VALIDO["objetivo"]

    cuenta = cliente.get(RUTA_SESION, headers=encabezado(token_usuario)).json()
    assert cuerpo["usuario_id"] == cuenta["id"]


def test_registro_ignora_el_usuario_declarado_en_la_peticion(
    cliente, token_usuario, token_segundo_usuario
):
    """La cuenta a la que se asocia el perfil proviene del token, no del cuerpo."""
    ajeno = cliente.get(RUTA_SESION, headers=encabezado(token_segundo_usuario)).json()

    respuesta = cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "usuario_id": ajeno["id"]},
        headers=encabezado(token_usuario),
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["usuario_id"] != ajeno["id"]


@pytest.mark.parametrize("campo", CAMPOS_OBLIGATORIOS)
def test_registro_exige_los_campos_obligatorios(cliente, token_usuario, campo):
    """Peso, estatura, edad, sexo, nivel de actividad y objetivo son obligatorios."""
    datos = {llave: valor for llave, valor in PERFIL_VALIDO.items() if llave != campo}

    respuesta = cliente.post(RUTA_PERFIL, json=datos, headers=encabezado(token_usuario))

    assert respuesta.status_code == 422


@pytest.mark.parametrize("peso", [29.9, 0, 250.1, 400])
def test_registro_rechaza_pesos_fuera_del_rango(cliente, token_usuario, peso):
    """El peso debe estar entre 30 y 250 kilogramos."""
    respuesta = cliente.post(
        RUTA_PERFIL, json={**PERFIL_VALIDO, "peso_kg": peso}, headers=encabezado(token_usuario)
    )

    assert respuesta.status_code == 422


@pytest.mark.parametrize("peso", [30, 145.75, 250])
def test_registro_acepta_los_pesos_limite(cliente, token_usuario, peso):
    """Los extremos del rango de peso son valores validos."""
    respuesta = cliente.post(
        RUTA_PERFIL, json={**PERFIL_VALIDO, "peso_kg": peso}, headers=encabezado(token_usuario)
    )

    assert respuesta.status_code == 201


@pytest.mark.parametrize("estatura", [119.9, 90, 220.1, 300])
def test_registro_rechaza_estaturas_fuera_del_rango(cliente, token_usuario, estatura):
    """La estatura debe estar entre 120 y 220 centimetros."""
    respuesta = cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "estatura_cm": estatura},
        headers=encabezado(token_usuario),
    )

    assert respuesta.status_code == 422


@pytest.mark.parametrize("estatura", [120, 172.5, 220])
def test_registro_acepta_las_estaturas_limite(cliente, token_usuario, estatura):
    """Los extremos del rango de estatura son valores validos."""
    respuesta = cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "estatura_cm": estatura},
        headers=encabezado(token_usuario),
    )

    assert respuesta.status_code == 201


@pytest.mark.parametrize("edad", [17, 12, 0, -3])
def test_registro_rechaza_a_los_menores_de_edad(cliente, token_usuario, edad):
    """Regla del negocio a: solo se generan planes para mayores de dieciocho anios."""
    respuesta = cliente.post(
        RUTA_PERFIL, json={**PERFIL_VALIDO, "edad": edad}, headers=encabezado(token_usuario)
    )

    assert respuesta.status_code == 422
    assert "dieciocho" in respuesta.text


def test_registro_acepta_la_edad_minima(cliente, token_usuario):
    """La persona de dieciocho anios cumplidos si puede registrar su perfil."""
    respuesta = cliente.post(
        RUTA_PERFIL, json={**PERFIL_VALIDO, "edad": 18}, headers=encabezado(token_usuario)
    )

    assert respuesta.status_code == 201


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("sexo", "indefinido"),
        ("nivel_actividad", "extremo"),
        ("objetivo", "bajar_de_peso"),
        ("nivel_experiencia", "profesional"),
    ],
)
def test_registro_rechaza_valores_fuera_del_catalogo(cliente, token_usuario, campo, valor):
    """Los campos de seleccion solo admiten los valores previstos por el sistema."""
    respuesta = cliente.post(
        RUTA_PERFIL, json={**PERFIL_VALIDO, campo: valor}, headers=encabezado(token_usuario)
    )

    assert respuesta.status_code == 422


@pytest.mark.parametrize("dias", [0, 8, -1])
def test_registro_rechaza_frecuencias_semanales_imposibles(cliente, token_usuario, dias):
    """La frecuencia semanal declarada debe caber en una semana."""
    respuesta = cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "dias_entrenamiento_semana": dias},
        headers=encabezado(token_usuario),
    )

    assert respuesta.status_code == 422


def test_registro_calcula_el_indice_de_masa_corporal(cliente, token_usuario):
    """El sistema calcula y devuelve el indice de masa corporal."""
    respuesta = cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "peso_kg": 70, "estatura_cm": 175},
        headers=encabezado(token_usuario),
    )

    cuerpo = respuesta.json()
    assert cuerpo["indice_masa_corporal"] == pytest.approx(22.86, abs=0.01)
    assert cuerpo["clasificacion_masa_corporal"] == "Peso normal"


@pytest.mark.parametrize(
    ("indice", "clasificacion"),
    [
        (17.0, "Peso por debajo de lo normal"),
        (22.0, "Peso normal"),
        (27.5, "Sobrepeso"),
        (33.1, "Obesidad"),
    ],
)
def test_clasificacion_del_indice_en_lenguaje_sencillo(indice, clasificacion):
    """Toda cifra tecnica se acompania de una lectura sencilla (requerimiento 4.5.3)."""
    assert clasificar_indice_masa_corporal(indice) == clasificacion


def test_sin_sesion_no_se_registra_ni_se_consulta_el_perfil(cliente):
    """La validacion de acceso ocurre en el servidor (requerimiento 4.5.1)."""
    assert cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO).status_code == 401
    assert cliente.get(RUTA_PERFIL).status_code == 401
    assert cliente.get(RUTA_HISTORIAL).status_code == 401


def test_consulta_sin_perfil_registrado_devuelve_no_encontrado(cliente, token_usuario):
    """Mientras no exista una medicion, el perfil vigente no esta disponible."""
    respuesta = cliente.get(RUTA_PERFIL, headers=encabezado(token_usuario))

    assert respuesta.status_code == 404


# --------------------------------------------------------------------------
# HU-05. Historial de medidas del usuario
# --------------------------------------------------------------------------


def test_actualizar_las_medidas_no_sobrescribe_la_medicion_anterior(cliente, token_usuario):
    """Cada actualizacion genera un registro nuevo en lugar de reemplazar el previo."""
    primero = cliente.post(
        RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario)
    ).json()
    segundo = cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "peso_kg": 76.0},
        headers=encabezado(token_usuario),
    ).json()

    historial = cliente.get(RUTA_HISTORIAL, headers=encabezado(token_usuario)).json()

    assert len(historial) == 2
    assert primero["id"] != segundo["id"]
    assert {medicion["id"] for medicion in historial} == {primero["id"], segundo["id"]}


def test_historial_se_devuelve_de_la_medicion_mas_reciente_a_la_mas_antigua(
    cliente, token_usuario
):
    """El historial se consulta ordenado por fecha."""
    pesos = [80.0, 78.0, 76.0]
    for peso in pesos:
        cliente.post(
            RUTA_PERFIL,
            json={**PERFIL_VALIDO, "peso_kg": peso},
            headers=encabezado(token_usuario),
        )

    historial = cliente.get(RUTA_HISTORIAL, headers=encabezado(token_usuario)).json()

    assert [medicion["peso_kg"] for medicion in historial] == list(reversed(pesos))


def test_el_perfil_vigente_es_la_ultima_medicion_registrada(cliente, token_usuario):
    """La consulta del perfil devuelve siempre la medicion mas reciente."""
    cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario))
    cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "peso_kg": 74.25, "objetivo": "mantenimiento"},
        headers=encabezado(token_usuario),
    )

    vigente = cliente.get(RUTA_PERFIL, headers=encabezado(token_usuario)).json()

    assert vigente["peso_kg"] == 74.25
    assert vigente["objetivo"] == "mantenimiento"


def test_historial_vacio_cuando_no_hay_mediciones(cliente, token_usuario):
    """Una cuenta recien creada tiene un historial vacio, no un error."""
    respuesta = cliente.get(RUTA_HISTORIAL, headers=encabezado(token_usuario))

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_los_datos_biometricos_solo_son_visibles_para_su_titular(
    cliente, token_usuario, token_segundo_usuario
):
    """Regla del negocio f: cada cuenta ve unicamente sus propias medidas."""
    cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario))

    historial_ajeno = cliente.get(
        RUTA_HISTORIAL, headers=encabezado(token_segundo_usuario)
    ).json()
    vigente_ajeno = cliente.get(RUTA_PERFIL, headers=encabezado(token_segundo_usuario))

    assert historial_ajeno == []
    assert vigente_ajeno.status_code == 404


def test_el_administrador_no_accede_a_los_datos_biometricos_de_otras_cuentas(
    cliente, token_usuario, token_administrador
):
    """El administrador no dispone de ninguna ruta para leer perfiles ajenos."""
    cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario))

    historial = cliente.get(RUTA_HISTORIAL, headers=encabezado(token_administrador)).json()

    assert historial == []
