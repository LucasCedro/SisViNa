"""Backfill perfis NULL → ['campo'] para usuários legados."""

from alembic import op

revision = "27_backfill_perfis_campo"
down_revision = "26_repair_schema_skipped"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE funcionarios
        SET perfis = '["campo"]'::json
        WHERE perfis IS NULL OR perfis::text = 'null' OR perfis::text = '[]'
        """
    )


def downgrade() -> None:
    pass
