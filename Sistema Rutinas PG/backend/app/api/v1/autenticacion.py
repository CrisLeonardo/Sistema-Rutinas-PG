"""Controlador de registro y sesion (historias HU-01 y HU-02)."""

import hashlib

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from sqlalchemy.orm import sessionmaker

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.usuario import (
    CambioContrasena,
    CredencialesAcceso,
    RegistroUsuario,
    TokenSesion,
    UsuarioPublico,
    SolicitudRecuperacion,
    RestablecimientoContrasena,
)
from app.nucleo.limitador import limitador_de_acceso, limitador_de_registro, LimitadorDeIntentos
from app.nucleo.configuracion import configuracion
from app.nucleo.seguridad import crear_token_sesion
from app.servicios import autenticacion
from app.servicios import recuperacion

enrutador = APIRouter(prefix="/autenticacion", tags=["Acceso seguro"])

_MENSAJE_CREDENCIALES = "El correo o la contraseña son incorrectos."
limitador_recuperacion = LimitadorDeIntentos(intentos_maximos=5, bloqueo_segundos=900)
limitador_restablecimiento = LimitadorDeIntentos(intentos_maximos=8, bloqueo_segundos=900)


def _direccion(peticion: Request) -> str:
    """Direccion de origen de la peticion, tal como la reporta el proxy.

    En produccion la peticion llega por el reenvio de Render y por nginx en el
    entorno de pruebas, de modo que la direccion del cliente viaja en el
    encabezado que ambos anaden y no en la conexion, que siempre seria la del
    proxy. Se toma la primera de la cadena, que es la del cliente original.
    """
    reenviada = peticion.headers.get("x-forwarded-for")
    if reenviada:
        return reenviada.split(",")[0].strip()
    return peticion.client.host if peticion.client else "desconocido"


def _rechazar_por_intentos(segundos: int) -> HTTPException:
    minutos = max(round(segundos / 60), 1)
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=(
            f"Demasiados intentos fallidos. Espere {minutos} "
            f"{'minuto' if minutos == 1 else 'minutos'} antes de volver a intentarlo."
        ),
        headers={"Retry-After": str(segundos)},
    )


@enrutador.post(
    "/registro",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una cuenta nueva",
)
def registrar(
    datos: RegistroUsuario, sesion: SesionBD, peticion: Request
) -> UsuarioPublico:
    """Da de alta una cuenta con rol de usuario deportista (historia HU-01)."""
    origen = _direccion(peticion)
    veredicto = limitador_de_registro.revisar(origen)
    if not veredicto.permitido:
        raise _rechazar_por_intentos(veredicto.segundos_de_espera)

    try:
        usuario = autenticacion.registrar_usuario(sesion, datos)
    except autenticacion.CorreoYaRegistrado:
        # Se cuenta como intento fallido: enumerar correos registrados a base de
        # peticiones de alta seria la otra forma de averiguar quien tiene cuenta.
        limitador_de_registro.registrar_fallo(origen)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta registrada con ese correo.",
        ) from None
    return UsuarioPublico.model_validate(usuario)


@enrutador.post(
    "/acceso",
    response_model=TokenSesion,
    summary="Iniciar sesion",
)
def iniciar_sesion(
    credenciales: CredencialesAcceso, sesion: SesionBD, peticion: Request
) -> TokenSesion:
    """Valida las credenciales y emite el token de sesion (historia HU-02).

    Los intentos fallidos se cuentan por cuenta y por dirección de origen a la
    vez: contar solo por cuenta permitiría a cualquiera dejar fuera al titular
    de un correo conocido, y contar solo por origen dejaría pasar un ataque
    repartido entre muchas direcciones.
    """
    origen = _direccion(peticion)
    cuenta = credenciales.correo.strip().lower()
    llaves = (f"origen:{origen}", f"cuenta:{cuenta}")

    for llave in llaves:
        veredicto = limitador_de_acceso.revisar(llave)
        if not veredicto.permitido:
            raise _rechazar_por_intentos(veredicto.segundos_de_espera)

    try:
        usuario = autenticacion.autenticar_usuario(
            sesion, credenciales.correo, credenciales.contrasena
        )
    except autenticacion.CredencialesInvalidas:
        espera = 0
        for llave in llaves:
            resultado = limitador_de_acceso.registrar_fallo(llave)
            espera = max(espera, resultado.segundos_de_espera)
        if espera:
            raise _rechazar_por_intentos(espera) from None
        # Mensaje unico para correo inexistente y contrasena incorrecta.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_MENSAJE_CREDENCIALES,
        ) from None
    except autenticacion.CuentaDesactivada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta se encuentra desactivada. Comuníquese con el administrador.",
        ) from None

    for llave in llaves:
        limitador_de_acceso.registrar_exito(llave)

    token, vigencia = crear_token_sesion(usuario.id, usuario.rol.value, usuario.version_sesion)
    return TokenSesion(
        token_acceso=token,
        expira_en_segundos=vigencia,
        usuario=UsuarioPublico.model_validate(usuario),
    )


