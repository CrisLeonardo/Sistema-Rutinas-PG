"""Catalogos maestros de alimentos y ejercicios (historia HU-11).

Ambas entidades se restringen a lo efectivamente disponible en el municipio de
El Progreso, Jutiapa, conforme al objetivo declarado en el apartado 4.1.2.
"""

from sqlalchemy import Boolean, Enum, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modelos.enumeraciones import CategoriaAlimento, GrupoMuscular, NivelExperiencia
from app.nucleo.base_datos import Base


class Alimento(Base):
    """Alimento disponible localmente, con su aporte nutricional por cada 100 gramos."""

    __tablename__ = "alimentos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    categoria: Mapped[CategoriaAlimento] = mapped_column(
        Enum(
            CategoriaAlimento,
            values_callable=lambda tipo: [miembro.value for miembro in tipo],
        ),
        index=True,
        nullable=False,
    )

    energia_kcal_100g: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    proteina_g_100g: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    carbohidrato_g_100g: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    grasa_g_100g: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    costo_aproximado_quetzales: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    disponible_localmente: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    medida_casera: Mapped[str | None] = mapped_column(String(80), nullable=True)

    def __repr__(self) -> str:
        return f"<Alimento id={self.id} nombre={self.nombre!r}>"


class Ejercicio(Base):
    """Ejercicio ejecutable con el equipamiento registrado para la institucion."""

    __tablename__ = "ejercicios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    grupo_muscular: Mapped[GrupoMuscular] = mapped_column(
        Enum(
            GrupoMuscular,
            values_callable=lambda tipo: [miembro.value for miembro in tipo],
        ),
        index=True,
        nullable=False,
    )
    nivel_minimo: Mapped[NivelExperiencia] = mapped_column(
        Enum(
            NivelExperiencia,
            values_callable=lambda tipo: [miembro.value for miembro in tipo],
        ),
        default=NivelExperiencia.PRINCIPIANTE,
        nullable=False,
    )

    equipamiento: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    es_compuesto: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disponible_localmente: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Ejercicio id={self.id} nombre={self.nombre!r}>"
