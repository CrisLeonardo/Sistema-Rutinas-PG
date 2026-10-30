"""Exportación de los informes a CSV, Excel y PDF (apartado 6.4).

Los tres formatos parten del mismo `Informe`, y cada uno sirve a un propósito
distinto:

- **CSV** es para llevar los datos a otro programa. Se entrega sin adornos: una
  fila de encabezados y una por registro, con las fechas en formato ISO y el
  punto como separador decimal, que es lo que cualquier programa sabe leer.
- **Excel** es para seguir trabajando con los datos. Las cifras se guardan
  como números y las fechas como fechas, no como texto, para que el usuario
  pueda sumarlas, graficarlas u ordenarlas sin convertir nada.
- **PDF** es para entregar o archivar. Repite los encabezados en cada página,
  numera las páginas y lleva al pie el aviso que corresponda al informe.

Las bibliotecas de Excel y PDF se importan dentro de su función: el servicio
corre en una instancia de 512 MB y casi ninguna petición pide un archivo.
"""

import csv
import io
from datetime import date, datetime

from app.nucleo.configuracion import configuracion
from app.servicios.informes import Columna, Informe, TipoDato

TIPOS_DE_CONTENIDO = {
    "csv": "text/csv; charset=utf-8",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
}

FORMATOS = tuple(TIPOS_DE_CONTENIDO)

# Verde de la marca, en su versión para papel (la misma que usa la hoja de
# estilos de impresión de la interfaz).
_VERDE = (20, 83, 45)
_VERDE_HEX = "14532D"
_FONDO_ALTERNO = (241, 245, 242)


def nombre_de_archivo(informe: Informe, formato: str) -> str:
    """Nombre sugerido para la descarga: informe-evolucion-2026-10-12.pdf."""
    return f"informe-{informe.clave}-{informe.generado:%Y-%m-%d}.{formato}"


def exportar(informe: Informe, formato: str) -> bytes:
    """Entrega el informe en el formato indicado."""
    if formato == "csv":
        return a_csv(informe)
    if formato == "xlsx":
        return a_excel(informe)
    if formato == "pdf":
        return a_pdf(informe)
    raise ValueError(f"Formato no admitido: {formato}")


# --------------------------------------------------------------------------
# Texto de cada celda
# --------------------------------------------------------------------------


def texto_de_celda(valor, columna: Columna) -> str:
    """Cifra o fecha redactada para leerse: 2,180 · 85.4 · 90 % · Q12.50 · 04/09/2026."""
    if valor is None or valor == "":
        return "—"
    if columna.tipo == TipoDato.FECHA and isinstance(valor, date | datetime):
        return valor.strftime("%d/%m/%Y")
    if columna.tipo == TipoDato.ENTERO:
        return f"{round(valor):,}"
    if columna.tipo == TipoDato.DECIMAL:
        return f"{valor:,.{columna.decimales}f}"
    if columna.tipo == TipoDato.PORCENTAJE:
        return f"{round(valor)} %"
    if columna.tipo == TipoDato.MONEDA:
        return f"Q{valor:,.2f}"
    return str(valor)


# Con estos caracteres al inicio, una hoja de cálculo interpreta el texto como
# una fórmula y la ejecuta al abrir el archivo. Un informe puede traer texto que
# otra persona escribió —el nombre con que se registró una cuenta, por ejemplo—,
# de modo que quien abre el informe de cuentas ejecutaría lo que un desconocido
# haya puesto ahí. La lista es la de OWASP para la inyección de fórmulas.
_INICIOS_DE_FORMULA = ("=", "+", "-", "@", "\t", "\r")


# --------------------------------------------------------------------------
# CSV
# --------------------------------------------------------------------------


def a_csv(informe: Informe) -> bytes:
    """Valores separados por comas, en UTF-8 con marca de orden de bytes.

    La marca no es un adorno: sin ella, Excel abre el archivo en la codificación
    regional de Windows y convierte «Proteína» en «ProteÃ­na».
    """
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\r\n")
    escritor.writerow([columna.titulo for columna in informe.columnas])
    for fila in informe.filas:
        escritor.writerow(
            [_valor_crudo(fila.get(columna.clave)) for columna in informe.columnas]
        )
    return salida.getvalue().encode("utf-8-sig")


