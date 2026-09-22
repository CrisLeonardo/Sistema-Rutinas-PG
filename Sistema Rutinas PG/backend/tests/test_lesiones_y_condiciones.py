"""Pruebas del historial de lesiones y de las condiciones medicas del perfil.

Verifican dos promesas de la tesis que el sistema no cumplia: el historial de
lesiones del alcance *b* del apartado 1.6.1, que adapta la rutina al perfil
individual, y las restricciones RE-02 y RE-06 del apartado 4.8.3, por las que
el servidor —y no solo la interfaz— se niega a generar planes cuando el usuario
declara una patologia cronica severa.
"""

import pytest

from app.modelos.enumeraciones import GrupoMuscular, NivelExperiencia, Objetivo, ZonaLesion
from app.motor.lesiones import (
    ZONAS_POR_EJERCICIO,
    describir_zonas,
    ejercicios_compatibles,
    zonas_que_carga,
)
from app.motor.rutina import EjercicioDisponible, generar_rutina
from app.nucleo.catalogo_inicial import EJERCICIOS_INICIALES
from tests.conftest import encabezado

RUTA_PERFIL = "/api/v1/perfil-biometrico"
RUTA_PLAN = "/api/v1/plan-nutricional"
RUTA_RUTINA = "/api/v1/rutina"
RUTA_PROGRESO = "/api/v1/progreso"

PERFIL_VALIDO = {
    "peso_kg": 85.0,
    "estatura_cm": 174.0,
    "edad": 28,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "perdida_grasa",
    "nivel_experiencia": "intermedio",
    "dias_entrenamiento_semana": 4,
}

CATALOGO = [
    EjercicioDisponible(
        id=posicion + 1,
        nombre=nombre,
        grupo_muscular=grupo,
        nivel_minimo=nivel,
        es_compuesto=compuesto,
    )
    for posicion, (nombre, grupo, nivel, _equipo, compuesto, _texto) in enumerate(
        EJERCICIOS_INICIALES
    )
]


# --------------------------------------------------------------------------
# Motor, sin base de datos
# --------------------------------------------------------------------------


def test_todo_ejercicio_del_catalogo_inicial_declara_las_zonas_que_carga():
    """Un ejercicio sin declarar caeria en la suposicion por grupo, que es mas burda."""
    faltantes = [nombre for nombre, *_ in EJERCICIOS_INICIALES if nombre not in ZONAS_POR_EJERCICIO]
    assert faltantes == []


def test_sin_lesiones_no_se_descarta_ningun_ejercicio():
    assert ejercicios_compatibles(CATALOGO, []) == CATALOGO


@pytest.mark.parametrize("zona", list(ZonaLesion))
def test_ningun_ejercicio_compatible_carga_la_zona_lesionada(zona):
    compatibles = ejercicios_compatibles(CATALOGO, [zona])
    assert compatibles, f"Una lesión de {zona} no debería vaciar el catálogo entero."
    assert all(zona not in zonas_que_carga(ejercicio) for ejercicio in compatibles)


def test_un_ejercicio_nuevo_se_juzga_por_su_grupo_con_prudencia():
    """Lo que el administrador agregue despues no conoce sus zonas: se supone lo peor."""
    nuevo = EjercicioDisponible(
        id=999,
        nombre="Sentadilla búlgara",
        grupo_muscular=GrupoMuscular.PIERNA,
        nivel_minimo=NivelExperiencia.INTERMEDIO,
        es_compuesto=True,
    )
    assert ejercicios_compatibles([nuevo], [ZonaLesion.RODILLA]) == []


def test_la_rutina_con_lesion_de_rodilla_no_prescribe_ejercicios_que_la_carguen():
    rutina = generar_rutina(
        series_semanales_por_grupo=12,
        dias_entrenamiento_semana=4,
        nivel_experiencia=NivelExperiencia.INTERMEDIO,
        objetivo=Objetivo.MANTENIMIENTO,
        disponibles=ejercicios_compatibles(CATALOGO, [ZonaLesion.RODILLA]),
        permitir_sesiones_vacias=True,
    )
    prohibidos = {"Sentadilla con barra", "Prensa de piernas", "Zancadas con mancuernas"}
    prescritos = {e.nombre for sesion in rutina.sesiones for e in sesion.ejercicios}
    assert not prescritos & prohibidos
    # La frecuencia declarada se respeta aunque la lesion reduzca el catalogo.
    assert len(rutina.sesiones) == 4


def test_una_lesion_que_vacia_el_catalogo_deja_sesiones_de_descanso():
    """Con todas las zonas lesionadas no se inventa nada: la sesion queda vacia."""
    rutina = generar_rutina(
        series_semanales_por_grupo=12,
        dias_entrenamiento_semana=4,
        nivel_experiencia=NivelExperiencia.INTERMEDIO,
        objetivo=Objetivo.MANTENIMIENTO,
        disponibles=ejercicios_compatibles(
            [e for e in CATALOGO if e.grupo_muscular != GrupoMuscular.ABDOMEN],
            list(ZonaLesion),
        ),
        permitir_sesiones_vacias=True,
    )
    assert len(rutina.sesiones) == 4
    assert rutina.series_totales == 0


def test_las_zonas_se_describen_en_lenguaje_sencillo():
    assert describir_zonas([ZonaLesion.HOMBRO]) == "hombro"
    assert (
        describir_zonas([ZonaLesion.HOMBRO, ZonaLesion.CODO_MUNECA, ZonaLesion.RODILLA])
        == "hombro, codo o muñeca y rodilla"
    )


# --------------------------------------------------------------------------
# Historial de lesiones contra la interfaz
# --------------------------------------------------------------------------


