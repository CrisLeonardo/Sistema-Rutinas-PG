"""Reexpresa el costo del catalogo en quetzales por cada 100 gramos.

Hasta ahora la columna `costo_aproximado_quetzales` no declaraba su unidad. La
instruccion del levantamiento de campo pedia «el precio observado en el mercado»,
de modo que el catalogo inicial quedo con unidades mezcladas: la tortilla a Q1.00
la pieza, el pollo a Q28.00 la libra, el aceite a Q2.00 el envase. Sumar esos
valores no producia ninguna cifra con sentido, y por eso el dato se capturaba, se
validaba, se editaba, y ningun modulo del sistema lo consultaba.

Ahora el costo se expresa por cada 100 gramos, igual que el aporte nutricional, y
el sistema lo usa para tres cosas: estimar lo que cuesta el menu, preferir el
alimento economico cuando existe uno equivalente, y armar la lista de compras.

Este script aplica la reexpresion a una base de datos que ya tenga el catalogo
cargado. El sembrado de arranque no sirve para esto: solo inserta los alimentos
que faltan y nunca modifica los existentes, precisamente para no deshacer lo que
el administrador corrija.

    uv run python actualizar_costos_del_catalogo.py            # muestra qué haría
    uv run python actualizar_costos_del_catalogo.py --aplicar  # lo aplica

**Solo se corrige el alimento cuyo costo siga siendo el sembrado originalmente.**
Un precio que el administrador ya haya corregido en el mercado se respeta y se
reporta aparte, para que se revise a mano: el script no puede saber en qué unidad
lo anotó quien lo escribió.
"""

import argparse
import logging
import sys

from sqlalchemy import select

from app.modelos.catalogo import Alimento
from app.nucleo.alimentos_iniciales import ALIMENTOS_INICIALES
from app.nucleo.base_datos import FabricaSesiones

bitacora = logging.getLogger(__name__)

# Costos que trajo el catalogo inicial antes de declararse la unidad. Se
# conservan aqui para reconocer que fila sigue con el valor sembrado y cual ya
# fue tocada por alguien.
COSTOS_ANTERIORES: dict[str, float] = {
    "Tortilla de maíz": 1.0,
    "Arroz blanco cocido": 3.0,
    "Pan francés": 1.5,
    "Avena en hojuelas": 12.0,
    "Incaparina en polvo": 14.0,
    "Pasta cocida": 6.0,
    "Pechuga de pollo": 28.0,
    "Huevo de gallina": 1.5,
    "Carne de res molida magra": 45.0,
    "Tilapia": 30.0,
    "Hígado de res": 25.0,
    "Frijol negro cocido": 4.0,
    "Lenteja cocida": 8.0,
    "Garbanzo cocido": 10.0,
    "Leche entera": 8.0,
    "Queso fresco": 35.0,
    "Yogur natural": 12.0,
    "Banano": 1.5,
    "Papaya": 5.0,
    "Mango": 3.0,
    "Naranja": 1.5,
    "Sandía": 4.0,
    "Güisquil": 2.0,
    "Tomate": 2.0,
    "Repollo": 3.0,
    "Zanahoria": 2.0,
    "Ejote": 5.0,
    "Espinaca": 6.0,
    "Aceite vegetal": 2.0,
    "Aguacate": 6.0,
    "Maní tostado": 10.0,
    "Semilla de marañón": 25.0,
    "Papa cocida": 3.0,
    "Camote cocido": 3.0,
    "Yuca cocida": 4.0,
    "Plátano macho cocido": 2.5,
}

COSTOS_POR_CIEN_GRAMOS: dict[str, float] = {
    nombre: costo for nombre, _, _, _, _, _, costo, _ in ALIMENTOS_INICIALES
}


def revisar(aplicar: bool) -> int:
    """Recorre el catalogo y reexpresa lo que siga con el costo sembrado."""
    corregidos: list[tuple[str, float, float]] = []
    respetados: list[tuple[str, float]] = []
    ausentes: list[str] = []

    with FabricaSesiones() as sesion:
        existentes = {
            alimento.nombre: alimento
            for alimento in sesion.execute(select(Alimento)).scalars()
        }

        for nombre, costo_nuevo in COSTOS_POR_CIEN_GRAMOS.items():
            alimento = existentes.get(nombre)
            if alimento is None:
                ausentes.append(nombre)
                continue

            actual = (
                float(alimento.costo_aproximado_quetzales)
                if alimento.costo_aproximado_quetzales is not None
                else None
            )
            anterior = COSTOS_ANTERIORES.get(nombre)

            if actual is not None and anterior is not None and abs(actual - anterior) < 0.005:
                corregidos.append((nombre, actual, costo_nuevo))
                if aplicar:
                    alimento.costo_aproximado_quetzales = costo_nuevo
            elif actual is not None and abs(actual - costo_nuevo) < 0.005:
                continue  # ya estaba reexpresado
            else:
                respetados.append((nombre, actual if actual is not None else 0.0))

        if aplicar and corregidos:
            sesion.commit()

    _informar(corregidos, respetados, ausentes, aplicar)
    return len(corregidos)


def _informar(corregidos, respetados, ausentes, aplicar) -> None:
    verbo = "Se reexpresaron" if aplicar else "Se reexpresarían"
    print(f"\n{verbo} {len(corregidos)} costos a quetzales por cada 100 gramos:\n")
    for nombre, antes, despues in corregidos:
        print(f"  {nombre:<30} Q{antes:>7.2f}  ->  Q{despues:>6.2f} / 100 g")

    if respetados:
        print(
            f"\n{len(respetados)} alimentos conservan un costo que alguien ya modificó. "
            "No se tocan: revíselos a mano y confirme en qué unidad están anotados.\n"
        )
        for nombre, actual in respetados:
            print(f"  {nombre:<30} Q{actual:>7.2f}  (sin cambio)")

    if ausentes:
        print(f"\n{len(ausentes)} alimentos del catálogo inicial no están en la base de datos.")

    if not aplicar and corregidos:
        print(
            "\nNada se ha modificado. Vuelva a ejecutar con «--aplicar» para guardar "
            "los cambios."
        )


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument(
        "--aplicar",
        action="store_true",
        help="Guarda los cambios. Sin esta opción solo se muestra lo que haría.",
    )
    argumentos = analizador.parse_args()

    corregidos = revisar(argumentos.aplicar)
    if argumentos.aplicar:
        print(f"\nListo. {corregidos} alimentos actualizados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
