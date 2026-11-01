"""Semana privada, validación vigente y control de cambios concurrentes."""
from copy import deepcopy
from datetime import date
import hashlib
import json

from fastapi import HTTPException
from sqlalchemy import select, update

from app.modelos.alimentacion import PreferenciasAlimentarias, SemanaAlimentaria
from app.modelos.perfil import PerfilBiometrico
from app.modelos.usuario import Usuario
from app.motor import semana_alimentaria as motor
from app.nucleo.recetas import FUENTES, VERSION_RECETAS
from app.nucleo.tiempo import hoy_local
from app.servicios import plan as planes
from app.servicios.restricciones_alimentarias import preferencias, filtrar


def bloquear_cuenta(sesion, usuario):
    # Una sola fila estable serializa creación y preferencias en PostgreSQL.
    sesion.execute(select(Usuario.id).where(Usuario.id == usuario.id).with_for_update()).scalar_one()


def contexto(sesion, usuario):
    perfil = sesion.scalars(select(PerfilBiometrico).where(PerfilBiometrico.usuario_id == usuario.id)
                            .order_by(PerfilBiometrico.fecha_registro.desc(), PerfilBiometrico.id.desc()).limit(1)).first()
    if perfil is None:
        raise HTTPException(409, "Registre su perfil biométrico antes de preparar la alimentación.")
    opciones = preferencias(sesion, usuario.id)
    if perfil.condiciones or opciones.otra_restriccion:
        raise HTTPException(403, "Su condición o restricción requiere valoración profesional. El sistema no prepara menús ni sustituciones para este caso.")
    return opciones


def catalogo(sesion, usuario):
    opciones = contexto(sesion, usuario)
    alimentos = filtrar(planes.alimentos_disponibles(sesion), opciones)
    serializado = [vars(a) for a in alimentos]
    firma = hashlib.sha256(json.dumps([VERSION_RECETAS, opciones.model_dump(), serializado], sort_keys=True, default=str).encode()).hexdigest()
    return alimentos, firma


def consultar(sesion, usuario, requerido=True):
    plan = planes.obtener_plan_vigente(sesion, usuario)
    semana = sesion.get(SemanaAlimentaria, usuario.id)
    if semana is None or plan is None or semana.plan_id != plan.id:
        if requerido:
            contexto(sesion, usuario)
            raise HTTPException(404, "Prepare una semana para su plan vigente.")
        return None
    _, firma = catalogo(sesion, usuario)
    if firma != semana.firma_catalogo:
        raise HTTPException(409, "Cambió el catálogo o sus restricciones. Prepare otra semana para recalcular alimentos y compras.")
    return semana


def dia_de_hoy(datos) -> int:
    """Día de la semana preparada que corresponde a hoy.

    El día en que se prepara la semana es el día 1 y la semana se repite en
    ciclo. Las semanas preparadas antes de guardar la fecha empiezan en el día 1.
    """
    preparada = datos.get("preparada_el")
    if not preparada:
        return 1
    return (hoy_local() - date.fromisoformat(preparada)).days % len(datos["dias"]) + 1


def publicar(semana):
    datos = deepcopy(semana.datos)
    datos["dia_de_hoy"] = dia_de_hoy(semana.datos)
    datos.update(plan_id=semana.plan_id, revision=semana.revision, compras=motor.compras(datos),
                 version_recetas=VERSION_RECETAS, fuentes=FUENTES,
                 estado_revision="pendiente", nota="Piloto pendiente de revisión profesional. Revise etiquetas y preparación: el filtro de ingredientes no certifica ausencia de trazas ni contacto cruzado.")
    datos["recetas_distintas"] = len({t["receta_id"] for d in datos["dias"] for t in d["tiempos"]})
    return datos


