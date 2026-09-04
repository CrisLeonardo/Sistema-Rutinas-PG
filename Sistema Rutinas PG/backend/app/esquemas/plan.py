"""Contratos de salida del plan nutricional (historia HU-06)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

# Regla del negocio *e* del apartado 4.3.4: el sistema no emite diagnosticos
# medicos y muestra este aviso en todos los planes.
AVISO_PROFESIONAL = (
    "Este plan es una orientación general generada de forma automática. No sustituye "
    "la valoración de un profesional de la salud. Si tiene alguna condición médica "
    "preexistente, consulte con su médico o nutricionista antes de seguirlo."
)


class MacronutrientePublico(BaseModel):
    """Un macronutriente expresado en gramos, en kilocalorias y en porcentaje.

    El criterio de aceptacion de la historia HU-06 exige las tres formas: los
    gramos para la compra y la preparacion, el porcentaje para interpretar el
    reparto, y la energia para comprobar que la suma cuadra con el total.
    """

    nombre: str
    gramos: int
    kilocalorias: int
    porcentaje: float
    explicacion: str


class PlanNutricionalPublico(BaseModel):
    """Plan de nutricion generado para el perfil biometrico vigente."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    perfil_id: int
    fecha_generacion: datetime
    activo: bool

    tasa_metabolica_basal: float
    gasto_energetico_total: float
    calorias_objetivo: float

    referencia_mifflin: float
    referencia_harris_benedict: float
    margen_error_porcentaje: float
    origen_calculo: str

    proteina_g: float
    carbohidrato_g: float
    grasa_g: float

    agua_ml: int
    objetivo: str
    explicacion_objetivo: str

    # Guardarrailes clinicos que gobiernan el plan (regla del negocio *e*). Las
    # correcciones explican por que el plan no es el calculo crudo; las
    # advertencias senalan cuando conviene consultar a un profesional.
    correcciones_de_seguridad: list[str] = []
    advertencias_de_salud: list[str] = []

    @computed_field(description="Aviso de consulta profesional (regla del negocio *e*)")
    @property
    def aviso_profesional(self) -> str:
        return AVISO_PROFESIONAL

    @computed_field(description="Reparto de macronutrientes en gramos y en porcentaje")
    @property
    def macronutrientes(self) -> list[MacronutrientePublico]:
        """Desglosa el reparto con la explicacion sencilla de cada cifra.

        Los porcentajes se calculan sobre la energia que aportan los propios
        gramos, de modo que sumen cien y coincidan con el total del plan.
        """
        aportes = [
            ("Proteína", int(self.proteina_g), 4, EXPLICACION_PROTEINA),
            ("Carbohidrato", int(self.carbohidrato_g), 4, EXPLICACION_CARBOHIDRATO),
            ("Grasa", int(self.grasa_g), 9, EXPLICACION_GRASA),
        ]
        total = sum(gramos * factor for _, gramos, factor, _ in aportes)
        return [
            MacronutrientePublico(
                nombre=nombre,
                gramos=gramos,
                kilocalorias=gramos * factor,
                porcentaje=round(100 * gramos * factor / total, 1) if total else 0.0,
                explicacion=explicacion,
            )
            for nombre, gramos, factor, explicacion in aportes
        ]

    @computed_field(description="Suma de los aportes energéticos de los macronutrientes")
    @property
    def energia_de_los_macronutrientes(self) -> int:
        return sum(macro.kilocalorias for macro in self.macronutrientes)

    @computed_field(description="Indica si el margen de error cumple el criterio del 5 %")
    @property
    def dentro_del_margen_admitido(self) -> bool:
        return self.margen_error_porcentaje < 5.0

    @computed_field(description="Indica si algún guardarraíl clínico modificó el plan")
    @property
    def ajustado_por_seguridad(self) -> bool:
        return bool(self.correcciones_de_seguridad)


EXPLICACION_PROTEINA = (
    "Construye y repara el músculo. Está en el huevo, el pollo, el frijol, la carne "
    "y los lácteos."
)
EXPLICACION_CARBOHIDRATO = (
    "Es el combustible principal del cuerpo y del entrenamiento. Está en la tortilla, "
    "el arroz, el pan, la papa y las frutas."
)
EXPLICACION_GRASA = (
    "Interviene en la producción de hormonas y en la absorción de vitaminas. Está en "
    "el aceite, el aguacate, la semilla de marañón y el maní."
)
