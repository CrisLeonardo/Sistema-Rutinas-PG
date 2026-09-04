"""Contratos de salida del menu diario (historia HU-08)."""

from datetime import datetime

from pydantic import BaseModel, computed_field

from app.esquemas.catalogo import NOMBRES_CATEGORIA
from app.modelos.enumeraciones import CategoriaAlimento


class SustitutoPublico(BaseModel):
    """Alternativa de aporte nutricional equivalente (criterio de HU-08)."""

    alimento_id: int
    nombre: str
    gramos: int
    medida_casera: str | None = None


class PorcionPublica(BaseModel):
    """Cantidad de un alimento dentro de un tiempo de comida."""

    alimento_id: int
    nombre: str
    categoria: CategoriaAlimento
    gramos: int
    energia_kcal: int
    proteina_g: int
    carbohidrato_g: int
    grasa_g: int
    medida_casera: str | None = None
    costo_quetzales: float | None = None
    sustituto: SustitutoPublico | None = None

    @computed_field(description="Nombre legible de la categoría")
    @property
    def nombre_categoria(self) -> str:
        return NOMBRES_CATEGORIA[self.categoria]

    @computed_field(description="Cantidad expresada en medida casera aproximada")
    @property
    def cantidad_en_medida_casera(self) -> str | None:
        """Traduce los gramos a la medida casera del alimento.

        El criterio de aceptacion de la historia HU-08 pide presentar tambien las
        cantidades en medidas caseras, porque la mayoria de los hogares del
        municipio no dispone de bascula de cocina.
        """
        if not self.medida_casera:
            return None

        # La medida casera se registra como «1 taza ≈ 160 g»: de ahí se extrae
        # el peso de referencia para calcular cuántas de esas medidas equivalen
        # a la porción propuesta.
        separador = "≈"
        if separador not in self.medida_casera:
            return self.medida_casera

        descripcion, peso = self.medida_casera.split(separador, 1)
        digitos = "".join(caracter for caracter in peso if caracter.isdigit())
        if not digitos:
            return self.medida_casera

        gramos_por_medida = int(digitos)
        if gramos_por_medida <= 0:
            return self.medida_casera

        cantidad = self.gramos / gramos_por_medida
        unidad = descripcion.strip()

        # Se retira la cantidad con que se registró la medida: aquí la sustituye
        # la que corresponde a esta porción.
        if unidad.startswith("1/2 "):
            unidad = unidad[4:]
            cantidad = cantidad / 2
        elif unidad.startswith("1 "):
            unidad = unidad[2:]

        # Se redondea a la media unidad más cercana: nadie sirve 1.37 tazas.
        cantidad = round(cantidad * 2) / 2

        if cantidad <= 0:
            return f"menos de media {unidad}"
        if cantidad == 0.5:
            return f"{_articulo_medio(unidad)} {unidad}"
        if cantidad == 1:
            return f"1 {unidad}"
        return f"{cantidad:g} {pluralizar(unidad)}"


class TiempoComidaPublico(BaseModel):
    """Un tiempo de comida con sus porciones."""

    nombre: str
    porciones: list[PorcionPublica]

    @computed_field(description="Energía total del tiempo de comida")
    @property
    def energia_kcal(self) -> int:
        return sum(porcion.energia_kcal for porcion in self.porciones)

    @computed_field(description="Proteína total del tiempo de comida")
    @property
    def proteina_g(self) -> int:
        return sum(porcion.proteina_g for porcion in self.porciones)

    @computed_field(description="Costo aproximado del tiempo de comida, en quetzales")
    @property
    def costo_quetzales(self) -> float:
        return round(sum(porcion.costo_quetzales or 0.0 for porcion in self.porciones), 2)


