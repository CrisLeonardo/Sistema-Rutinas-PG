"""Entidad usuario del modelo entidad-relacion (apartado 3.4.3)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos.enumeraciones import RolUsuario
from app.nucleo.base_datos import Base


class Usuario(Base):
    """Cuenta de acceso al sistema.

    Concentra las credenciales y el rol; los datos biometricos se registran en
    la entidad PerfilBiometrico para conservar el historial de medidas.
    """

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    correo: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    contrasena_cifrada: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario, values_callable=lambda tipo: [miembro.value for miembro in tipo]),
        default=RolUsuario.USUARIO,
        nullable=False,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    perfiles: Mapped[list["PerfilBiometrico"]] = relationship(  # noqa: F821
        back_populates="usuario",
        cascade="all, delete-orphan",
        order_by="PerfilBiometrico.fecha_registro.desc()",
    )
    planes: Mapped[list["Plan"]] = relationship(  # noqa: F821
        back_populates="usuario",
        cascade="all, delete-orphan",
        order_by="Plan.fecha_generacion.desc()",
    )

    @property
    def es_administrador(self) -> bool:
        """Indica si la cuenta puede administrar catalogos y roles."""
        return self.rol == RolUsuario.ADMINISTRADOR

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} correo={self.correo!r} rol={self.rol}>"
