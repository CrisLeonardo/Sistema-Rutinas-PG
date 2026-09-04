"""Pruebas de la bitacora de entrenamiento.

La rutina era de solo lectura: el sistema prescribia series y repeticiones y no
tenia forma de saber si se ejecutaron ni con cuanto peso. Estas pruebas verifican
el ciclo completo —abrir la sesion, registrar lo hecho, recibir la carga de la
proxima— y el aislamiento de la bitacora entre cuentas, que es la regla del
negocio *f* aplicada a un dato personal nuevo.
"""

from datetime import date, timedelta

import pytest

from app.motor.progresion import Decision

from .conftest import encabezado

RUTA_SESIONES = "/api/v1/entrenamiento/sesiones"
RUTA_RESUMEN = "/api/v1/entrenamiento/resumen"

PERFIL = {
    "peso_kg": 75.0,
    "estatura_cm": 172.0,
    "edad": 26,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "ganancia_muscular",
    "nivel_experiencia": "principiante",
    "dias_entrenamiento_semana": 4,
}


@pytest.fixture(name="con_rutina")
def fixture_con_rutina(cliente, token_usuario):
    """Deja al usuario con plan y rutina generados."""
    cliente.post("/api/v1/perfil-biometrico", json=PERFIL, headers=encabezado(token_usuario))
    respuesta = cliente.post("/api/v1/plan-nutricional", headers=encabezado(token_usuario))
    assert respuesta.status_code == 201, respuesta.text
    return token_usuario


def primera_sesion(cliente, token) -> dict:
    rutina = cliente.get("/api/v1/rutina", headers=encabezado(token)).json()
    return rutina["sesiones"][0]


def abrir(cliente, token, sesion_id) -> dict:
    respuesta = cliente.get(f"{RUTA_SESIONES}/{sesion_id}", headers=encabezado(token))
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def registrar(cliente, token, abierta, repeticiones, peso, dias_atras=0, esfuerzo=6):
    """Registra la sesion completa con las mismas repeticiones y peso en todo."""
    series = [
        {
            "ejercicio_id": ejercicio["ejercicio_id"],
            "numero_serie": numero,
            "repeticiones": repeticiones,
            "peso_kg": peso,
        }
        for ejercicio in abierta["ejercicios"]
        for numero in range(1, ejercicio["series"] + 1)
    ]
    return cliente.post(
        RUTA_SESIONES,
        json={
            "sesion_id": abierta["sesion_id"],
            "fecha": str(date.today() - timedelta(days=dias_atras)),
            "duracion_minutos": 55,
            "percepcion_esfuerzo": esfuerzo,
            "series": series,
        },
        headers=encabezado(token),
    )


# --------------------------------------------------------------------------
# Abrir una sesion
# --------------------------------------------------------------------------


def test_la_sesion_se_abre_con_su_prescripcion(cliente, con_rutina):
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])

    assert abierta["nombre_grupo"] == prescrita["nombre_grupo"]
    assert abierta["nombre_dia"] == prescrita["nombre_dia"]
    assert len(abierta["ejercicios"]) == len(prescrita["ejercicios"])
    assert abierta["series_totales"] > 0
    assert abierta["ya_registrada_hoy"] is False


def test_sin_historial_cada_ejercicio_pide_elegir_la_carga(cliente, con_rutina):
    abierta = abrir(cliente, con_rutina, primera_sesion(cliente, con_rutina)["id"])

    for ejercicio in abierta["ejercicios"]:
        assert ejercicio["recomendacion"]["decision"] == Decision.PRIMERA_VEZ
        assert ejercicio["recomendacion"]["carga_sugerida_kg"] is None
        assert ejercicio["ultima_vez"] == []


def test_no_se_puede_abrir_la_sesion_de_otra_persona(
    cliente, con_rutina, token_segundo_usuario
):
    """Regla del negocio *f*: la rutina y su bitacora son datos personales."""
    prescrita = primera_sesion(cliente, con_rutina)

    respuesta = cliente.get(
        f"{RUTA_SESIONES}/{prescrita['id']}", headers=encabezado(token_segundo_usuario)
    )

    assert respuesta.status_code == 404


def test_abrir_una_sesion_inexistente_devuelve_no_encontrado(cliente, con_rutina):
    assert (
        cliente.get(f"{RUTA_SESIONES}/99999", headers=encabezado(con_rutina)).status_code
        == 404
    )


