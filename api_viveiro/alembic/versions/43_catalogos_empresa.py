"""Catálogos operacionais e premissas financeiras escopados por empresa."""

from alembic import op
import sqlalchemy as sa

revision = "43_catalogos_empresa"
down_revision = "42_codigos_unique_viveiro"
branch_labels = None
depends_on = None

DEFAULT_EMPRESA_ID = 1

CATALOG_TABLES = ("tipos_pragas", "metodos_combate", "tipos_atividades", "financeiro_premissas")


def upgrade() -> None:
    for table in CATALOG_TABLES:
        op.add_column(table, sa.Column("id_empresa", sa.Integer(), nullable=True))
        op.execute(f"UPDATE {table} SET id_empresa = {DEFAULT_EMPRESA_ID}")
        op.alter_column(table, "id_empresa", nullable=False)
        op.create_foreign_key(
            f"fk_{table}_id_empresa", table, "empresas", ["id_empresa"], ["id"]
        )
        op.create_index(f"ix_{table}_id_empresa", table, ["id_empresa"])

    op.drop_constraint("tipos_atividades_nome_key", "tipos_atividades", type_="unique")
    op.create_unique_constraint(
        "uq_tipos_atividades_empresa_nome", "tipos_atividades", ["id_empresa", "nome"]
    )

    op.drop_constraint("financeiro_premissas_chave_key", "financeiro_premissas", type_="unique")
    op.create_unique_constraint(
        "uq_fin_premissas_empresa_chave", "financeiro_premissas", ["id_empresa", "chave"]
    )

    op.create_unique_constraint(
        "uq_tipos_pragas_empresa_nome", "tipos_pragas", ["id_empresa", "nome"]
    )
    op.create_unique_constraint(
        "uq_metodos_combate_empresa_nome", "metodos_combate", ["id_empresa", "nome"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_metodos_combate_empresa_nome", "metodos_combate", type_="unique")
    op.drop_constraint("uq_tipos_pragas_empresa_nome", "tipos_pragas", type_="unique")
    op.drop_constraint("uq_fin_premissas_empresa_chave", "financeiro_premissas", type_="unique")
    op.create_unique_constraint(
        "financeiro_premissas_chave_key", "financeiro_premissas", ["chave"]
    )
    op.drop_constraint("uq_tipos_atividades_empresa_nome", "tipos_atividades", type_="unique")
    op.create_unique_constraint("tipos_atividades_nome_key", "tipos_atividades", ["nome"])

    for table in reversed(CATALOG_TABLES):
        op.drop_index(f"ix_{table}_id_empresa", table_name=table)
        op.drop_constraint(f"fk_{table}_id_empresa", table, type_="foreignkey")
        op.drop_column(table, "id_empresa")
