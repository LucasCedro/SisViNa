"""Coleta de campo — horas × valor homem-hora no CMV do lote

Revision ID: 31_coleta_custo_campo
Revises: 30_especies_master_chave_gin
"""

from alembic import op
import sqlalchemy as sa

revision = "31_coleta_custo_campo"
down_revision = "30_especies_master_chave_gin"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("coletas_sementes", sa.Column("horas_campo", sa.Numeric(8, 2), nullable=True))
    op.add_column("coletas_sementes", sa.Column("custo_campo_total", sa.Numeric(12, 2), nullable=True))
    op.execute(
        """
        INSERT INTO financeiro_premissas (chave, nome, descricao, natureza, tipo_calculo, unidade, valor, ordem, ativo)
        VALUES (
            'coleta_campo',
            'Mão de obra de coleta',
            'Valor homem-hora (R$/h). Informe as horas em cada coleta; o custo total é rateado pelas sementes do lote.',
            'CUSTO',
            'valor_hora',
            'R$/h',
            0,
            5,
            TRUE
        )
        ON CONFLICT (chave) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM financeiro_premissas WHERE chave = 'coleta_campo'")
    op.drop_column("coletas_sementes", "custo_campo_total")
    op.drop_column("coletas_sementes", "horas_campo")
