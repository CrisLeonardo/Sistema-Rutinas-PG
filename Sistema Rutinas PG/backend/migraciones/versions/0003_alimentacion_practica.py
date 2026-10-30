"""Preferencias alimentarias y semana persistente. Conserva los menús anteriores."""
from alembic import op
import sqlalchemy as sa

revision = "0003_alimentacion_practica"
down_revision = "0002_recuperacion_acceso"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "preferencias_alimentarias",
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("datos", sa.JSON(), nullable=False),
    )
    op.create_table(
        "semanas_alimentarias",
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("planes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("firma_catalogo", sa.String(64), nullable=False),
        sa.Column("datos", sa.JSON(), nullable=False),
    )


def downgrade():
    op.drop_table("semanas_alimentarias")
    op.drop_table("preferencias_alimentarias")
