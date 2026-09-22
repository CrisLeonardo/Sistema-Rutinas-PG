"""Pruebas del sistema de puntos, niveles e insignias.

Verifican sobre todo lo que el modulo promete NO hacer: no pagar dos veces el
mismo hecho, no premiar sin techo el volumen de carga y no dejar que una cuenta
vea la senda de otra. Un sistema de recompensas que se puede inflar deja de
medir el esfuerzo y empieza a medir la insistencia.
"""

from datetime import date, timedelta

import pytest

from app.motor import juego as motor
from tests.conftest import encabezado


# --------------------------------------------------------------------------
# Reglas del motor, sin base de datos
# --------------------------------------------------------------------------


def test_los_niveles_crecen_de_forma_estricta():
    """Dos niveles con el mismo umbral harian imposible situar al usuario."""
    umbrales = [nivel.xp_requerido for nivel in motor.NIVELES]
    assert umbrales == sorted(umbrales)
    assert len(set(umbrales)) == len(umbrales)
    assert umbrales[0] == 0

    numeros = [nivel.numero for nivel in motor.NIVELES]
    assert numeros == list(range(1, len(motor.NIVELES) + 1))


#: Presupuesto semanal del usuario de referencia: tres sesiones en tres dias
#: distintos, con su pesaje semanal y buena adherencia. Es el mismo supuesto con
#: que se calibro `motor.juego.NIVELES`.
SESIONES_POR_SEMANA = 3
VOLUMEN_POR_SESION_KG = 5_500


def _puntos_de_una_semana_estable() -> int:
    """Lo que gana en una semana quien cumple su rutina, sin insignias nuevas."""
    por_sesion = (
        motor.PUNTOS_POR_SESION
        + motor.PUNTOS_POR_SESION_PRESCRITA
        + motor.puntos_por_volumen(VOLUMEN_POR_SESION_KG)
    )
    return (
        SESIONES_POR_SEMANA * por_sesion
        + motor.PUNTOS_MAXIMOS_POR_RACHA
        + motor.PUNTOS_POR_AVANCE_SEMANAL
        + motor.PUNTOS_POR_ADHERENCIA
        + motor.PUNTOS_POR_DESCANSO
    )


def test_la_curva_de_niveles_crece_sin_saltos_bruscos():
    """Un tramo menor que el anterior haría el nivel siguiente más fácil.

    Y un tramo más del doble que el anterior deja al usuario semanas enteras sin
    ninguna señal de avance, que es la falla que el sistema viene a corregir.
    """
    tramos = [
        siguiente.xp_requerido - anterior.xp_requerido
        for anterior, siguiente in zip(motor.NIVELES, motor.NIVELES[1:], strict=False)
    ]
    assert tramos == sorted(tramos)
    for anterior, siguiente in zip(tramos, tramos[1:], strict=False):
        assert siguiente <= anterior * 2, (
            f"El tramo de {siguiente} puntos más que duplica el anterior de {anterior}."
        )


def test_la_curva_esta_calibrada_al_presupuesto_semanal():
    """La senda debe durar del orden de un año al usuario de referencia.

    Es la prueba que ata la tabla de niveles a la tabla de puntos. Si alguien
    sube lo que vale una sesión sin recalibrar los umbrales, la senda se termina
    en meses y esta prueba lo dice; si los umbrales se estiran de más, los
    primeros meses dejan de mostrar avance y también lo dice.
    """
    semanal = _puntos_de_una_semana_estable()
    assert 600 <= semanal <= 700, (
        f"El presupuesto semanal cambió a {semanal} puntos: recalibre NIVELES."
    )

    # La primera señal tiene que llegar dentro del primer mes. En las primeras
    # semanas el usuario gana algo más que el presupuesto estable, porque las
    # insignias de arranque reparten de golpe; aun midiendo solo con el
    # presupuesto estable, el segundo nivel debe quedar cerca.
    semanas_al_segundo = motor.NIVELES[1].xp_requerido / semanal
    assert semanas_al_segundo <= 4, (
        f"El segundo nivel queda a {semanas_al_segundo:.1f} semanas: es demasiado lejos."
    )

    semanas_al_ultimo = motor.NIVELES[-1].xp_requerido / semanal
    assert 40 <= semanas_al_ultimo <= 70, (
        f"El último nivel queda a {semanas_al_ultimo:.1f} semanas: recalibre NIVELES."
    )