def test_abrir_una_sesion_exige_sesion_activa(cliente, con_rutina):
    prescrita = primera_sesion(cliente, con_rutina)

    assert cliente.get(f"{RUTA_SESIONES}/{prescrita['id']}").status_code == 401


# --------------------------------------------------------------------------
# Registrar
# --------------------------------------------------------------------------


def test_una_sesion_registrada_se_guarda_completa(cliente, con_rutina):
    abierta = abrir(cliente, con_rutina, primera_sesion(cliente, con_rutina)["id"])

    respuesta = registrar(cliente, con_rutina, abierta, repeticiones=8, peso=40.0)

    assert respuesta.status_code == 201, respuesta.text
    guardada = respuesta.json()["sesion"]
    assert guardada["series_totales"] == abierta["series_totales"]
    assert guardada["duracion_minutos"] == 55
    assert guardada["percepcion_esfuerzo"] == 6
    assert guardada["volumen_kg"] == pytest.approx(abierta["series_totales"] * 8 * 40.0)


def test_la_respuesta_dice_que_hara_el_sistema_la_proxima_vez(cliente, con_rutina):
    """Una bitacora que no devuelve nada es un formulario, no una herramienta."""
    abierta = abrir(cliente, con_rutina, primera_sesion(cliente, con_rutina)["id"])

    cuerpo = registrar(cliente, con_rutina, abierta, repeticiones=8, peso=40.0).json()

    assert cuerpo["mensaje"]
    assert len(cuerpo["progresiones"]) == len(abierta["ejercicios"])


def test_la_sesion_registrada_se_marca_como_hecha_hoy(cliente, con_rutina):
    """Registrar dos veces el mismo entrenamiento duplicaria el volumen."""
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    registrar(cliente, con_rutina, abierta, repeticiones=8, peso=40.0)

    de_nuevo = abrir(cliente, con_rutina, prescrita["id"])

    assert de_nuevo["ya_registrada_hoy"] is True


def test_no_se_admite_una_sesion_sin_series(cliente, con_rutina):
    respuesta = cliente.post(
        RUTA_SESIONES,
        json={"series": []},
        headers=encabezado(con_rutina),
    )

    assert respuesta.status_code == 422


def test_no_se_admite_entrenar_en_el_futuro(cliente, con_rutina):
    abierta = abrir(cliente, con_rutina, primera_sesion(cliente, con_rutina)["id"])

    respuesta = registrar(cliente, con_rutina, abierta, 8, 40.0, dias_atras=-3)

    assert respuesta.status_code == 422


def test_no_se_admite_una_carga_fuera_de_escala(cliente, con_rutina):
    abierta = abrir(cliente, con_rutina, primera_sesion(cliente, con_rutina)["id"])

    respuesta = registrar(cliente, con_rutina, abierta, 8, 900.0)

    assert respuesta.status_code == 422


def test_no_se_admite_un_ejercicio_que_no_existe(cliente, con_rutina):
    respuesta = cliente.post(
        RUTA_SESIONES,
        json={
            "series": [
                {"ejercicio_id": 99999, "numero_serie": 1, "repeticiones": 10, "peso_kg": 40}
            ]
        },
        headers=encabezado(con_rutina),
    )

    assert respuesta.status_code == 404


def test_no_se_puede_registrar_contra_la_sesion_de_otra_persona(
    cliente, con_rutina, token_segundo_usuario
):
    """Sin esta comprobacion, bastaria enviar el identificador ajeno."""
    prescrita = primera_sesion(cliente, con_rutina)

    respuesta = cliente.post(
        RUTA_SESIONES,
        json={
            "sesion_id": prescrita["id"],
            "series": [
                {
                    "ejercicio_id": prescrita["ejercicios"][0]["ejercicio_id"],
                    "numero_serie": 1,
                    "repeticiones": 10,
                    "peso_kg": 40,
                }
            ],
        },
        headers=encabezado(token_segundo_usuario),
    )

    assert respuesta.status_code == 404


