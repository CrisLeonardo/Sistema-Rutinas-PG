"""Pruebas funcionales de la epica E1, Acceso seguro.

Cada prueba corresponde a un criterio de aceptacion de la Tabla 10 del
Capitulo IV del proyecto de graduacion.
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.nucleo.configuracion import configuracion
from app.nucleo.seguridad import cifrar_contrasena, verificar_contrasena
from tests.conftest import encabezado

RUTA_REGISTRO = "/api/v1/autenticacion/registro"
RUTA_ACCESO = "/api/v1/autenticacion/acceso"
RUTA_SESION = "/api/v1/autenticacion/sesion"
RUTA_USUARIOS = "/api/v1/usuarios"

CUENTA_VALIDA = {
    "correo": "deportista@correo.com",
    "nombre": "Usuario Deportista",
    "contrasena": "Entreno2026",
}


# --------------------------------------------------------------------------
# HU-01. Registro de usuarios
# --------------------------------------------------------------------------


def test_registro_crea_la_cuenta_con_rol_de_usuario(cliente):
    """Al completar el registro, la cuenta queda creada con rol de usuario."""
    respuesta = cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["correo"] == CUENTA_VALIDA["correo"]
    assert cuerpo["rol"] == "usuario"
    assert cuerpo["activo"] is True


def test_registro_no_devuelve_la_contrasena(cliente):
    """La respuesta no expone la contrasena ni su resumen criptografico."""
    cuerpo = cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA).json()

    texto = str(cuerpo)
    assert "contrasena" not in cuerpo
    assert CUENTA_VALIDA["contrasena"] not in texto


@pytest.mark.parametrize(
    "correo",
    ["sin-arroba", "espacio @correo.com", "@correo.com", "usuario@", ""],
)
def test_registro_rechaza_correos_con_formato_invalido(cliente, correo):
    """El sistema rechaza correos con formato invalido."""
    datos = {**CUENTA_VALIDA, "correo": correo}

    assert cliente.post(RUTA_REGISTRO, json=datos).status_code == 422


def test_registro_rechaza_correo_ya_registrado(cliente):
    """El sistema rechaza correos ya registrados."""
    assert cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA).status_code == 201

    repetido = cliente.post(RUTA_REGISTRO, json={**CUENTA_VALIDA, "nombre": "Otro nombre"})

    assert repetido.status_code == 409


def test_registro_rechaza_correo_repetido_en_mayusculas(cliente):
    """La comparacion de correos no distingue mayusculas de minusculas."""
    cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)

    repetido = cliente.post(
        RUTA_REGISTRO, json={**CUENTA_VALIDA, "correo": "Deportista@Correo.com"}
    )

    assert repetido.status_code == 409


@pytest.mark.parametrize("contrasena", ["Corta1", "Abc123", "1234567"])
def test_registro_exige_minimo_ocho_caracteres(cliente, contrasena):
    """La contrasena exige un minimo de ocho caracteres."""
    datos = {**CUENTA_VALIDA, "contrasena": contrasena}

    assert cliente.post(RUTA_REGISTRO, json=datos).status_code == 422


def test_contrasena_se_almacena_cifrada(cliente, fabrica_sesiones):
    """La contrasena se almacena cifrada y no puede recuperarse en texto plano."""
    from app.servicios import autenticacion

    cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)

    with fabrica_sesiones() as sesion:
        usuario = autenticacion.buscar_por_correo(sesion, CUENTA_VALIDA["correo"])
        assert usuario is not None
        assert usuario.contrasena_cifrada != CUENTA_VALIDA["contrasena"]
        assert usuario.contrasena_cifrada.startswith("$2b$")
        assert verificar_contrasena(CUENTA_VALIDA["contrasena"], usuario.contrasena_cifrada)


def test_el_cifrado_usa_sal_aleatoria():
    """Dos cifrados de la misma contrasena producen resumenes distintos."""
    primero = cifrar_contrasena("Entreno2026")
    segundo = cifrar_contrasena("Entreno2026")

    assert primero != segundo
    assert verificar_contrasena("Entreno2026", primero)
    assert verificar_contrasena("Entreno2026", segundo)


# --------------------------------------------------------------------------
# HU-02. Inicio y cierre de sesion seguro
# --------------------------------------------------------------------------


def test_acceso_con_credenciales_correctas_emite_token(cliente):
    """El inicio de sesion valido devuelve el token y los datos de la cuenta."""
    cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)

    respuesta = cliente.post(
        RUTA_ACCESO,
        json={
            "correo": CUENTA_VALIDA["correo"],
            "contrasena": CUENTA_VALIDA["contrasena"],
        },
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_acceso"]
    assert cuerpo["usuario"]["correo"] == CUENTA_VALIDA["correo"]


def test_el_mensaje_de_error_no_revela_cual_dato_es_erroneo(cliente):
    """Correo inexistente y contrasena incorrecta producen el mismo mensaje."""
    cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)

    correo_inexistente = cliente.post(
        RUTA_ACCESO, json={"correo": "nadie@correo.com", "contrasena": "Entreno2026"}
    )
    contrasena_incorrecta = cliente.post(
        RUTA_ACCESO,
        json={"correo": CUENTA_VALIDA["correo"], "contrasena": "OtraClave2026"},
    )

    assert correo_inexistente.status_code == contrasena_incorrecta.status_code == 401
    assert correo_inexistente.json()["detail"] == contrasena_incorrecta.json()["detail"]


def test_la_sesion_expira_en_los_minutos_configurados(cliente):
    """La vigencia del token corresponde al periodo de inactividad configurado."""
    cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)

    cuerpo = cliente.post(
        RUTA_ACCESO,
        json={
            "correo": CUENTA_VALIDA["correo"],
            "contrasena": CUENTA_VALIDA["contrasena"],
        },
    ).json()

    assert cuerpo["expira_en_segundos"] == configuracion.minutos_expiracion_sesion * 60


def test_sin_sesion_activa_no_se_accede_a_ninguna_pantalla_interna(cliente):
    """Sin token, los recursos protegidos responden con acceso no autorizado."""
    assert cliente.get(RUTA_SESION).status_code == 401
    assert cliente.get(RUTA_USUARIOS).status_code == 401


def test_un_token_vencido_es_rechazado(cliente):
    """Un token cuya vigencia expiro no permite acceder a los recursos."""
    cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)
    emitido = datetime.now(timezone.utc) - timedelta(minutes=90)
    token_vencido = jwt.encode(
        {
            "sub": "1",
            "rol": "usuario",
            "iat": emitido,
            "exp": emitido + timedelta(minutes=configuracion.minutos_expiracion_sesion),
        },
        configuracion.clave_secreta,
        algorithm=configuracion.algoritmo_firma,
    )

    respuesta = cliente.get(RUTA_SESION, headers=encabezado(token_vencido))

    assert respuesta.status_code == 401


def test_un_token_firmado_con_otra_clave_es_rechazado(cliente):
    """Un token alterado o firmado con otra clave no es aceptado."""
    cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)
    token_falso = jwt.encode(
        {
            "sub": "1",
            "rol": "administrador",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        "clave-que-no-corresponde-al-sistema",
        algorithm=configuracion.algoritmo_firma,
    )

    respuesta = cliente.get(RUTA_SESION, headers=encabezado(token_falso))

    assert respuesta.status_code == 401


def test_la_renovacion_entrega_un_token_vigente(cliente):
    """La sesion se renueva mientras el usuario permanece activo."""
    cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)
    token = cliente.post(
        RUTA_ACCESO,
        json={
            "correo": CUENTA_VALIDA["correo"],
            "contrasena": CUENTA_VALIDA["contrasena"],
        },
    ).json()["token_acceso"]

    respuesta = cliente.post(
        "/api/v1/autenticacion/renovacion", headers=encabezado(token)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["expira_en_segundos"] == (
        configuracion.minutos_expiracion_sesion * 60
    )


# --------------------------------------------------------------------------
# HU-03. Gestion de roles y permisos
# --------------------------------------------------------------------------


def test_el_usuario_deportista_no_puede_listar_las_cuentas(cliente):
    """La gestion de cuentas esta reservada al administrador."""
    cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA)
    token = cliente.post(
        RUTA_ACCESO,
        json={
            "correo": CUENTA_VALIDA["correo"],
            "contrasena": CUENTA_VALIDA["contrasena"],
        },
    ).json()["token_acceso"]

    respuesta = cliente.get(RUTA_USUARIOS, headers=encabezado(token))

    assert respuesta.status_code == 403


def test_el_administrador_asigna_el_rol_de_administrador(cliente, token_administrador):
    """El administrador puede elevar el rol de una cuenta (historia HU-03)."""
    creada = cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA).json()

    respuesta = cliente.put(
        f"{RUTA_USUARIOS}/{creada['id']}/rol",
        json={"rol": "administrador"},
        headers=encabezado(token_administrador),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "administrador"


def test_no_es_posible_dejar_al_sistema_sin_administrador(cliente, token_administrador):
    """El sistema conserva siempre al menos una cuenta administradora activa."""
    cuentas = cliente.get(RUTA_USUARIOS, headers=encabezado(token_administrador)).json()
    unico = next(cuenta for cuenta in cuentas if cuenta["rol"] == "administrador")

    respuesta = cliente.put(
        f"{RUTA_USUARIOS}/{unico['id']}/rol",
        json={"rol": "usuario"},
        headers=encabezado(token_administrador),
    )

    assert respuesta.status_code == 409


def test_una_cuenta_desactivada_no_puede_iniciar_sesion(cliente, token_administrador):
    """La desactivacion impide el acceso sin borrar el historial de la cuenta."""
    creada = cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA).json()
    cliente.put(
        f"{RUTA_USUARIOS}/{creada['id']}/estado",
        json={"activo": False},
        headers=encabezado(token_administrador),
    )

    respuesta = cliente.post(
        RUTA_ACCESO,
        json={
            "correo": CUENTA_VALIDA["correo"],
            "contrasena": CUENTA_VALIDA["contrasena"],
        },
    )

    assert respuesta.status_code == 403


def test_el_rol_del_token_no_sustituye_la_verificacion_en_el_servidor(
    cliente, token_administrador
):
    """El permiso se decide con el rol almacenado, no con el declarado en el token.

    Verifica el requerimiento no funcional 4.5.1: el acceso a cada recurso se
    valida en el servidor y no unicamente en la interfaz.
    """
    creada = cliente.post(RUTA_REGISTRO, json=CUENTA_VALIDA).json()
    token_manipulado = jwt.encode(
        {
            "sub": str(creada["id"]),
            "rol": "administrador",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        configuracion.clave_secreta,
        algorithm=configuracion.algoritmo_firma,
    )

    respuesta = cliente.get(RUTA_USUARIOS, headers=encabezado(token_manipulado))

    assert respuesta.status_code == 403
