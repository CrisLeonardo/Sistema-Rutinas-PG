"""Guardarrailes clinicos sobre el plan calculado (regla del negocio *e*).

El motor de calculo produce el requerimiento energetico que las formulas de
referencia determinan; este modulo comprueba que lo prescrito quepa dentro de
lo que es seguro comer, y lo corrige cuando no.

Se aplica *despues* del calculo y no dentro de las formulas a proposito. Las
formulas de Mifflin-St Jeor y Harris-Benedict son el patron cientifico contra el
que se mide el margen de error del modelo (tercer objetivo especifico), y
alterarlas cambiaria la referencia misma de esa medicion. La correccion de
seguridad es una regla del negocio, no una correccion del modelo: se aplica
aparte, se declara aparte y se le explica al usuario aparte.

Las tres situaciones que atiende son las que el calculo original no distinguia:

1. El deficit se aplicaba siempre al maximo. La regla del negocio *b* del
   apartado 4.3.4 dice que el ajuste «nunca excede» el 20 %, no que sea
   siempre el 20 %: una persona con indice de masa corporal de 19.5 recibia el
   mismo recorte que una con indice de 40.
2. Nada impedia prescribir por debajo del minimo alimentario. Una mujer de
   50 kilogramos, sedentaria y de 55 anios recibia 1 049 kilocalorias al dia.
3. La proteina se calculaba sobre el peso corporal total. Con 130 kilogramos
   el plan pedia 286 gramos diarios, cantidad que ni es necesaria ni se puede
   pagar en el municipio.

Ninguna de las tres correcciones emite un diagnostico: acotan una prescripcion
y explican por que, que es justamente lo que la regla del negocio *e* permite.
"""

from dataclasses import dataclass, field

from app.modelos.enumeraciones import Objetivo, Sexo
from app.motor.formulas import (
    DEFICIT_MAXIMO,
    KCAL_POR_GRAMO_CARBOHIDRATO,
    KCAL_POR_GRAMO_GRASA,
    KCAL_POR_GRAMO_PROTEINA,
    PROPORCION_GRASA,
    SUPERAVIT_MAXIMO,
)

# Techos que fija la regla del negocio *b*. Se leen de `formulas` para que un
# cambio en la regla no deje aqui una copia desactualizada.
DEFICIT_MAXIMO_REGLA = DEFICIT_MAXIMO
SUPERAVIT_MAXIMO_REGLA = SUPERAVIT_MAXIMO

# Holgura con que se reconoce que un plan quedo apoyado en el piso energetico.
# El redondeo de los gramos desplaza la energia final unas pocas kilocalorias
# respecto del piso exacto, y sin esta holgura el aviso no se mostraria.
TOLERANCIA_PISO_KCAL = 25

# Energia diaria por debajo de la cual una dieta deja de cubrir de forma fiable
# los micronutrientes esenciales y requiere supervision clinica. Son los valores
# que la literatura de nutricion senala como piso para una dieta autoadministrada.
ENERGIA_MINIMA_KCAL: dict[Sexo, int] = {
    Sexo.FEMENINO: 1200,
    Sexo.MASCULINO: 1500,
}

# Cortes del indice de masa corporal de la Organizacion Mundial de la Salud.
IMC_BAJO_PESO = 18.5
IMC_SOBREPESO = 25.0
IMC_OBESIDAD = 30.0

# Deficit admitido segun el indice de masa corporal. La reserva de grasa
# disponible es lo que determina cuanta energia puede retirarse sin que el
# cuerpo compense consumiendo musculo: quien tiene poca no tolera el recorte
# que quien tiene mucha si tolera. El techo sigue siendo el 20 % de la regla *b*.
DEFICIT_POR_INDICE: tuple[tuple[float, float], ...] = (
    (IMC_BAJO_PESO, 0.00),  # bajo peso: no se retira energia
    (21.0, 0.10),
    (IMC_SOBREPESO, 0.15),
    (float("inf"), 0.20),
)