class MenuPublico(BaseModel):
    """Menu diario asociado al plan vigente (historia HU-08)."""

    plan_id: int
    fecha_generacion: datetime
    activo: bool
    energia_objetivo_kcal: float
    proteina_objetivo_g: float
    tiempos: list[TiempoComidaPublico]

    @computed_field(description="Energía que suman todos los tiempos de comida")
    @property
    def energia_kcal(self) -> int:
        return sum(tiempo.energia_kcal for tiempo in self.tiempos)

    @computed_field(description="Proteína que suman todos los tiempos de comida")
    @property
    def proteina_g(self) -> int:
        return sum(tiempo.proteina_g for tiempo in self.tiempos)

    @computed_field(description="Costo aproximado del día completo, en quetzales")
    @property
    def costo_diario_quetzales(self) -> float:
        """Costo del menu de un dia, con los precios vigentes del catalogo.

        Es una estimacion: los precios del catalogo se levantan en el mercado y
        varian con la temporada. Los alimentos sin precio registrado suman cero,
        de modo que la cifra es un piso y no un techo.
        """
        return round(sum(tiempo.costo_quetzales for tiempo in self.tiempos), 2)

    @computed_field(description="Costo aproximado de una semana completa, en quetzales")
    @property
    def costo_semanal_quetzales(self) -> float:
        return round(self.costo_diario_quetzales * 7, 2)

    @computed_field(description="Costo aproximado de un mes de treinta días, en quetzales")
    @property
    def costo_mensual_quetzales(self) -> float:
        """Cifra con la que el usuario puede decidir si el plan le es asequible.

        El estudio de campo del Capitulo I encontro que buena parte de la
        poblacion no puede destinar mas de Q200 mensuales a este fin: sin esta
        cifra, el plan propone una alimentacion cuyo costo el usuario descubre
        recien en el mercado.
        """
        return round(self.costo_diario_quetzales * 30, 2)

    @computed_field(description="Porciones cuyo alimento no tiene precio registrado")
    @property
    def porciones_sin_precio(self) -> int:
        return sum(
            1
            for tiempo in self.tiempos
            for porcion in tiempo.porciones
            if porcion.costo_quetzales is None
        )

    @computed_field(description="Diferencia porcentual entre el menú y el plan")
    @property
    def desviacion_energia_porcentaje(self) -> float:
        if not self.energia_objetivo_kcal:
            return 0.0
        return round(
            100 * abs(self.energia_kcal - self.energia_objetivo_kcal)
            / self.energia_objetivo_kcal,
            1,
        )

    @computed_field(description="Cantidad de alimentos distintos que propone el menú")
    @property
    def alimentos_distintos(self) -> int:
        return len(
            {porcion.alimento_id for tiempo in self.tiempos for porcion in tiempo.porciones}
        )


# Palabras que introducen un complemento y no se pluralizan: en «taza en cubos»
# el plural afecta a «taza», no a «cubos».
_PREPOSICIONES = {"en", "de", "con", "para", "por", "a", "sin"}


def _es_femenina(palabra: str) -> bool:
    """Heuristica de genero para las unidades de medida casera.

    Cubre las terminaciones que aparecen en el catalogo: taza, unidad, porcion,
    cucharada y rebanada son femeninas; pan, puno, filete, vaso y huevo,
    masculinos.
    """
    limpia = palabra.lower()
    return limpia.endswith(("a", "ión", "ion", "ad", "umbre"))


def _articulo_medio(unidad: str) -> str:
    """Devuelve «media» o «medio» segun el genero de la unidad."""
    primera = unidad.split()[0] if unidad.split() else unidad
    return "media" if _es_femenina(primera) else "medio"


def pluralizar(unidad: str) -> str:
    """Pone en plural la unidad de medida, respetando su complemento.

    Se pluralizan las palabras hasta la primera preposicion: «unidad mediana»
    pasa a «unidades medianas», pero «taza en cubos» pasa a «tazas en cubos».
    """
    palabras = unidad.split()
    if not palabras:
        return unidad

    resultado: list[str] = []
    pluralizando = True
    for palabra in palabras:
        if palabra.lower() in _PREPOSICIONES:
            pluralizando = False
        if pluralizando:
            resultado.append(_plural_de(palabra))
        else:
            resultado.append(palabra)
    return " ".join(resultado)


def _plural_de(palabra: str) -> str:
    """Forma el plural de una palabra en espanol, para los casos del catalogo."""
    if not palabra:
        return palabra
    if palabra.endswith("ión"):
        # porción -> porciones: se sustituyen la vocal acentuada y la ene
        # finales por «ones», que es donde recae el acento en el plural.
        return palabra[:-2] + "ones"
    if palabra[-1] in "aeiouáéíóú":
        return palabra + "s"
    if palabra.endswith("z"):
        return palabra[:-1] + "ces"
    return palabra + "es"
