"""Configuracion central del sistema, cargada desde variables de entorno."""

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import EmailStr, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_BACKEND = Path(__file__).resolve().parents[2]

# Equivalencias de los prefijos con que los proveedores administrados entregan
# la cadena de conexion. Supabase la publica como «postgresql://» y algunos
# paneles todavia usan el prefijo historico «postgres://»; SQLAlchemy necesita
# que el controlador venga declarado, porque de lo contrario intenta cargar
# psycopg2, que no esta instalado.
_CONTROLADOR_POSTGRESQL = "postgresql+psycopg"
_PREFIJOS_SIN_CONTROLADOR = ("postgres", "postgresql")

# Anfitriones locales, donde la base de datos no sale a la red y exigir cifrado
# solo estorbaria al entorno de desarrollo.
_ANFITRIONES_LOCALES = {"localhost", "127.0.0.1", "::1", "base_datos"}


def normalizar_url_base_datos(url: str) -> str:
    """Adapta la cadena de conexion que entrega el proveedor administrado.

    Hace dos ajustes, ambos necesarios para que el sistema conecte con Supabase
    sin obligar a quien despliega a recordar la sintaxis de SQLAlchemy:

    1. Declara el controlador. Supabase entrega «postgresql://...», que
       SQLAlchemy interpreta como una peticion de psycopg2.
    2. Exige el cifrado del transito cuando la base de datos es remota. El
       requerimiento 4.5.1 pide proteger los datos en transito, y entre el
       servicio y la base viajan las medidas biometricas de los usuarios. Si
       la cadena ya trae su propio «sslmode», se respeta.
    """
    url = url.strip()
    if not url:
        return url

    partes = urlsplit(url)
    esquema = partes.scheme
    if esquema.split("+")[0] not in _PREFIJOS_SIN_CONTROLADOR:
        # SQLite conserva tres barras y, en Windows, la letra de unidad.
        return url
    if esquema in _PREFIJOS_SIN_CONTROLADOR:
        esquema = _CONTROLADOR_POSTGRESQL

    consulta = dict(parse_qsl(partes.query, keep_blank_values=True))
    es_postgresql = esquema.split("+")[0] in _PREFIJOS_SIN_CONTROLADOR
    if es_postgresql and "sslmode" not in consulta and partes.hostname not in _ANFITRIONES_LOCALES:
        consulta["sslmode"] = "require"

    return urlunsplit(
        (esquema, partes.netloc, partes.path, urlencode(consulta), partes.fragment)
    )


