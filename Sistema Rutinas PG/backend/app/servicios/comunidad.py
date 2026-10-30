"""Piloto privado: permisos por grupo y puntuación derivada, sin puntos del cliente.

El conjunto de fechas válidas es idempotente incluso si se registra dos veces
una sesión. No se exporta la bitácora ni los motivos de una pausa al grupo.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from fastapi import HTTPException
from sqlalchemy import select, or_, and_, func
from app.modelos.comunidad import (GrupoPrivado, MiembroPrivado, InvitacionPrivada,
                                  SemanaPrivada, BloqueoPrivado, DenunciaPrivada, EventoConstancia)
from app.modelos.entrenamiento import SesionRealizada
from app.modelos.plan import Plan, SesionEntrenamiento
from app.modelos.usuario import Usuario

def ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def hoy():
    return (ahora() - timedelta(hours=6)).date()

def lunes():
    return hoy() - timedelta(days=hoy().weekday())

def error(mensaje="Grupo o recurso no disponible.", codigo=404):
    raise HTTPException(codigo, mensaje)

def cuenta(s, u):
    # Serializa las altas y el límite de tres grupos de esta cuenta.
    s.execute(select(Usuario).where(Usuario.id == u.id).with_for_update()).scalar_one()

def acceso(s, u, gid, propietario=False):
    g = s.execute(select(GrupoPrivado).where(GrupoPrivado.id == gid).with_for_update()).scalar_one_or_none()
    m = s.scalar(select(MiembroPrivado).where(MiembroPrivado.grupo_id == gid,
                 MiembroPrivado.usuario_id == u.id, MiembroPrivado.activo.is_(True)))
    if not g or g.cerrado or not m or (propietario and g.propietario_id != u.id):
        error()
    return g, m

def bloqueados(s, a, b):
    return s.scalar(select(BloqueoPrivado).where(or_(
        and_(BloqueoPrivado.autor_id == a, BloqueoPrivado.destino_id == b),
        and_(BloqueoPrivado.autor_id == b, BloqueoPrivado.destino_id == a)))) is not None

def limite_grupos(s, u):
    cantidad = s.scalar(select(func.count()).select_from(MiembroPrivado).where(
        MiembroPrivado.usuario_id == u.id, MiembroPrivado.activo.is_(True)))
    if cantidad >= 3:
        error("Puede participar en un máximo de tres grupos.", 409)

def crear(s, u, d):
    cuenta(s, u); limite_grupos(s, u)
    g = GrupoPrivado(propietario_id=u.id, nombre=d.nombre)
    s.add(g); s.flush()
    s.add(MiembroPrivado(grupo_id=g.id, usuario_id=u.id, alias=d.alias))
    s.commit()
    return ver(s, u, g.id)

def listar(s, u):
    ids = s.scalars(select(GrupoPrivado.id).join(MiembroPrivado,
        MiembroPrivado.grupo_id == GrupoPrivado.id).where(MiembroPrivado.usuario_id == u.id,
        MiembroPrivado.activo.is_(True), GrupoPrivado.cerrado.is_(False))).all()
    return [ver(s, u, gid) for gid in ids]

def puntos(s, m, semana):
    if not semana or semana.pausada:
        return None
    cantidad = s.scalar(select(func.count()).select_from(EventoConstancia).where(
        EventoConstancia.semana_id == semana.id, EventoConstancia.fecha <= hoy()))
    return min(100, cantidad * 100 // semana.meta)

def registrar_evento(s, realizada):
    """Dentro de la transacción de entrenamiento: un evento por semana y fecha.

    Bloquea la participación antes de comprobar duplicados. La clave compuesta
    conserva esa garantía en la base. No vuelve a otorgar puntos al consultar.
    """
    if (realizada.fecha > hoy() or
        (realizada.fecha_registro - timedelta(hours=6)).date() != realizada.fecha or
        not any(x.repeticiones > 0 or (x.duracion_segundos or 0) > 0 for x in realizada.series)):
        return
    semanas = s.scalars(select(SemanaPrivada).join(MiembroPrivado,
        MiembroPrivado.id == SemanaPrivada.miembro_id).join(GrupoPrivado,
        GrupoPrivado.id == MiembroPrivado.grupo_id).where(
        MiembroPrivado.usuario_id == realizada.usuario_id,
        MiembroPrivado.activo.is_(True), GrupoPrivado.cerrado.is_(False),
        SemanaPrivada.lunes == realizada.fecha - timedelta(days=realizada.fecha.weekday())
        ).order_by(SemanaPrivada.id).with_for_update(of=SemanaPrivada)).all()
    for semana in semanas:
        dias = {x["id"]: x["dia"] for x in semana.sesiones}
        if (semana.pausada or realizada.fecha_registro < semana.inicio or
            dias.get(realizada.sesion_id) != realizada.fecha.weekday()+1):
            continue
        if not s.get(EventoConstancia, (semana.id, realizada.fecha)):
            s.add(EventoConstancia(semana_id=semana.id, fecha=realizada.fecha,
                                  sesion_realizada_id=realizada.id))
            s.flush()

def ver(s, u, gid):
    g, propio = acceso(s, u, gid)
    miembros = s.scalars(select(MiembroPrivado).where(MiembroPrivado.grupo_id == gid,
                         MiembroPrivado.activo.is_(True)).order_by(MiembroPrivado.id)).all()
    salida = []; total = objetivo = 0
    for m in miembros:
        if bloqueados(s, u.id, m.usuario_id):
            continue
        semana = s.scalar(select(SemanaPrivada).where(SemanaPrivada.miembro_id == m.id,
                                                    SemanaPrivada.lunes == lunes()))
        p = puntos(s, m, semana)
        if p is not None:
            total += p; objetivo += 100
        salida.append(dict(id=m.id, alias=m.alias, soy_yo=m.id == propio.id,
            puntos=p, estado="pausa" if semana and semana.pausada else
            "participando" if semana else "sin_inscribir"))
    return dict(id=g.id, nombre=g.nombre, soy_propietario=g.propietario_id == u.id,
        semana=lunes().isoformat(), objetivo_colectivo=objetivo,
        puntos_colectivos=total, miembros=salida)

def invitar(s, u, gid):
    acceso(s, u, gid, True)
    cantidad = s.scalar(select(func.count()).select_from(InvitacionPrivada).where(
        InvitacionPrivada.grupo_id == gid, InvitacionPrivada.usada.is_(False),
        InvitacionPrivada.vence > ahora()))
    if cantidad >= 10: error("Ya hay diez invitaciones vigentes. Revoque las anteriores.", 409)
    codigo = secrets.token_urlsafe(32)
    i = InvitacionPrivada(id=hashlib.sha256(codigo.encode()).hexdigest(), grupo_id=gid,
                          vence=ahora()+timedelta(hours=48))
    s.add(i); s.commit()
    return dict(codigo=codigo, vence=i.vence.isoformat()+"Z")

def revocar(s, u, gid):
    acceso(s, u, gid, True)
    for i in s.scalars(select(InvitacionPrivada).where(InvitacionPrivada.grupo_id == gid)):
        i.usada = True
    s.commit()

def responder(s, u, d):
    cuenta(s, u)
    # Primero grupo, después invitación: mismo orden de bloqueo que revocar.
    iid = hashlib.sha256(d.codigo.encode()).hexdigest()
    referencia = s.get(InvitacionPrivada, iid)
    if referencia is None: error("Invitación no disponible.")
    g = s.execute(select(GrupoPrivado).where(GrupoPrivado.id == referencia.grupo_id).with_for_update()).scalar_one()
    i = s.execute(select(InvitacionPrivada).where(InvitacionPrivada.id == iid).with_for_update()
                  .execution_options(populate_existing=True)).scalar_one()
    if i.usada or i.vence <= ahora() or g.cerrado or bloqueados(s, u.id, g.propietario_id):
        error("Invitación no disponible.")
    if not d.aceptar:
        i.usada = True; s.commit(); return None
    if not d.consentimiento or len(d.alias) < 2:
        error("Acepte las reglas y elija un alias de al menos dos caracteres.", 422)
    prev = s.scalar(select(MiembroPrivado).where(MiembroPrivado.grupo_id == g.id,
                    MiembroPrivado.usuario_id == u.id))
    if prev: error("Ya participó en este grupo. El piloto no permite reingresos.", 409)
    limite_grupos(s, u)
    miembros = s.scalars(select(MiembroPrivado).where(MiembroPrivado.grupo_id == g.id,
                         MiembroPrivado.activo.is_(True))).all()
    if len(miembros) >= 20: error("El grupo alcanzó sus veinte participantes.", 409)
    if any(m.alias.casefold() == d.alias.casefold() for m in miembros):
        error("Ese alias ya se utiliza en el grupo.", 409)
    s.add(MiembroPrivado(grupo_id=g.id, usuario_id=u.id, alias=d.alias))
    i.usada = True; s.commit()
    return ver(s, u, g.id)

def participar(s, u, gid, d):
    _, m = acceso(s, u, gid)
    if s.scalar(select(SemanaPrivada).where(SemanaPrivada.miembro_id == m.id, SemanaPrivada.lunes == lunes())):
        error("La meta quedó fijada esta semana. Puede pausar y volver la próxima semana.", 409)
    plan = s.scalar(select(Plan).where(Plan.usuario_id == u.id, Plan.activo.is_(True)).order_by(Plan.id.desc()))
    sesiones = [] if not plan else [x for x in plan.sesiones if x.ejercicios]
    if len(sesiones) < d.meta:
        error("La meta debe ser de 2 a 5 y no superar las sesiones de su plan vigente.", 409)
    s.add(SemanaPrivada(miembro_id=m.id, lunes=lunes(), inicio=ahora(), meta=d.meta,
          sesiones=[dict(id=x.id, dia=x.dia) for x in sesiones]))
    s.commit(); return ver(s, u, gid)

def pausar(s, u, gid):
    _, m = acceso(s, u, gid)
    semana = s.scalar(select(SemanaPrivada).where(SemanaPrivada.miembro_id == m.id, SemanaPrivada.lunes == lunes()))
    if semana: semana.pausada = True
    s.commit()

def salir(s, u, gid):
    g, m = acceso(s, u, gid)
    m.activo = False
    if g.propietario_id == u.id:
        g.cerrado = True
        for otro in s.scalars(select(MiembroPrivado).where(MiembroPrivado.grupo_id == gid)):
            otro.activo = False
    s.commit()

def destino(s, gid, mid):
    m = s.get(MiembroPrivado, mid)
    if not m or m.grupo_id != gid or not m.activo: error()
    return m

def bloquear(s, u, gid, mid):
    _, propio = acceso(s, u, gid)
    otro = destino(s, gid, mid)
    if propio.id == mid: error("No puede bloquearse a sí mismo.", 422)
    if not s.get(BloqueoPrivado, (u.id, otro.usuario_id)):
        s.add(BloqueoPrivado(autor_id=u.id, destino_id=otro.usuario_id))
    s.commit()

def denunciar(s, u, gid, d):
    _, propio = acceso(s, u, gid)
    otro = destino(s, gid, d.miembro_id)
    if propio.id == otro.id: error("Seleccione otro participante.", 422)
    if s.scalar(select(func.count()).select_from(DenunciaPrivada).where(
        DenunciaPrivada.grupo_id == gid, DenunciaPrivada.autor_id == u.id,
        DenunciaPrivada.resuelta.is_(False))) >= 5:
        error("Ya tiene cinco denuncias abiertas en este grupo.", 409)
    s.add(DenunciaPrivada(grupo_id=gid, autor_id=u.id, miembro_id=otro.id, motivo=d.motivo))
    s.commit()

def denuncias(s, u, gid):
    acceso(s, u, gid, True)
    return s.scalars(select(DenunciaPrivada).where(DenunciaPrivada.grupo_id == gid).limit(100)).all()

def moderar(s, u, gid, mid):
    acceso(s, u, gid, True)
    otro = destino(s, gid, mid)
    if otro.usuario_id == u.id: error("Para cerrar el grupo use Salir.", 422)
    otro.activo = False; otro.expulsado = True
    s.commit()

def resolver(s, u, gid, did):
    acceso(s, u, gid, True)
    d = s.get(DenunciaPrivada, did)
    if not d or d.grupo_id != gid: error()
    d.resuelta = True; s.commit()
