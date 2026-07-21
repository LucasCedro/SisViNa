"""insumo_movimentacoes — status e data de pagamento da compra."""

from alembic import op
import sqlalchemy as sa

revision = "37_insumo_compra_pagamento"
down_revision = "36_venda_data_pagamento"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "insumo_movimentacoes",
        sa.Column("status_pagamento", sa.String(20), nullable=True),
    )
    op.add_column(
        "insumo_movimentacoes",
        sa.Column("data_pagamento", sa.Date(), nullable=True),
    )
    op.execute(
        """
        UPDATE insumo_movimentacoes
        SET status_pagamento = 'PAGO',
            data_pagamento = data_movimento
        WHERE tipo = 'entrada' AND status_pagamento IS NULL
        """
    )


def downgrade() -> None:
    op.drop_column("insumo_movimentacoes", "data_pagamento")
    op.drop_column("insumo_movimentacoes", "status_pagamento")
