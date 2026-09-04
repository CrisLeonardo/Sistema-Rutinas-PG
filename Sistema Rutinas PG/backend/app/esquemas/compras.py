"""Contratos de la lista de compras semanal.

El menu diario de la historia HU-08 dice que comer en cada tiempo, pero nadie
va al mercado con un menu de cinco tiempos en la mano: hay que sumar cuanto se
necesita de cada alimento en la semana y agruparlo por el puesto donde se
compra. Esa suma es lo que este contrato entrega.

No corresponde a ninguna historia de la pila de producto. Se agrega porque el
estudio de campo del Capitulo I encontro que la barrera principal declarada es
economica, y un plan cuyo costo el usuario descubre recien frente al puesto no
resuelve esa barrera: la traslada.
"""

from datetime import datetime

from pydantic import BaseModel, computed_field

from app.esquemas.catalogo import NOMBRES_CATEGORIA
from app.modelos.enumeraciones import CategoriaAlimento

DIAS_DE_LA_SEMANA = 7

# Cantidad a partir de la cual conviene expresar la compra en libras, que es la
# unidad con que se vende en los mercados del municipio.
GRAMOS_POR_LIBRA = 454
GRAMOS_PARA_EXPRESAR_EN_LIBRAS = 300


class RenglonDeCompra(BaseModel):
    """Un alimento con la cantidad que hace falta comprar para la semana."""

    alimento_id: int
    nombre: str
    categoria: CategoriaAlimento
    gramos_semana: int
    costo_quetzales: float | None = None
    medida_casera: str | None = None

    @computed_field(description="Nombre legible de la categoría")
    @property
    def nombre_categoria(self) -> str:
        return NOMBRES_CATEGORIA[self.categoria]

    @computed_field(description="Cantidad expresada como se pide en el mercado")
    @property
    def cantidad_de_mercado(self) -> str:
        """Traduce los gramos a la unidad con que se compra el alimento.

        En los mercados del municipio se pide por libras, no por gramos: pedir
        «1 815 gramos de pollo» no es una instruccion que alguien pueda seguir
        en un puesto.
        """
        if self.gramos_semana >= GRAMOS_PARA_EXPRESAR_EN_LIBRAS:
            libras = self.gramos_semana / GRAMOS_POR_LIBRA
            # Se redondea al cuarto de libra, que es como se despacha.
            libras = round(libras * 4) / 4
            if libras <= 0.25:
                return "1/4 de libra"
            if libras == 0.5:
                return "1/2 libra"
            if libras == 0.75:
                return "3/4 de libra"
            if libras == 1:
                return "1 libra"
            return f"{libras:g} libras"
        return f"{self.gramos_semana} gramos"


class GrupoDeCompra(BaseModel):
    """Los renglones de una misma categoria, que se compran en el mismo puesto."""

    categoria: CategoriaAlimento
    renglones: list[RenglonDeCompra]

    @computed_field(description="Nombre legible de la categoría")
    @property
    def nombre_categoria(self) -> str:
        return NOMBRES_CATEGORIA[self.categoria]

    @computed_field(description="Costo aproximado del grupo, en quetzales")
    @property
    def costo_quetzales(self) -> float:
        return round(sum(renglon.costo_quetzales or 0.0 for renglon in self.renglones), 2)


class ListaDeCompras(BaseModel):
    """Todo lo que el plan de la semana requiere comprar."""

    plan_id: int
    fecha_generacion: datetime
    dias: int = DIAS_DE_LA_SEMANA
    grupos: list[GrupoDeCompra]

    @computed_field(description="Costo aproximado de la semana completa, en quetzales")
    @property
    def costo_total_quetzales(self) -> float:
        return round(sum(grupo.costo_quetzales for grupo in self.grupos), 2)

    @computed_field(description="Costo aproximado de un mes de treinta días")
    @property
    def costo_mensual_quetzales(self) -> float:
        if not self.dias:
            return 0.0
        return round(self.costo_total_quetzales / self.dias * 30, 2)

    @computed_field(description="Cantidad de alimentos distintos que hay que comprar")
    @property
    def alimentos_distintos(self) -> int:
        return sum(len(grupo.renglones) for grupo in self.grupos)

    @computed_field(description="Renglones cuyo alimento no tiene precio registrado")
    @property
    def renglones_sin_precio(self) -> int:
        return sum(
            1
            for grupo in self.grupos
            for renglon in grupo.renglones
            if renglon.costo_quetzales is None
        )

    @computed_field(description="Advertencia sobre la exactitud del costo")
    @property
    def aviso_costo(self) -> str:
        if self.renglones_sin_precio:
            return (
                f"{self.renglones_sin_precio} de los alimentos de esta lista todavía no "
                "tienen precio registrado en el catálogo, de modo que el total mostrado "
                "se queda corto. Los precios son estimaciones del mercado local y varían "
                "con la temporada."
            )
        return (
            "Los precios son estimaciones del mercado local y varían con la temporada. "
            "Use el total como referencia para presupuestar, no como cuenta exacta."
        )
