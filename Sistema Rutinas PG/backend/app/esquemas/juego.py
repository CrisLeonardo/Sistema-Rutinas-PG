"""Contratos de los puntos, los niveles y las insignias.

Igual que los de la bitacora, no corresponden a ninguna de las once historias de
la pila de producto: el sistema de recompensas se agrega sobre datos que el
sistema ya tenia, para devolverle al usuario la continuidad de su esfuerzo.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.motor.juego import Animo, TipoEvento, gala_de_nivel


class PuntoGanadoPublico(BaseModel):
    """Un motivo por el que se acaban de sumar puntos."""

    model_config = ConfigDict(from_attributes=True)

    tipo: TipoEvento
    motivo: str
    puntos: int


class RecompensaPublica(BaseModel):
    """Lo que el usuario gano con la accion que acaba de realizar."""

    model_config = ConfigDict(from_attributes=True)

    puntos_ganados: int
    puntos_totales: int
    detalle: list[PuntoGanadoPublico] = []
    nivel_anterior: int
    nivel_actual: int
    nombre_nivel: str
    logros_nuevos: list[str] = []

    @computed_field(description="Indica si la acción hizo subir de nivel")
    @property
    def subio_de_nivel(self) -> bool:
        return self.nivel_actual > self.nivel_anterior

    @computed_field(
        description="Grado de atavío con que se dibuja la mascota en el nivel alcanzado"
    )
    @property
    def gala(self) -> int:
        """Para que la pantalla que celebra la subida dibuje el atavío nuevo.

        Sin este dato tendría que consultar la senda otra vez solo para saber si
        al lobo le toca ya la corona de laurel.
        """
        return gala_de_nivel(self.nivel_actual)


class LogroPublico(BaseModel):
    """Una insignia del catalogo, conseguida o todavia bloqueada.

    Las bloqueadas viajan con su pista y sin su fecha. La pista es lo que
    convierte la insignia en un objetivo en lugar de en un hueco.
    """

    clave: str
    nombre: str
    descripcion: str
    pista: str
    puntos: int
    categoria: str
    obtenido: bool
    fecha: datetime | None = None


class HitoPublico(BaseModel):
    """Un momento del camino recorrido."""

    model_config = ConfigDict(from_attributes=True)

    tipo: str = Field(description="«inicio», «nivel» o «logro»")
    titulo: str
    detalle: str
    fecha: datetime
    puntos: int = 0


class MotivoPublico(BaseModel):
    """Cuanto vale cada motivo, para la pantalla que explica las reglas."""

    motivo: str
    puntos: int
    variable: bool = Field(
        default=False,
        description=(
            "Si los puntos dependen de la sesión, en cuyo caso la cifra es el techo"
        ),
    )


class EstadoJuego(BaseModel):
    """El estado completo de la senda del usuario."""

    nivel: int
    nombre_nivel: str
    lema: str
    gala: int = Field(description="Grado de atavío con que se dibuja la mascota, de 0 a 4")
    nivel_maximo: int

    puntos_totales: int
    puntos_en_el_nivel: int
    puntos_del_tramo: int
    puntos_para_el_proximo: int
    porcentaje: int
    nombre_proximo_nivel: str | None

    animo: Animo = Field(description="Estado con que se dibuja la mascota")

    racha_semanas: int
    racha_maxima_semanas: int
    sesiones_totales: int
    volumen_acumulado_kg: float
    marcas_personales: int

    logros: list[LogroPublico] = []
    hitos: list[HitoPublico] = []
    motivos: list[MotivoPublico] = []

    @computed_field(description="Insignias conseguidas")
    @property
    def logros_obtenidos(self) -> int:
        return sum(1 for logro in self.logros if logro.obtenido)

    @computed_field(description="Insignias del catálogo completo")
    @property
    def logros_totales(self) -> int:
        return len(self.logros)
