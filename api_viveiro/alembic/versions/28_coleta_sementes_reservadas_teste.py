"""Reserva de sementes para teste de germinação (fora do lote)."""

from alembic import op
import sqlalchemy as sa

revision = "28_reserva_teste_germ"
down_revision = "27_backfill_perfis_campo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "coletas_sementes",
        sa.Column(
            "sementes_reservadas_teste",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_check_constraint(
        "ck_coletas_sementes_reserva_teste_nonneg",
        "coletas_sementes",
        "sementes_reservadas_teste >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_coletas_sementes_reserva_teste_nonneg", "coletas_sementes", type_="check"
    )
    op.drop_column("coletas_sementes", "sementes_reservadas_teste")
