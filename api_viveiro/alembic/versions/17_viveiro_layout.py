"""viveiro_layout — planta baixa persistida

Revision ID: 17
Revises: 16
"""

from alembic import op
import sqlalchemy as sa

revision = "17_viveiro_layout"
down_revision = "16_corrigir_angico"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "viveiro_layout",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("layout_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column(
            "atualizado_em",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
    )
    op.execute("INSERT INTO viveiro_layout (id, layout_json) VALUES (1, '{}')")


def downgrade() -> None:
    op.drop_table("viveiro_layout")
