"""Entidad perfil biometrico del modelo entidad-relacion (apartado 3.4.3)."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos.enumeraciones import NivelActividad, NivelExperiencia, Objetivo, Sexo
from app.nucleo.base_datos import Base


class PerfilBiometrico(Base):
    """Medidas corporales y objetivos declarados por el usuario en un momento dado.

    Cada actualizacion de medidas genera un registro nuevo en lugar de sobrescribir
    el anterior, lo que produce el historial que exige la historia HU-05.
    """

    __tablename__ = "perfiles_biometricos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=False
    )

    peso_kg: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    estatura_cm: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    edad: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    sexo: Mapped[Sexo] = mapped_column(
        Enum(Sexo, values_callable=lambda tipo: [miembro.value for miembro in tipo]),
        nullable=False,
    )
    nivel_actividad: Mapped[NivelActividad] = mapped_column(
        Enum(
            NivelActividad,
            values_callable=lambda tipo: [miembro.value for miembro in tipo],
        ),
        nullable=False,
    )
    objetivo: Mapped[Objetivo] = mapped_column(
        Enum(Objetivo, values_callable=lambda tipo: [miembro.value for miembro in tipo]),
        nullable=False,
    )
    nivel_experiencia: Mapped[NivelExperiencia] = mapped_column(
        Enum(
            NivelExperiencia,
            values_callable=lambda tipo: [miembro.value for miembro in tipo],
        ),
        default=NivelExperiencia.PRINCIPIANTE,
        nullable=False,
    )
    dias_entrenamiento_semana: Mapped[int] = mapped_column(SmallInteger, default=3, nullable=False)

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True, nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="perfiles")  # noqa: F821
    planes: Mapped[list["Plan"]] = relationship(back_populates="perfil")  # noqa: F821

    @property
    def indice_masa_corporal(self) -> float:
        """Calcula el indice de masa corporal a partir del peso y la estatura."""
        estatura_m = float(self.estatura_cm) / 100
        return round(float(self.peso_kg) / (estatura_m**2), 2)

    def __repr__(self) -> str:
        return (
            f"<PerfilBiometrico id={self.id} usuario_id={self.usuario_id} "
            f"peso={self.peso_kg} objetivo={self.objetivo}>"
        )


class RegistroProgreso(Base):
    """Avance semanal reportado por el usuario (historia HU-09).

    Sirve de insumo para el reajuste automatico del plan descrito en el
    apartado 4.7.2 de la tesis.
    """

    __tablename__ = "registros_progreso"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("planes.id", ondelete="SET NULL"), nullable=True
    )

    peso_kg: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    perimetro_cintura_cm: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    sesiones_cumplidas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    adherencia_nutricional: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"<RegistroProgreso id={self.id} usuario_id={self.usuario_id} peso={self.peso_kg}>"
