"""Fecha y hora locales del sistema.

Las marcas de tiempo se guardan en UTC sin zona, tanto las que pone el gestor
con `func.now()` como las que asigna el servidor. Eso es correcto para guardar,
pero no para decidir qué día es: el servicio publicado corre en UTC, y en
Guatemala las seis de la tarde ya son la medianoche del día siguiente. Sin esta
conversión, una sesión registrada un lunes por la noche quedaba con fecha de
martes y la insignia «Antes del sol» se otorgaba a quien entrenaba de noche.

Guatemala usa UTC−6 todo el año —no aplica horario de verano desde 2006—, de
modo que un desplazamiento fijo basta y no depende de que la imagen del
contenedor traiga la base de datos de zonas horarias.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from pydantic import PlainSerializer

ZONA_LOCAL = timezone(timedelta(hours=-6), "America/Guatemala")


def ahora_local() -> datetime:
    """Fecha y hora actuales en Guatemala, con zona."""
    return datetime.now(ZONA_LOCAL)


def hoy_local() -> date:
    """El día de hoy en Guatemala, con independencia de la zona del servidor."""
    return ahora_local().date()


def a_hora_local(valor: datetime) -> datetime:
    """Convierte una marca guardada en UTC —con zona o sin ella— a la hora local."""
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(ZONA_LOCAL)


def _como_utc(valor: datetime) -> str:
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.isoformat()


# Marca de tiempo guardada en UTC sin zona. Se publica con la zona explícita
# («+00:00») para que el navegador la convierta a la hora local; publicada sin
# zona, el navegador la leía como hora local y mostraba seis horas de más.
MarcaUTC = Annotated[datetime, PlainSerializer(_como_utc, return_type=str, when_used="json")]
