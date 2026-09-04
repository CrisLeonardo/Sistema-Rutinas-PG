"""Distribucion del plan en tiempos de comida (historia HU-08).

El criterio de aceptacion exige tres cosas: que todos los alimentos propuestos
existan en el catalogo local, que las cantidades se presenten tambien en medidas
caseras, y que el sistema ofrezca un sustituto de aporte nutricional equivalente
cuando un alimento no este disponible.

Como el resto del paquete `motor`, no depende de la base de datos: recibe la
lista de alimentos disponibles y devuelve el menu ya armado, de modo que su
logica pueda verificarse por separado.

El reparto no busca el optimo matematico. Sigue la estructura de comidas
habitual del municipio —desayuno, refaccion, almuerzo, refaccion y cena— y
asigna a cada tiempo una porcion del requerimiento diario, cubriendo primero la
proteina, que es la que la regla del negocio *c* fija con menos holgura.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from app.modelos.enumeraciones import CategoriaAlimento

# Proporcion del requerimiento diario que corresponde a cada tiempo de comida.
# Suman uno. El almuerzo concentra la mayor parte porque es la comida principal
# en el municipio.
TIEMPOS_DE_COMIDA: tuple[tuple[str, float], ...] = (
    ("Desayuno", 0.25),
    ("Refacción de la mañana", 0.10),
    ("Almuerzo", 0.35),
    ("Refacción de la tarde", 0.10),
    ("Cena", 0.20),
)

# Categorias que aportan sobre todo cada macronutriente. Se usan para elegir con
# que alimento cubrir cada parte del reparto.
CATEGORIAS_PROTEICAS = (
    CategoriaAlimento.PROTEINA_ANIMAL,
    CategoriaAlimento.LEGUMINOSA,
    CategoriaAlimento.LACTEO,
)
CATEGORIAS_ENERGETICAS = (
    CategoriaAlimento.CEREAL,
    CategoriaAlimento.TUBERCULO,
)
CATEGORIAS_GRASAS = (CategoriaAlimento.GRASA,)
CATEGORIAS_FRESCAS = (
    CategoriaAlimento.VERDURA,
    CategoriaAlimento.FRUTA,
)

# Estructura de cada tiempo: que tipo de alimento lo compone. La cena prescinde
# del tuberculo pesado, por costumbre local.
#
# Las dos refacciones llevan componente energetico —el pan, la tortilla o el
# platano que acompanan a la fruta— y no solo fruta suelta. Sin el, cada
# refaccion entregaba la mitad de la energia que le correspondia y las comidas
# principales tenian que absorber ese faltante: en un plan de 3 500 kilocalorias
# el cereal del almuerzo llegaba a su porcion maxima y el menu se quedaba 300
# kilocalorias corto. Ademas, una refaccion de solo fruta no es la que se come
# en el municipio.
COMPOSICION_POR_TIEMPO: dict[str, tuple[tuple[CategoriaAlimento, ...], ...]] = {
    "Desayuno": (CATEGORIAS_PROTEICAS, CATEGORIAS_ENERGETICAS, CATEGORIAS_FRESCAS),
    "Refacción de la mañana": (
        CATEGORIAS_FRESCAS,
        CATEGORIAS_PROTEICAS,
        CATEGORIAS_ENERGETICAS,
    ),
    "Almuerzo": (
        CATEGORIAS_PROTEICAS,
        CATEGORIAS_ENERGETICAS,
        CATEGORIAS_FRESCAS,
        CATEGORIAS_GRASAS,
    ),
    "Refacción de la tarde": (
        CATEGORIAS_FRESCAS,
        CATEGORIAS_GRASAS,
        CATEGORIAS_ENERGETICAS,
    ),
    "Cena": (CATEGORIAS_PROTEICAS, CATEGORIAS_FRESCAS, CATEGORIAS_ENERGETICAS),
}

# Limites de la porcion de un mismo alimento, en gramos. Sirven para que el
# reparto no proponga cantidades impracticables, como veinte gramos de tortilla
# o un kilo de pollo.
PORCION_MINIMA_G = 20
PORCION_MAXIMA_G = 400
# Los alimentos muy densos —el aceite, sobre todo— necesitan un tope propio.
PORCION_MAXIMA_GRASA_G = 30

# Las verduras y las frutas no se dimensionan por energía. Aportan muy pocas
# kilocalorías por gramo, de modo que pedirles cubrir una parte del
# requerimiento produce porciones impracticables: cuatrocientos gramos de
# repollo en un tiempo de comida. Se sirven en porciones fijas y razonables, y
# la energía la cubren los cereales, los tubérculos y las grasas.
PORCION_VERDURA_G = 150
PORCION_FRUTA_G = 150

# Proporción de la energía de cada tiempo que se cubre con grasa añadida.
PROPORCION_GRASA_POR_TIEMPO = 0.15

# Proporción de la energía de un tiempo de comida que puede ocupar su alimento
# proteico. El resto queda para la verdura, la grasa añadida y el cereal, que
# son los que completan el plato: sin este tope, el alimento proteico se comía
# el tiempo entero y el menú desbordaba la energía del plan.
PROPORCION_MAXIMA_PROTEICA_POR_TIEMPO = 0.55

# Tolerancia con que se da por cerrado el ajuste final de energía.
TOLERANCIA_ENERGIA = 0.03

# Pasadas del ajuste final. Cada una reparte el faltante solo entre las porciones
# que todavía admiten crecer o menguar, de modo que lo que una porción topada no
# puede absorber lo recoja otra en la pasada siguiente.
PASADAS_DE_AJUSTE = 6

# Cantidad de alimentos a partir de la cual se considera que el catalogo permite
# armar un menu con variedad suficiente.
MINIMO_ALIMENTOS_PARA_MENU = 8

# Proporcion de los candidatos de cada categoria que entra en la rotacion, una
# vez ordenados del mas economico al mas caro por unidad de lo que aportan.
#
# Sin este filtro el reparto rota por todos los alimentos de la categoria por
# igual, y la semilla de maranon —a Q13.20 los 100 gramos— aparece tantas veces
# como el mani, que cumple la misma funcion a la cuarta parte del precio. El
# estudio de campo del Capitulo I encontro que la barrera declarada con mas
# frecuencia es economica: proponer el alimento caro cuando existe el barato
# equivalente es proponer un plan que el usuario no va a sostener.
PROPORCION_CANDIDATOS_ECONOMICOS = 0.5

# Nunca se rota sobre menos de esta cantidad de alimentos por categoria: la
# variedad tambien sostiene la adherencia, y un menu de un solo alimento por
# categoria se abandona por aburrimiento antes que por precio.
MINIMO_CANDIDATOS_EN_ROTACION = 3


@dataclass(frozen=True)
class AlimentoDisponible:
    """Alimento del catalogo, en la forma minima que el generador necesita."""

    id: int
    nombre: str
    categoria: CategoriaAlimento
    energia_kcal_100g: float
    proteina_g_100g: float
    carbohidrato_g_100g: float
    grasa_g_100g: float
    medida_casera: str | None = None
    # Quetzales por cada 100 gramos, igual que el aporte nutricional. Es None
    # mientras el levantamiento de campo no registre el precio del alimento.
    costo_quetzales_100g: float | None = None

    def energia_de(self, gramos: float) -> float:
        return self.energia_kcal_100g * gramos / 100

    def costo_de(self, gramos: float) -> float | None:
        """Costo de la porcion, o None si el alimento no tiene precio registrado."""
        if self.costo_quetzales_100g is None:
            return None
        return self.costo_quetzales_100g * gramos / 100

    def proteina_de(self, gramos: float) -> float:
        return self.proteina_g_100g * gramos / 100

    def carbohidrato_de(self, gramos: float) -> float:
        return self.carbohidrato_g_100g * gramos / 100

    def grasa_de(self, gramos: float) -> float:
        return self.grasa_g_100g * gramos / 100


@dataclass(frozen=True)
class PorcionPropuesta:
    """Cantidad concreta de un alimento dentro de un tiempo de comida."""

    alimento_id: int
    nombre: str
    categoria: CategoriaAlimento
    gramos: int
    energia_kcal: int
    proteina_g: int
    carbohidrato_g: int
    grasa_g: int
    medida_casera: str | None
    costo_quetzales: float | None = None
    sustituto: "PorcionPropuesta | None" = None


@dataclass(frozen=True)
class TiempoComida:
    """Un tiempo de comida con las porciones que lo componen."""

    nombre: str
    proporcion: float
    porciones: list[PorcionPropuesta] = field(default_factory=list)

    @property
    def energia_kcal(self) -> int:
        return sum(porcion.energia_kcal for porcion in self.porciones)

    @property
    def proteina_g(self) -> int:
        return sum(porcion.proteina_g for porcion in self.porciones)

    @property
    def costo_quetzales(self) -> float:
        """Costo del tiempo de comida. Los alimentos sin precio suman cero."""
        return round(
            sum(porcion.costo_quetzales or 0.0 for porcion in self.porciones), 2
        )


@dataclass(frozen=True)
class MenuDiario:
    """Reparto del plan nutricional en los tiempos de comida del dia."""

    tiempos: list[TiempoComida]
    energia_objetivo_kcal: float
    proteina_objetivo_g: float

    @property
    def energia_kcal(self) -> int:
        return sum(tiempo.energia_kcal for tiempo in self.tiempos)

    @property
    def proteina_g(self) -> int:
        return sum(tiempo.proteina_g for tiempo in self.tiempos)

    @property
    def costo_quetzales(self) -> float:
        """Costo aproximado del dia completo, en quetzales."""
        return round(sum(tiempo.costo_quetzales for tiempo in self.tiempos), 2)

    @property
    def desviacion_energia(self) -> float:
        """Diferencia relativa entre la energia del menu y la del plan."""
        if not self.energia_objetivo_kcal:
            return 0.0
        return abs(self.energia_kcal - self.energia_objetivo_kcal) / self.energia_objetivo_kcal


class CatalogoDeAlimentosInsuficiente(Exception):
    """El catalogo no tiene alimentos suficientes para armar un menu."""


def _porcion_maxima(alimento: AlimentoDisponible) -> int:
    """Tope de gramos para un alimento, segun su densidad energetica."""
    if alimento.categoria == CategoriaAlimento.GRASA:
        return PORCION_MAXIMA_GRASA_G
    return PORCION_MAXIMA_G


def _gramos_para_energia(alimento: AlimentoDisponible, energia_kcal: float) -> int:
    """Gramos del alimento que aportan la energia pedida, dentro de sus topes."""
    if alimento.energia_kcal_100g <= 0:
        return PORCION_MINIMA_G
    gramos = energia_kcal * 100 / alimento.energia_kcal_100g
    return int(min(max(round(gramos / 5) * 5, PORCION_MINIMA_G), _porcion_maxima(alimento)))


def _construir_porcion(
    alimento: AlimentoDisponible, gramos: int, sustituto: PorcionPropuesta | None = None
) -> PorcionPropuesta:
    """Arma la porcion con sus aportes ya calculados y redondeados."""
    return PorcionPropuesta(
        alimento_id=alimento.id,
        nombre=alimento.nombre,
        categoria=alimento.categoria,
        gramos=gramos,
        energia_kcal=round(alimento.energia_de(gramos)),
        proteina_g=round(alimento.proteina_de(gramos)),
        carbohidrato_g=round(alimento.carbohidrato_de(gramos)),
        grasa_g=round(alimento.grasa_de(gramos)),
        medida_casera=alimento.medida_casera,
        costo_quetzales=alimento.costo_de(gramos),
        sustituto=sustituto,
    )


def buscar_sustituto(
    alimento: AlimentoDisponible,
    gramos: int,
    disponibles: list[AlimentoDisponible],
) -> PorcionPropuesta | None:
    """Encuentra el alimento de aporte nutricional mas parecido.

    Criterio de aceptacion de la historia HU-08: si un alimento no esta
    disponible, el sistema ofrece un sustituto con aporte nutricional
    equivalente. Se compara el perfil por cada 100 gramos —energia, proteina,
    carbohidrato y grasa— y se elige el mas cercano de la misma categoria; si la
    categoria no tiene otro, se busca en el resto del catalogo.
    """
    del_mismo_grupo = [
        candidato
        for candidato in disponibles
        if candidato.id != alimento.id and candidato.categoria == alimento.categoria
    ]
    universo = del_mismo_grupo or [
        candidato for candidato in disponibles if candidato.id != alimento.id
    ]
    if not universo:
        return None

    def distancia(candidato: AlimentoDisponible) -> float:
        # La energia se escala para que pese lo mismo que los macronutrientes:
        # sin escalarla, una diferencia de 200 kcal opacaria por completo una
        # diferencia de 10 gramos de proteina.
        return (
            abs(candidato.energia_kcal_100g - alimento.energia_kcal_100g) / 10
            + abs(candidato.proteina_g_100g - alimento.proteina_g_100g)
            + abs(candidato.carbohidrato_g_100g - alimento.carbohidrato_g_100g)
            + abs(candidato.grasa_g_100g - alimento.grasa_g_100g)
        )

    elegido = min(universo, key=distancia)
    energia_original = alimento.energia_de(gramos)
    return _construir_porcion(elegido, _gramos_para_energia(elegido, energia_original))


def _gramos_para_proteina(
    alimento: AlimentoDisponible,
    proteina_g: float,
    energia_disponible_kcal: float | None = None,
) -> int:
    """Gramos del alimento que aportan la proteina pedida, dentro de sus topes.

    Cuando se indica la energia disponible del tiempo de comida, la porcion se
    acota tambien por ella. Sin ese tope, un alimento proteico poco denso
    desbordaba el tiempo entero: el garbanzo cocido aporta 8.9 gramos de
    proteina por cada 100, de modo que cubrir 35 gramos exigia 395 gramos de
    garbanzo, que arrastran 648 kilocalorias cuando el almuerzo disponia de 631.

    El efecto se concentraba justamente en los planes de perdida de grasa, que
    son los que combinan poca energia con mucha proteina y los que declara la
    mayoria de los usuarios: el menu de un plan de 1 200 kilocalorias entregaba
    1 783, un 48 % de mas.
    """
    if alimento.proteina_g_100g <= 0:
        return PORCION_MINIMA_G

    gramos = proteina_g * 100 / alimento.proteina_g_100g

    if energia_disponible_kcal is not None and alimento.energia_kcal_100g > 0:
        gramos_que_caben = energia_disponible_kcal * 100 / alimento.energia_kcal_100g
        gramos = min(gramos, gramos_que_caben)

    return int(min(max(round(gramos / 5) * 5, PORCION_MINIMA_G), _porcion_maxima(alimento)))


def energia_por_gramo_de_proteina(alimento: AlimentoDisponible) -> float:
    """Kilocalorias que arrastra cada gramo de proteina del alimento.

    Es la medida con que se decide si un alimento proteico cabe en el tiempo de
    comida: el pollo entrega proteina a 5.3 kilocalorias el gramo y el garbanzo
    a 18.4, de modo que cubrir la misma proteina con garbanzo cuesta el triple
    de energia.
    """
    if alimento.proteina_g_100g <= 0:
        return float("inf")
    return alimento.energia_kcal_100g / alimento.proteina_g_100g


def costo_por_unidad_aportada(
    alimento: AlimentoDisponible, categorias: tuple[CategoriaAlimento, ...]
) -> float | None:
    """Cuanto cuesta lo que el alimento aporta en el papel que va a cumplir.

    Un alimento no es caro o barato en abstracto, sino en relacion con aquello
    por lo que se le incluye: el pollo se compra por su proteina y la tortilla
    por su energia. Comparar ambos por el precio del kilogramo diria que la
    tortilla es mas barata sin decir nada util, porque no cumplen la misma
    funcion dentro del tiempo de comida.

    Devuelve None cuando el alimento todavia no tiene precio registrado.
    """
    if alimento.costo_quetzales_100g is None:
        return None

    if categorias == CATEGORIAS_PROTEICAS:
        if alimento.proteina_g_100g <= 0:
            return None
        return alimento.costo_quetzales_100g / alimento.proteina_g_100g

    if categorias in (CATEGORIAS_ENERGETICAS, CATEGORIAS_GRASAS):
        if alimento.energia_kcal_100g <= 0:
            return None
        return alimento.costo_quetzales_100g / alimento.energia_kcal_100g

    # Las verduras y las frutas se sirven en porcion fija, de modo que lo que
    # cuenta es el precio de esa porcion y no su densidad de nada.
    return alimento.costo_quetzales_100g


def candidatos_economicos(
    candidatos: list[AlimentoDisponible], categorias: tuple[CategoriaAlimento, ...]
) -> list[AlimentoDisponible]:
    """Reduce la rotacion a la mitad mas economica de la categoria.

    Conserva el orden original dentro de los elegidos, de modo que el menu siga
    siendo el mismo para el mismo perfil. Los alimentos sin precio registrado se
    conservan: excluirlos castigaria al catalogo por estar incompleto, que es
    justo lo que el levantamiento de campo esta pendiente de resolver.
    """
    if len(candidatos) <= MINIMO_CANDIDATOS_EN_ROTACION:
        return candidatos

    con_precio = [
        (alimento, costo_por_unidad_aportada(alimento, categorias))
        for alimento in candidatos
    ]
    sin_precio = [alimento for alimento, costo in con_precio if costo is None]
    tasados = [(alimento, costo) for alimento, costo in con_precio if costo is not None]
    if not tasados:
        return candidatos

    cuantos = max(
        round(len(candidatos) * PROPORCION_CANDIDATOS_ECONOMICOS),
        MINIMO_CANDIDATOS_EN_ROTACION,
    )
    economicos = {
        id(alimento)
        for alimento, _ in sorted(tasados, key=lambda par: par[1])[: cuantos - len(sin_precio)]
    }
    elegidos = [
        alimento
        for alimento in candidatos
        if id(alimento) in economicos or alimento in sin_precio
    ]
    return elegidos or candidatos


def _porcion_fija(alimento: AlimentoDisponible) -> int:
    """Porcion habitual de una verdura o una fruta, en gramos."""
    if alimento.categoria == CategoriaAlimento.VERDURA:
        return PORCION_VERDURA_G
    return PORCION_FRUTA_G


def _ajustar_energia(
    tiempos: list[TiempoComida],
    energia_objetivo: float,
    disponibles: list[AlimentoDisponible],
) -> list[TiempoComida]:
    """Corrige la energia del menu escalando sus componentes energeticos.

    Los redondeos a multiplos de cinco gramos y los topes de porcion dejan una
    diferencia entre la energia del menu y la del plan. Aqui se reparte esa
    diferencia entre los cereales y los tuberculos, que son los alimentos cuya
    porcion admite variar sin volverse impracticable, y no entre la proteina,
    que la regla del negocio *c* fija con poca holgura.
    """
    if energia_objetivo <= 0:
        return tiempos

    ajustables = [
        (indice_tiempo, indice_porcion)
        for indice_tiempo, tiempo in enumerate(tiempos)
        for indice_porcion, porcion in enumerate(tiempo.porciones)
        if porcion.categoria in CATEGORIAS_ENERGETICAS
    ]
    if not ajustables:
        return tiempos

    por_nombre = {alimento.nombre: alimento for alimento in disponibles}
    corregidos = [
        TiempoComida(
            nombre=tiempo.nombre,
            proporcion=tiempo.proporcion,
            porciones=list(tiempo.porciones),
        )
        for tiempo in tiempos
    ]

    # Se ajusta en varias pasadas. Con una sola, las porciones que topan en su
    # limite se llevan una parte de la correccion que no pueden absorber, y esa
    # parte se pierde: el menu queda descuadrado sin que nada lo intente de
    # nuevo. En cada pasada se recalcula el faltante y se reparte entre las
    # porciones que todavia tienen margen.
    for _ in range(PASADAS_DE_AJUSTE):
        energia_actual = sum(tiempo.energia_kcal for tiempo in corregidos)
        diferencia = energia_objetivo - energia_actual
        if abs(diferencia) / energia_objetivo <= TOLERANCIA_ENERGIA:
            break

        con_margen = []
        for indice_tiempo, indice_porcion in ajustables:
            porcion = corregidos[indice_tiempo].porciones[indice_porcion]
            alimento = por_nombre.get(porcion.nombre)
            if alimento is None or alimento.energia_kcal_100g <= 0:
                continue
            tope = _porcion_maxima(alimento)
            crece = diferencia > 0 and porcion.gramos < tope
            mengua = diferencia < 0 and porcion.gramos > PORCION_MINIMA_G
            if crece or mengua:
                con_margen.append((indice_tiempo, indice_porcion, alimento))

        if not con_margen:
            break

        energia_por_porcion = diferencia / len(con_margen)
        for indice_tiempo, indice_porcion, alimento in con_margen:
            porcion = corregidos[indice_tiempo].porciones[indice_porcion]
            gramos_extra = energia_por_porcion * 100 / alimento.energia_kcal_100g
            gramos = int(
                min(
                    max(round((porcion.gramos + gramos_extra) / 5) * 5, PORCION_MINIMA_G),
                    _porcion_maxima(alimento),
                )
            )
            corregidos[indice_tiempo].porciones[indice_porcion] = _construir_porcion(
                alimento, gramos, porcion.sustituto
            )

    return corregidos


def generar_menu(
    energia_kcal: float,
    proteina_g: float,
    disponibles: list[AlimentoDisponible],
) -> MenuDiario:
    """Reparte el plan del dia entre los tiempos de comida (historia HU-08).

    El reparto sigue el orden en que los macronutrientes admiten menos holgura:

    1. La proteina de cada tiempo dimensiona su alimento proteico, porque es la
       que la regla del negocio *c* acota entre 1.6 y 2.2 gramos por kilogramo.
    2. Las verduras y las frutas se sirven en porciones fijas, no por energia:
       aportan muy pocas kilocalorias por gramo y pedirles cubrir parte del
       requerimiento produciria porciones impracticables.
    3. La grasa anadida cubre una fraccion pequena y acotada de cada tiempo.
    4. Los cereales y los tuberculos absorben la energia que queda, y son
       tambien los que el ajuste final escala para cerrar la diferencia.

    Todos los alimentos propuestos provienen de la lista recibida, que el
    servicio construye filtrando por disponibilidad local: por construccion,
    ninguna propuesta puede salirse del catalogo.
    """
    if len(disponibles) < MINIMO_ALIMENTOS_PARA_MENU:
        raise CatalogoDeAlimentosInsuficiente(
            "El catálogo local no tiene alimentos suficientes para armar un menú."
        )

    por_categoria: dict[CategoriaAlimento, list[AlimentoDisponible]] = {}
    for alimento in disponibles:
        por_categoria.setdefault(alimento.categoria, []).append(alimento)

    tiempos_con_proteina = [
        (nombre, proporcion)
        for nombre, proporcion in TIEMPOS_DE_COMIDA
        if CATEGORIAS_PROTEICAS in COMPOSICION_POR_TIEMPO[nombre]
    ]
    peso_proteico = sum(proporcion for _, proporcion in tiempos_con_proteina) or 1.0

    # El desplazamiento hace que los tiempos no repitan siempre el mismo
    # alimento de cada categoría, sin introducir aleatoriedad: el mismo perfil
    # produce siempre el mismo menú, lo que hace el plan auditable.
    desplazamiento = 0
    tiempos: list[TiempoComida] = []

    for nombre_tiempo, proporcion in TIEMPOS_DE_COMIDA:
        energia_del_tiempo = energia_kcal * proporcion
        composicion = COMPOSICION_POR_TIEMPO[nombre_tiempo]
        porciones: list[PorcionPropuesta] = []
        energia_asignada = 0.0

        def elegir(
            categorias: tuple[CategoriaAlimento, ...],
            cabe: "Callable[[AlimentoDisponible], bool] | None" = None,
        ) -> AlimentoDisponible | None:
            """Toma el siguiente alimento de la rotacion que cumpla la condicion.

            La rotacion es la que da variedad al menu: se avanza una posicion en
            cada eleccion, de modo que los tiempos no repitan el mismo alimento.
            Cuando se indica una condicion, se recorre la rotacion desde esa
            posicion y se toma el primero que la cumpla; si ninguno la cumple, se
            devuelve el de la posicion original y el ajuste posterior se encarga.
            """
            nonlocal desplazamiento
            candidatos = [
                alimento
                for categoria in categorias
                for alimento in por_categoria.get(categoria, [])
            ]
            if not candidatos:
                return None

            en_rotacion = candidatos_economicos(candidatos, categorias)
            inicio = desplazamiento % len(en_rotacion)
            desplazamiento += 1

            if cabe is None:
                return en_rotacion[inicio]

            for salto in range(len(en_rotacion)):
                candidato = en_rotacion[(inicio + salto) % len(en_rotacion)]
                if cabe(candidato):
                    return candidato
            return en_rotacion[inicio]

        def agregar(alimento: AlimentoDisponible, gramos: int) -> None:
            nonlocal energia_asignada
            porcion = _construir_porcion(
                alimento, gramos, buscar_sustituto(alimento, gramos, disponibles)
            )
            porciones.append(porcion)
            energia_asignada += porcion.energia_kcal

        # 1. Proteína.
        if CATEGORIAS_PROTEICAS in composicion:
            proteina_del_tiempo = proteina_g * proporcion / peso_proteico
            # La proteína puede ocupar buena parte de la energía del tiempo,
            # pero no toda: hay que dejar sitio para el resto de la composición.
            energia_para_proteina = energia_del_tiempo * PROPORCION_MAXIMA_PROTEICA_POR_TIEMPO

            def cabe_en_el_tiempo(candidato: AlimentoDisponible) -> bool:
                return (
                    energia_por_gramo_de_proteina(candidato) * proteina_del_tiempo
                    <= energia_para_proteina
                )

            alimento = elegir(CATEGORIAS_PROTEICAS, cabe_en_el_tiempo)
            if alimento is not None:
                agregar(
                    alimento,
                    _gramos_para_proteina(
                        alimento, proteina_del_tiempo, energia_para_proteina
                    ),
                )

        # 2. Verduras y frutas, en porción fija.
        if CATEGORIAS_FRESCAS in composicion:
            alimento = elegir(CATEGORIAS_FRESCAS)
            if alimento is not None:
                agregar(alimento, _porcion_fija(alimento))

        # 3. Grasa añadida, acotada.
        if CATEGORIAS_GRASAS in composicion:
            alimento = elegir(CATEGORIAS_GRASAS)
            if alimento is not None:
                energia_grasa = energia_del_tiempo * PROPORCION_GRASA_POR_TIEMPO
                agregar(alimento, _gramos_para_energia(alimento, energia_grasa))

        # 4. Cereales y tubérculos: absorben la energía restante.
        if CATEGORIAS_ENERGETICAS in composicion:
            alimento = elegir(CATEGORIAS_ENERGETICAS)
            if alimento is not None:
                energia_restante = max(energia_del_tiempo - energia_asignada, 0.0)
                agregar(alimento, _gramos_para_energia(alimento, energia_restante))

        tiempos.append(
            TiempoComida(nombre=nombre_tiempo, proporcion=proporcion, porciones=porciones)
        )

    tiempos = _ajustar_energia(tiempos, energia_kcal, disponibles)

    return MenuDiario(
        tiempos=tiempos,
        energia_objetivo_kcal=energia_kcal,
        proteina_objetivo_g=proteina_g,
    )
