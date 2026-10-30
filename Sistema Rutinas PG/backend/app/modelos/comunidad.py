"""Datos sociales separados: alias, invitaciones y constancia, sin biometría."""
from datetime import datetime, date
from uuid import uuid4
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.nucleo.base_datos import Base

def identificador():
    return uuid4().hex

class GrupoPrivado(Base):
    __tablename__ = "grupos_privados"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=identificador)
    propietario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(60), nullable=False)
    cerrado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class MiembroPrivado(Base):
    __tablename__ = "miembros_privados"
    __table_args__ = (UniqueConstraint("grupo_id", "usuario_id"),)
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=identificador)
    grupo_id: Mapped[str] = mapped_column(ForeignKey("grupos_privados.id", ondelete="CASCADE"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    alias: Mapped[str] = mapped_column(String(30), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expulsado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class InvitacionPrivada(Base):
    __tablename__ = "invitaciones_privadas"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # SHA-256, nunca el código
    grupo_id: Mapped[str] = mapped_column(ForeignKey("grupos_privados.id", ondelete="CASCADE"), nullable=False)
    vence: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    usada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class SemanaPrivada(Base):
    __tablename__ = "semanas_privadas"
    __table_args__ = (UniqueConstraint("miembro_id", "lunes"),)
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=identificador)
    miembro_id: Mapped[str] = mapped_column(ForeignKey("miembros_privados.id", ondelete="CASCADE"), nullable=False)
    lunes: Mapped[date] = mapped_column(Date, nullable=False)
    inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # UTC sin zona
    meta: Mapped[int] = mapped_column(nullable=False)
    sesiones: Mapped[list] = mapped_column(JSON, nullable=False)  # IDs y días del plan aceptado
    pausada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class BloqueoPrivado(Base):
    __tablename__ = "bloqueos_privados"
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    destino_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)

class EventoConstancia(Base):
    __tablename__ = "eventos_constancia"
    semana_id: Mapped[str] = mapped_column(ForeignKey("semanas_privadas.id", ondelete="CASCADE"), primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, primary_key=True)
    sesion_realizada_id: Mapped[int | None] = mapped_column(ForeignKey("sesiones_realizadas.id", ondelete="SET NULL"), nullable=True)

class DenunciaPrivada(Base):
    __tablename__ = "denuncias_privadas"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=identificador)
    grupo_id: Mapped[str] = mapped_column(ForeignKey("grupos_privados.id", ondelete="CASCADE"), nullable=False)
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    miembro_id: Mapped[str] = mapped_column(ForeignKey("miembros_privados.id", ondelete="CASCADE"), nullable=False)
    motivo: Mapped[str] = mapped_column(String(30), nullable=False)
    resuelta: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