def test_el_nivel_se_deduce_de_los_puntos():
    assert motor.nivel_para(0).numero == 1
    assert motor.nivel_para(-50).numero == 1
    assert motor.nivel_para(motor.NIVELES[1].xp_requerido).numero == 2
    assert motor.nivel_para(motor.NIVELES[1].xp_requerido - 1).numero == 1
    assert motor.nivel_para(10_000_000).numero == motor.NIVEL_MAXIMO


def test_el_avance_dentro_del_nivel_cierra_el_tramo():
    """El porcentaje y lo que falta tienen que hablar del mismo tramo."""
    segundo = motor.NIVELES[1]
    tercero = motor.NIVELES[2]
    a_mitad = segundo.xp_requerido + (tercero.xp_requerido - segundo.xp_requerido) // 2

    avance = motor.avance_de_nivel(a_mitad)
    assert avance.nivel.numero == 2
    assert avance.proximo is not None and avance.proximo.numero == 3
    assert avance.puntos_en_el_nivel + avance.puntos_para_el_proximo == avance.puntos_del_tramo
    assert 49 <= avance.porcentaje <= 51


def test_el_ultimo_nivel_no_deja_tramo_pendiente():
    """En el nivel maximo la pantalla no debe pedir puntos que no existen."""
    avance = motor.avance_de_nivel(motor.NIVELES[-1].xp_requerido + 5_000)
    assert avance.proximo is None
    assert avance.puntos_para_el_proximo == 0
    assert avance.porcentaje == 100


def test_el_volumen_tiene_techo():
    """Es la regla de seguridad: mas carga no puede valer siempre mas puntos."""
    assert motor.puntos_por_volumen(0) == 0
    assert motor.puntos_por_volumen(-100) == 0
    assert motor.puntos_por_volumen(250) == 1
    assert motor.puntos_por_volumen(motor.VOLUMEN_CON_TECHO_KG) == (
        motor.PUNTOS_MAXIMOS_POR_VOLUMEN
    )
    # Diez veces el techo no vale ni un punto mas.
    assert motor.puntos_por_volumen(motor.VOLUMEN_CON_TECHO_KG * 10) == (
        motor.PUNTOS_MAXIMOS_POR_VOLUMEN
    )


def test_la_racha_crece_y_tiene_techo():
    assert motor.puntos_por_racha(0) == 0
    assert motor.puntos_por_racha(1) == motor.PUNTOS_POR_SEMANA_DE_RACHA
    assert motor.puntos_por_racha(2) > motor.puntos_por_racha(1)
    assert motor.puntos_por_racha(52) == motor.PUNTOS_MAXIMOS_POR_RACHA


def test_las_insignias_no_repiten_clave():
    """Dos insignias con la misma clave harian que una tapara a la otra."""
    claves = [logro.clave for logro in motor.LOGROS]
    assert len(set(claves)) == len(claves)
    assert set(motor.LOGROS_POR_CLAVE) == set(claves)
    for logro in motor.LOGROS:
        assert logro.categoria in motor.CATEGORIAS
        assert logro.pista, f"La insignia {logro.clave} no dice cómo conseguirla."


def test_una_trayectoria_vacia_no_cumple_ninguna_insignia():
    assert motor.logros_cumplidos(motor.Trayectoria()) == ()


def test_las_insignias_se_cumplen_por_umbral():
    trayectoria = motor.Trayectoria(sesiones_totales=10, racha_maxima_semanas=4)
    cumplidas = motor.logros_cumplidos(trayectoria)
    assert "primera_sesion" in cumplidas
    assert "diez_sesiones" in cumplidas
    assert "racha_4" in cumplidas
    assert "cincuenta_sesiones" not in cumplidas
    assert "racha_12" not in cumplidas


