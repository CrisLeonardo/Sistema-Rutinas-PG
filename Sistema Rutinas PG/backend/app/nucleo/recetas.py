"""Recetario v1: 18 recetas originales, revisadas por un nutricionista (octubre de 2026).

Los gramos son de parte comestible en el estado indicado. El rendimiento es una
porción de referencia; el motor calcula las cantidades para el plan por separado.
Los precios provienen del catálogo, levantado en los mercados de El Progreso en
octubre de 2026. Las recetas no incluyen fotografías.
"""
from dataclasses import dataclass

VERSION_RECETAS = "2026-10-30.1"
FUENTES = [
    {"titulo": "FDA: alergias e ingredientes", "url": "https://www.fda.gov/food/buy-store-serve-safe-food/food-allergies-what-you-need-know"},
    {"titulo": "FoodSafety.gov: temperaturas de cocción", "url": "https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures"},
]

# Composición inferida del alimento genérico, no certificación de marca o trazas.
# Los productos compuestos o de composición ambigua quedan fuera del piloto.
# (estado de pesada, alérgenos/otros componentes, origen animal)
DETALLES = {
    "Tortilla de maíz": ("lista para comer", set(), False),
    "Arroz blanco cocido": ("cocido", set(), False),
    "Pan francés": ("listo para comer", {"trigo", "gluten"}, False),
    "Avena en hojuelas": ("seca", {"gluten"}, False),
    "Pasta cocida": ("cocida", {"trigo", "gluten", "huevo"}, False),
    "Pechuga de pollo": ("cocida", set(), True),
    "Huevo de gallina": ("crudo, sin cáscara", {"huevo"}, True),
    "Carne de res molida magra": ("cruda", set(), True),
    "Tilapia": ("cruda, sin espinas", {"pescado"}, True),
    "Hígado de res": ("crudo", set(), True),
    "Frijol negro cocido": ("cocido, escurrido", set(), False),
    "Lenteja cocida": ("cocida, escurrida", set(), False),
    "Garbanzo cocido": ("cocido, escurrido", set(), False),
    "Leche entera": ("lista para beber, pasteurizada", {"leche", "lactosa"}, True),
    "Queso fresco": ("listo para comer, pasteurizado", {"leche", "lactosa"}, True),
    "Yogur natural": ("listo para comer, pasteurizado", {"leche", "lactosa"}, True),
    "Banano": ("crudo, sin cáscara", set(), False),
    "Papaya": ("cruda, sin cáscara ni semillas", set(), False),
    "Mango": ("crudo, sin cáscara ni semilla", set(), False),
    "Naranja": ("cruda, sin cáscara", set(), False),
    "Sandía": ("cruda, sin cáscara", set(), False),
    "Güisquil": ("crudo, parte comestible", set(), False),
    "Tomate": ("crudo", set(), False),
    "Repollo": ("crudo", set(), False),
    "Zanahoria": ("cruda", set(), False),
    "Ejote": ("crudo, sin puntas", set(), False),
    "Espinaca": ("cruda", set(), False),
    "Aguacate": ("crudo, sin cáscara ni semilla", set(), False),
    "Maní tostado": ("tostado, sin cáscara", {"mani"}, False),
    "Semilla de marañón": ("lista para comer", {"frutos_secos"}, False),
    "Papa cocida": ("cocida", set(), False),
    "Camote cocido": ("cocido", set(), False),
    "Yuca cocida": ("cocida", set(), False),
    "Plátano macho cocido": ("cocido", set(), False),
}
# Aceite vegetal e Incaparina no declaran mezcla/marca: composición desconocida.


@dataclass(frozen=True)
class Receta:
    id: str
    nombre: str
    tiempos: tuple[int, ...]
    minutos: int
    ingredientes: tuple[tuple[str, float], ...]
    pasos: tuple[str, ...]
    rendimiento_porciones: int = 1
    estado_revision: str = "revisada"


