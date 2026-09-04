"""Carga en el catálogo el resultado del levantamiento de campo (historia HU-11).

Lee los CSV que deja la visita a los mercados de El Progreso, Jutiapa y al
Gimnasio FAMAS (ver `operaciones/campo/INSTRUCCIONES.md`) y reemplaza los
valores provisionales del catálogo por los reales: crea lo que no existe,
actualiza lo que ya existe por nombre, y nunca borra nada, para no romper los
planes que ya referencian un alimento o un ejercicio.

    uv run python cargar_catalogo_de_campo.py --alimentos ruta.csv
    uv run python cargar_catalogo_de_campo.py --ejercicios ruta.csv
    uv run python cargar_catalogo_de_campo.py --alimentos a.csv --ejercicios e.csv
"""

import argparse
import csv
import logging
import sys
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select

from app.esquemas.catalogo import AlimentoEntrada, EjercicioEntrada
from app.modelos.catalogo import Alimento, Ejercicio
from app.nucleo.base_datos import FabricaSesiones
from app.servicios.catalogo import (
    crear_alimento,
    crear_ejercicio,
    modificar_alimento,
    modificar_ejercicio,
)

bitacora = logging.getLogger(__name__)

_VALORES_AFIRMATIVOS = {"si", "sí", "true", "1", "yes"}


def _texto_a_booleano(valor: str, predeterminado: bool) -> bool:
    """Interpreta la columna 'disponible'/'es_compuesto', tolerante a mayúsculas y acentos."""
    valor = (valor or "").strip().lower()
    if not valor:
        return predeterminado
    return valor in _VALORES_AFIRMATIVOS


def _numero_o_ninguno(valor: str) -> float | None:
    valor = (valor or "").strip()
    return None if not valor else float(valor)


def _fila_a_alimento(fila: dict[str, str]) -> AlimentoEntrada:
    return AlimentoEntrada(
        nombre=fila["nombre"],
        categoria=fila["categoria"].strip().lower(),
        energia_kcal_100g=float(fila["energia_kcal_100g"]),
        proteina_g_100g=float(fila["proteina_g_100g"]),
        carbohidrato_g_100g=float(fila["carbohidrato_g_100g"]),
        grasa_g_100g=float(fila["grasa_g_100g"]),
        costo_aproximado_quetzales=_numero_o_ninguno(fila.get("costo_aproximado_quetzales", "")),
        medida_casera=(fila.get("medida_casera") or "").strip() or None,
        disponible_localmente=_texto_a_booleano(fila.get("disponible", ""), predeterminado=True),
    )


def _fila_a_ejercicio(fila: dict[str, str]) -> EjercicioEntrada:
    return EjercicioEntrada(
        nombre=fila["nombre"],
        grupo_muscular=fila["grupo_muscular"].strip().lower(),
        nivel_minimo=(fila.get("nivel_minimo") or "principiante").strip().lower(),
        equipamiento=fila["equipamiento"],
        descripcion=(fila.get("descripcion") or "").strip() or None,
        es_compuesto=_texto_a_booleano(fila.get("es_compuesto", ""), predeterminado=False),
        disponible_localmente=_texto_a_booleano(fila.get("disponible", ""), predeterminado=True),
    )


def cargar_alimentos(ruta: Path) -> tuple[int, int, list[str]]:
    """Crea o actualiza alimentos desde el CSV. Devuelve (creados, actualizados, errores)."""
    creados = actualizados = 0
    errores: list[str] = []
    with FabricaSesiones() as sesion:
        existentes = {
            alimento.nombre.strip().lower(): alimento
            for alimento in sesion.execute(select(Alimento)).scalars()
        }
        with ruta.open(encoding="utf-8-sig", newline="") as archivo:
            for numero, fila in enumerate(csv.DictReader(archivo), start=2):
                if not (fila.get("nombre") or "").strip():
                    continue
                try:
                    datos = _fila_a_alimento(fila)
                except (ValidationError, ValueError, KeyError) as error:
                    errores.append(f"fila {numero} ({fila.get('nombre', '?')}): {error}")
                    continue

                existente = existentes.get(datos.nombre.strip().lower())
                if existente is None:
                    crear_alimento(sesion, datos)
                    creados += 1
                else:
                    modificar_alimento(sesion, existente.id, datos)
                    actualizados += 1
    return creados, actualizados, errores


def cargar_ejercicios(ruta: Path) -> tuple[int, int, list[str]]:
    """Crea o actualiza ejercicios desde el CSV. Devuelve (creados, actualizados, errores)."""
    creados = actualizados = 0
    errores: list[str] = []
    with FabricaSesiones() as sesion:
        existentes = {
            ejercicio.nombre.strip().lower(): ejercicio
            for ejercicio in sesion.execute(select(Ejercicio)).scalars()
        }
        with ruta.open(encoding="utf-8-sig", newline="") as archivo:
            for numero, fila in enumerate(csv.DictReader(archivo), start=2):
                if not (fila.get("nombre") or "").strip():
                    continue
                try:
                    datos = _fila_a_ejercicio(fila)
                except (ValidationError, ValueError, KeyError) as error:
                    errores.append(f"fila {numero} ({fila.get('nombre', '?')}): {error}")
                    continue

                existente = existentes.get(datos.nombre.strip().lower())
                if existente is None:
                    crear_ejercicio(sesion, datos)
                    creados += 1
                else:
                    modificar_ejercicio(sesion, existente.id, datos)
                    actualizados += 1
    return creados, actualizados, errores


def principal() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    analizador = argparse.ArgumentParser(
        description="Carga en el catálogo el resultado del levantamiento de campo (HU-11)."
    )
    analizador.add_argument("--alimentos", type=Path, help="Ruta al CSV de alimentos")
    analizador.add_argument("--ejercicios", type=Path, help="Ruta al CSV de ejercicios")
    argumentos = analizador.parse_args()

    if not argumentos.alimentos and not argumentos.ejercicios:
        analizador.error("indique --alimentos, --ejercicios o ambos")

    hubo_errores = False

    if argumentos.alimentos:
        if not argumentos.alimentos.exists():
            bitacora.error("No se encontró el archivo %s", argumentos.alimentos)
            return 1
        creados, actualizados, errores = cargar_alimentos(argumentos.alimentos)
        bitacora.info(
            "Alimentos: %d creados, %d actualizados, %d con error.",
            creados, actualizados, len(errores),
        )
        for error in errores:
            bitacora.error("  - %s", error)
        hubo_errores = hubo_errores or bool(errores)

    if argumentos.ejercicios:
        if not argumentos.ejercicios.exists():
            bitacora.error("No se encontró el archivo %s", argumentos.ejercicios)
            return 1
        creados, actualizados, errores = cargar_ejercicios(argumentos.ejercicios)
        bitacora.info(
            "Ejercicios: %d creados, %d actualizados, %d con error.",
            creados, actualizados, len(errores),
        )
        for error in errores:
            bitacora.error("  - %s", error)
        hubo_errores = hubo_errores or bool(errores)

    return 1 if hubo_errores else 0


if __name__ == "__main__":
    sys.exit(principal())
