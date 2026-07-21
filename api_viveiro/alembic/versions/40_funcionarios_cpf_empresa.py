"""CPF único por empresa (multi-tenant SaaS)."""

from alembic import op

revision = "40_funcionarios_cpf_empresa"
down_revision = "39_empresas_saas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("funcionarios_cpf_key", "funcionarios", type_="unique")
    op.create_unique_constraint(
        "uq_funcionarios_empresa_cpf", "funcionarios", ["id_empresa", "cpf"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_funcionarios_empresa_cpf", "funcionarios", type_="unique")
    op.create_unique_constraint("funcionarios_cpf_key", "funcionarios", ["cpf"])
