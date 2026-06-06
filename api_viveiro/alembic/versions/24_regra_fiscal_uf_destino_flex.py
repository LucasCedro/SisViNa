"""Regras fiscais — UF destino flexível (INTERESTADUAL, listas)

Revision ID: 24_regra_fiscal_uf_destino_flex
Revises: 23_regras_fiscais_contador
"""

from alembic import op
import sqlalchemy as sa

revision = "24_regra_fiscal_uf_destino_flex"
down_revision = "23_regras_fiscais_contador"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "regras_fiscais",
        "uf_destino",
        existing_type=sa.String(2),
        type_=sa.String(80),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "regras_fiscais",
        "uf_destino",
        existing_type=sa.String(80),
        type_=sa.String(2),
        existing_nullable=False,
    )