def _valor_crudo(valor) -> str:
    if valor is None:
        return ""
    if isinstance(valor, date | datetime):
        return valor.isoformat()
    texto = str(valor)
    # Un CSV no distingue texto de número: el programa que lo abre decide por el
    # primer carácter. Solo se neutraliza el texto; una cifra negativa, como
    # −0.8, no es una fórmula y debe seguir siendo un número.
    if isinstance(valor, str) and texto.startswith(_INICIOS_DE_FORMULA):
        return "'" + texto
    return texto


# --------------------------------------------------------------------------
# Excel
# --------------------------------------------------------------------------

_FORMATOS_EXCEL = {
    TipoDato.ENTERO: "#,##0",
    TipoDato.PORCENTAJE: '0" %"',
    TipoDato.MONEDA: '"Q"#,##0.00',
    TipoDato.FECHA: "dd/mm/yyyy",
}


def _formato_excel(columna: Columna) -> str | None:
    if columna.tipo == TipoDato.DECIMAL:
        return "#,##0" if columna.decimales == 0 else "#,##0." + "0" * columna.decimales
    return _FORMATOS_EXCEL.get(columna.tipo)


def _fijar_textos_como_texto(libro) -> None:
    """Impide que una celda de texto que parece fórmula se ejecute.

    openpyxl guarda como fórmula toda cadena que empieza con «=». Aquí se la
    fuerza a texto y se le pone el prefijo de comilla de Excel, que además la
    protege si alguien edita la celda después. A diferencia de anteponer una
    comilla al valor, el texto se conserva intacto: «+1.2 kg» del resumen sigue
    leyéndose «+1.2 kg».
    """
    for hoja in libro.worksheets:
        for fila in hoja.iter_rows():
            for celda in fila:
                if isinstance(celda.value, str) and celda.value.startswith(_INICIOS_DE_FORMULA):
                    celda.data_type = "s"
                    celda.quotePrefix = True


