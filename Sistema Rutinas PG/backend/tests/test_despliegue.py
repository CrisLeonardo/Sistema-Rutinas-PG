"""Pruebas de las condiciones de despliegue (apartado 3.8 y requerimiento 4.5.6).

Verifican que el sistema no arranque en produccion con credenciales de ejemplo,
que la inicializacion tolere los varios procesos de trabajo con que corre el
servicio en produccion, y que el modelo pueda recargarse sin detenerlo.
"""

import pytest

from app.nucleo import arranque
from app.nucleo.configuracion import Configuracion
from tests.conftest import encabezado

RUTA_ESTADO = "/api/v1/administracion/estado"
RUTA_RECARGA = "/api/v1/administracion/modelo/recargar"


# --------------------------------------------------------------------------
# Credenciales predeterminadas (apartado 3.8)
# --------------------------------------------------------------------------


def test_la_configuracion_de_ejemplo_se_reporta_como_pendiente():
    """El sistema reconoce sus propias credenciales de ejemplo."""
    configuracion = Configuracion(
        clave_secreta="clave-de-desarrollo-no-apta-para-produccion",
        admin_correo="admin@sistemarutinas.gt",
        admin_contrasena="Admin12345",
        _env_file=None,
    )

    pendientes = configuracion.credenciales_predeterminadas()

    assert set(pendientes) == {"CLAVE_SECRETA", "ADMIN_CORREO", "ADMIN_CONTRASENA"}


def test_una_configuracion_propia_no_reporta_pendientes():
    """Con credenciales propias, la comprobación no encuentra nada que advertir."""
    configuracion = Configuracion(
        clave_secreta="una-clave-larga-y-aleatoria-generada-para-este-despliegue",
        admin_correo="administrador@gimnasiofamas.gt",
        admin_contrasena="UnaContrasenaPropia2026",
        _env_file=None,
    )

    assert configuracion.credenciales_predeterminadas() == []


def test_en_produccion_el_arranque_se_detiene_con_credenciales_de_ejemplo(monkeypatch):
    """Un despliegue con la contraseña del repositorio no es un descuido recuperable."""
    configuracion = Configuracion(
        entorno="produccion",
        clave_secreta="clave-de-desarrollo-no-apta-para-produccion",
        admin_correo="admin@sistemarutinas.gt",
        admin_contrasena="Admin12345",
        _env_file=None,
    )
    monkeypatch.setattr(arranque, "configuracion", configuracion)

    with pytest.raises(arranque.CredencialesPredeterminadas) as error:
        arranque.verificar_credenciales()

    assert "CLAVE_SECRETA" in str(error.value)


def test_en_desarrollo_las_credenciales_de_ejemplo_solo_advierten(monkeypatch, caplog):
    """En desarrollo el sistema avisa, pero no impide trabajar."""
    configuracion = Configuracion(
        entorno="desarrollo",
        clave_secreta="clave-de-desarrollo-no-apta-para-produccion",
        admin_contrasena="Admin12345",
        _env_file=None,
    )
    monkeypatch.setattr(arranque, "configuracion", configuracion)

    with caplog.at_level("WARNING"):
        arranque.verificar_credenciales()

    assert "CLAVE_SECRETA" in caplog.text


@pytest.mark.parametrize(
    ("entorno", "esperado"),
    [("produccion", True), ("Producción", False), ("desarrollo", False), ("pruebas", False)],
)
def test_el_entorno_productivo_se_reconoce_por_su_nombre(entorno, esperado):
    """Solo el valor «produccion» activa las comprobaciones estrictas."""
    configuracion = Configuracion(entorno=entorno, _env_file=None)

    assert configuracion.es_produccion is esperado


# --------------------------------------------------------------------------
# Inicializacion con varios procesos de trabajo
# --------------------------------------------------------------------------


def test_el_esquema_se_verifica_como_completo(fabrica_sesiones, monkeypatch):
    """Tras crear el esquema no debe faltar ninguna tabla del modelo.

    Se apunta al motor del fixture y no al del sistema, que en desarrollo
    apunta a un MySQL que no tiene por qué estar levantado para correr pruebas.
    """
    monkeypatch.setattr(arranque, "motor", fabrica_sesiones.kw["bind"])

    assert arranque.tablas_faltantes() == []


def test_crear_el_esquema_dos_veces_no_falla(fabrica_sesiones):
    """Dos procesos de trabajo pueden crear el esquema a la vez sin tumbarse.

    Este fue un defecto real: con varios procesos, el que perdía la carrera
    recibía un error de tabla duplicada y mataba al servidor completo.
    """
    from app.nucleo.base_datos import Base

    motor = fabrica_sesiones.kw["bind"]
    Base.metadata.create_all(bind=motor)
    Base.metadata.create_all(bind=motor)


def test_asegurar_el_administrador_dos_veces_no_falla(cliente, fabrica_sesiones, monkeypatch):
    """El proceso que llega tarde encuentra la cuenta ya creada y continúa."""
    from app.nucleo import base_datos

    monkeypatch.setattr(base_datos, "FabricaSesiones", fabrica_sesiones)
    monkeypatch.setattr(arranque, "FabricaSesiones", fabrica_sesiones)

    arranque.asegurar_administrador()
    arranque.asegurar_administrador()

    with fabrica_sesiones() as sesion:
        from app.servicios import autenticacion

        assert autenticacion.contar_administradores(sesion, solo_activos=False) >= 1


