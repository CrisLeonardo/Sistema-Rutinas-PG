"""Fechas y horas en la zona de Guatemala, aunque el servidor corra en UTC.

Regresiones de la auditoría final del 31 de octubre de 2026: el servicio
publicado corre en UTC, de modo que después de las seis de la tarde en
Guatemala el servidor ya vive el día siguiente. Una sesión registrada por la
noche quedaba con la fecha de mañana, recibía la insignia «Antes del sol» y las
pantallas mostraban las marcas de tiempo con seis horas de más.
"""

from datetime import date, datetime, timezone

import pytest

from app.nucleo import tiempo
from app.servicios import alimentacion as servicio_alimentacion
from app.servicios import entrenamiento as servicio_entrenamiento
from tests.conftest import encabezado


def _fijar_reloj(monkeypatch, instante_utc: datetime) -> None:
    """Hace que el servidor crea que es `instante_utc`, sin depender del equipo."""

    class Reloj(datetime):
        @classmethod
        def now(cls, tz=None):
            return instante_utc.replace(tzinfo=None) if tz is None else instante_utc.astimezone(tz)

    monkeypatch.setattr(tiempo, "datetime", Reloj)
    monkeypatch.setattr(servicio_entrenamiento, "datetime", Reloj)


def _sesion(ejercicio_id: int) -> dict:
    return {"series": [{"ejercicio_id": ejercicio_id, "numero_serie": 1, "repeticiones": 10, "peso_kg": 20}]}


@pytest.fixture(name="ejercicio_id")
def fixture_ejercicio_id(cliente, token_usuario) -> int:
    respuesta = cliente.get("/api/v1/catalogos/ejercicios", headers=encabezado(token_usuario))
    return respuesta.json()[0]["id"]


def test_la_hora_local_es_la_de_guatemala():
    local = tiempo.a_hora_local(datetime(2026, 11, 1, 0, 40))
    assert (local.date(), local.hour, local.minute) == (date(2026, 10, 31), 18, 40)


def test_una_sesion_nocturna_queda_con_la_fecha_de_hoy_y_sin_insignia_de_madrugada(
    monkeypatch, cliente, token_usuario, ejercicio_id
):
    # 00:40 UTC del 1 de noviembre son las 18:40 del 31 de octubre en Guatemala.
    _fijar_reloj(monkeypatch, datetime(2026, 11, 1, 0, 40, tzinfo=timezone.utc))
    respuesta = cliente.post("/api/v1/entrenamiento/sesiones", json=_sesion(ejercicio_id),
                             headers=encabezado(token_usuario))
    assert respuesta.status_code == 201
    assert respuesta.json()["sesion"]["fecha"] == "2026-10-31"
    assert "madrugador" not in respuesta.json()["recompensa"]["logros_nuevos"]


def test_una_sesion_antes_de_las_siete_locales_si_es_de_madrugada(
    monkeypatch, cliente, token_usuario, ejercicio_id
):
    # 12:30 UTC son las 06:30 en Guatemala.
    _fijar_reloj(monkeypatch, datetime(2026, 10, 31, 12, 30, tzinfo=timezone.utc))
    respuesta = cliente.post("/api/v1/entrenamiento/sesiones", json=_sesion(ejercicio_id),
                             headers=encabezado(token_usuario))
    assert respuesta.status_code == 201
    assert "madrugador" in respuesta.json()["recompensa"]["logros_nuevos"]


def test_las_marcas_de_tiempo_se_publican_con_su_zona(cliente, token_usuario):
    """Sin la zona, el navegador leía la hora UTC como si fuera local."""
    cuenta = cliente.get("/api/v1/autenticacion/sesion", headers=encabezado(token_usuario)).json()
    assert cuenta["fecha_registro"].endswith("+00:00")
    assert datetime.fromisoformat(cuenta["fecha_registro"]).tzinfo is not None


def test_el_menu_de_hoy_sigue_el_dia_de_la_semana_preparada(monkeypatch):
    datos = {"dias": [{"dia": n} for n in range(1, 8)], "preparada_el": "2026-10-26"}
    monkeypatch.setattr(servicio_alimentacion, "hoy_local", lambda: date(2026, 10, 26))
    assert servicio_alimentacion.dia_de_hoy(datos) == 1
    monkeypatch.setattr(servicio_alimentacion, "hoy_local", lambda: date(2026, 10, 31))
    assert servicio_alimentacion.dia_de_hoy(datos) == 6
    monkeypatch.setattr(servicio_alimentacion, "hoy_local", lambda: date(2026, 11, 2))
    assert servicio_alimentacion.dia_de_hoy(datos) == 1  # la semana se repite en ciclo
    assert servicio_alimentacion.dia_de_hoy({"dias": datos["dias"]}) == 1  # semana antigua sin fecha


@pytest.mark.parametrize(
    ("proteina", "carbohidrato", "grasa", "energia"),
    [(90, 90, 0.3, 26), (1, 5, 0.3, 500)],
    ids=["macronutrientes-sobre-100-g", "energia-incoherente"],
)
def test_el_catalogo_rechaza_una_composicion_imposible(
    cliente, token_administrador, proteina, carbohidrato, grasa, energia
):
    respuesta = cliente.post(
        "/api/v1/catalogos/alimentos",
        json={"nombre": "Alimento imposible", "categoria": "verdura", "energia_kcal_100g": energia,
              "proteina_g_100g": proteina, "carbohidrato_g_100g": carbohidrato, "grasa_g_100g": grasa},
        headers=encabezado(token_administrador),
    )
    assert respuesta.status_code == 422
    assert "Revise los valores" in respuesta.json()["detail"][0]["msg"]