class Configuracion(BaseSettings):
    """Parametros de ejecucion del sistema.

    Los valores se leen del archivo .env ubicado en la raiz del backend; los que
    se declaran aqui funcionan como respaldo para el entorno de desarrollo.
    """

    model_config = SettingsConfigDict(
        env_file=(RAIZ_BACKEND / ".env", RAIZ_BACKEND / ".env.gmail"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    nombre_sistema: str = "Sistema de rutinas y planes nutricionales"
    version: str = "0.1.0"

    # Entorno de ejecucion. En produccion el sistema rechaza arrancar con las
    # credenciales predeterminadas, que es el ultimo punto del apartado 3.8.
    entorno: str = "desarrollo"

    url_base_datos: str = (
        "postgresql+psycopg://rutinas:rutinas_pass@localhost:5433/sistema_rutinas"
    )

    # Procesos de trabajo del servidor. En produccion cada uno carga su propia
    # copia de TensorFlow, que ocupa cerca de 190 MB, de modo que el numero no
    # se elige por gusto sino por la memoria de la instancia contratada.
    procesos_de_trabajo: int = 1

    # Ampliación social pospuesta por el autor; Mi senda individual sigue activa.
    comunidad_habilitada: bool = False
    # Coincide con las cinco conexiones persistentes del pool; evita rotar
    # conexiones de desbordamiento durante una ráfaga. El máximo total es diez.
    solicitudes_activas_bd: int = Field(default=5, ge=1, le=10)

    clave_secreta: str = "clave-de-desarrollo-no-apta-para-produccion"
    algoritmo_firma: str = "HS256"
    minutos_expiracion_sesion: int = 30

    origenes_permitidos: str = "http://localhost:5173,http://127.0.0.1:5173"

    admin_correo: str = "admin@sistemarutinas.gt"
    admin_contrasena: str = "Admin12345"
    admin_nombre: str = "Administrador del sistema"

    # Se configura fuera del código. Nunca se deriva un enlace del encabezado Host.
    url_publica_frontend: str = "http://127.0.0.1:5173"
    correo_contacto: EmailStr | None = "senda1986.gt@gmail.com"
    correo_transporte: Literal["gmail_api", "smtp"] = "gmail_api"
    correo_remitente: EmailStr = "senda1986.gt@gmail.com"
    gmail_cliente_id: str = ""
    gmail_cliente_secreto: SecretStr | None = None
    gmail_refresh_token: SecretStr | None = None
    smtp_servidor: str = ""
    smtp_puerto: int = Field(default=587, ge=1, le=65535)
    smtp_seguridad: Literal["starttls", "ssl", "ninguna"] = "starttls"
    smtp_usuario: str = ""
    smtp_contrasena: SecretStr | None = None
    smtp_remitente: EmailStr | None = None

    @field_validator("url_publica_frontend")
    @classmethod
    def validar_url_publica(cls, valor: str) -> str:
        partes = urlsplit(valor)
        if (partes.scheme not in {"http", "https"} or not partes.hostname
                or partes.username or partes.password or partes.query or partes.fragment
                or partes.path not in {"", "/"}):
            raise ValueError("URL_PUBLICA_FRONTEND debe ser un origen HTTP(S) sin ruta ni credenciales.")
        return valor.rstrip("/")

    @property
    def recuperacion_habilitada(self) -> bool:
        if self.es_produccion and not self.url_publica_frontend.startswith("https://"):
            return False
        if self.correo_transporte == "gmail_api":
            return bool(self.gmail_cliente_id and self.gmail_cliente_secreto
                        and self.gmail_cliente_secreto.get_secret_value()
                        and self.gmail_refresh_token and self.gmail_refresh_token.get_secret_value())
        secreto = self.smtp_contrasena.get_secret_value() if self.smtp_contrasena else ""
        credenciales = bool(secreto) if self.smtp_usuario else self.smtp_servidor.lower() != "smtp.gmail.com"
        cifrado = self.smtp_seguridad != "ninguna" or (
            not self.es_produccion and self.smtp_servidor in {"localhost", "127.0.0.1", "::1"}
        )
        return bool(self.smtp_servidor and self.smtp_remitente and credenciales and cifrado
                    and (not self.es_produccion or self.url_publica_frontend.startswith("https://")))

    @field_validator("url_base_datos")
    @classmethod
    def _normalizar_url(cls, valor: str) -> str:
        """Acepta la cadena tal como la entrega el proveedor administrado."""
        return normalizar_url_base_datos(valor)

    @property
    def lista_origenes(self) -> list[str]:
        """Convierte la cadena de origenes en la lista que espera el middleware.

        Se completa el protocolo cuando falta. Render entrega la direccion de
        un servicio como nombre de anfitrion a secas, sin protocolo, y el
        control de origenes cruzados compara la cadena completa: sin este
        arreglo, un origen legitimo escrito como «sistema.onrender.com» seria
        rechazado sin que nada explicara por que.
        """
        origenes = []
        for origen in self.origenes_permitidos.split(","):
            origen = origen.strip()
            if not origen:
                continue
            if "://" not in origen:
                origen = f"https://{origen}"
            origenes.append(origen)
        return origenes

    @property
    def es_produccion(self) -> bool:
        """Indica si el sistema se ejecuta en el entorno productivo."""
        return self.entorno.strip().lower() == "produccion"

    def credenciales_predeterminadas(self) -> list[str]:
        """Enumera las credenciales que siguen con su valor de ejemplo.

        El apartado 3.8 exige cambiar todas antes del despliegue. Dejarlas
        equivaldria a publicar el sistema con la contrasena del administrador
        escrita en el repositorio.
        """
        pendientes = []
        if self.clave_secreta in _CLAVES_DE_EJEMPLO:
            pendientes.append("CLAVE_SECRETA")
        if self.admin_contrasena in _CONTRASENAS_DE_EJEMPLO:
            pendientes.append("ADMIN_CONTRASENA")
        if self.admin_correo == "admin@sistemarutinas.gt":
            pendientes.append("ADMIN_CORREO")
        return pendientes


# Valores que traen los archivos de ejemplo y que jamas deben llegar a
# produccion. Deben coincidir exactamente con backend/.env.example y con
# .env.pruebas.example: la comprobacion compara cadenas literales, y una
# discrepancia con lo que esos archivos traen deja pasar la credencial de
# ejemplo sin que nada avise.
_CLAVES_DE_EJEMPLO = {
    "clave-de-desarrollo-no-apta-para-produccion",
    "cambie-esta-clave-antes-de-desplegar",
    "cambie-esta-clave-antes-de-desplegar-en-produccion",
    "CAMBIE-esta-clave-antes-de-desplegar",
    "",
}
_CONTRASENAS_DE_EJEMPLO = {
    "Admin12345",
    "admin",
    "cambieme",
    "CAMBIE-esta-contrasena-de-administrador",
    "",
}


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve una unica instancia de la configuracion para toda la aplicacion."""
    return Configuracion()


configuracion = obtener_configuracion()
