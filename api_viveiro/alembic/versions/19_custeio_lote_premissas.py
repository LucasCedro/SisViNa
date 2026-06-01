"""Premissas financeiras + custo por lote/semeadura

Revision ID: 19_custeio_lote
Revises: 18_item_venda_custo
"""

from alembic import op
import sqlalchemy as sa

revision = "19_custeio_lote"
down_revision = "18_item_venda_custo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "financeiro_premissas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chave", sa.String(60), nullable=False, unique=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column(
            "natureza",
            sa.String(20),
            nullable=False,
            server_default="CUSTO",
        ),
        sa.Column(
            "tipo_calculo",
            sa.String(30),
            nullable=False,
            server_default="por_muda",
        ),
        sa.Column("unidade", sa.String(40), nullable=True),
        sa.Column("valor", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("quantidade", sa.Numeric(12, 4), nullable=True),
        sa.Column("id_insumo", sa.Integer(), sa.ForeignKey("insumos.id"), nullable=True),
        sa.Column("ordem", sa.Integer(), server_default="0"),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("data_atualizacao", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_fin_premissas_natureza", "financeiro_premissas", ["natureza"])

    op.add_column(
        "lotes_sementes",
        sa.Column("valor_total", sa.Numeric(14, 2), nullable=True),
    )
    op.add_column(
        "lotes_sementes",
        sa.Column("custo_unitario", sa.Numeric(12, 4), nullable=True),
    )

    op.add_column(
        "semeaduras",
        sa.Column("custo_sementes", sa.Numeric(12, 2), server_default="0"),
    )
    op.add_column(
        "semeaduras",
        sa.Column("custo_insumos", sa.Numeric(12, 2), server_default="0"),
    )
    op.add_column(
        "semeaduras",
        sa.Column("custo_indireto", sa.Numeric(12, 2), server_default="0"),
    )
    op.add_column(
        "semeaduras",
        sa.Column("custo_total", sa.Numeric(12, 2), server_default="0"),
    )
    op.add_column(
        "semeaduras",
        sa.Column("custo_unitario_muda", sa.Numeric(12, 2), nullable=True),
    )

    op.add_column(
        "plantas",
        sa.Column("custo_inicial", sa.Numeric(10, 2), nullable=True),
    )

    op.execute(
        """
        INSERT INTO financeiro_premissas (chave, nome, descricao, natureza, tipo_calculo, unidade, valor, quantidade, ordem)
        VALUES
        ('substrato_tubete', 'Substrato por tubete', 'Quantidade de substrato (unidade do insumo) por tubete/muda — custo via preço médio do estoque', 'CUSTO', 'insumo_medio', 'un/tubete', 0, 1, 10),
        ('agua_muda_dia', 'Água de irrigação por muda/dia', 'Litros (ou unidade do insumo água) por muda por dia × preço médio', 'CUSTO', 'insumo_medio', 'L/muda/dia', 0, 2, 20),
        ('cif_energia_muda', 'CIF energia por muda', 'Rateio produtivo de energia (R$ por muda produzida no lote) — entra no CMV', 'CUSTO', 'por_muda', 'R$/muda', 0, NULL, 30),
        ('cif_mo_producao_muda', 'Mão de obra produtiva por muda', 'Custo de MO direta/indireta produtiva rateada por muda do lote', 'CUSTO', 'por_muda', 'R$/muda', 0, NULL, 40),
        ('energia_fatura_mes', 'Energia elétrica (fatura)', 'Despesa operacional mensal — entra na DRE, não no CMV', 'DESPESA', 'mensal', 'R$/mês', 0, NULL, 100),
        ('agua_fatura_mes', 'Água (fatura/concessionária)', 'Despesa operacional mensal', 'DESPESA', 'mensal', 'R$/mês', 0, NULL, 110),
        ('salarios_admin_mes', 'Salários administrativos', 'Despesa — não compõe custo da muda', 'DESPESA', 'mensal', 'R$/mês', 0, NULL, 120),
        ('comissao_vendas_pct', 'Comissão de vendas', 'Percentual sobre receita — despesa comercial na DRE', 'DESPESA', 'percentual_receita', '%', 0, NULL, 130)
        ON CONFLICT (chave) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_column("plantas", "custo_inicial")
    op.drop_column("semeaduras", "custo_unitario_muda")
    op.drop_column("semeaduras", "custo_total")
    op.drop_column("semeaduras", "custo_indireto")
    op.drop_column("semeaduras", "custo_insumos")
    op.drop_column("semeaduras", "custo_sementes")
    op.drop_column("lotes_sementes", "custo_unitario")
    op.drop_column("lotes_sementes", "valor_total")
    op.drop_table("financeiro_premissas")
