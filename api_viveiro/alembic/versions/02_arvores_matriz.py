"""arvores matriz

Revision ID: 002_arvores_matriz
Revises: 001_criar_tabelas_iniciais
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa

revision = "002_arvores_matriz"
down_revision = "001_criar_tabelas_iniciais"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "arvores_matriz",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("id_especie", sa.Integer(), nullable=False),
        sa.Column("cidade", sa.String(length=100), nullable=True),
        sa.Column("estado", sa.String(length=2), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column("tipo_coordenada", sa.String(length=20), nullable=False, server_default="geografica"),
        sa.Column("utm_zona", sa.Integer(), nullable=True),
        sa.Column("utm_easting", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("utm_northing", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("sementes_coletadas", sa.Integer(), server_default="0", nullable=True),
        sa.Column("taxa_germinacao", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("data_ultima_coleta", sa.Date(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("data_cadastro", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["id_especie"], ["especies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_arvores_matriz_id", "arvores_matriz", ["id"])


def downgrade():
    op.drop_index("ix_arvores_matriz_id", table_name="arvores_matriz")
    op.drop_table("arvores_matriz")
