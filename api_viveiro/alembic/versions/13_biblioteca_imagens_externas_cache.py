"""Cache JSON de URLs de imagens externas (speciesLink) na biblioteca.

Revision ID: 13_biblioteca_imagens_externas
Revises: 12_limpar_especies_legado
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa


revision = "13_biblioteca_imagens_externas"
down_revision = "12_limpar_especies_legado"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("especies_biblioteca", sa.Column("imagens_externas", sa.JSON(), nullable=True))
    op.add_column(
        "especies_biblioteca",
        sa.Column("imagens_externas_atualizado_em", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("especies_biblioteca", "imagens_externas_atualizado_em")
    op.drop_column("especies_biblioteca", "imagens_externas")
