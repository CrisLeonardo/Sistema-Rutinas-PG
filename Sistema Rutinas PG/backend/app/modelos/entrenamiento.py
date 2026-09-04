"""Bitacora de entrenamiento: lo que el usuario hizo de verdad en el gimnasio.

Hasta ahora la rutina era de solo lectura. El sistema prescribia series,
repeticiones y repeticiones en reserva, y no tenia forma de saber si el usuario
las ejecuto ni con cuanto peso. Al final de la semana el usuario reportaba
cuantas sesiones cumplio —un numero suelto— y con eso el sistema decidia si
reajustaba el plan.

Esa falta de datos tenia una consecuencia concreta: la regla del negocio *d* del
apartado 4.3.4, que acota el incremento de carga al 10 % entre microciclos,
estaba implementada en `formulas.progresion_admitida` y no se invocaba desde
ningun servicio. El principio de sobrecarga progresiva del apartado 2.5.2
aparecia unicamente como un parrafo que le pedia al usuario subir la carga por su
cuenta. En la practica, la rutina de la semana doce era identica a la de la
primera.

Estas dos entidades registran la ejecucion real y son las que permiten calcular
la progresion. Se enlazan al ejercicio del catalogo y no a la sesion prescrita:
al regenerarse el plan, las sesiones prescritas se sustituyen por otras nuevas,
pero el historial de cargas de un ejercicio debe sobrevivir a ese cambio, porque
es justamente lo que da continuidad al entrenamiento.
"""

from datetime import datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.nucleo.base_datos import Base


class SesionRealizada(Base):
    """Una sesion de entrenamiento que el usuario declaro haber completado."""

    __tablename__ = "sesiones_realizadas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Sesion prescrita que se estaba ejecutando. Es opcional y se anula al
    # borrarse: sirve para saber que grupo muscular se trabajo, pero el
    # historial no depende de que esa sesion siga existiendo.
    sesion_id: Mapped[int | None] = mapped_column(
        ForeignKey("sesiones_entrenamiento.id", ondelete="SET NULL"), nullable=True
    )
    plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("planes.id", ondelete="SET NULL"), nullable=True
    )

    fecha: Mapped[datetime] = mapped_column(Date, index=True, nullable=False)
    duracion_minutos: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # Percepcion del esfuerzo de la sesion completa, de 1 a 10. Es el dato que
    # permite distinguir un estancamiento por fatiga de uno por falta de
    # estimulo, que exigen respuestas opuestas.
    percepcion_esfuerzo: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    series: Mapped[list["SerieRealizada"]] = relationship(
        back_populates="sesion",
        cascade="all, delete-orphan",
        order_by="SerieRealizada.id",
    )

    @property
    def series_totales(self) -> int:
        """Series que la sesion registro."""
        return len(self.series)

    @property
    def repeticiones_totales(self) -> int:
        return sum(serie.repeticiones for serie in self.series)

    @property
    def volumen_kg(self) -> float:
        """Volumen de carga de la sesion: la suma de peso por repeticiones.

        Es la medida con que se compara una sesion contra otra. Las series sin
        peso —las de peso corporal— no suman aqui; su progreso se lee en las
        repeticiones.
        """
        return round(
            sum(
                float(serie.peso_kg) * serie.repeticiones
                for serie in self.series
                if serie.peso_kg is not None
            ),
            1,
        )

    def __repr__(self) -> str:
        return (
            f"<SesionRealizada id={self.id} usuario_id={self.usuario_id} "
            f"fecha={self.fecha} series={len(self.series)}>"
        )


class SerieRealizada(Base):
    """Una serie concreta: cuantas repeticiones y con cuanto peso."""

    __tablename__ = "series_realizadas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sesion_realizada_id: Mapped[int] = mapped_column(
        ForeignKey("sesiones_realizadas.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # El enlace al catalogo es el que da continuidad: sobrevive a la
    # regeneracion del plan y es sobre el que se calcula la progresion.
    ejercicio_id: Mapped[int] = mapped_column(
        ForeignKey("ejercicios.id"), index=True, nullable=False
    )

    numero_serie: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    repeticiones: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # Nulo en los ejercicios de peso corporal, donde no hay carga que anotar.
    peso_kg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    repeticiones_en_reserva: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )

    sesion: Mapped["SesionRealizada"] = relationship(back_populates="series")
    ejercicio: Mapped["Ejercicio"] = relationship()  # noqa: F821

    @property
    def volumen_kg(self) -> float:
        """Peso por repeticiones de esta serie."""
        if self.peso_kg is None:
            return 0.0
        return round(float(self.peso_kg) * self.repeticiones, 1)

    def __repr__(self) -> str:
        return (
            f"<SerieRealizada ejercicio_id={self.ejercicio_id} "
            f"n={self.numero_serie} {self.repeticiones}x{self.peso_kg}>"
        )
