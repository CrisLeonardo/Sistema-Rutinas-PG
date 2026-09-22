"""Entidad perfil biometrico del modelo entidad-relacion (apartado 3.4.3)."""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos.enumeraciones import (
    CondicionMedica,
    NivelActividad,
    NivelExperiencia,
    Objetivo,
    Sexo,
    ZonaLesion,
)
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

    # El historial de lesiones y las condiciones medicas viven en tablas propias
    # y no en columnas de esta entidad. Cada medicion puede declarar varias, y el
    # esquema se crea con `create_all`, que agrega tablas nuevas pero no altera
    # las existentes: una columna nueva aqui romperia la base ya desplegada.
    registros_lesion: Mapped[list["LesionPerfil"]] = relationship(
        back_populates="perfil", cascade="all, delete-orphan", lazy="selectin"
    )
    registros_condicion: Mapped[list["CondicionPerfil"]] = relationship(
        back_populates="perfil", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def indice_masa_corporal(self) -> float:
        """Calcula el indice de masa corporal a partir del peso y la estatura."""
        estatura_m = float(self.estatura_cm) / 100
        return round(float(self.peso_kg) / (estatura_m**2), 2)

    @property
    def lesiones(self) -> list[ZonaLesion]:
        """Zonas lesionadas declaradas en esta medicion, en orden estable."""
        return sorted(
            (registro.zona for registro in self.registros_lesion), key=list(ZonaLesion).index
        )

    @property
    def condiciones(self) -> list[CondicionMedica]:
        """Condiciones medicas declaradas en esta medicion, en orden estable."""
        return sorted(
            (registro.condicion for registro in self.registros_condicion),
            key=list(CondicionMedica).index,
        )

    def declarar_antecedentes(
        self, lesiones: list[ZonaLesion], condiciones: list[CondicionMedica]
    ) -> None:
        """Asocia a la medicion su historial de lesiones y sus condiciones."""
        self.registros_lesion = [LesionPerfil(zona=zona) for zona in dict.fromkeys(lesiones)]
        self.registros_condicion = [
            CondicionPerfil(condicion=condicion) for condicion in dict.fromkeys(condiciones)
        ]

    def __repr__(self) -> str:
        return (
            f"<PerfilBiometrico id={self.id} usuario_id={self.usuario_id} "
            f"peso={self.peso_kg} objetivo={self.objetivo}>"
        )


class LesionPerfil(Base):
    """Zona lesionada que el usuario declara en una medicion.

    Cuelga de la medicion y no del usuario: asi el historial de lesiones se
    conserva igual que el de las medidas, y la rutina se arma con las lesiones
    vigentes en el momento en que se genero.
    """

    __tablename__ = "lesiones_perfil"
    __table_args__ = (UniqueConstraint("perfil_id", "zona", name="uq_lesion_por_perfil"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    perfil_id: Mapped[int] = mapped_column(
        ForeignKey("perfiles_biometricos.id", ondelete="CASCADE"), index=True, nullable=False
    )
    zona: Mapped[ZonaLesion] = mapped_column(
        Enum(ZonaLesion, values_callable=lambda tipo: [miembro.value for miembro in tipo]),
        nullable=False,
    )

    perfil: Mapped[PerfilBiometrico] = relationship(back_populates="registros_lesion")


class CondicionPerfil(Base):
    """Patologia cronica severa que el usuario declara en una medicion (RE-02)."""

    __tablename__ = "condiciones_perfil"
    __table_args__ = (
        UniqueConstraint("perfil_id", "condicion", name="uq_condicion_por_perfil"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    perfil_id: Mapped[int] = mapped_column(
        ForeignKey("perfiles_biometricos.id", ondelete="CASCADE"), index=True, nullable=False
    )
    condicion: Mapped[CondicionMedica] = mapped_column(
        Enum(CondicionMedica, values_callable=lambda tipo: [miembro.value for miembro in tipo]),
        nullable=False,
    )

    perfil: Mapped[PerfilBiometrico] = relationship(back_populates="registros_condicion")


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
