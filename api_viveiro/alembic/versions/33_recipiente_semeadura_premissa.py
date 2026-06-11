"""Configuração tubete vs saquinho nas premissas de CMV

Revision ID: 33_recipiente_semeadura
Revises: 32_reseed_financeiro_premissas
"""

from alembic import op

revision = "33_recipiente_semeadura"
down_revision = "32_reseed_financeiro_premissas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO financeiro_premissas (chave, nome, descricao, natureza, tipo_calculo, unidade, valor, ordem, ativo)
        VALUES (
            'recipiente_semeadura',
            'Recipiente na semeadura',
            'Tubete ou saquinho — define os rótulos e a unidade de referência do substrato e hidrogel no CMV.',
            'CUSTO',
            'config',
            'tubete',
            0,
            8,
            TRUE
        )
        ON CONFLICT (chave) DO UPDATE SET
            nome = EXCLUDED.nome,
            descricao = EXCLUDED.descricao,
            tipo_calculo = EXCLUDED.tipo_calculo,
            ordem = EXCLUDED.ordem,
            ativo = EXCLUDED.ativo
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM financeiro_premissas WHERE chave = 'recipiente_semeadura'")
