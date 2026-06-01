"""CMV snapshot em itens_venda

Revision ID: 18_item_venda_custo
Revises: 17_viveiro_layout
"""

from alembic import op
import sqlalchemy as sa

revision = "18_item_venda_custo"
down_revision = "17_viveiro_layout"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "itens_venda",
        sa.Column("custo_unitario", sa.Numeric(10, 2), nullable=True),
    )
    op.execute(
        """
        UPDATE itens_venda iv
        SET custo_unitario = COALESCE(p.custo_atual, 0)
        FROM plantas p
        WHERE p.id = iv.id_planta AND iv.custo_unitario IS NULL
        """
    )


def downgrade() -> None:
    op.drop_column("itens_venda", "custo_unitario")
