"""Tareas de inicializacion que se ejecutan al levantar el servicio."""

import logging

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

from app.esquemas.usuario import RegistroUsuario
from app.modelos.enumeraciones import RolUsuario
from app.nucleo.base_datos import Base, FabricaSesiones, motor
from app.nucleo.configuracion import configuracion
from app.servicios import autenticacion

# Importar el paquete de modelos registra todas las entidades en los metadatos
# de SQLAlchemy antes de crear el esquema.
import app.modelos  # noqa: F401  isort:skip

bitacora = logging.getLogger(__name__)


def tablas_faltantes() -> list[str]:
    """Enumera las tablas del modelo que todavia no existen en la base de datos."""
    existentes = set(inspect(motor).get_table_names())
    return sorted(set(Base.metadata.tables) - existentes)


def crear_esquema() -> None:
    """Crea las tablas que aun no existan en la base de datos.

    En produccion el servicio corre con varios procesos de trabajo que arrancan
    a la vez. `create_all` consulta primero que la tabla no exista y despues la
    crea, y entre esas dos operaciones cabe otro proceso: el que llega tarde
    recibe un error de tabla duplicada.

    Ese error no describe una falla del sistema sino una carrera con final
    correcto, de modo que se comprueba el esquema y, si quedo completo, el
    arranque continua. Si de verdad faltan tablas, el error se propaga.
    """
    try:
        Base.metadata.create_all(bind=motor)
    except (OperationalError, ProgrammingError):
        faltantes = tablas_faltantes()
        if faltantes:
            bitacora.error("El esquema quedó incompleto. Faltan las tablas: %s", faltantes)
            raise
        bitacora.info("Otro proceso de trabajo creó el esquema de la base de datos.")

    bitacora.info("Esquema de base de datos verificado.")


def asegurar_administrador() -> None:
    """Crea la cuenta de administrador inicial si el sistema no tiene ninguna.

    Sin esta cuenta no seria posible ejercer la historia HU-03, ya que el
    registro publico solo produce cuentas con rol de usuario deportista.

    En produccion el servicio corre con varios procesos de trabajo, y todos
    ejecutan esta funcion al arrancar. Los que pierden la carrera encuentran la
    cuenta ya creada: eso no es un error, es el resultado esperado, y por eso la
    excepcion se registra y se continúa en lugar de propagarse. Si se propagara,
    el proceso moriria y arrastraria consigo al servidor completo.
    """
    with FabricaSesiones() as sesion:
        if autenticacion.contar_administradores(sesion, solo_activos=False) > 0:
            return

        existente = autenticacion.buscar_por_correo(sesion, configuracion.admin_correo)
        if existente is not None:
            autenticacion.cambiar_rol(sesion, existente, RolUsuario.ADMINISTRADOR)
            bitacora.info("Se elevo a administrador la cuenta %s.", existente.correo)
            return

        try:
            autenticacion.registrar_usuario(
                sesion,
                RegistroUsuario(
                    correo=configuracion.admin_correo,
                    nombre=configuracion.admin_nombre,
                    contrasena=configuracion.admin_contrasena,
                ),
                rol=RolUsuario.ADMINISTRADOR,
            )
        except autenticacion.CorreoYaRegistrado:
            bitacora.info(
                "Otro proceso de trabajo creo la cuenta de administrador %s.",
                configuracion.admin_correo,
            )
            return

        bitacora.warning(
            "Se creo la cuenta de administrador inicial %s. "
            "Cambie su contrasena antes de desplegar en produccion.",
            configuracion.admin_correo,
        )


def asegurar_catalogos_iniciales() -> None:
    """Carga los catalogos iniciales si el sistema no tiene ninguno.

    Sin ejercicios registrados, la historia HU-07 no tendria de donde elegir y
    los planes se guardarian sin rutina. La carga es idempotente y no deshace las
    altas ni las bajas que haga el administrador.
    """
    from app.nucleo.alimentos_iniciales import cargar_alimentos, contar_alimentos
    from app.nucleo.catalogo_inicial import cargar_ejercicios, contar_ejercicios

    with FabricaSesiones() as sesion:
        # Igual que la cuenta de administrador, la carga puede ejecutarse a la
        # vez desde varios procesos de trabajo. El que llega tarde choca con la
        # restriccion de unicidad del nombre; eso significa que el catalogo ya
        # esta cargado, no que el arranque haya fallado.
        if contar_ejercicios(sesion) == 0:
            try:
                agregados = cargar_ejercicios(sesion)
            except IntegrityError:
                sesion.rollback()
                bitacora.info("Otro proceso de trabajo cargo el catalogo de ejercicios.")
            else:
                bitacora.info(
                    "Se cargaron %s ejercicios iniciales en el catálogo. "
                    "Verifíquelos contra el equipamiento del Gimnasio FAMAS (historia HU-11).",
                    agregados,
                )

        if contar_alimentos(sesion) == 0:
            try:
                agregados = cargar_alimentos(sesion)
            except IntegrityError:
                sesion.rollback()
                bitacora.info("Otro proceso de trabajo cargo el catalogo de alimentos.")
            else:
                bitacora.info(
                    "Se cargaron %s alimentos iniciales en el catálogo. "
                    "Verifíquelos mediante visita a los mercados del municipio (historia HU-11).",
                    agregados,
                )


def precargar_modelo_neuronal() -> None:
    """Carga el modelo entrenado antes de atender la primera peticion.

    Sin esta precarga, el primer usuario en pedir su plan pagaria el costo de
    importar TensorFlow y leer el modelo del disco —varios segundos— y el sistema
    incumpliria el criterio de aceptacion de la historia HU-06, que exige generar
    el plan en menos de tres segundos.

    Si el modelo aun no se ha entrenado, el arranque continua: los planes se
    calcularan con las formulas de referencia hasta que se ejecute
    `uv run python entrenar_modelo.py`.
    """
    from app.servicios.plan import obtener_motor

    if obtener_motor() is None:
        bitacora.warning(
            "El sistema arrancó sin modelo neuronal entrenado. "
            "Ejecute: uv run python entrenar_modelo.py"
        )


class CredencialesPredeterminadas(Exception):
    """El sistema no puede arrancar en produccion con credenciales de ejemplo."""


def verificar_credenciales() -> None:
    """Impide arrancar en produccion con las credenciales de los ejemplos.

    Es el ultimo punto del apartado 3.8 —cambiar todas las credenciales
    predeterminadas— convertido en una comprobacion que el sistema hace por su
    cuenta. En desarrollo solo advierte; en produccion detiene el arranque,
    porque un despliegue con la contrasena del repositorio no es un descuido
    recuperable: cualquiera que lea el codigo entra como administrador.
    """
    pendientes = configuracion.credenciales_predeterminadas()
    if not pendientes:
        return

    listado = ", ".join(pendientes)
    if configuracion.es_produccion:
        raise CredencialesPredeterminadas(
            f"No se puede arrancar en producción con credenciales de ejemplo: {listado}. "
            "Genere valores propios antes de desplegar."
        )

    bitacora.warning(
        "Estas credenciales conservan su valor de ejemplo: %s. "
        "Cámbielas antes de desplegar en producción.",
        listado,
    )


def inicializar() -> None:
    """Ejecuta en orden todas las tareas de arranque."""
    verificar_credenciales()
    crear_esquema()
    asegurar_administrador()
    asegurar_catalogos_iniciales()
    precargar_modelo_neuronal()