def test_se_puede_registrar_sin_sesion_prescrita(cliente, con_rutina):
    """Entrenar por fuera de la rutina tambien cuenta."""
    prescrita = primera_sesion(cliente, con_rutina)

    respuesta = cliente.post(
        RUTA_SESIONES,
        json={
            "series": [
                {
                    "ejercicio_id": prescrita["ejercicios"][0]["ejercicio_id"],
                    "numero_serie": 1,
                    "repeticiones": 12,
                    "peso_kg": 30,
                }
            ]
        },
        headers=encabezado(con_rutina),
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["sesion"]["sesion_id"] is None


# --------------------------------------------------------------------------
# El ciclo de progresion, extremo a extremo
# --------------------------------------------------------------------------


def test_sin_completar_el_rango_la_carga_se_repite(cliente, con_rutina):
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    minimo = abierta["ejercicios"][0]["repeticiones_min"]

    registrar(cliente, con_rutina, abierta, repeticiones=minimo, peso=40.0, dias_atras=7)
    siguiente = abrir(cliente, con_rutina, prescrita["id"])

    recomendacion = siguiente["ejercicios"][0]["recomendacion"]
    assert recomendacion["decision"] == Decision.MANTENER
    assert recomendacion["carga_sugerida_kg"] == 40.0


def test_al_dominar_el_rango_el_sistema_sube_la_carga_solo(cliente, con_rutina):
    """Es lo que la rutina no hacia: la de la semana doce era la de la primera."""
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    maximo = abierta["ejercicios"][0]["repeticiones_max"]

    registrar(cliente, con_rutina, abierta, repeticiones=maximo, peso=40.0, dias_atras=7)
    siguiente = abrir(cliente, con_rutina, prescrita["id"])

    recomendacion = siguiente["ejercicios"][0]["recomendacion"]
    assert recomendacion["decision"] == Decision.SUBIR_CARGA
    assert recomendacion["carga_sugerida_kg"] == 42.5
    assert recomendacion["carga_previa_kg"] == 40.0


def test_el_incremento_respeta_la_regla_del_negocio_d(cliente, con_rutina):
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    maximo = abierta["ejercicios"][0]["repeticiones_max"]

    registrar(cliente, con_rutina, abierta, repeticiones=maximo, peso=60.0, dias_atras=7)
    siguiente = abrir(cliente, con_rutina, prescrita["id"])

    recomendacion = siguiente["ejercicios"][0]["recomendacion"]
    incremento = (recomendacion["carga_sugerida_kg"] - 60.0) / 60.0
    assert incremento <= 0.10 + 1e-9


def test_la_sesion_muestra_lo_que_se_hizo_la_ultima_vez(cliente, con_rutina):
    """La sugerencia sin el antecedente no se puede juzgar."""
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])

    registrar(cliente, con_rutina, abierta, repeticiones=10, peso=45.0, dias_atras=7)
    siguiente = abrir(cliente, con_rutina, prescrita["id"])

    ejercicio = siguiente["ejercicios"][0]
    assert ejercicio["ultima_vez"]
    assert ejercicio["fecha_ultima_vez"] == str(date.today() - timedelta(days=7))
    assert all(serie["peso_kg"] == 45.0 for serie in ejercicio["ultima_vez"])


def test_el_historial_sobrevive_a_regenerar_el_plan(cliente, con_rutina):
    """La bitacora se enlaza al catalogo, no a la sesion prescrita.

    Al regenerarse el plan, las sesiones prescritas se sustituyen por otras
    nuevas. El historial de cargas debe sobrevivir a ese cambio: es lo que da
    continuidad al entrenamiento.
    """
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    maximo = abierta["ejercicios"][0]["repeticiones_max"]
    registrar(cliente, con_rutina, abierta, repeticiones=maximo, peso=50.0, dias_atras=7)

    cliente.post("/api/v1/plan-nutricional", headers=encabezado(con_rutina))

    nueva = primera_sesion(cliente, con_rutina)
    assert nueva["id"] != prescrita["id"], "el plan nuevo trae sesiones nuevas"

    abierta_nueva = abrir(cliente, con_rutina, nueva["id"])
    recomendacion = abierta_nueva["ejercicios"][0]["recomendacion"]
    assert recomendacion["carga_previa_kg"] == 50.0
    assert recomendacion["decision"] == Decision.SUBIR_CARGA


# --------------------------------------------------------------------------
# Historial, marcas y resumen
# --------------------------------------------------------------------------


def test_la_bitacora_lista_las_sesiones_de_la_mas_reciente(cliente, con_rutina):
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    registrar(cliente, con_rutina, abierta, 8, 40.0, dias_atras=14)
    registrar(cliente, con_rutina, abierta, 9, 42.5, dias_atras=7)

    sesiones = cliente.get(RUTA_SESIONES, headers=encabezado(con_rutina)).json()

    assert len(sesiones) == 2
    assert sesiones[0]["fecha"] > sesiones[1]["fecha"]
    assert sesiones[0]["nombre_grupo"] == prescrita["nombre_grupo"]


