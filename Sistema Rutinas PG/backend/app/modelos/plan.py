"""Entidad plan y su desglose nutricional y de entrenamiento (apartado 3.4.3)."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos.enumeraciones import GrupoMuscular
from app.nucleo.base_datos import Base


class Plan(Base):
    """Plan de nutricion y entrenamiento generado para un perfil biometrico.

    Almacena tanto el resultado del modelo neuronal como los valores de las
    formulas de Mifflin-St Jeor y Harris-Benedict, lo que permite verificar de
    forma permanente el margen de error menor al cinco por ciento exigido por
    el criterio de aceptacion de la historia HU-06.
    """

    __tablename__ = "planes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    perfil_id: Mapped[int] = mapped_column(
        ForeignKey("perfiles_biometricos.id", ondelete="CASCADE"), nullable=False
    )

    tasa_metabolica_basal: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    gasto_energetico_total: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    calorias_objetivo: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)

    referencia_mifflin: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    referencia_harris_benedict: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
    margen_error_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    proteina_g: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    carbohidrato_g: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    grasa_g: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)

    origen_calculo: Mapped[str] = mapped_column(String(30), default="formula", nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True, nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="planes")  # noqa: F821
    perfil: Mapped["PerfilBiometrico"] = relationship(back_populates="planes")  # noqa: F821
    comidas: Mapped[list["ComidaPlan"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )
    sesiones: Mapped[list["SesionEntrenamiento"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="SesionEntrenamiento.dia"
    )

    def __repr__(self) -> str:
        return f"<Plan id={self.id} usuario_id={self.usuario_id} kcal={self.calorias_objetivo}>"


class ComidaPlan(Base):
    """Alimento asignado a un tiempo de comida dentro del plan nutricional."""

    __tablename__ = "comidas_plan"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("planes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    alimento_id: Mapped[int] = mapped_column(ForeignKey("alimentos.id"), nullable=False)

    tiempo_comida: Mapped[str] = mapped_column(String(40), nullable=False)
    cantidad_g: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)

    plan: Mapped["Plan"] = relationship(back_populates="comidas")
    alimento: Mapped["Alimento"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return f"<ComidaPlan plan_id={self.plan_id} alimento_id={self.alimento_id}>"


class SesionEntrenamiento(Base):
    """Sesion de un dia dentro de la rutina semanal (historia HU-07)."""

    __tablename__ = "sesiones_entrenamiento"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("planes.id", ondelete="CASCADE"), index=True, nullable=False
    )

    dia: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    grupo_muscular: Mapped[GrupoMuscular] = mapped_column(
        Enum(
            GrupoMuscular,
            values_callable=lambda tipo: [miembro.value for miembro in tipo],
        ),
        nullable=False,
    )

    plan: Mapped["Plan"] = relationship(back_populates="sesiones")
    ejercicios: Mapped[list["EjercicioSesion"]] = relationship(
        back_populates="sesion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SesionEntrenamiento plan_id={self.plan_id} dia={self.dia}>"


class EjercicioSesion(Base):
    """Prescripcion concreta de un ejercicio dentro de una sesion.

    Registra series, repeticiones y repeticiones en reserva, conforme al
    criterio de aceptacion de la historia HU-07.
    """

    __tablename__ = "ejercicios_sesion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sesion_id: Mapped[int] = mapped_column(
        ForeignKey("sesiones_entrenamiento.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ejercicio_id: Mapped[int] = mapped_column(ForeignKey("ejercicios.id"), nullable=False)

    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    series: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    repeticiones_min: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    repeticiones_max: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    repeticiones_en_reserva: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    descanso_segundos: Mapped[int] = mapped_column(SmallInteger, default=90, nullable=False)

    sesion: Mapped["SesionEntrenamiento"] = relationship(back_populates="ejercicios")
    ejercicio: Mapped["Ejercicio"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return f"<EjercicioSesion sesion_id={self.sesion_id} ejercicio_id={self.ejercicio_id}>"