RECETAS = (
    Receta("huevo-frijol", "Huevos con frijoles y tortilla", (0, 4), 15,
           (("Huevo de gallina", 100), ("Frijol negro cocido", 90), ("Tortilla de maíz", 60), ("Tomate", 100), ("Aguacate", 40)),
           ("Lave el tomate y córtelo. Caliente los frijoles y las tortillas por separado.", "Cocine el huevo en sartén antiadherente, sin aceite añadido, hasta que clara y yema estén firmes. Sirva con el tomate y aguacate.")),
    Receta("avena-yogur", "Avena con yogur y banano", (0, 1, 3), 10,
           (("Avena en hojuelas", 50), ("Yogur natural", 200), ("Banano", 100), ("Maní tostado", 15)),
           ("Cueza la avena con agua según su envase; pésela seca antes de cocer.", "Deje entibiar, añada el yogur, el banano cortado y el maní. No añada azúcar u otros ingredientes al cálculo.")),
    Receta("frijol-aguacate", "Tortillas con frijol y aguacate", (0, 4), 10,
           (("Frijol negro cocido", 180), ("Tortilla de maíz", 90), ("Aguacate", 60), ("Tomate", 100)),
           ("Caliente el frijol ya cocido y las tortillas.", "Sirva el frijol sobre las tortillas y acompañe con tomate lavado y aguacate.")),
    Receta("huevo-papa", "Huevos con papa y espinaca", (0, 4), 20,
           (("Huevo de gallina", 100), ("Papa cocida", 200), ("Espinaca", 60), ("Aguacate", 40)),
           ("Lave la espinaca. Corte la papa ya cocida.", "Cocine la espinaca y el huevo en sartén antiadherente, sin aceite, hasta que el huevo quede firme. Acompañe con papa caliente y aguacate.")),
    Receta("pollo-arroz", "Pollo con arroz y ensalada", (2, 4), 15,
           (("Pechuga de pollo", 140), ("Arroz blanco cocido", 200), ("Repollo", 100), ("Tomate", 80), ("Aguacate", 60)),
           ("Lave y corte el repollo y el tomate con utensilios limpios.", "Pese el pollo ya cocido y el arroz cocido. Si son sobras refrigeradas, recaliéntelas hasta 74 °C en el centro. Sirva con ensalada y aguacate.")),
    Receta("pollo-camote", "Pollo con camote y zanahoria", (2, 4), 20,
           (("Pechuga de pollo", 140), ("Camote cocido", 220), ("Zanahoria", 100), ("Aguacate", 60)),
           ("Lave, pese y cueza la zanahoria al vapor; pese el camote ya cocido.", "Caliente el pollo cocido y el camote. Las sobras refrigeradas deben alcanzar 74 °C al recalentarlas. Acompañe con aguacate.")),
    Receta("tilapia-arroz", "Tilapia al vapor con arroz", (2, 4), 25,
           (("Tilapia", 180), ("Arroz blanco cocido", 200), ("Zanahoria", 100), ("Aguacate", 70)),
           ("Pese la tilapia cruda sin espinas. Use utensilios separados para el pescado crudo y las verduras.", "Cocine el pescado al vapor hasta 63 °C en el centro. Cueza la zanahoria y sirva con arroz cocido caliente y aguacate.")),
    Receta("res-papa", "Picadillo sencillo con papa", (2, 4), 30,
           (("Carne de res molida magra", 150), ("Papa cocida", 220), ("Tomate", 100), ("Zanahoria", 80), ("Tortilla de maíz", 60)),
           ("Lave y corte las verduras. Pese la carne cruda y la papa ya cocida.", "Cocine la carne en sartén antiadherente con tomate y zanahoria; debe alcanzar 71 °C en el centro. Agregue papa y sirva con tortillas calientes.")),
    Receta("lenteja-arroz", "Lentejas con arroz y ensalada", (2, 4), 15,
           (("Lenteja cocida", 220), ("Arroz blanco cocido", 160), ("Repollo", 100), ("Tomate", 80), ("Aguacate", 60)),
           ("Caliente las lentejas y el arroz ya cocidos.", "Lave y corte repollo y tomate. Sirva aparte con aguacate. No agregue caldo comercial sin revisar sus ingredientes.")),
    Receta("garbanzo-papa", "Garbanzos con papa y tomate", (2, 4), 15,
           (("Garbanzo cocido", 180), ("Papa cocida", 180), ("Tomate", 100), ("Espinaca", 60), ("Aguacate", 50)),
           ("Lave el tomate y la espinaca; caliéntelos con un poco de agua.", "Agregue los garbanzos y la papa ya cocidos. Caliente por completo y sirva con aguacate.")),
    Receta("pollo-tortillas", "Tortillas con pollo y repollo", (2, 4), 15,
           (("Pechuga de pollo", 140), ("Tortilla de maíz", 120), ("Repollo", 100), ("Tomate", 80), ("Aguacate", 50)),
           ("Lave y corte repollo y tomate; reserve con utensilios limpios.", "Caliente el pollo ya cocido y las tortillas. Si recalienta sobras de pollo, compruebe 74 °C. Reparta el pollo en las tortillas y acompañe con verduras y aguacate.")),
    Receta("frijol-queso", "Frijoles con queso y plátano", (0, 4), 15,
           (("Frijol negro cocido", 160), ("Queso fresco", 50), ("Plátano macho cocido", 150), ("Tomate", 100)),
           ("Use queso de leche pasteurizada y manténgalo refrigerado hasta servir.", "Caliente el frijol y el plátano ya cocidos sin freír. Sirva con el queso y tomate lavado.")),
    Receta("yogur-papaya", "Yogur con papaya y avena", (1, 3), 10,
           (("Yogur natural", 180), ("Papaya", 150), ("Avena en hojuelas", 30), ("Maní tostado", 15)),
           ("Cueza la avena con agua según el envase y deje entibiar.", "Corte la papaya sin semillas ni cáscara. Mezcle con yogur y avena; agregue el maní.")),
    Receta("banano-mani", "Banano, maní y tortilla", (1, 3), 5,
           (("Banano", 120), ("Maní tostado", 25), ("Tortilla de maíz", 60)),
           ("Pele el banano y pese la parte comestible.", "Sirva con el maní sin cáscara y las tortillas calientes. Revise ingredientes y trazas del maní envasado.")),
    Receta("naranja-queso", "Naranja con queso y tortillas", (1, 3), 5,
           (("Naranja", 150), ("Queso fresco", 50), ("Tortilla de maíz", 60)),
           ("Pele la naranja y retire las semillas.", "Sirva con queso de leche pasteurizada y tortillas calientes. Mantenga el queso refrigerado hasta servir.")),
    Receta("mango-yogur", "Mango con yogur y marañón", (1, 3), 5,
           (("Mango", 150), ("Yogur natural", 200), ("Semilla de marañón", 25), ("Avena en hojuelas", 25)),
           ("Cueza la avena con agua según el envase y deje entibiar.", "Pele y corte el mango sin semilla. Sirva con yogur, avena y marañón; revise ingredientes y trazas de los productos envasados.")),
    Receta("frijol-camote", "Frijoles con camote y repollo", (2, 4), 15,
           (("Frijol negro cocido", 200), ("Camote cocido", 200), ("Repollo", 100), ("Aguacate", 60)),
           ("Lave y corte el repollo.", "Caliente los frijoles y el camote ya cocidos. Sirva con repollo y aguacate, sin añadir ingredientes al cálculo.")),
    Receta("huevo-arroz", "Huevo con arroz y tomate", (0, 4), 15,
           (("Huevo de gallina", 100), ("Arroz blanco cocido", 180), ("Tomate", 100), ("Aguacate", 50)),
           ("Lave y corte el tomate; pese el huevo sin cáscara.", "Cocine el huevo con tomate en sartén antiadherente sin aceite, hasta que quede firme. Sirva con arroz caliente y aguacate.")),
)
