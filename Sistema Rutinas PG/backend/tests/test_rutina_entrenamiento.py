"""Pruebas funcionales de la rutina de entrenamiento (historia HU-07).

Verifican los tres criterios de aceptacion de la Tabla 9 —ejercicio, series,
repeticiones y repeticiones en reserva por sesion; coincidencia con la frecuencia
declarada; y ningun grupo muscular en dos dias consecutivos— junto con la regla
del negocio *d* del apartado 4.3.4.
"""

import pytest

from app.modelos.enumeraciones import GrupoMuscular, NivelExperiencia, Objetivo
from app.motor import formulas
from app.motor.rutina import (
    ESQUEMAS_SEMANALES,
    GRUPOS_DE_CUERPO_COMPLETO,
    CatalogoInsuficiente,
    EjercicioDisponible,
    generar_rutina,
    hay_grupo_en_dias_consecutivos,
)
from app.nucleo.catalogo_inicial import EJERCICIOS_INICIALES
from tests.conftest import encabezado

RUTA_PERFIL = "/api/v1/perfil-biometrico"
RUTA_PLAN = "/api/v1/plan-nutricional"
RUTA_RUTINA = "/api/v1/rutina"

PERFIL_VALIDO = {
    "peso_kg": 78.0,
    "estatura_cm": 174.0,
    "edad": 28,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "mantenimiento",
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


@pytest.fixture(name="con_plan")
def fixture_con_plan(cliente, token_usuario):
    """Registra el perfil y genera el plan, que arrastra consigo la rutina."""
    assert (
        cliente.post(RUTA_PERFIL, json=PERFIL_VALIDO, headers=encabezado(token_usuario)).status_code
        == 201
    )
    assert cliente.post(RUTA_PLAN, headers=encabezado(token_usuario)).status_code == 201
    return token_usuario


# --------------------------------------------------------------------------
# Generador, verificado sin base de datos
# --------------------------------------------------------------------------


@pytest.mark.parametrize("dias", [1, 2, 3, 4, 5, 6, 7])
def test_el_numero_de_sesiones_coincide_con_la_frecuencia_declarada(dias):
    """Criterio de aceptación: tantas sesiones como días declaró el usuario."""
    rutina = generar_rutina(14.0, dias, NivelExperiencia.INTERMEDIO, Objetivo.MANTENIMIENTO, CATALOGO)

    assert len(rutina.sesiones) == dias
    assert rutina.dias_entrenamiento_semana == dias


@pytest.mark.parametrize("dias", [1, 2, 3, 4, 5, 6, 7])
@pytest.mark.parametrize("nivel", list(NivelExperiencia))
def test_ningun_grupo_muscular_recibe_estimulo_en_dias_consecutivos(dias, nivel):
    """Criterio de aceptación central de la historia HU-07."""
    rutina = generar_rutina(14.0, dias, nivel, Objetivo.MANTENIMIENTO, CATALOGO)

    assert not hay_grupo_en_dias_consecutivos(rutina.sesiones)


@pytest.mark.parametrize("dias", [1, 2, 3, 4, 5, 6, 7])
def test_la_restriccion_se_cumple_tambien_al_cerrar_la_semana(dias):
    """El microciclo se repite: el último día precede al primero de la semana siguiente."""
    esquema = ESQUEMAS_SEMANALES[dias]
    dias_usados = [dia for dia, _ in esquema]

    # Ningún esquema puede ocupar el día 7 y el día 1 con el mismo grupo.
    if 7 in dias_usados and 1 in dias_usados:
        grupo_ultimo = dict(esquema)[7]
        grupo_primero = dict(esquema)[1]
        estimulados_ultimo = (
            set(GRUPOS_DE_CUERPO_COMPLETO)
            if grupo_ultimo == GrupoMuscular.CUERPO_COMPLETO
            else {grupo_ultimo}
        )
        estimulados_primero = (
            set(GRUPOS_DE_CUERPO_COMPLETO)
            if grupo_primero == GrupoMuscular.CUERPO_COMPLETO
            else {grupo_primero}
        )
        assert not (estimulados_ultimo & estimulados_primero)


@pytest.mark.parametrize("dias", [1, 2, 3, 4, 5, 6, 7])
def test_cada_ejercicio_indica_series_repeticiones_y_reserva(dias):
    """Criterio de aceptación: la rutina indica las cuatro variables por ejercicio."""
    rutina = generar_rutina(14.0, dias, NivelExperiencia.INTERMEDIO, Objetivo.MANTENIMIENTO, CATALOGO)

    for sesion in rutina.sesiones:
        assert sesion.ejercicios, f"La sesión del día {sesion.dia} quedó vacía"
        for ejercicio in sesion.ejercicios:
            assert ejercicio.nombre
            assert ejercicio.series >= 2
            assert 0 < ejercicio.repeticiones_min <= ejercicio.repeticiones_max
            assert ejercicio.repeticiones_en_reserva >= 1
            assert ejercicio.descanso_segundos > 0


@pytest.mark.parametrize("nivel", list(NivelExperiencia))
def test_el_volumen_se_ajusta_al_nivel_de_experiencia(nivel):
    """A mayor experiencia, mayor volumen semanal prescrito."""
    volumen = formulas.series_semanales_por_grupo(nivel, 5, 28, Objetivo.MANTENIMIENTO)
    rutina = generar_rutina(volumen, 5, nivel, Objetivo.MANTENIMIENTO, CATALOGO)

    assert rutina.series_totales > 0
    assert rutina.alcanza_el_volumen_objetivo


def test_el_principiante_recibe_menos_volumen_que_el_avanzado():
    """El nivel de experiencia condiciona el volumen, no solo la selección."""
    volumenes = {}
    for nivel in NivelExperiencia:
        volumen = formulas.series_semanales_por_grupo(nivel, 5, 28, Objetivo.MANTENIMIENTO)
        volumenes[nivel] = generar_rutina(
            volumen, 5, nivel, Objetivo.MANTENIMIENTO, CATALOGO
        ).series_totales

    assert (
        volumenes[NivelExperiencia.PRINCIPIANTE]
        < volumenes[NivelExperiencia.INTERMEDIO]
        < volumenes[NivelExperiencia.AVANZADO]
    )


def test_la_intensidad_se_ajusta_al_nivel_de_experiencia():
    """El principiante se detiene más lejos del fallo que el avanzado."""
    reservas = {}
    for nivel in NivelExperiencia:
        rutina = generar_rutina(12.0, 4, nivel, Objetivo.MANTENIMIENTO, CATALOGO)
        reservas[nivel] = rutina.sesiones[0].ejercicios[0].repeticiones_en_reserva

    assert (
        reservas[NivelExperiencia.PRINCIPIANTE]
        > reservas[NivelExperiencia.INTERMEDIO]
        > reservas[NivelExperiencia.AVANZADO]
    )


@pytest.mark.parametrize(
    ("objetivo", "minimo_esperado"),
    [
        (Objetivo.PERDIDA_GRASA, 12),
        (Objetivo.MANTENIMIENTO, 8),
        (Objetivo.GANANCIA_MUSCULAR, 6),
    ],
)
def test_el_rango_de_repeticiones_responde_al_objetivo(objetivo, minimo_esperado):
    """La ganancia de masa prescribe rangos más bajos que la pérdida de grasa."""
    rutina = generar_rutina(14.0, 4, NivelExperiencia.INTERMEDIO, objetivo, CATALOGO)

    assert rutina.sesiones[0].ejercicios[0].repeticiones_min == minimo_esperado


def test_los_ejercicios_compuestos_encabezan_la_sesion():
    """Se ejecutan sin fatiga acumulada, porque involucran más masa muscular."""
    rutina = generar_rutina(14.0, 5, NivelExperiencia.INTERMEDIO, Objetivo.MANTENIMIENTO, CATALOGO)
    por_nombre = {ejercicio.nombre: ejercicio for ejercicio in CATALOGO}

    for sesion in rutina.sesiones:
        compuestos = [
            ejercicio.orden
            for ejercicio in sesion.ejercicios
            if por_nombre[ejercicio.nombre].es_compuesto
        ]
        aislados = [
            ejercicio.orden
            for ejercicio in sesion.ejercicios
            if not por_nombre[ejercicio.nombre].es_compuesto
        ]
        if compuestos and aislados:
            assert max(compuestos) < min(aislados)


def test_el_principiante_no_recibe_ejercicios_por_encima_de_su_nivel():
    """Las dominadas y el peso muerto exigen nivel intermedio."""
    rutina = generar_rutina(
        10.0, 6, NivelExperiencia.PRINCIPIANTE, Objetivo.MANTENIMIENTO, CATALOGO
    )
    prescritos = {
        ejercicio.nombre for sesion in rutina.sesiones for ejercicio in sesion.ejercicios
    }

    assert "Dominadas" not in prescritos
    assert "Peso muerto rumano" not in prescritos


def test_la_rutina_declara_cuando_no_alcanza_el_volumen_objetivo():
    """Con una sola sesión semanal no cabe el volumen que la red determinó.

    El generador prescribe lo que sí cabe y lo dice, en lugar de declarar un
    volumen que la rutina no entrega.
    """
    rutina = generar_rutina(18.0, 1, NivelExperiencia.AVANZADO, Objetivo.MANTENIMIENTO, CATALOGO)

    assert len(rutina.sesiones) == 1
    assert not rutina.alcanza_el_volumen_objetivo


def test_con_cuatro_dias_se_declara_que_grupos_no_tienen_sesion_propia():
    """El brazo y el abdomen trabajan de forma indirecta; el sistema lo dice."""
    rutina = generar_rutina(14.0, 4, NivelExperiencia.INTERMEDIO, Objetivo.MANTENIMIENTO, CATALOGO)

    sin_directo = set(rutina.grupos_sin_trabajo_directo)
    assert sin_directo == {GrupoMuscular.BRAZO, GrupoMuscular.ABDOMEN}


def test_sin_catalogo_no_se_puede_armar_la_rutina():
    """El generador lo dice en lugar de devolver una rutina vacía."""
    with pytest.raises(CatalogoInsuficiente):
        generar_rutina(14.0, 4, NivelExperiencia.INTERMEDIO, Objetivo.MANTENIMIENTO, [])


def test_la_progresion_no_supera_el_diez_por_ciento():
    """Regla del negocio d: el incremento entre microciclos no pasa del 10 %."""
    assert formulas.progresion_admitida(100) == pytest.approx(110)
    assert formulas.INCREMENTO_MAXIMO_ENTRE_MICROCICLOS == 0.10


# --------------------------------------------------------------------------
# Rutina expuesta como servicio
# --------------------------------------------------------------------------


def test_sin_sesion_no_se_consulta_la_rutina(cliente):
    """La validación de acceso ocurre en el servidor (requerimiento 4.5.1)."""
    assert cliente.get(RUTA_RUTINA).status_code == 401


def test_sin_plan_generado_no_hay_rutina(cliente, token_usuario):
    """La rutina se genera junto con el plan."""
    assert cliente.get(RUTA_RUTINA, headers=encabezado(token_usuario)).status_code == 404


def test_generar_el_plan_produce_tambien_la_rutina(cliente, con_plan):
    """El plan y la rutina se entregan juntos, como pide la visión del producto."""
    respuesta = cliente.get(RUTA_RUTINA, headers=encabezado(con_plan))

    assert respuesta.status_code == 200
    rutina = respuesta.json()
    assert len(rutina["sesiones"]) == PERFIL_VALIDO["dias_entrenamiento_semana"]


def test_la_rutina_expuesta_cumple_la_separacion_de_grupos(cliente, con_plan):
    """El propio servicio declara si cumple el criterio de días consecutivos."""
    rutina = cliente.get(RUTA_RUTINA, headers=encabezado(con_plan)).json()

    assert rutina["cumple_separacion_de_grupos"] is True


def test_cada_sesion_expuesta_trae_sus_ejercicios_completos(cliente, con_plan):
    """Criterio de aceptación: ejercicio, series, repeticiones y reserva."""
    rutina = cliente.get(RUTA_RUTINA, headers=encabezado(con_plan)).json()

    for sesion in rutina["sesiones"]:
        assert sesion["nombre_dia"]
        assert sesion["ejercicios"]
        assert sesion["duracion_estimada_minutos"] > 0
        for ejercicio in sesion["ejercicios"]:
            assert ejercicio["nombre"]
            assert ejercicio["equipamiento"]
            assert ejercicio["series"] >= 2
            assert ejercicio["repeticiones_min"] <= ejercicio["repeticiones_max"]
            assert ejercicio["repeticiones_en_reserva"] >= 1
            assert "series" in ejercicio["prescripcion"]
            assert ejercicio["explicacion_reserva"]


def test_la_rutina_explica_la_progresion_y_advierte_sobre_la_tecnica(cliente, con_plan):
    """Requerimiento 4.5.3 y regla del negocio e."""
    rutina = cliente.get(RUTA_RUTINA, headers=encabezado(con_plan)).json()

    assert "10 %" in rutina["explicacion_progresion"]
    assert "no sustituye" in rutina["aviso_tecnica"].lower()


def test_la_rutina_reporta_las_series_efectivas_por_grupo(cliente, con_plan):
    """Permite comparar lo prescrito con el volumen que determinó la red."""
    rutina = cliente.get(RUTA_RUTINA, headers=encabezado(con_plan)).json()

    assert rutina["series_efectivas_por_grupo"]
    assert rutina["series_totales"] == sum(rutina["series_efectivas_por_grupo"].values())
    assert rutina["series_objetivo_por_grupo"] > 0


@pytest.mark.parametrize("dias", [2, 3, 5, 6])
def test_la_rutina_expuesta_respeta_la_frecuencia_declarada(cliente, token_usuario, dias):
    """El número de sesiones coincide con lo que el usuario declaró."""
    cliente.post(
        RUTA_PERFIL,
        json={**PERFIL_VALIDO, "dias_entrenamiento_semana": dias},
        headers=encabezado(token_usuario),
    )
    cliente.post(RUTA_PLAN, headers=encabezado(token_usuario))

    rutina = cliente.get(RUTA_RUTINA, headers=encabezado(token_usuario)).json()

    assert len(rutina["sesiones"]) == dias
    assert rutina["dias_entrenamiento_semana"] == dias
    assert rutina["cumple_separacion_de_grupos"] is True


def test_la_rutina_solo_es_visible_para_su_titular(cliente, con_plan, token_segundo_usuario):
    """Regla del negocio f: cada cuenta ve únicamente su propia rutina."""
    ajena = cliente.get(RUTA_RUTINA, headers=encabezado(token_segundo_usuario))

    assert ajena.status_code == 404


def test_generar_un_plan_nuevo_reemplaza_la_rutina_vigente(cliente, con_plan):
    """La rutina que se consulta es siempre la del plan vigente."""
    primera = cliente.get(RUTA_RUTINA, headers=encabezado(con_plan)).json()
    cliente.post(RUTA_PLAN, headers=encabezado(con_plan))
    segunda = cliente.get(RUTA_RUTINA, headers=encabezado(con_plan)).json()

    assert segunda["plan_id"] != primera["plan_id"]
    assert segunda["activo"] is True