def guardar_preferencias(sesion, usuario, opciones):
    bloquear_cuenta(sesion, usuario)
    registro = sesion.get(PreferenciasAlimentarias, usuario.id)
    if registro is None:
        registro = PreferenciasAlimentarias(usuario_id=usuario.id)
        sesion.add(registro)
    registro.datos = opciones.model_dump()
    # Conserva revisión monotónica: una pestaña antigua nunca puede sobrescribirla.
    semana = sesion.get(SemanaAlimentaria, usuario.id)
    if semana is not None:
        semana.firma_catalogo = ""
    sesion.commit()


def generar(sesion, usuario):
    bloquear_cuenta(sesion, usuario)
    alimentos, firma = catalogo(sesion, usuario)
    plan = planes.obtener_plan_vigente(sesion, usuario)
    if plan is None:
        raise HTTPException(409, "Genere primero su plan de alimentación.")
    objetivo = {"energia_kcal": float(plan.calorias_objetivo), "proteina_g": float(plan.proteina_g),
                "carbohidrato_g": float(plan.carbohidrato_g), "grasa_g": float(plan.grasa_g)}
    try:
        datos = motor.generar(objetivo, alimentos)
    except motor.SemanaNoFactible as error:
        raise HTTPException(409, str(error)) from None
    datos["preparada_el"] = hoy_local().isoformat()
    semana = sesion.get(SemanaAlimentaria, usuario.id)
    if semana is None:
        semana = SemanaAlimentaria(usuario_id=usuario.id, revision=0)
        sesion.add(semana)
    semana.plan_id, semana.datos, semana.firma_catalogo = plan.id, datos, firma
    semana.revision += 1
    sesion.commit()
    return publicar(semana)


def opciones_de_cambio(sesion, usuario, dia, tiempo):
    semana = consultar(sesion, usuario)
    alimentos, _ = catalogo(sesion, usuario)
    return {"revision": semana.revision, "opciones": motor.alternativas(semana.datos, alimentos, dia, tiempo)}


def cambiar(sesion, usuario, cambio):
    bloquear_cuenta(sesion, usuario)
    semana = consultar(sesion, usuario)
    if semana.revision != cambio.revision:
        raise HTTPException(409, "La semana cambió en otra ventana. Recargue antes de elegir una alternativa.")
    alimentos, _ = catalogo(sesion, usuario)
    opcion = next((o for o in motor.alternativas(semana.datos, alimentos, cambio.dia, cambio.tiempo)
                   if o["receta_id"] == cambio.receta_id), None)
    if opcion is None:
        raise HTTPException(409, "La receta no es una alternativa compatible con estas porciones y restricciones.")
    datos = deepcopy(semana.datos)
    dia = datos["dias"][cambio.dia - 1]
    dia["tiempos"][cambio.tiempo] = opcion
    dia.update(motor.totales(dia["tiempos"]))
    # Compare-and-swap también protege SQLite, donde FOR UPDATE no bloquea filas.
    resultado = sesion.execute(update(SemanaAlimentaria).where(
        SemanaAlimentaria.usuario_id == usuario.id, SemanaAlimentaria.revision == cambio.revision
    ).values(datos=datos, revision=cambio.revision + 1), execution_options={"synchronize_session": False})
    if resultado.rowcount != 1:
        sesion.rollback()
        raise HTTPException(409, "La semana cambió. Recargue antes de continuar.")
    sesion.commit()
    sesion.expire(semana)
    return publicar(semana)


def verificar_menu_anterior(sesion, usuario, porciones):
    """Nunca devuelve un ingrediente excluido conservado en un plan antiguo."""
    opciones = contexto(sesion, usuario)
    permitidos = {a.id for a in filtrar(planes.alimentos_disponibles(sesion), opciones)}
    restringido = opciones.alergias or opciones.intolerancias or opciones.patron != "omnivoro" or opciones.alimentos_excluidos
    if restringido and any(p.alimento_id not in permitidos for p in porciones):
        raise HTTPException(409, "El menú anterior no cumple sus restricciones actuales. Prepare una nueva semana en Alimentación.")
