"""Angico colubrina: nome popular curto (sem angico-branco).

Revision ID: 16_corrigir_angico
Revises: 15_estoques_insumos_mov
"""

from alembic import op

revision = "16_corrigir_angico"
down_revision = "15_estoques_insumos_mov"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE especies
        SET nome_popular = 'Angico vermelho'
        WHERE nome_cientifico ILIKE 'Anadenanthera colubrina%'
           OR nome_popular ILIKE '%angico-vermelho%angico-branco%'
           OR nome_popular ILIKE '%angico-branco%angico-vermelho%'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE especies
        SET nome_popular = 'Angico-vermelho, angico-branco'
        WHERE nome_cientifico ILIKE 'Anadenanthera colubrina%'
        """
    )
