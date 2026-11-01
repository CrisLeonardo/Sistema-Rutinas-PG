"""MEJ-08/09: restricciones, recetas, semana y sustitución calculada."""
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.alimentacion import ALERGENOS, INTOLERANCIAS, CambioComida, PreferenciasEntrada
from app.modelos.catalogo import Alimento
from app.motor.semana_alimentaria import disponibles_para_recetas, componer
from app.nucleo.recetas import FUENTES, VERSION_RECETAS
from app.servicios import alimentacion as servicio
from app.servicios.restricciones_alimentarias import preferencias
from app.nucleo.revision import FECHA_REVISION, PRECIO_FUENTE, REVISION_NUTRICIONAL

enrutador = APIRouter(prefix="/alimentacion", tags=["Alimentación práctica"])


@enrutador.get("/preferencias")
def consultar_preferencias(sesion: SesionBD, usuario: UsuarioAutenticado):
    return {"preferencias": preferencias(sesion, usuario.id), "alergenos": ALERGENOS,
            "intolerancias": INTOLERANCIAS,
            "nota": "Declare alergias por separado de gustos. Otra restricción detiene la propuesta y requiere valoración profesional. El filtro no verifica trazas de marcas ni contacto cruzado en cocina."}


@enrutador.put("/preferencias")
def guardar_preferencias(datos: PreferenciasEntrada, sesion: SesionBD, usuario: UsuarioAutenticado):
    ids = set(sesion.scalars(select(Alimento.id)).all())
    if not set(datos.alimentos_excluidos).issubset(ids):
        raise HTTPException(422, "Algún alimento excluido no pertenece al catálogo.")
    servicio.guardar_preferencias(sesion, usuario, datos)
    return {"preferencias": datos, "mensaje": "Restricciones guardadas. Prepare otra semana para aplicarlas."}


@enrutador.get("/recetas")
def consultar_recetas(sesion: SesionBD, usuario: UsuarioAutenticado):
    alimentos, _ = servicio.catalogo(sesion, usuario)
    recetas, por_nombre = disponibles_para_recetas(alimentos)
    return {"recetas": [componer(r, por_nombre, [g for _, g in r.ingredientes]) for r in recetas],
            "version": VERSION_RECETAS, "fuentes": FUENTES, "nota": f"Porciones de referencia, no asignadas a su plan. {REVISION_NUTRICIONAL}. Precios: {PRECIO_FUENTE}, {FECHA_REVISION}."}


@enrutador.get("/semana")
def consultar_semana(sesion: SesionBD, usuario: UsuarioAutenticado):
    return servicio.publicar(servicio.consultar(sesion, usuario))


@enrutador.post("/semana", status_code=201)
def preparar_semana(sesion: SesionBD, usuario: UsuarioAutenticado):
    return servicio.generar(sesion, usuario)


@enrutador.get("/alternativas")
def alternativas(sesion: SesionBD, usuario: UsuarioAutenticado,
                 dia: int = Query(ge=1, le=7), tiempo: int = Query(ge=0, le=4)):
    return servicio.opciones_de_cambio(sesion, usuario, dia, tiempo)


@enrutador.put("/semana/comida")
def cambiar_comida(datos: CambioComida, sesion: SesionBD, usuario: UsuarioAutenticado):
    return servicio.cambiar(sesion, usuario, datos)
