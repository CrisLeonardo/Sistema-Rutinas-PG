"""Pruebas del endurecimiento del acceso (requerimiento no funcional 4.5.1).

Cubren tres huecos que la Iteracion 1 dejo abiertos: nada limitaba los intentos
de acceso, no existia forma de cambiar la contrasena, y las respuestas de la
interfaz de programacion no llevaban encabezados de seguridad.
"""

import pytest

from app.nucleo.limitador import (
    LimitadorDeIntentos,
    limitador_de_acceso,
    limitador_de_registro,
)

from .conftest import CONTRASENA_DEPORTISTA, CORREO_DEPORTISTA, encabezado


@pytest.fixture(autouse=True)
def limitadores_limpios():
    """Aisla cada prueba: el limitador vive en la memoria del proceso."""
    limitador_de_acceso.reiniciar()
    limitador_de_registro.reiniciar()
    yield
    limitador_de_acceso.reiniciar()
    limitador_de_registro.reiniciar()


# --------------------------------------------------------------------------
# Limitador
# --------------------------------------------------------------------------


def test_el_limitador_admite_los_intentos_declarados():
    limitador = LimitadorDeIntentos(intentos_maximos=3)

    assert limitador.revisar("llave").permitido
    assert limitador.registrar_fallo("llave").permitido
    assert limitador.registrar_fallo("llave").permitido


def test_el_limitador_bloquea_al_agotar_los_intentos():
    limitador = LimitadorDeIntentos(intentos_maximos=3, bloqueo_segundos=60)

    limitador.registrar_fallo("llave")
    limitador.registrar_fallo("llave")
    veredicto = limitador.registrar_fallo("llave")

    assert not veredicto.permitido
    assert veredicto.segundos_de_espera == 60
    assert not limitador.revisar("llave").permitido


def test_un_acceso_correcto_limpia_el_historial():
    limitador = LimitadorDeIntentos(intentos_maximos=3)

    limitador.registrar_fallo("llave")
    limitador.registrar_fallo("llave")
    limitador.registrar_exito("llave")

    assert limitador.registrar_fallo("llave").permitido


def test_el_bloqueo_de_una_llave_no_alcanza_a_las_demas():
    limitador = LimitadorDeIntentos(intentos_maximos=2)

    limitador.registrar_fallo("una")
    limitador.registrar_fallo("una")

    assert not limitador.revisar("una").permitido
    assert limitador.revisar("otra").permitido


def test_el_registro_no_crece_sin_limite():
    """Una avalancha de llaves distintas no debe agotar la memoria del proceso."""
    limitador = LimitadorDeIntentos(intentos_maximos=50, ventana_segundos=0)

    for indice in range(5000):
        limitador.registrar_fallo(f"llave-{indice}")

    assert len(limitador._intentos) < 5000


# --------------------------------------------------------------------------
# Limite sobre la ruta de acceso
# --------------------------------------------------------------------------


def test_los_intentos_fallidos_terminan_bloqueados(cliente, token_usuario):
    """Nada impedia adivinar una contrasena a base de repetir la peticion."""
    del token_usuario  # la cuenta debe existir para que el caso sea el real

    respuestas = [
        cliente.post(
            "/api/v1/autenticacion/acceso",
            json={"correo": CORREO_DEPORTISTA, "contrasena": "incorrecta9"},
        ).status_code
        for _ in range(12)
    ]

    assert 401 in respuestas, "los primeros intentos se rechazan con normalidad"
    assert 429 in respuestas, "a partir de cierto punto el sistema deja de responder"
    assert respuestas[-1] == 429


def test_el_bloqueo_indica_cuanto_esperar(cliente, token_usuario):
    del token_usuario
    respuesta = None
    for _ in range(12):
        respuesta = cliente.post(
            "/api/v1/autenticacion/acceso",
            json={"correo": CORREO_DEPORTISTA, "contrasena": "incorrecta9"},
        )
        if respuesta.status_code == 429:
            break

    assert respuesta.status_code == 429
    assert "Retry-After" in respuesta.headers
    assert "minuto" in respuesta.json()["detail"]


def test_el_bloqueo_alcanza_tambien_a_la_contrasena_correcta(cliente, token_usuario):
    """Un bloqueo que la credencial correcta saltara no seria un bloqueo."""
    del token_usuario
    for _ in range(12):
        cliente.post(
            "/api/v1/autenticacion/acceso",
            json={"correo": CORREO_DEPORTISTA, "contrasena": "incorrecta9"},
        )

    respuesta = cliente.post(
        "/api/v1/autenticacion/acceso",
        json={"correo": CORREO_DEPORTISTA, "contrasena": CONTRASENA_DEPORTISTA},
    )

    assert respuesta.status_code == 429


