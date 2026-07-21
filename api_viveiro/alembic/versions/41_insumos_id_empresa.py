"""Insumos escopados por empresa (estoque compartilhado entre viveiros da mesma empresa)."""

from alembic import op
import sqlalchemy as sa

revision = "41_insumos_id_empresa"
down_revision = "40_funcionarios_cpf_empresa"
branch_labels = None
depends_on = None

DEFAULT_EMPRESA_ID = 1


def upgrade() -> None:
    op.add_column("insumos", sa.Column("id_empresa", sa.Integer(), nullable=True))
    op.execute(f"UPDATE insumos SET id_empresa = {DEFAULT_EMPRESA_ID}")
    op.alter_column("insumos", "id_empresa", nullable=False)
    op.create_foreign_key(
        "fk_insumos_id_empresa", "insumos", "empresas", ["id_empresa"], ["id"]
    )
    op.create_index("ix_insumos_id_empresa", "insumos", ["id_empresa"])
    op.create_unique_constraint("uq_insumos_empresa_nome", "insumos", ["id_empresa", "nome"])


def downgrade() -> None:
    op.drop_constraint("uq_insumos_empresa_nome", "insumos", type_="unique")
    op.drop_index("ix_insumos_id_empresa", table_name="insumos")
    op.drop_constraint("fk_insumos_id_empresa", "insumos", type_="foreignkey")
    op.drop_column("insumos", "id_empresa")
