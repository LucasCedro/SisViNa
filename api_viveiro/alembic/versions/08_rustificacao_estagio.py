"""rustificacao: tipo_local e estagio em_rustificacao

Revision ID: 08_rustificacao_estagio
Revises: 07_plantas_estagio_producao
Create Date: 2026-05-27
"""
from alembic import op

revision = "08_rustificacao_estagio"
down_revision = "07_plantas_estagio_producao"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE canteiros DROP CONSTRAINT IF EXISTS canteiros_tipo_local_check"
    )
    op.execute(
        """
        ALTER TABLE canteiros ADD CONSTRAINT canteiros_tipo_local_check
        CHECK (tipo_local IN ('sementeira', 'canteiro', 'armazem', 'rustificacao'))
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE canteiros DROP CONSTRAINT IF EXISTS canteiros_tipo_local_check"
    )
    op.execute(
        """
        ALTER TABLE canteiros ADD CONSTRAINT canteiros_tipo_local_check
        CHECK (tipo_local IN ('sementeira', 'canteiro', 'armazem'))
        """
    )