def test_la_bitacora_de_una_cuenta_no_alcanza_a_la_otra(
    cliente, con_rutina, token_segundo_usuario
):
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    registrar(cliente, con_rutina, abierta, 10, 40.0)

    ajenas = cliente.get(RUTA_SESIONES, headers=encabezado(token_segundo_usuario)).json()

    assert ajenas == []


def test_el_historial_de_un_ejercicio_se_lee_en_el_tiempo(cliente, con_rutina):
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    ejercicio_id = abierta["ejercicios"][0]["ejercicio_id"]
    registrar(cliente, con_rutina, abierta, 10, 40.0, dias_atras=14)
    registrar(cliente, con_rutina, abierta, 10, 45.0, dias_atras=7)

    historial = cliente.get(
        f"/api/v1/entrenamiento/ejercicios/{ejercicio_id}", headers=encabezado(con_rutina)
    ).json()

    assert historial["sesiones_registradas"] == 2
    assert [p["carga_maxima_kg"] for p in historial["puntos"]] == [40.0, 45.0]
    assert historial["cambio_carga_kg"] == 5.0


def test_la_marca_personal_estima_la_repeticion_maxima(cliente, con_rutina):
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    ejercicio_id = abierta["ejercicios"][0]["ejercicio_id"]
    registrar(cliente, con_rutina, abierta, 10, 60.0, dias_atras=7)

    marca = cliente.get(
        f"/api/v1/entrenamiento/ejercicios/{ejercicio_id}", headers=encabezado(con_rutina)
    ).json()["marca"]

    assert marca["carga_maxima_kg"] == 60.0
    assert marca["repeticiones_en_la_maxima"] == 10
    # Epley: 60 x (1 + 10/30) = 80
    assert marca["repeticion_maxima_estimada_kg"] == pytest.approx(80.0)


def test_el_resumen_cuenta_la_constancia(cliente, con_rutina):
    prescrita = primera_sesion(cliente, con_rutina)
    abierta = abrir(cliente, con_rutina, prescrita["id"])
    registrar(cliente, con_rutina, abierta, 10, 40.0, dias_atras=0)

    resumen = cliente.get(RUTA_RESUMEN, headers=encabezado(con_rutina)).json()

    assert resumen["sesiones_totales"] == 1
    assert resumen["sesiones_esta_semana"] >= 1
    assert resumen["racha_semanas"] >= 1
    assert resumen["ultima_sesion"] == str(date.today())
    assert resumen["marcas"]


def test_el_resumen_de_una_cuenta_sin_bitacora_no_falla(cliente, token_usuario):
    resumen = cliente.get(RUTA_RESUMEN, headers=encabezado(token_usuario))

    assert resumen.status_code == 200
    cuerpo = resumen.json()
    assert cuerpo["sesiones_totales"] == 0
    assert cuerpo["racha_semanas"] == 0
    assert cuerpo["ultima_sesion"] is None
    assert cuerpo["marcas"] == []


def test_el_volumen_ignora_los_ejercicios_sin_carga(cliente, con_rutina):
    """El progreso del peso corporal se lee en repeticiones, no en volumen."""
    prescrita = primera_sesion(cliente, con_rutina)
    ejercicio_id = prescrita["ejercicios"][0]["ejercicio_id"]

    respuesta = cliente.post(
        RUTA_SESIONES,
        json={
            "series": [
                {"ejercicio_id": ejercicio_id, "numero_serie": 1, "repeticiones": 15},
                {
                    "ejercicio_id": ejercicio_id,
                    "numero_serie": 2,
                    "repeticiones": 10,
                    "peso_kg": 20,
                },
            ]
        },
        headers=encabezado(con_rutina),
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["sesion"]["volumen_kg"] == pytest.approx(200.0)
    assert respuesta.json()["sesion"]["repeticiones_totales"] == 25


def test_la_bitacora_exige_sesion_activa(cliente):
    assert cliente.get(RUTA_SESIONES).status_code == 401
    assert cliente.get(RUTA_RESUMEN).status_code == 401
    assert cliente.post(RUTA_SESIONES, json={"series": []}).status_code == 401
