"""Un único enlace de recuperación vigente por cuenta; solo conserva su hash."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.nucleo.base_datos import Base


class RecuperacionAcceso(Base):
    __tablename__ = "recuperaciones_acceso"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    resumen_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    vence_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