def test_un_acceso_correcto_no_deja_rastro_de_intentos(cliente, token_usuario):
    del token_usuario
    for _ in range(3):
        cliente.post(
            "/api/v1/autenticacion/acceso",
            json={"correo": CORREO_DEPORTISTA, "contrasena": "incorrecta9"},
        )

    correcto = cliente.post(
        "/api/v1/autenticacion/acceso",
        json={"correo": CORREO_DEPORTISTA, "contrasena": CONTRASENA_DEPORTISTA},
    )
    assert correcto.status_code == 200

    # Tras el acceso correcto vuelve a haber margen completo de intentos.
    siguiente = cliente.post(
        "/api/v1/autenticacion/acceso",
        json={"correo": CORREO_DEPORTISTA, "contrasena": "incorrecta9"},
    )
    assert siguiente.status_code == 401


# --------------------------------------------------------------------------
# Cambio de contrasena
# --------------------------------------------------------------------------


def test_el_usuario_puede_cambiar_su_contrasena(cliente, token_usuario):
    respuesta = cliente.post(
        "/api/v1/autenticacion/cambio-de-contrasena",
        json={
            "contrasena_actual": CONTRASENA_DEPORTISTA,
            "contrasena_nueva": "Renovada2026",
        },
        headers=encabezado(token_usuario),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["token_acceso"], "debe emitir un token nuevo"

    limitador_de_acceso.reiniciar()
    con_la_nueva = cliente.post(
        "/api/v1/autenticacion/acceso",
        json={"correo": CORREO_DEPORTISTA, "contrasena": "Renovada2026"},
    )
    assert con_la_nueva.status_code == 200

    con_la_vieja = cliente.post(
        "/api/v1/autenticacion/acceso",
        json={"correo": CORREO_DEPORTISTA, "contrasena": CONTRASENA_DEPORTISTA},
    )
    assert con_la_vieja.status_code == 401


def test_el_cambio_exige_la_contrasena_vigente(cliente, token_usuario):
    """Un teléfono desatendido no debe bastar para quedarse con la cuenta."""
    respuesta = cliente.post(
        "/api/v1/autenticacion/cambio-de-contrasena",
        json={"contrasena_actual": "loQueSea9", "contrasena_nueva": "Renovada2026"},
        headers=encabezado(token_usuario),
    )

    assert respuesta.status_code == 400
    assert "actual" in respuesta.json()["detail"]


def test_la_contrasena_nueva_debe_ser_distinta(cliente, token_usuario):
    respuesta = cliente.post(
        "/api/v1/autenticacion/cambio-de-contrasena",
        json={
            "contrasena_actual": CONTRASENA_DEPORTISTA,
            "contrasena_nueva": CONTRASENA_DEPORTISTA,
        },
        headers=encabezado(token_usuario),
    )

    assert respuesta.status_code == 400


def test_la_contrasena_nueva_conserva_las_reglas_de_robustez(cliente, token_usuario):
    for debil in ("corta1", "sinnumeros", "12345678"):
        respuesta = cliente.post(
            "/api/v1/autenticacion/cambio-de-contrasena",
            json={
                "contrasena_actual": CONTRASENA_DEPORTISTA,
                "contrasena_nueva": debil,
            },
            headers=encabezado(token_usuario),
        )
        assert respuesta.status_code == 422, debil


def test_el_cambio_de_contrasena_exige_sesion(cliente):
    respuesta = cliente.post(
        "/api/v1/autenticacion/cambio-de-contrasena",
        json={"contrasena_actual": "cualquiera1", "contrasena_nueva": "Renovada2026"},
    )

    assert respuesta.status_code == 401


# --------------------------------------------------------------------------
# Encabezados de seguridad
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "encabezado_esperado",
    [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Content-Security-Policy",
        "Cache-Control",
    ],
)
def test_las_respuestas_llevan_encabezados_de_seguridad(cliente, encabezado_esperado):
    respuesta = cliente.get("/api/v1/estado")

    assert encabezado_esperado in respuesta.headers


def test_las_respuestas_con_datos_biometricos_no_se_guardan_en_memoria_intermedia(
    cliente, token_usuario
):
    """Un plan contiene datos de salud: no debe quedar en ninguna caché."""
    respuesta = cliente.get(
        "/api/v1/perfil-biometrico/historial", headers=encabezado(token_usuario)
    )

    assert respuesta.headers["Cache-Control"] == "no-store"


def test_el_servicio_no_puede_incrustarse_en_un_marco_ajeno(cliente):
    respuesta = cliente.get("/api/v1/estado")

    assert respuesta.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in respuesta.headers["Content-Security-Policy"]
