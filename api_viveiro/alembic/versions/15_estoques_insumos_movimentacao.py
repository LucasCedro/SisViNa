"""Insumos: limites de estoque, valor em estoque e histórico de movimentações.

Revision ID: 15_estoques_insumos_mov
Revises: 14_corrigir_stryphnodendron
"""

from alembic import op
import sqlalchemy as sa

revision = "15_estoques_insumos_mov"
down_revision = "14_corrigir_stryphnodendron"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "insumos",
        sa.Column("estoque_minimo", sa.Numeric(10, 2), server_default="0"),
    )
    op.add_column(
        "insumos",
        sa.Column("estoque_maximo", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "insumos",
        sa.Column("valor_estoque", sa.Numeric(12, 2), server_default="0"),
    )
    op.create_table(
        "insumo_movimentacoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_insumo", sa.Integer(), sa.ForeignKey("insumos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("quantidade", sa.Numeric(10, 2), nullable=False),
        sa.Column("valor_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("preco_unitario", sa.Numeric(10, 4), nullable=True),
        sa.Column("saldo_quantidade", sa.Numeric(10, 2), nullable=False),
        sa.Column("data_movimento", sa.Date(), nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_insumo_mov_id_insumo", "insumo_movimentacoes", ["id_insumo"])
    op.create_index("ix_insumo_mov_data", "insumo_movimentacoes", ["data_movimento"])

    op.execute(
        """
        UPDATE insumos
        SET valor_estoque = COALESCE(quantidade_estoque, 0) * COALESCE(preco_unitario, 0)
        """
    )


def downgrade() -> None:
    op.drop_index("ix_insumo_mov_data", table_name="insumo_movimentacoes")
    op.drop_index("ix_insumo_mov_id_insumo", table_name="insumo_movimentacoes")
    op.drop_table("insumo_movimentacoes")
    op.drop_column("insumos", "valor_estoque")
    op.drop_column("insumos", "estoque_maximo")
    op.drop_column("insumos", "estoque_minimo")
