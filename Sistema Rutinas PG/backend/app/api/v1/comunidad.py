"""Controladores del piloto voluntario de grupos privados."""
from fastapi import APIRouter, Response, Depends, HTTPException
from app.nucleo.configuracion import configuracion

def comprobar_disponibilidad():
    if not configuracion.comunidad_habilitada:
        raise HTTPException(404, "Recurso no disponible.")
from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.comunidad import (CrearGrupo, ResponderInvitacion, Participar,
    Denunciar, GrupoPublico, InvitacionPublica, DenunciaPublica)
from app.servicios import comunidad as servicio

enrutador = APIRouter(prefix="/comunidad", tags=["Comunidad privada"], dependencies=[Depends(comprobar_disponibilidad)])

@enrutador.get("/grupos", response_model=list[GrupoPublico])
def listar(sesion: SesionBD, usuario: UsuarioAutenticado, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return servicio.listar(sesion, usuario)

@enrutador.post("/grupos", response_model=GrupoPublico, status_code=201)
def crear(datos: CrearGrupo, sesion: SesionBD, usuario: UsuarioAutenticado):
    return servicio.crear(sesion, usuario, datos)

@enrutador.get("/grupos/{gid}", response_model=GrupoPublico)
def ver(gid: str, sesion: SesionBD, usuario: UsuarioAutenticado, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return servicio.ver(sesion, usuario, gid)

@enrutador.post("/grupos/{gid}/invitaciones", response_model=InvitacionPublica)
def invitar(gid: str, sesion: SesionBD, usuario: UsuarioAutenticado, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return servicio.invitar(sesion, usuario, gid)

@enrutador.delete("/grupos/{gid}/invitaciones", status_code=204)
def revocar(gid: str, sesion: SesionBD, usuario: UsuarioAutenticado):
    servicio.revocar(sesion, usuario, gid)

@enrutador.post("/invitaciones/responder", response_model=GrupoPublico | None)
def responder(datos: ResponderInvitacion, sesion: SesionBD, usuario: UsuarioAutenticado):
    return servicio.responder(sesion, usuario, datos)

@enrutador.post("/grupos/{gid}/participar", response_model=GrupoPublico)
def participar(gid: str, datos: Participar, sesion: SesionBD, usuario: UsuarioAutenticado):
    return servicio.participar(sesion, usuario, gid, datos)

@enrutador.post("/grupos/{gid}/pausar", status_code=204)
def pausar(gid: str, sesion: SesionBD, usuario: UsuarioAutenticado):
    servicio.pausar(sesion, usuario, gid)

@enrutador.delete("/grupos/{gid}/membresia", status_code=204)
def salir(gid: str, sesion: SesionBD, usuario: UsuarioAutenticado):
    servicio.salir(sesion, usuario, gid)

@enrutador.post("/grupos/{gid}/bloqueos/{mid}", status_code=204)
def bloquear(gid: str, mid: str, sesion: SesionBD, usuario: UsuarioAutenticado):
    servicio.bloquear(sesion, usuario, gid, mid)

@enrutador.post("/grupos/{gid}/denuncias", status_code=204)
def denunciar(gid: str, datos: Denunciar, sesion: SesionBD, usuario: UsuarioAutenticado):
    servicio.denunciar(sesion, usuario, gid, datos)

@enrutador.get("/grupos/{gid}/denuncias", response_model=list[DenunciaPublica])
def denuncias(gid: str, sesion: SesionBD, usuario: UsuarioAutenticado):
    return servicio.denuncias(sesion, usuario, gid)

@enrutador.post("/grupos/{gid}/expulsiones/{mid}", status_code=204)
def moderar(gid: str, mid: str, sesion: SesionBD, usuario: UsuarioAutenticado):
    servicio.moderar(sesion, usuario, gid, mid)

@enrutador.post("/grupos/{gid}/denuncias/{did}/resolver", status_code=204)
def resolver(gid: str, did: str, sesion: SesionBD, usuario: UsuarioAutenticado):
    servicio.resolver(sesion, usuario, gid, did)
