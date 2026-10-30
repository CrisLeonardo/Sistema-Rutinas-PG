"""Contratos de salida de los informes (apartado 6.4)."""

from datetime import date, datetime

from pydantic import BaseModel

from app.servicios.informes import Ambito, TipoDato


class InformeDisponible(BaseModel):
    """Entrada del catálogo de informes que la cuenta puede consultar."""

    clave: str
    titulo: str
    descripcion: str
    ambito: Ambito
    formatos: list[str]


class ColumnaPublica(BaseModel):
    """Columna del informe, con el tipo que decide su alineación y su formato."""

    clave: str
    titulo: str
    tipo: TipoDato
    decimales: int


class IndicadorPublico(BaseModel):
    """Cifra del resumen, redactada tal como se lee."""

    rotulo: str
    valor: str


class InformePublico(BaseModel):
    """Informe completo, para presentarlo en pantalla.

    Es el mismo contenido que se exporta a CSV, Excel y PDF: la pantalla y los
    archivos no pueden mostrar cifras distintas.
    """

    clave: str
    titulo: str
    descripcion: str
    titular: str
    generado: datetime
    columnas: list[ColumnaPublica]
    filas: list[dict[str, str | int | float | date | None]]
    resumen: list[IndicadorPublico]
    nota: str | None
