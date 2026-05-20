"""lancamentos financeiros e view resumo

Revision ID: 005_lancamentos_financeiros
Revises: 004_coleta_integracao
"""
from alembic import op
import sqlalchemy as sa

revision = "005_lancamentos_financeiros"
down_revision = "004_coleta_integracao"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "lancamentos_financeiros",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(10), nullable=False),
        sa.Column("descricao", sa.String(200), nullable=False),
        sa.Column("categoria", sa.String(80), nullable=False),
        sa.Column("data_lancamento", sa.Date(), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        sa.Column("forma_pagamento", sa.String(40), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("id_funcionario", sa.Integer(), nullable=True),
        sa.Column("data_registro", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["id_funcionario"], ["funcionarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("tipo IN ('CAPEX', 'OPEX')", name="check_lancamento_tipo"),
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW vw_resumo_financeiro AS
        SELECT
            (SELECT COALESCE(SUM(valor), 0) FROM lancamentos_financeiros WHERE tipo = 'CAPEX') AS total_capex,
            (SELECT COALESCE(SUM(valor), 0) FROM lancamentos_financeiros WHERE tipo = 'OPEX') AS total_opex,
            (SELECT COALESCE(SUM(valor_total), 0) FROM vendas WHERE status = 'PAGO') AS receita_vendas_paga,
            (SELECT COALESCE(SUM(valor_total), 0) FROM vendas WHERE status = 'PAGO'
                AND date_trunc('month', data_venda) = date_trunc('month', CURRENT_TIMESTAMP)) AS receita_mes_atual,
            (SELECT COALESCE(SUM(custo_atividade), 0) FROM atividades) AS custo_atividades,
            (SELECT COALESCE(SUM(custo_total), 0) FROM combates_realizados) AS custo_fitossanidade,
            (SELECT COALESCE(SUM(custo_atual), 0) FROM plantas WHERE status NOT IN ('VENDIDA', 'MORTA')) AS custo_estoque_mudas,
            (SELECT COUNT(*) FROM plantas WHERE status NOT IN ('VENDIDA', 'MORTA')) AS mudas_ativas
        """
    )


def downgrade():
    op.execute("DROP VIEW IF EXISTS vw_resumo_financeiro")
    op.drop_table("lancamentos_financeiros")
