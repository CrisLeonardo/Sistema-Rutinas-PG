"""Piloto privado de comunidad, separado de la puntuación histórica."""
from alembic import op
import sqlalchemy as sa

revision = "0005_comunidad_privada"
down_revision = "0004_duracion_sostenes"
branch_labels = depends_on = None

def upgrade():
    op.create_table("grupos_privados",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("propietario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nombre", sa.String(60), nullable=False),
        sa.Column("cerrado", sa.Boolean(), nullable=False))
    op.create_table("miembros_privados",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("grupo_id", sa.String(32), sa.ForeignKey("grupos_privados.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias", sa.String(30), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("expulsado", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("grupo_id", "usuario_id"))
    op.create_table("invitaciones_privadas",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("grupo_id", sa.String(32), sa.ForeignKey("grupos_privados.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vence", sa.DateTime(), nullable=False),
        sa.Column("usada", sa.Boolean(), nullable=False))
    op.create_table("semanas_privadas",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("miembro_id", sa.String(32), sa.ForeignKey("miembros_privados.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lunes", sa.Date(), nullable=False),
        sa.Column("inicio", sa.DateTime(), nullable=False),
        sa.Column("meta", sa.Integer(), nullable=False),
        sa.Column("sesiones", sa.JSON(), nullable=False),
        sa.Column("pausada", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("miembro_id", "lunes"))
    op.create_table("eventos_constancia",
        sa.Column("semana_id", sa.String(32), sa.ForeignKey("semanas_privadas.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("fecha", sa.Date(), primary_key=True),
        sa.Column("sesion_realizada_id", sa.Integer(), sa.ForeignKey("sesiones_realizadas.id", ondelete="SET NULL"), nullable=True))
    op.create_table("bloqueos_privados",
        sa.Column("autor_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("destino_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("denuncias_privadas",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("grupo_id", sa.String(32), sa.ForeignKey("grupos_privados.id", ondelete="CASCADE"), nullable=False),
        sa.Column("autor_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("miembro_id", sa.String(32), sa.ForeignKey("miembros_privados.id", ondelete="CASCADE"), nullable=False),
        sa.Column("motivo", sa.String(30), nullable=False),
        sa.Column("resuelta", sa.Boolean(), nullable=False))

def downgrade():
    for tabla in ("denuncias_privadas", "bloqueos_privados", "eventos_constancia", "semanas_privadas",
                  "invitaciones_privadas", "miembros_privados", "grupos_privados"):
        op.drop_table(tabla)
