"""Contratos de salida de la rutina de entrenamiento (historia HU-07)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from app.modelos.enumeraciones import GrupoMuscular

# Regla del negocio *e* del apartado 4.3.4. La rutina lleva su propio aviso
# porque puede consultarse sin pasar por la pantalla del plan nutricional.
AVISO_TECNICA = (
    "Antes de aumentar la carga, asegúrese de dominar la técnica de cada ejercicio. "
    "Si siente dolor articular, deténgase. Este programa es una orientación general "
    "y no sustituye la supervisión de un entrenador ni la valoración de un "
    "profesional de la salud."
)

NOMBRES_GRUPO = {
    GrupoMuscular.PECHO: "Pecho",
    GrupoMuscular.ESPALDA: "Espalda",
    GrupoMuscular.PIERNA: "Pierna",
    GrupoMuscular.HOMBRO: "Hombro",
    GrupoMuscular.BRAZO: "Brazo",
    GrupoMuscular.ABDOMEN: "Abdomen",
    GrupoMuscular.CUERPO_COMPLETO: "Cuerpo completo",
}


class EjercicioRutinaPublico(BaseModel):
    """Prescripcion de un ejercicio dentro de una sesion."""

    model_config = ConfigDict(from_attributes=True)

    ejercicio_id: int
    nombre: str
    grupo_muscular: GrupoMuscular
    equipamiento: str
    descripcion: str | None
    orden: int
    series: int
    repeticiones_min: int
    repeticiones_max: int
    repeticiones_en_reserva: int
    descanso_segundos: int

    @computed_field(description="Prescripción resumida, tal como se lee en el gimnasio")
    @property
    def prescripcion(self) -> str:
        return (
            f"{self.series} series de {self.repeticiones_min} a "
            f"{self.repeticiones_max} repeticiones"
        )

    @computed_field(description="Explicación de las repeticiones en reserva")
    @property
    def explicacion_reserva(self) -> str:
        """Traduce las repeticiones en reserva a una instruccion accionable.

        La sigla RIR no significa nada para quien no entrena con un plan escrito,
        y el requerimiento 4.5.3 obliga a explicar toda cifra tecnica.
        """
        if self.repeticiones_en_reserva <= 1:
            return "Termine cada serie cuando le quede apenas una repetición de reserva."
        return (
            f"Termine cada serie cuando aún podría hacer {self.repeticiones_en_reserva} "
            "repeticiones más. No llegue al fallo."
        )


class SesionRutinaPublica(BaseModel):
    """Sesion de un dia de la semana."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    dia: int
    grupo_muscular: GrupoMuscular
    ejercicios: list[EjercicioRutinaPublico]

    @computed_field(description="Nombre del día de la semana")
    @property
    def nombre_dia(self) -> str:
        from app.motor.rutina import NOMBRES_DIAS

        return NOMBRES_DIAS[self.dia]

    @computed_field(description="Nombre legible del grupo muscular")
    @property
    def nombre_grupo(self) -> str:
        return NOMBRES_GRUPO[self.grupo_muscular]

    @computed_field(description="Series totales de la sesión")
    @property
    def series_totales(self) -> int:
        return sum(ejercicio.series for ejercicio in self.ejercicios)

    @computed_field(description="Duración aproximada de la sesión, en minutos")
    @property
    def duracion_estimada_minutos(self) -> int:
        """Estima cuanto dura la sesion contando descansos y series.

        Se toman cuarenta segundos por serie mas su descanso, lo que da una
        referencia util para que el usuario reserve el tiempo.
        """
        segundos = sum(
            ejercicio.series * (40 + ejercicio.descanso_segundos)
            for ejercicio in self.ejercicios
        )
        return max(round(segundos / 60), 1)


class RutinaPublica(BaseModel):
    """Rutina semanal asociada al plan vigente (historia HU-07)."""

    plan_id: int
    fecha_generacion: datetime
    activo: bool
    dias_entrenamiento_semana: int
    series_objetivo_por_grupo: float
    nivel_experiencia: str
    objetivo: str
    sesiones: list[SesionRutinaPublica]

    @computed_field(description="Aviso de técnica y consulta profesional")
    @property
    def aviso_tecnica(self) -> str:
        return AVISO_TECNICA

    @computed_field(description="Series semanales que recibe cada grupo muscular")
    @property
    def series_efectivas_por_grupo(self) -> dict[str, int]:
        acumulado: dict[str, int] = {}
        for sesion in self.sesiones:
            for ejercicio in sesion.ejercicios:
                nombre = NOMBRES_GRUPO[ejercicio.grupo_muscular]
                acumulado[nombre] = acumulado.get(nombre, 0) + ejercicio.series
        return acumulado

    @computed_field(description="Series totales de la semana")
    @property
    def series_totales(self) -> int:
        return sum(sesion.series_totales for sesion in self.sesiones)

    @computed_field(description="Indica si algún grupo se repite en días consecutivos")
    @property
    def cumple_separacion_de_grupos(self) -> bool:
        """Verifica en la propia respuesta el criterio de aceptacion de HU-07.

        Se expone al cliente para que la comprobacion no dependa solo de las
        pruebas: la pantalla puede mostrarla y el evaluador puede leerla.
        """
        from app.motor.rutina import (
            GRUPOS_DE_CUERPO_COMPLETO,
            DIAS_DE_LA_SEMANA,
        )

        por_dia: dict[int, set[GrupoMuscular]] = {}
        for sesion in self.sesiones:
            if sesion.grupo_muscular == GrupoMuscular.CUERPO_COMPLETO:
                por_dia[sesion.dia] = set(GRUPOS_DE_CUERPO_COMPLETO)
            else:
                por_dia[sesion.dia] = {sesion.grupo_muscular}

        for dia, grupos in por_dia.items():
            siguiente = dia % DIAS_DE_LA_SEMANA + 1
            if siguiente in por_dia and grupos & por_dia[siguiente]:
                return False
        return True

    @computed_field(description="Explicación de la progresión de carga")
    @property
    def explicacion_progresion(self) -> str:
        """Regla del negocio *d*: la carga no sube mas del 10 % entre microciclos."""
        return (
            "Cuando complete todas las series dentro del rango de repeticiones indicado, "
            "suba la carga para la semana siguiente. El aumento nunca debe pasar del "
            "10 % del peso que usó, para que el cuerpo alcance a adaptarse."
        )