# --------------------------------------------------------------------------
# Recorrido completo contra la interfaz
# --------------------------------------------------------------------------


@pytest.fixture(name="ejercicio_id")
def fixture_ejercicio_id(cliente, token_usuario) -> int:
    """Un ejercicio cualquiera del catalogo inicial."""
    respuesta = cliente.get(
        "/api/v1/catalogos/ejercicios", headers=encabezado(token_usuario)
    )
    assert respuesta.status_code == 200
    return respuesta.json()[0]["id"]


def _sesion(ejercicio_id: int, peso: float, fecha: date | None = None) -> dict:
    """Cuerpo de una sesion de tres series con la carga indicada."""
    cuerpo = {
        "series": [
            {
                "ejercicio_id": ejercicio_id,
                "numero_serie": numero,
                "repeticiones": 10,
                "peso_kg": peso,
            }
            for numero in (1, 2, 3)
        ]
    }
    if fecha is not None:
        cuerpo["fecha"] = fecha.isoformat()
    return cuerpo


def test_la_senda_empieza_en_el_primer_nivel(cliente, token_usuario):
    """Una cuenta nueva ve la pantalla completa, no una pantalla vacia."""
    respuesta = cliente.get("/api/v1/juego", headers=encabezado(token_usuario))
    assert respuesta.status_code == 200

    estado = respuesta.json()
    assert estado["nivel"] == 1
    assert estado["puntos_totales"] == 0
    # El catalogo de insignias viaja completo, con las bloqueadas y sus pistas.
    assert estado["logros_totales"] == len(motor.LOGROS)
    assert estado["logros_obtenidos"] == 0
    # El unico hito del primer dia es haberse unido.
    assert [hito["tipo"] for hito in estado["hitos"]] == ["inicio"]
    assert estado["motivos"], "La pantalla debe poder explicar de dónde salen los puntos."
    assert "animo" not in estado and "gala" not in estado


def test_registrar_una_sesion_otorga_puntos_y_la_primera_insignia(
    cliente, token_usuario, ejercicio_id
):
    respuesta = cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json=_sesion(ejercicio_id, 40.0),
        headers=encabezado(token_usuario),
    )
    assert respuesta.status_code == 201

    recompensa = respuesta.json()["recompensa"]
    assert recompensa is not None
    assert recompensa["puntos_ganados"] >= motor.PUNTOS_POR_SESION
    assert recompensa["puntos_totales"] == recompensa["puntos_ganados"]
    assert "primera_sesion" in recompensa["logros_nuevos"]
    assert "primera_marca" in recompensa["logros_nuevos"]
    # El detalle nombra cada motivo: la cifra sola no explica de dónde salió.
    assert any(
        punto["tipo"] == motor.TipoEvento.SESION for punto in recompensa["detalle"]
    )


def test_la_segunda_sesion_del_mismo_dia_no_vuelve_a_pagar(
    cliente, token_usuario, ejercicio_id
):
    """Es la regla que impide que el sistema premie entrenar dos veces al día."""
    primera = cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json=_sesion(ejercicio_id, 40.0),
        headers=encabezado(token_usuario),
    )
    assert primera.status_code == 201
    total_tras_la_primera = primera.json()["recompensa"]["puntos_totales"]

    segunda = cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json=_sesion(ejercicio_id, 40.0),
        headers=encabezado(token_usuario),
    )
    assert segunda.status_code == 201

    recompensa = segunda.json()["recompensa"]
    # La sesión se guarda —el usuario entrenó— pero no paga de nuevo el día.
    assert not any(
        punto["tipo"] == motor.TipoEvento.SESION for punto in recompensa["detalle"]
    )
    assert recompensa["puntos_totales"] == total_tras_la_primera


