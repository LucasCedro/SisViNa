"""Premissas CMV — substrato por volume (ml/L), hidrogel em gramas

Revision ID: 34_premissas_unidades_volume
Revises: 33_recipiente_semeadura
"""

from alembic import op

revision = "34_premissas_unidades_volume"
down_revision = "33_recipiente_semeadura"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE financeiro_premissas SET
            nome = 'Substrato por recipiente',
            descricao = 'Volume de substrato por recipiente na semeadura (ml no tubete, litros no saquinho). O peso varia com umidade e mistura — o CMV usa volume × preço do estoque (em L ou kg com densidade).',
            unidade = 'ml/tubete',
            quantidade = CASE WHEN quantidade IS NULL OR quantidade = 1 THEN 50 ELSE quantidade END
        WHERE chave = 'substrato_tubete'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
            nome = 'Hidrogel por recipiente',
            descricao = 'Dosagem em gramas por recipiente (tubete ou saquinho). Deixe 0 se não utilizar.',
            unidade = 'g/recipiente',
            quantidade = COALESCE(quantidade, 0)
        WHERE chave = 'hidrogel_tubete'
        """
    )


def downgrade() -> None:
    pass
