"""Controlador de los informes: consulta en pantalla y descarga (apartado 6.4).

Los informes personales operan sobre la cuenta que inició sesión; los de
administración exigen el rol de administrador, verificado aquí en el servidor
y no solo ocultando el botón en la interfaz (requerimiento 4.5.1).
"""

from dataclasses import asdict
from typing import Literal

from fastapi import APIRouter, HTTPException, Response, status

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.informe import (
    ColumnaPublica,
    IndicadorPublico,
    InformeDisponible,
    InformePublico,
)
from app.servicios import exportacion
from app.servicios import informes as servicio_informes

enrutador = APIRouter(prefix="/informes", tags=["Informes"])


def _construir(sesion: SesionBD, usuario: UsuarioAutenticado, clave: str):
    """Arma el informe o traduce sus fallos a la respuesta que corresponde."""
    try:
        return servicio_informes.construir_informe(sesion, usuario, clave)
    except servicio_informes.InformeNoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El informe solicitado no existe.",
        ) from None
    except servicio_informes.InformeReservado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este informe está reservado a las cuentas de administrador.",
        ) from None


@enrutador.get(
    "",
    response_model=list[InformeDisponible],
    summary="Listar los informes disponibles",
)
def listar(usuario: UsuarioAutenticado) -> list[InformeDisponible]:
    """Devuelve los informes que la cuenta puede consultar según su rol."""
    return [
        InformeDisponible(
            clave=definicion.clave,
            titulo=definicion.titulo,
            descripcion=definicion.descripcion,
            ambito=definicion.ambito,
            formatos=list(exportacion.FORMATOS),
        )
        for definicion in servicio_informes.informes_disponibles(usuario)
    ]


@enrutador.get(
    "/{clave}",
    response_model=InformePublico,
    summary="Consultar un informe en pantalla",
)
def consultar(clave: str, sesion: SesionBD, usuario: UsuarioAutenticado) -> InformePublico:
    """Entrega el informe completo para dibujarlo en la pantalla."""
    informe = _construir(sesion, usuario, clave)
    return InformePublico(
        clave=informe.clave,
        titulo=informe.titulo,
        descripcion=informe.descripcion,
        titular=informe.titular,
        generado=informe.generado,
        columnas=[ColumnaPublica(**asdict(columna)) for columna in informe.columnas],
        filas=informe.filas,
        resumen=[IndicadorPublico(**asdict(indicador)) for indicador in informe.resumen],
        nota=informe.nota,
    )


@enrutador.get(
    "/{clave}/{formato}",
    summary="Descargar un informe en CSV, Excel o PDF",
    response_class=Response,
    responses={200: {"description": "El archivo del informe"}},
)
def descargar(
    clave: str,
    formato: Literal["csv", "xlsx", "pdf"],
    sesion: SesionBD,
    usuario: UsuarioAutenticado,
) -> Response:
    """Genera el archivo y lo entrega como descarga.

    El nombre del archivo lleva la fecha de generación, para que dos descargas
    de días distintos no se sobrescriban en la carpeta del usuario.
    """
    informe = _construir(sesion, usuario, clave)
    contenido = exportacion.exportar(informe, formato)
    nombre = exportacion.nombre_de_archivo(informe, formato)
    return Response(
        content=contenido,
        media_type=exportacion.TIPOS_DE_CONTENIDO[formato],
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            # Un informe trae datos personales: que ningún intermediario lo guarde.
            "Cache-Control": "no-store",
        },
    )