def test_cargar_los_catalogos_dos_veces_no_duplica(fabrica_sesiones, monkeypatch):
    """La carga inicial es idempotente."""
    from app.nucleo.alimentos_iniciales import cargar_alimentos, contar_alimentos
    from app.nucleo.catalogo_inicial import cargar_ejercicios, contar_ejercicios

    with fabrica_sesiones() as sesion:
        antes_alimentos = contar_alimentos(sesion)
        antes_ejercicios = contar_ejercicios(sesion)

        assert cargar_alimentos(sesion) == 0
        assert cargar_ejercicios(sesion) == 0

        assert contar_alimentos(sesion) == antes_alimentos
        assert contar_ejercicios(sesion) == antes_ejercicios


# --------------------------------------------------------------------------
# Estado del sistema y recarga del modelo (requerimiento 4.5.6)
# --------------------------------------------------------------------------


def test_el_estado_del_sistema_esta_reservado_al_administrador(cliente, token_usuario):
    """Un usuario deportista no ve la configuración operativa."""
    assert cliente.get(RUTA_ESTADO, headers=encabezado(token_usuario)).status_code == 403


def test_la_recarga_del_modelo_esta_reservada_al_administrador(cliente, token_usuario):
    """Solo el administrador pone en operación un modelo reentrenado."""
    assert cliente.post(RUTA_RECARGA, headers=encabezado(token_usuario)).status_code == 403


def test_el_estado_reune_lo_que_el_administrador_debe_revisar(cliente, token_administrador):
    """Antes y después de desplegar hay que poder ver en qué estado quedó el sistema."""
    respuesta = cliente.get(RUTA_ESTADO, headers=encabezado(token_administrador))

    assert respuesta.status_code == 200
    estado = respuesta.json()
    assert estado["entorno"]
    assert estado["alimentos_disponibles"] > 0
    assert estado["ejercicios_disponibles"] > 0
    assert estado["modelo"]["origen_de_los_planes"] in {"red_neuronal", "formula"}
    assert isinstance(estado["credenciales_pendientes"], list)


@pytest.mark.lenta
def test_el_modelo_se_recarga_sin_detener_el_servicio(cliente, token_administrador):
    """Requerimiento 4.5.6: reentrenar no obliga a interrumpir el servicio."""
    respuesta = cliente.post(RUTA_RECARGA, headers=encabezado(token_administrador))

    # Si no hay modelo entrenado, el sistema lo dice con un 503 en lugar de
    # fingir que recargó algo.
    assert respuesta.status_code in {200, 503}

    if respuesta.status_code == 200:
        assert respuesta.json()["modelo_cargado"] is True
        # El servicio sigue atendiendo peticiones después de la recarga.
        assert cliente.get("/api/v1/estado").status_code == 200


@pytest.mark.lenta
def test_la_memoria_de_predicciones_devuelve_el_mismo_resultado():
    """La memoria de planes recientes no puede alterar lo que el modelo predice.

    Es la mitigación de la Tabla 12 para la degradación con usuarios
    concurrentes; sería inaceptable que acelerara el sistema cambiando sus
    respuestas.
    """
    from app.modelos.enumeraciones import (
        NivelActividad,
        NivelExperiencia,
        Objetivo,
        Sexo,
    )
    from app.motor.red_neuronal import ModeloNoEntrenado, MotorNeuronal

    try:
        motor = MotorNeuronal.cargar()
    except ModeloNoEntrenado:
        pytest.skip("El modelo no está entrenado en este entorno.")

    argumentos = (
        80.0,
        175.0,
        30,
        Sexo.MASCULINO,
        NivelActividad.MODERADO,
        Objetivo.MANTENIMIENTO,
        NivelExperiencia.INTERMEDIO,
        4,
    )

    motor.vaciar_memoria()
    primera = motor.predecir(*argumentos)
    segunda = motor.predecir(*argumentos)

    assert primera == segunda
    assert motor.aciertos_de_memoria == 1
    assert motor.tasa_de_aciertos == 0.5


@pytest.mark.lenta
def test_vaciar_la_memoria_obliga_a_predecir_de_nuevo():
    """Al recargar el modelo, las predicciones anteriores dejan de valer."""
    from app.modelos.enumeraciones import (
        NivelActividad,
        NivelExperiencia,
        Objetivo,
        Sexo,
    )
    from app.motor.red_neuronal import ModeloNoEntrenado, MotorNeuronal

    try:
        motor = MotorNeuronal.cargar()
    except ModeloNoEntrenado:
        pytest.skip("El modelo no está entrenado en este entorno.")

    argumentos = (
        72.0,
        168.0,
        35,
        Sexo.FEMENINO,
        NivelActividad.LIGERO,
        Objetivo.PERDIDA_GRASA,
        NivelExperiencia.PRINCIPIANTE,
        3,
    )

    motor.predecir(*argumentos)
    motor.vaciar_memoria()

    assert motor.consultas == 0
    assert motor.aciertos_de_memoria == 0
