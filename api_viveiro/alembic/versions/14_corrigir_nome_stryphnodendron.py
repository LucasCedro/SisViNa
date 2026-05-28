"""Corrige grafia do gênero Stryphnodendron (barbatimão).

Revision ID: 14_corrigir_stryphnodendron
Revises: 13_biblioteca_imagens_externas
Create Date: 2026-05-28

"""

from alembic import op

revision = "14_corrigir_stryphnodendron"
down_revision = "13_biblioteca_imagens_externas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE especies
        SET nome_cientifico = 'Stryphnodendron adstringens (Mart.) Coville'
        WHERE nome_cientifico ILIKE 'Stryphondendron adstringens%'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE especies
        SET nome_cientifico = 'Stryphondendron adstringens (Mart.) Coville'
        WHERE nome_cientifico ILIKE 'Stryphnodendron adstringens%'
        """
    )
