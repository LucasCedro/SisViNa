"""vendas.data_pagamento — regime de caixa no financeiro."""

from alembic import op
import sqlalchemy as sa

revision = "36_venda_data_pagamento"
down_revision = "35_premissas_agua_mo_fatura_mes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("vendas", sa.Column("data_pagamento", sa.DateTime(), nullable=True))
    op.execute(
        "UPDATE vendas SET data_pagamento = data_venda WHERE status = 'PAGO' AND data_pagamento IS NULL"
    )


def downgrade() -> None:
    op.drop_column("vendas", "data_pagamento")