# Superavit admitido. Con exceso de grasa corporal, el excedente calorico se
# acumula sobre todo como grasa, de modo que se modera. El techo sigue siendo
# el 15 % de la regla *b*.
SUPERAVIT_POR_INDICE: tuple[tuple[float, float], ...] = (
    (IMC_SOBREPESO, 0.15),
    (IMC_OBESIDAD, 0.10),
    (float("inf"), 0.05),
)

# Proporcion del exceso de peso que se suma al peso teorico para calcular la
# proteina cuando hay obesidad. Es el «peso ajustado» de uso clinico habitual:
# el tejido graso tiene un requerimiento proteico mucho menor que el magro, de
# modo que calcular sobre el peso total sobreestima la necesidad.
FRACCION_EXCESO_PARA_PROTEINA = 0.25

# Proporcion maxima de la energia diaria que puede provenir de la proteina.
# Por encima de esta cifra el reparto desplaza al carbohidrato hasta dejar al
# entrenamiento sin combustible, y el costo del plan se dispara.
PROPORCION_MAXIMA_PROTEINA = 0.35


@dataclass(frozen=True)
class PlanSeguro:
    """Plan ya acotado por los guardarrailes, con la explicacion de cada ajuste."""

    energia_kcal: int
    proteina_g: int
    carbohidrato_g: int
    grasa_g: int

    energia_calculada_kcal: int
    hubo_correccion: bool = False
    correcciones: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)


def indice_masa_corporal(peso_kg: float, estatura_cm: float) -> float:
    """Indice de masa corporal en kilogramos por metro cuadrado."""
    estatura_m = estatura_cm / 100
    return peso_kg / (estatura_m**2)


def _tramo(tabla: tuple[tuple[float, float], ...], indice: float) -> float:
    """Devuelve el valor del primer tramo de la tabla que cubre el indice."""
    for limite, valor in tabla:
        if indice < limite:
            return valor
    return tabla[-1][1]


def ajuste_admitido(objetivo: Objetivo, indice: float) -> float:
    """Ajuste calorico que corresponde al objetivo y a la composicion corporal.

    Devuelve una fraccion con signo: negativa en deficit, positiva en superavit.
    Nunca excede los limites de la regla del negocio *b*.
    """
    if objetivo == Objetivo.MANTENIMIENTO:
        return 0.0
    if objetivo == Objetivo.PERDIDA_GRASA:
        return -_tramo(DEFICIT_POR_INDICE, indice)
    return _tramo(SUPERAVIT_POR_INDICE, indice)


def peso_de_referencia_proteico(peso_kg: float, estatura_cm: float) -> float:
    """Peso sobre el que se calcula la proteina diaria.

    Coincide con el peso corporal salvo cuando hay obesidad. En ese caso se usa
    el peso que corresponderia a un indice de 25 mas la cuarta parte del exceso,
    porque el tejido graso apenas contribuye al requerimiento proteico.
    """
    indice = indice_masa_corporal(peso_kg, estatura_cm)
    if indice < IMC_OBESIDAD:
        return peso_kg

    estatura_m = estatura_cm / 100
    peso_de_referencia = IMC_SOBREPESO * estatura_m**2
    exceso = peso_kg - peso_de_referencia
    return peso_de_referencia + exceso * FRACCION_EXCESO_PARA_PROTEINA


def energia_minima(sexo: Sexo) -> int:
    """Piso energetico diario para una dieta que no requiera supervision clinica."""
    return ENERGIA_MINIMA_KCAL[sexo]