def a_excel(informe: Informe) -> bytes:
    """Libro con dos hojas: los datos del informe y su resumen."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Datos"

    hoja["A1"] = informe.titulo
    hoja["A1"].font = Font(bold=True, size=14, color=_VERDE_HEX)
    hoja["A2"] = informe.descripcion
    hoja["A3"] = f"Titular: {informe.titular} · Generado: {informe.generado:%d/%m/%Y %H:%M}"
    hoja["A3"].font = Font(italic=True, color="555555")

    fila_encabezado = 5
    relleno = PatternFill("solid", start_color=_VERDE_HEX)
    for indice, columna in enumerate(informe.columnas, start=1):
        celda = hoja.cell(row=fila_encabezado, column=indice, value=columna.titulo)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = relleno
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for desplazamiento, fila in enumerate(informe.filas, start=1):
        for indice, columna in enumerate(informe.columnas, start=1):
            celda = hoja.cell(
                row=fila_encabezado + desplazamiento,
                column=indice,
                value=fila.get(columna.clave),
            )
            formato = _formato_excel(columna)
            if formato:
                celda.number_format = formato

    # Ancho de cada columna según su contenido más largo, con tope para que una
    # descripción extensa no empuje las demás fuera de la pantalla.
    for indice, columna in enumerate(informe.columnas, start=1):
        largo = max(
            [len(columna.titulo)]
            + [len(texto_de_celda(fila.get(columna.clave), columna)) for fila in informe.filas]
        )
        hoja.column_dimensions[get_column_letter(indice)].width = min(max(largo + 3, 10), 45)

    hoja.freeze_panes = hoja.cell(row=fila_encabezado + 1, column=1)
    if informe.filas:
        ultima = get_column_letter(len(informe.columnas))
        hoja.auto_filter.ref = (
            f"A{fila_encabezado}:{ultima}{fila_encabezado + len(informe.filas)}"
        )

    resumen = libro.create_sheet("Resumen")
    resumen["A1"] = informe.titulo
    resumen["A1"].font = Font(bold=True, size=14, color=_VERDE_HEX)
    resumen.append([])
    for indicador in informe.resumen:
        resumen.append([indicador.rotulo, indicador.valor])
    for fila in resumen.iter_rows(min_row=3, max_col=1):
        for celda in fila:
            celda.font = Font(bold=True)
    if informe.nota:
        resumen.append([])
        resumen.append([informe.nota])
    resumen.column_dimensions["A"].width = 38
    resumen.column_dimensions["B"].width = 28

    _fijar_textos_como_texto(libro)

    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------

# Las fuentes base de PDF solo cubren el alfabeto latino básico. Las letras del
# español caben; estos signos tipográficos no, y se sustituyen por su
# equivalente más cercano en lugar de hacer fallar el documento.
_SUSTITUTOS_PDF = str.maketrans(
    {
        "—": "-",
        "–": "-",
        "−": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
    }
)


def _texto_pdf(texto: str) -> str:
    return texto.translate(_SUSTITUTOS_PDF).encode("latin-1", "replace").decode("latin-1")


def a_pdf(informe: Informe) -> bytes:
    """Documento con encabezado, resumen, tabla paginada y pie numerado."""
    from fpdf import FPDF
    from fpdf.fonts import FontFace

    titulo_sistema = _texto_pdf(configuracion.nombre_sistema)

    class Documento(FPDF):
        def header(self) -> None:
            self.set_font("helvetica", "", 8)
            self.set_text_color(90, 90, 90)
            self.cell(0, 5, titulo_sistema, align="L", new_x="LMARGIN")
            self.cell(
                0, 5, _texto_pdf(f"Generado el {informe.generado:%d/%m/%Y %H:%M}"), align="R"
            )
            self.ln(8)

        def footer(self) -> None:
            self.set_y(-12)
            self.set_font("helvetica", "", 8)
            self.set_text_color(90, 90, 90)
            self.cell(0, 5, f"Página {self.page_no()} de {{nb}}", align="C")

    # Con más de seis columnas la tabla no cabe a lo alto de la hoja.
    orientacion = "landscape" if len(informe.columnas) > 6 else "portrait"
    documento = Documento(orientation=orientacion, format="A4")
    documento.set_title(_texto_pdf(informe.titulo))
    documento.set_author(titulo_sistema)
    documento.set_auto_page_break(auto=True, margin=16)
    documento.add_page()

    documento.set_font("helvetica", "B", 16)
    documento.set_text_color(*_VERDE)
    documento.cell(0, 9, _texto_pdf(informe.titulo), new_x="LMARGIN", new_y="NEXT")
    documento.set_font("helvetica", "", 10)
    documento.set_text_color(40, 40, 40)
    documento.multi_cell(0, 5, _texto_pdf(informe.descripcion), new_x="LMARGIN", new_y="NEXT")
    documento.set_font("helvetica", "I", 9)
    documento.cell(
        0, 6, _texto_pdf(f"Titular: {informe.titular}"), new_x="LMARGIN", new_y="NEXT"
    )
    documento.ln(3)

    if informe.resumen:
        documento.set_font("helvetica", "", 9)
        with documento.table(
            col_widths=(1, 1),
            width=min(documento.epw, 140),
            align="LEFT",
            first_row_as_headings=False,
            borders_layout="HORIZONTAL_LINES",
            line_height=6,
        ) as tabla:
            for indicador in informe.resumen:
                fila = tabla.row()
                fila.cell(_texto_pdf(indicador.rotulo), style=FontFace(emphasis="BOLD"))
                fila.cell(_texto_pdf(indicador.valor))
        documento.ln(4)

    if informe.filas:
        alineaciones = tuple(
            "LEFT" if columna.tipo in (TipoDato.TEXTO, TipoDato.FECHA) else "RIGHT"
            for columna in informe.columnas
        )
        # El ancho de cada columna se reparte según su contenido más largo.
        pesos = tuple(
            max(
                [min(len(columna.titulo), 14)]
                + [len(texto_de_celda(f.get(columna.clave), columna)) for f in informe.filas]
            )
            for columna in informe.columnas
        )
        documento.set_font("helvetica", "", 8.5)
        with documento.table(
            col_widths=pesos,
            text_align=alineaciones,
            headings_style=FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=_VERDE),
            cell_fill_color=_FONDO_ALTERNO,
            cell_fill_mode="ROWS",
            line_height=5.5,
            repeat_headings=1,
        ) as tabla:
            encabezado = tabla.row()
            for columna in informe.columnas:
                encabezado.cell(_texto_pdf(columna.titulo))
            for fila in informe.filas:
                renglon = tabla.row()
                for columna in informe.columnas:
                    renglon.cell(_texto_pdf(texto_de_celda(fila.get(columna.clave), columna)))
    else:
        documento.set_font("helvetica", "I", 10)
        documento.cell(0, 8, "El informe todavía no tiene registros.", new_x="LMARGIN", new_y="NEXT")

    if informe.nota:
        documento.ln(4)
        documento.set_font("helvetica", "I", 8.5)
        documento.set_text_color(70, 70, 70)
        documento.multi_cell(0, 4.5, _texto_pdf(informe.nota))

    return bytes(documento.output())
