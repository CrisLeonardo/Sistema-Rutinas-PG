"""Preferencias privadas y semana calculada; no modifica los planes históricos."""
from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.nucleo.base_datos import Base


class PreferenciasAlimentarias(Base):
    __tablename__ = "preferencias_alimentarias"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    datos: Mapped[dict] = mapped_column(JSON, nullable=False)


class SemanaAlimentaria(Base):
    __tablename__ = "semanas_alimentarias"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("planes.id", ondelete="CASCADE"), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    firma_catalogo: Mapped[str] = mapped_column(String(64), nullable=False)
    datos: Mapped[dict] = mapped_column(JSON, nullable=False)