def _redistribuir(energia_kcal: int, proteina_g: int) -> tuple[int, int, int]:
    """Reparte la energia entre los tres macronutrientes con la proteina fijada.

    Sigue el mismo orden que `formulas.distribuir_macronutrientes`: primero la
    proteina, despues la grasa como proporcion de la energia, y el carbohidrato
    ocupa lo que queda.
    """
    grasa_g = round((energia_kcal * PROPORCION_GRASA) / KCAL_POR_GRAMO_GRASA)
    restante = (
        energia_kcal
        - proteina_g * KCAL_POR_GRAMO_PROTEINA
        - grasa_g * KCAL_POR_GRAMO_GRASA
    )
    if restante < 0:
        grasa_g = max(round(grasa_g + restante / KCAL_POR_GRAMO_GRASA), 0)
        restante = (
            energia_kcal
            - proteina_g * KCAL_POR_GRAMO_PROTEINA
            - grasa_g * KCAL_POR_GRAMO_GRASA
        )
    carbohidrato_g = max(round(restante / KCAL_POR_GRAMO_CARBOHIDRATO), 0)
    return proteina_g, carbohidrato_g, grasa_g


def notas_del_perfil(
    peso_kg: float,
    estatura_cm: float,
    sexo: Sexo,
    objetivo: Objetivo,
    energia_prescrita_kcal: float,
) -> tuple[list[str], list[str]]:
    """Explica que guardarrailes gobiernan el plan de este perfil.

    Devuelve el par (correcciones, advertencias). Depende unicamente del perfil
    y de la energia ya prescrita, de modo que puede reconstruirse al consultar
    un plan guardado sin necesidad de conservar los valores previos al ajuste.
    """
    indice = indice_masa_corporal(peso_kg, estatura_cm)
    correcciones: list[str] = []
    advertencias: list[str] = []

    if objetivo == Objetivo.PERDIDA_GRASA:
        if indice < IMC_BAJO_PESO:
            correcciones.append(
                "Su índice de masa corporal está por debajo de lo normal, de modo que su "
                "plan no recorta energía: se calculó para que sostenga su peso mientras "
                "gana músculo con el entrenamiento."
            )
            advertencias.append(
                "Perder peso partiendo de un índice de masa corporal bajo puede afectar su "
                "salud. Antes de proponérselo, consulte con un profesional de la nutrición."
            )
        else:
            deficit = _tramo(DEFICIT_POR_INDICE, indice)
            if deficit < DEFICIT_MAXIMO_REGLA:
                correcciones.append(
                    f"El recorte de energía se ajustó al {deficit * 100:.0f} % de su gasto "
                    "diario, no al máximo del 20 %: con su composición corporal actual, un "
                    "recorte mayor haría que perdiera músculo junto con la grasa."
                )
    elif objetivo == Objetivo.GANANCIA_MUSCULAR:
        superavit = _tramo(SUPERAVIT_POR_INDICE, indice)
        if superavit < SUPERAVIT_MAXIMO_REGLA:
            correcciones.append(
                f"El excedente de energía se ajustó al {superavit * 100:.0f} % de su gasto "
                "diario. Con su composición corporal actual, un excedente mayor se "
                "acumularía sobre todo como grasa."
            )

    piso = energia_minima(sexo)
    if energia_prescrita_kcal <= piso + TOLERANCIA_PISO_KCAL:
        correcciones.append(
            f"Su plan se elevó a {piso} kilocalorías diarias. Por debajo de esa cantidad "
            "una dieta deja de cubrir de forma confiable las vitaminas y los minerales "
            "que el cuerpo necesita, y ya requiere seguimiento profesional."
        )
        advertencias.append(
            "Su requerimiento calculado quedó cerca del mínimo que el sistema prescribe "
            "sin supervisión. Avance despacio y consulte a un profesional de la nutrición "
            "si busca reducir más."
        )

    if indice >= IMC_OBESIDAD:
        correcciones.append(
            "La proteína de su plan se calculó sobre un peso de referencia y no sobre su "
            "peso total: el tejido graso necesita mucha menos proteína que el muscular, "
            "de modo que pedir más ni ayudaría ni sería asequible."
        )

    return correcciones, advertencias


