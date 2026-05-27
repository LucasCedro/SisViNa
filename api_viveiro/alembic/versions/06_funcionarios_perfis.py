"""perfis JSON em funcionarios

Revision ID: 06_funcionarios_perfis
Revises: 05_lancamentos_financeiros
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "06_funcionarios_perfis"
down_revision = "005_lancamentos_financeiros"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("funcionarios", sa.Column("perfis", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("funcionarios", "perfis")