def test_repetir_la_misma_carga_no_vuelve_a_pagar_la_marca(
    cliente, token_usuario, ejercicio_id
):
    """Una marca personal se paga la primera vez que se alcanza, no cada vez."""
    ayer = date.today() - timedelta(days=1)
    cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json=_sesion(ejercicio_id, 50.0, ayer),
        headers=encabezado(token_usuario),
    )

    hoy = cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json=_sesion(ejercicio_id, 50.0),
        headers=encabezado(token_usuario),
    )
    assert hoy.status_code == 201

    detalle = hoy.json()["recompensa"]["detalle"]
    assert not any(
        punto["tipo"] == motor.TipoEvento.MARCA_PERSONAL for punto in detalle
    )


def test_subir_la_carga_paga_una_marca_nueva(cliente, token_usuario, ejercicio_id):
    ayer = date.today() - timedelta(days=1)
    cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json=_sesion(ejercicio_id, 50.0, ayer),
        headers=encabezado(token_usuario),
    )

    hoy = cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json=_sesion(ejercicio_id, 55.0),
        headers=encabezado(token_usuario),
    )
    assert hoy.status_code == 201

    detalle = hoy.json()["recompensa"]["detalle"]
    assert any(punto["tipo"] == motor.TipoEvento.MARCA_PERSONAL for punto in detalle)


def test_el_volumen_declarado_no_infla_los_puntos_sin_limite(
    cliente, token_usuario, ejercicio_id
):
    """Quien anota una carga desmedida no gana más que quien entrena bien."""
    respuesta = cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json={
            "series": [
                {
                    "ejercicio_id": ejercicio_id,
                    "numero_serie": numero,
                    "repeticiones": 100,
                    "peso_kg": 500.0,
                }
                for numero in range(1, 21)
            ]
        },
        headers=encabezado(token_usuario),
    )
    assert respuesta.status_code == 201

    detalle = respuesta.json()["recompensa"]["detalle"]
    volumen = next(
        punto for punto in detalle if punto["tipo"] == motor.TipoEvento.VOLUMEN
    )
    assert volumen["puntos"] == motor.PUNTOS_MAXIMOS_POR_VOLUMEN
    # Y las marcas de una sola sesión también están acotadas.
    marcas = [
        punto for punto in detalle if punto["tipo"] == motor.TipoEvento.MARCA_PERSONAL
    ]
    assert len(marcas) <= motor.MARCAS_QUE_PUNTUAN_POR_SESION


def test_la_senda_registra_el_camino_recorrido(cliente, token_usuario, ejercicio_id):
    """El camino es el argumento de la pantalla: sin hitos no hay nada que ver."""
    cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json=_sesion(ejercicio_id, 60.0),
        headers=encabezado(token_usuario),
    )

    respuesta = cliente.get("/api/v1/juego", headers=encabezado(token_usuario))
    assert respuesta.status_code == 200

    estado = respuesta.json()
    assert estado["puntos_totales"] > 0
    assert estado["sesiones_totales"] == 1
    assert estado["racha_semanas"] >= 1

    tipos = [hito["tipo"] for hito in estado["hitos"]]
    assert "logro" in tipos
    assert tipos[-1] == "inicio", "El camino se lee del hito más nuevo al más antiguo."

    conseguidas = [logro for logro in estado["logros"] if logro["obtenido"]]
    assert conseguidas and all(logro["fecha"] for logro in conseguidas)
    bloqueadas = [logro for logro in estado["logros"] if not logro["obtenido"]]
    assert bloqueadas and all(logro["pista"] for logro in bloqueadas)


def test_la_senda_es_un_dato_personal(cliente, token_usuario, token_segundo_usuario, ejercicio_id):
    """Regla del negocio RN-06: nadie ve el avance de otra cuenta."""
    cliente.post(
        "/api/v1/entrenamiento/sesiones",
        json=_sesion(ejercicio_id, 70.0),
        headers=encabezado(token_usuario),
    )

    ajena = cliente.get("/api/v1/juego", headers=encabezado(token_segundo_usuario))
    assert ajena.status_code == 200
    assert ajena.json()["puntos_totales"] == 0
    assert ajena.json()["sesiones_totales"] == 0


def test_la_senda_exige_sesion_iniciada(cliente):
    assert cliente.get("/api/v1/juego").status_code == 401