@enrutador.post(
    "/renovacion",
    response_model=TokenSesion,
    summary="Renovar la sesion activa",
)
def renovar_sesion(usuario: UsuarioAutenticado) -> TokenSesion:
    """Emite un token nuevo mientras el usuario permanezca activo.

    Es el mecanismo que convierte la vigencia fija del token en la expiracion
    por inactividad que exige el criterio de aceptacion de la historia HU-02.
    """
    token, vigencia = crear_token_sesion(usuario.id, usuario.rol.value, usuario.version_sesion)
    return TokenSesion(
        token_acceso=token,
        expira_en_segundos=vigencia,
        usuario=UsuarioPublico.model_validate(usuario),
    )


@enrutador.get(
    "/sesion",
    response_model=UsuarioPublico,
    summary="Consultar la cuenta de la sesion actual",
)
def consultar_sesion(usuario: UsuarioAutenticado) -> UsuarioPublico:
    """Devuelve los datos de la cuenta autenticada."""
    return UsuarioPublico.model_validate(usuario)


@enrutador.post(
    "/cambio-de-contrasena",
    response_model=TokenSesion,
    summary="Cambiar la contrasena de la cuenta",
)
def cambiar_contrasena(
    datos: CambioContrasena, sesion: SesionBD, usuario: UsuarioAutenticado
) -> TokenSesion:
    """Sustituye la contrasena de la cuenta en sesion.

    Se exige la contrasena vigente aunque la sesion ya este autenticada: sin esa
    comprobacion, un teléfono desbloqueado y desatendido bastaria para quedarse
    con la cuenta de forma permanente.

    Revoca las sesiones anteriores y devuelve un token de la nueva versión.
    """
    if not autenticacion.contrasena_coincide(usuario, datos.contrasena_actual):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual no es correcta.",
        )

    if datos.contrasena_actual == datos.contrasena_nueva:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña nueva debe ser distinta de la actual.",
        )

    try:
        autenticacion.cambiar_contrasena(sesion, usuario, datos.contrasena_nueva)
    except autenticacion.CredencialesInvalidas:
        raise HTTPException(409, "Las credenciales cambiaron. Inicia sesión nuevamente.") from None

    token, vigencia = crear_token_sesion(usuario.id, usuario.rol.value, usuario.version_sesion)
    return TokenSesion(
        token_acceso=token,
        expira_en_segundos=vigencia,
        usuario=UsuarioPublico.model_validate(usuario),
    )


@enrutador.get("/opciones-publicas")
def opciones_publicas() -> dict:
    return {
        "recuperacion_habilitada": configuracion.recuperacion_habilitada,
        "correo_contacto": str(configuracion.correo_contacto) if configuracion.correo_contacto else None,
    }


@enrutador.post("/recuperacion", status_code=202)
def solicitar_recuperacion(datos: SolicitudRecuperacion, sesion: SesionBD, peticion: Request, tareas: BackgroundTasks) -> dict:
    if not configuracion.recuperacion_habilitada:
        raise HTTPException(503, "La recuperación por correo no está disponible por el momento.")
    correo = str(datos.correo).strip().lower()
    cuenta = hashlib.sha256(correo.encode()).hexdigest()
    for llave in (f"origen:{_direccion(peticion)}", f"cuenta:{cuenta}"):
        veredicto = limitador_recuperacion.registrar_fallo(llave)
        if not veredicto.permitido:
            raise _rechazar_por_intentos(veredicto.segundos_de_espera)
    fabrica = sessionmaker(bind=sesion.get_bind(), expire_on_commit=False)
    tareas.add_task(recuperacion.procesar_solicitud, correo, fabrica)
    return {"mensaje": "Si el correo corresponde a una cuenta activa, recibirás un enlace para recuperar el acceso. Revisa también la carpeta de correo no deseado."}


@enrutador.post("/restablecimiento")
def restablecer_acceso(datos: RestablecimientoContrasena, sesion: SesionBD, peticion: Request) -> dict:
    veredicto = limitador_restablecimiento.registrar_fallo(_direccion(peticion))
    if not veredicto.permitido:
        raise _rechazar_por_intentos(veredicto.segundos_de_espera)
    try:
        recuperacion.restablecer(sesion, datos.token, datos.contrasena_nueva)
    except recuperacion.EnlaceNoValido:
        raise HTTPException(400, "El enlace no es válido o ya venció. Solicita uno nuevo.") from None
    return {"mensaje": "Contraseña actualizada. Inicia sesión con tu nueva contraseña."}
