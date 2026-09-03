"""Configuracion central del sistema, cargada desde variables de entorno."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_BACKEND = Path(__file__).resolve().parents[2]


class Configuracion(BaseSettings):
    """Parametros de ejecucion del sistema.

    Los valores se leen del archivo .env ubicado en la raiz del backend; los que
    se declaran aqui funcionan como respaldo para el entorno de desarrollo.
    """

    model_config = SettingsConfigDict(
        env_file=RAIZ_BACKEND / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    nombre_sistema: str = "Sistema de rutinas y planes nutricionales"
    version: str = "0.1.0"

    # Entorno de ejecucion. En produccion el sistema rechaza arrancar con las
    # credenciales predeterminadas, que es el ultimo punto del apartado 3.8.
    entorno: str = "desarrollo"

    url_base_datos: str = (
        "mysql+pymysql://rutinas:rutinas_pass@localhost:3307/sistema_rutinas"
    )

    clave_secreta: str = "clave-de-desarrollo-no-apta-para-produccion"
    algoritmo_firma: str = "HS256"
    minutos_expiracion_sesion: int = 30

    origenes_permitidos: str = "http://localhost:5173,http://127.0.0.1:5173"

    admin_correo: str = "admin@sistemarutinas.gt"
    admin_contrasena: str = "Admin12345"
    admin_nombre: str = "Administrador del sistema"

    @property
    def lista_origenes(self) -> list[str]:
        """Convierte la cadena de origenes en la lista que espera el middleware."""
        return [origen.strip() for origen in self.origenes_permitidos.split(",") if origen.strip()]

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
# produccion.
_CLAVES_DE_EJEMPLO = {
    "clave-de-desarrollo-no-apta-para-produccion",
    "cambie-esta-clave-antes-de-desplegar",
    "",
}
_CONTRASENAS_DE_EJEMPLO = {"Admin12345", "admin", "cambieme", ""}


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve una unica instancia de la configuracion para toda la aplicacion."""
    return Configuracion()


configuracion = obtener_configuracion()
