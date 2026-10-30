"""Duración aditiva; jamás interpreta repeticiones históricas como segundos."""
from alembic import op
import sqlalchemy as sa

revision = "0004_duracion_sostenes"
down_revision = "0003_alimentacion_practica"
branch_labels = depends_on = None

def upgrade():
    op.add_column("ejercicios_sesion", sa.Column("duracion_segundos_min", sa.SmallInteger(), nullable=True))
    op.add_column("ejercicios_sesion", sa.Column("duracion_segundos_max", sa.SmallInteger(), nullable=True))
    op.add_column("series_realizadas", sa.Column("duracion_segundos", sa.SmallInteger(), nullable=True))
    # Nueva orientación provisional de 20–30 s, independiente de las cifras antiguas.
    op.execute(sa.text("""UPDATE ejercicios_sesion SET duracion_segundos_min=20,
        duracion_segundos_max=30 WHERE ejercicio_id IN
        (SELECT id FROM ejercicios WHERE nombre='Plancha frontal'
         AND grupo_muscular='abdomen' AND equipamiento='Peso corporal')"""))

def downgrade():
    if op.get_bind().execute(sa.text("SELECT count(*) FROM series_realizadas WHERE duracion_segundos IS NOT NULL")).scalar():
        raise RuntimeError("Hay duraciones registradas. Restaure un respaldo compatible; no se borrarán sus unidades.")
    op.drop_column("series_realizadas", "duracion_segundos")
    op.drop_column("ejercicios_sesion", "duracion_segundos_max")
    op.drop_column("ejercicios_sesion", "duracion_segundos_min")