def aplicar(
    energia_kcal: float,
    proteina_g: float,
    carbohidrato_g: float,
    grasa_g: float,
    peso_kg: float,
    estatura_cm: float,
    sexo: Sexo,
    objetivo: Objetivo,
    gasto_energetico_total: float,
) -> PlanSeguro:
    """Acota el plan calculado a lo que es seguro prescribir.

    Recibe el resultado del modelo neuronal o de las formulas, indistintamente,
    y devuelve el plan corregido junto con la explicacion de cada correccion.
    Cuando no hay nada que corregir, devuelve los mismos valores y lo declara.
    """
    indice = indice_masa_corporal(peso_kg, estatura_cm)
    energia_calculada = round(energia_kcal)

    energia = float(energia_kcal)
    proteina = round(proteina_g)
    corregido = False

    # 1. El ajuste calorico se acota segun la composicion corporal.
    techo_admitido = gasto_energetico_total * (1 + ajuste_admitido(objetivo, indice))
    if objetivo == Objetivo.PERDIDA_GRASA and energia < techo_admitido:
        energia = techo_admitido
        corregido = True
    elif objetivo == Objetivo.GANANCIA_MUSCULAR and energia > techo_admitido:
        energia = techo_admitido
        corregido = True

    # 2. Piso energetico absoluto.
    piso = energia_minima(sexo)
    if energia < piso:
        energia = float(piso)
        corregido = True

    # 3. La proteina se calcula sobre el peso de referencia, no sobre el total.
    peso_proteico = peso_de_referencia_proteico(peso_kg, estatura_cm)
    if peso_proteico < peso_kg:
        proteina = max(round(proteina * peso_proteico / peso_kg), 1)
        corregido = True

    # 4. Tope de proteina como proporcion de la energia.
    energia_entera = round(energia)
    tope_proteina = round(
        energia_entera * PROPORCION_MAXIMA_PROTEINA / KCAL_POR_GRAMO_PROTEINA
    )
    if proteina > tope_proteina:
        proteina = max(tope_proteina, 1)
        corregido = True

    if not corregido:
        return PlanSeguro(
            energia_kcal=energia_calculada,
            proteina_g=round(proteina_g),
            carbohidrato_g=round(carbohidrato_g),
            grasa_g=round(grasa_g),
            energia_calculada_kcal=energia_calculada,
            hubo_correccion=False,
        )

    # La energia declarada es la que aportan los gramos ya redondeados, para que
    # la suma cuadre exactamente, igual que en `formulas.distribuir_macronutrientes`.
    proteina, carbohidrato, grasa = _redistribuir(energia_entera, proteina)
    energia_final = (
        proteina * KCAL_POR_GRAMO_PROTEINA
        + carbohidrato * KCAL_POR_GRAMO_CARBOHIDRATO
        + grasa * KCAL_POR_GRAMO_GRASA
    )

    # Redondear los gramos puede dejar la suma unas pocas kilocalorias por
    # debajo del piso, y un piso que el redondeo puede cruzar no es un piso. Se
    # completa con carbohidrato, que es el macronutriente cuya porcion admite
    # variar sin volverse impracticable.
    if energia_final < piso:
        faltante = piso - energia_final
        carbohidrato += -(-faltante // KCAL_POR_GRAMO_CARBOHIDRATO)  # division hacia arriba
        energia_final = (
            proteina * KCAL_POR_GRAMO_PROTEINA
            + carbohidrato * KCAL_POR_GRAMO_CARBOHIDRATO
            + grasa * KCAL_POR_GRAMO_GRASA
        )
    correcciones, advertencias = notas_del_perfil(
        peso_kg, estatura_cm, sexo, objetivo, energia_final
    )

    return PlanSeguro(
        energia_kcal=energia_final,
        proteina_g=proteina,
        carbohidrato_g=carbohidrato,
        grasa_g=grasa,
        energia_calculada_kcal=energia_calculada,
        hubo_correccion=True,
        correcciones=correcciones,
        advertencias=advertencias,
    )
