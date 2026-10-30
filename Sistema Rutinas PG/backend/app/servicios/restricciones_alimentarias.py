"""Exclusión por composición, nunca por coincidencias parciales del nombre."""
from sqlalchemy.orm import Session

from app.esquemas.alimentacion import PreferenciasEntrada
from app.modelos.alimentacion import PreferenciasAlimentarias
from app.nucleo.alimentos_iniciales import ALIMENTOS_INICIALES
from app.nucleo.recetas import DETALLES

FIRMAS_INICIALES = {r[0]: tuple(float(v) for v in r[2:6]) for r in ALIMENTOS_INICIALES}


def preferencias(sesion: Session, usuario_id: int) -> PreferenciasEntrada:
    registro = sesion.get(PreferenciasAlimentarias, usuario_id)
    return PreferenciasEntrada.model_validate(registro.datos if registro else {})


def detalle(alimento):
    firma = tuple(float(getattr(alimento, k)) for k in (
        "energia_kcal_100g", "proteina_g_100g", "carbohidrato_g_100g", "grasa_g_100g"))
    if firma != FIRMAS_INICIALES.get(alimento.nombre):
        return None
    return DETALLES.get(alimento.nombre)


def compatible(alimento, opciones: PreferenciasEntrada) -> bool:
    if opciones.otra_restriccion or alimento.id in opciones.alimentos_excluidos:
        return False
    datos = detalle(alimento)
    restringido = opciones.patron != "omnivoro" or opciones.alergias or opciones.intolerancias
    if datos is None:
        return not restringido  # Sin datos no se infiere ausencia de alérgenos.
    _, componentes, animal = datos
    if componentes.intersection(opciones.alergias + opciones.intolerancias):
        return False
    if opciones.patron == "vegano" and (animal or componentes.intersection({"huevo", "leche"})):
        return False
    if opciones.patron == "vegetariano" and animal and not componentes.intersection({"huevo", "leche"}):
        return False
    return True


def filtrar(alimentos, opciones):
    return [a for a in alimentos if compatible(a, opciones)]