def _registrar_perfil(cliente, token, **campos):
    return cliente.post(RUTA_PERFIL, json={**PERFIL_VALIDO, **campos}, headers=encabezado(token))


def test_el_perfil_guarda_y_devuelve_el_historial_de_lesiones(cliente, token_usuario):
    respuesta = _registrar_perfil(
        cliente, token_usuario, lesiones=["rodilla", "hombro", "rodilla"]
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    # Sin repetidos y en el orden estable de la enumeracion.
    assert cuerpo["lesiones"] == ["hombro", "rodilla"]
    assert cuerpo["condiciones"] == []
    assert cuerpo["requiere_valoracion_profesional"] is False


def test_una_zona_desconocida_se_rechaza(cliente, token_usuario):
    assert _registrar_perfil(cliente, token_usuario, lesiones=["cuello"]).status_code == 422


def test_el_historial_conserva_las_lesiones_de_cada_medicion(cliente, token_usuario):
    """HU-05: cada medicion guarda sus propias lesiones; el historial no se reescribe."""
    _registrar_perfil(cliente, token_usuario, lesiones=["rodilla"])
    _registrar_perfil(cliente, token_usuario, peso_kg=84.0)

    historial = cliente.get(f"{RUTA_PERFIL}/historial", headers=encabezado(token_usuario))
    assert historial.status_code == 200
    assert [medicion["lesiones"] for medicion in historial.json()] == [[], ["rodilla"]]


def test_la_rutina_generada_evita_la_zona_lesionada(cliente, token_usuario):
    _registrar_perfil(cliente, token_usuario, lesiones=["rodilla"])
    assert cliente.post(RUTA_PLAN, headers=encabezado(token_usuario)).status_code == 201

    rutina = cliente.get(RUTA_RUTINA, headers=encabezado(token_usuario)).json()
    nombres = {e["nombre"] for sesion in rutina["sesiones"] for e in sesion["ejercicios"]}
    assert "Sentadilla con barra" not in nombres
    assert "Prensa de piernas" not in nombres
    assert rutina["lesiones_consideradas"] == ["rodilla"]
    assert "rodilla" in rutina["explicacion_lesiones"]


def test_sin_lesiones_la_rutina_no_menciona_ninguna(cliente, token_usuario):
    _registrar_perfil(cliente, token_usuario)
    cliente.post(RUTA_PLAN, headers=encabezado(token_usuario))

    rutina = cliente.get(RUTA_RUTINA, headers=encabezado(token_usuario)).json()
    assert rutina["lesiones_consideradas"] == []
    assert rutina["explicacion_lesiones"] is None


def test_el_reajuste_semanal_conserva_el_historial_de_lesiones(cliente, token_usuario):
    """Sin esto, el primer reajuste armaria una rutina que vuelve a cargar la rodilla."""
    _registrar_perfil(cliente, token_usuario, lesiones=["rodilla"])
    cliente.post(RUTA_PLAN, headers=encabezado(token_usuario))

    avance = cliente.post(
        RUTA_PROGRESO,
        json={"peso_kg": 83.0, "sesiones_cumplidas": 4, "adherencia_nutricional": 90},
        headers=encabezado(token_usuario),
    )
    assert avance.status_code == 201
    assert avance.json()["reajuste"]["reajusto_el_plan"] is True

    vigente = cliente.get(RUTA_PERFIL, headers=encabezado(token_usuario)).json()
    assert vigente["peso_kg"] == 83.0
    assert vigente["lesiones"] == ["rodilla"]

    rutina = cliente.get(RUTA_RUTINA, headers=encabezado(token_usuario)).json()
    assert rutina["lesiones_consideradas"] == ["rodilla"]


# --------------------------------------------------------------------------
# Restricciones RE-02 y RE-06: patologias cronicas severas
# --------------------------------------------------------------------------


def test_con_una_condicion_severa_el_servidor_no_genera_el_plan(cliente, token_usuario):
    registro = _registrar_perfil(cliente, token_usuario, condiciones=["cardiopatia"])
    assert registro.status_code == 201
    assert registro.json()["requiere_valoracion_profesional"] is True

    respuesta = cliente.post(RUTA_PLAN, headers=encabezado(token_usuario))
    assert respuesta.status_code == 403
    assert "profesional de la salud" in respuesta.json()["detail"]
    # Tampoco queda una rutina: la negativa cubre los dos planes.
    assert cliente.get(RUTA_RUTINA, headers=encabezado(token_usuario)).status_code == 404


def test_declarar_la_condicion_retira_el_plan_que_ya_tenia(cliente, token_usuario):
    """Un plan calculado antes de conocer la condicion no puede seguir vigente."""
    _registrar_perfil(cliente, token_usuario)
    assert cliente.post(RUTA_PLAN, headers=encabezado(token_usuario)).status_code == 201

    _registrar_perfil(cliente, token_usuario, condiciones=["diabetes"])

    assert cliente.get(RUTA_PLAN, headers=encabezado(token_usuario)).status_code == 404
    # El plan anterior se conserva en el historial, como todo plan retirado.
    historial = cliente.get(f"{RUTA_PLAN}/historial", headers=encabezado(token_usuario))
    assert len(historial.json()) == 1


def test_al_retirar_la_condicion_se_puede_volver_a_generar(cliente, token_usuario):
    _registrar_perfil(cliente, token_usuario, condiciones=["enfermedad_renal"])
    assert cliente.post(RUTA_PLAN, headers=encabezado(token_usuario)).status_code == 403

    _registrar_perfil(cliente, token_usuario)
    assert cliente.post(RUTA_PLAN, headers=encabezado(token_usuario)).status_code == 201


def test_una_condicion_desconocida_se_rechaza(cliente, token_usuario):
    assert _registrar_perfil(cliente, token_usuario, condiciones=["gripe"]).status_code == 422
