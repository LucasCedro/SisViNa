"""empresas SaaS multi-tenant, id_empresa e auditoria cross-tenant."""

from alembic import op
import sqlalchemy as sa

revision = "39_empresas_saas"
down_revision = "38_viveiros_florestal"
branch_labels = None
depends_on = None

DEFAULT_EMPRESA_ID = 1


def upgrade() -> None:
    op.create_table(
        "empresas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("razao_social", sa.String(200), nullable=False),
        sa.Column("nome_fantasia", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("cnpj", sa.String(18)),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("data_cadastro", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("slug", name="uq_empresas_slug"),
    )
    op.execute(
        f"""
        INSERT INTO empresas (id, razao_social, nome_fantasia, slug, ativo)
        VALUES ({DEFAULT_EMPRESA_ID}, 'Brotare Viveiros Ltda', 'Brotare Viveiros', 'brotare', true)
        """
    )
    op.execute("SELECT setval(pg_get_serial_sequence('empresas', 'id'), (SELECT MAX(id) FROM empresas))")

    op.add_column("viveiros", sa.Column("id_empresa", sa.Integer(), nullable=True))
    op.execute(f"UPDATE viveiros SET id_empresa = {DEFAULT_EMPRESA_ID}")
    op.alter_column("viveiros", "id_empresa", nullable=False)
    op.create_foreign_key("fk_viveiros_id_empresa", "viveiros", "empresas", ["id_empresa"], ["id"])
    op.create_index("ix_viveiros_id_empresa", "viveiros", ["id_empresa"])
    op.drop_constraint("uq_viveiros_slug", "viveiros", type_="unique")
    op.create_unique_constraint("uq_viveiros_empresa_slug", "viveiros", ["id_empresa", "slug"])

    op.add_column("funcionarios", sa.Column("id_empresa", sa.Integer(), nullable=True))
    op.execute(f"UPDATE funcionarios SET id_empresa = {DEFAULT_EMPRESA_ID}")
    op.alter_column("funcionarios", "id_empresa", nullable=False)
    op.create_foreign_key("fk_funcionarios_id_empresa", "funcionarios", "empresas", ["id_empresa"], ["id"])
    op.create_index("ix_funcionarios_id_empresa", "funcionarios", ["id_empresa"])

    op.add_column("compradores", sa.Column("id_empresa", sa.Integer(), nullable=True))
    op.execute(f"UPDATE compradores SET id_empresa = {DEFAULT_EMPRESA_ID}")
    op.alter_column("compradores", "id_empresa", nullable=False)
    op.create_foreign_key("fk_compradores_id_empresa", "compradores", "empresas", ["id_empresa"], ["id"])
    op.create_index("ix_compradores_id_empresa", "compradores", ["id_empresa"])
    op.drop_constraint("compradores_cpf_cnpj_key", "compradores", type_="unique")
    op.create_unique_constraint("uq_compradores_empresa_cpf_cnpj", "compradores", ["id_empresa", "cpf_cnpj"])

    op.add_column("lancamentos_financeiros", sa.Column("id_empresa", sa.Integer(), nullable=True))
    op.execute(f"UPDATE lancamentos_financeiros SET id_empresa = {DEFAULT_EMPRESA_ID}")
    op.alter_column("lancamentos_financeiros", "id_empresa", nullable=False)
    op.create_foreign_key(
        "fk_lancamentos_financeiros_id_empresa",
        "lancamentos_financeiros",
        "empresas",
        ["id_empresa"],
        ["id"],
    )
    op.create_index("ix_lancamentos_financeiros_id_empresa", "lancamentos_financeiros", ["id_empresa"])

    op.create_table(
        "auditoria_cross_tenant",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("data_evento", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("id_funcionario", sa.Integer(), sa.ForeignKey("funcionarios.id"), nullable=True),
        sa.Column("usuario", sa.String(50)),
        sa.Column("id_empresa_origem", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=True),
        sa.Column("id_empresa_alvo", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=True),
        sa.Column("id_viveiro_alvo", sa.Integer(), sa.ForeignKey("viveiros.id"), nullable=True),
        sa.Column("acao", sa.String(80), nullable=False),
        sa.Column("recurso_tipo", sa.String(80)),
        sa.Column("recurso_id", sa.Integer()),
        sa.Column("detalhes", sa.JSON()),
        sa.Column("ip_origem", sa.String(45)),
        sa.Column("bloqueado", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.create_index("ix_auditoria_cross_tenant_data", "auditoria_cross_tenant", ["data_evento"])
    op.create_index("ix_auditoria_cross_tenant_empresa_alvo", "auditoria_cross_tenant", ["id_empresa_alvo"])


def downgrade() -> None:
    op.drop_table("auditoria_cross_tenant")

    op.drop_constraint("fk_lancamentos_financeiros_id_empresa", "lancamentos_financeiros", type_="foreignkey")
    op.drop_index("ix_lancamentos_financeiros_id_empresa", "lancamentos_financeiros")
    op.drop_column("lancamentos_financeiros", "id_empresa")

    op.drop_constraint("uq_compradores_empresa_cpf_cnpj", "compradores", type_="unique")
    op.create_unique_constraint("compradores_cpf_cnpj_key", "compradores", ["cpf_cnpj"])
    op.drop_constraint("fk_compradores_id_empresa", "compradores", type_="foreignkey")
    op.drop_index("ix_compradores_id_empresa", "compradores")
    op.drop_column("compradores", "id_empresa")

    op.drop_constraint("fk_funcionarios_id_empresa", "funcionarios", type_="foreignkey")
    op.drop_index("ix_funcionarios_id_empresa", "funcionarios")
    op.drop_column("funcionarios", "id_empresa")

    op.drop_constraint("uq_viveiros_empresa_slug", "viveiros", type_="unique")
    op.create_unique_constraint("uq_viveiros_slug", "viveiros", ["slug"])
    op.drop_constraint("fk_viveiros_id_empresa", "viveiros", type_="foreignkey")
    op.drop_index("ix_viveiros_id_empresa", "viveiros")
    op.drop_column("viveiros", "id_empresa")

    op.drop_table("empresas")
