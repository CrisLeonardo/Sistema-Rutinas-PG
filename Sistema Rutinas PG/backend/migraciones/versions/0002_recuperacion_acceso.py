"""Recuperación de acceso y revocación de sesiones.

Revision ID: 0002_recuperacion_acceso
Revises: 0001_esquema_inicial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_recuperacion_acceso"
down_revision = "0001_esquema_inicial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("usuarios", sa.Column("version_sesion", sa.Integer(), server_default="0", nullable=False))
    op.create_table(
        "recuperaciones_acceso",
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("resumen_token", sa.String(64), nullable=False, unique=True),
        sa.Column("vence_en", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table("recuperaciones_acceso")
    op.drop_column("usuarios", "version_sesion")
