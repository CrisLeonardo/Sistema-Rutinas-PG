"""Contraseña temporal del administrador, que sustituye a la recuperación por correo."""

from app.esquemas.usuario import RegistroUsuario
from tests.conftest import CORREO_DEPORTISTA, encabezado


def _id_de(cliente, token_administrador, correo):
    cuentas = cliente.get("/api/v1/usuarios", headers=encabezado(token_administrador)).json()
    return next(c["id"] for c in cuentas if c["correo"] == correo)


def test_el_administrador_restablece_el_acceso_y_cierra_las_sesiones(cliente, token_administrador, token_usuario):
    cuenta = _id_de(cliente, token_administrador, CORREO_DEPORTISTA)
    respuesta = cliente.post(f"/api/v1/usuarios/{cuenta}/contrasena-temporal", headers=encabezado(token_administrador))
    assert respuesta.status_code == 200
    temporal = respuesta.json()["contrasena_temporal"]
    # Cumple las reglas del registro.
    RegistroUsuario(correo="regla@ejemplo.gt", nombre="Regla", contrasena=temporal)
    assert "una sola vez" in respuesta.json()["mensaje"]
    # La sesión anterior queda cerrada y la contraseña nueva permite entrar.
    assert cliente.get("/api/v1/autenticacion/sesion", headers=encabezado(token_usuario)).status_code == 401
    acceso = cliente.post("/api/v1/autenticacion/acceso", json={"correo": CORREO_DEPORTISTA, "contrasena": temporal})
    assert acceso.status_code == 200


def test_solo_el_administrador_genera_contrasenas_y_nunca_la_propia(cliente, token_administrador, token_usuario):
    cuenta = _id_de(cliente, token_administrador, CORREO_DEPORTISTA)
    assert cliente.post(f"/api/v1/usuarios/{cuenta}/contrasena-temporal", headers=encabezado(token_usuario)).status_code == 403
    propia = cliente.get("/api/v1/autenticacion/sesion", headers=encabezado(token_administrador)).json()["id"]
    respuesta = cliente.post(f"/api/v1/usuarios/{propia}/contrasena-temporal", headers=encabezado(token_administrador))
    assert respuesta.status_code == 409
    assert cliente.post("/api/v1/usuarios/99999/contrasena-temporal", headers=encabezado(token_administrador)).status_code == 404
