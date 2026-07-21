"""viveiros multi-unidade, isolamento id_viveiro e módulo florestal."""

from alembic import op
import sqlalchemy as sa

revision = "38_viveiros_florestal"
down_revision = "37_insumo_compra_pagamento"
branch_labels = None
depends_on = None

DEFAULT_VIVEIRO_ID = 1
DEMO_FLORESTAL_ID = 2
FLORESTAL_SLUG = "viveiro-florestal"


def upgrade() -> None:
    op.create_table(
        "viveiros",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("modo_operacao", sa.String(20), nullable=False, server_default="nativo"),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("data_cadastro", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("slug", name="uq_viveiros_slug"),
    )

    op.execute(
        f"""
        INSERT INTO viveiros (id, nome, slug, modo_operacao, ativo)
        VALUES
            ({DEFAULT_VIVEIRO_ID}, 'Viveiro Principal', 'principal', 'nativo', true),
            ({DEMO_FLORESTAL_ID}, 'Viveiro Florestal', '{FLORESTAL_SLUG}', 'florestal', true)
        """
    )
    op.execute("SELECT setval(pg_get_serial_sequence('viveiros', 'id'), (SELECT MAX(id) FROM viveiros))")

    op.create_table(
        "funcionario_viveiros",
        sa.Column("id_funcionario", sa.Integer(), sa.ForeignKey("funcionarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("id_viveiro", sa.Integer(), sa.ForeignKey("viveiros.id", ondelete="CASCADE"), nullable=False),
        sa.PrimaryKeyConstraint("id_funcionario", "id_viveiro"),
    )

    op.execute(
        f"""
        INSERT INTO funcionario_viveiros (id_funcionario, id_viveiro)
        SELECT id, {DEFAULT_VIVEIRO_ID} FROM funcionarios
        """
    )
    op.execute(
        """
        INSERT INTO funcionario_viveiros (id_funcionario, id_viveiro)
        SELECT f.id, 2
        FROM funcionarios f
        WHERE f.usuario IN ('admin', 'demo.admin')
        ON CONFLICT DO NOTHING
        """
    )

    for table in ("canteiros", "plantas", "arvores_matriz", "lotes_sementes", "semeaduras", "vendas"):
        op.add_column(
            table,
            sa.Column("id_viveiro", sa.Integer(), nullable=True, server_default="1"),
        )
        op.execute(f"UPDATE {table} SET id_viveiro = {DEFAULT_VIVEIRO_ID} WHERE id_viveiro IS NULL")
        op.alter_column(table, "id_viveiro", nullable=False, server_default=None)
        op.create_foreign_key(
            f"fk_{table}_id_viveiro",
            table,
            "viveiros",
            ["id_viveiro"],
            ["id"],
        )
        op.create_index(f"ix_{table}_id_viveiro", table, ["id_viveiro"])

    op.add_column("viveiro_layout", sa.Column("id_viveiro", sa.Integer(), nullable=True))
    op.execute(f"UPDATE viveiro_layout SET id_viveiro = {DEFAULT_VIVEIRO_ID}")
    op.alter_column("viveiro_layout", "id_viveiro", nullable=False)
    op.create_foreign_key(
        "fk_viveiro_layout_id_viveiro",
        "viveiro_layout",
        "viveiros",
        ["id_viveiro"],
        ["id"],
    )
    op.create_index("ix_viveiro_layout_id_viveiro", "viveiro_layout", ["id_viveiro"], unique=True)

    op.create_table(
        "genotipos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_viveiro", sa.Integer(), sa.ForeignKey("viveiros.id"), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(100)),
        sa.Column("fornecedor", sa.String(100)),
        sa.Column("material_genetico", sa.String(100)),
        sa.Column("observacoes", sa.Text()),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("data_cadastro", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("id_viveiro", "codigo", name="uq_genotipos_viveiro_codigo"),
    )
    op.create_index("ix_genotipos_id_viveiro", "genotipos", ["id_viveiro"])

    op.create_table(
        "lotes_producao",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_viveiro", sa.Integer(), sa.ForeignKey("viveiros.id"), nullable=False),
        sa.Column("id_genotipo", sa.Integer(), sa.ForeignKey("genotipos.id"), nullable=False),
        sa.Column("codigo_lote", sa.String(30), nullable=False),
        sa.Column("data_entrada", sa.Date(), nullable=False),
        sa.Column("quantidade_inicial", sa.Integer(), nullable=False),
        sa.Column("quantidade_atual", sa.Integer(), nullable=False),
        sa.Column("estagio", sa.String(30), nullable=False, server_default="entrada_material"),
        sa.Column("id_canteiro", sa.Integer(), sa.ForeignKey("canteiros.id")),
        sa.Column("observacoes", sa.Text()),
        sa.Column("data_registro", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("id_viveiro", "codigo_lote", name="uq_lotes_producao_viveiro_codigo"),
    )
    op.create_index("ix_lotes_producao_id_viveiro", "lotes_producao", ["id_viveiro"])
    op.create_index("ix_lotes_producao_estagio", "lotes_producao", ["estagio"])

    op.create_table(
        "movimentacoes_lote",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_lote_producao", sa.Integer(), sa.ForeignKey("lotes_producao.id"), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("estagio_origem", sa.String(30)),
        sa.Column("estagio_destino", sa.String(30)),
        sa.Column("id_canteiro_origem", sa.Integer(), sa.ForeignKey("canteiros.id")),
        sa.Column("id_canteiro_destino", sa.Integer(), sa.ForeignKey("canteiros.id")),
        sa.Column("id_funcionario", sa.Integer(), sa.ForeignKey("funcionarios.id"), nullable=False),
        sa.Column("observacoes", sa.Text()),
        sa.Column("data_movimento", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_movimentacoes_lote_id_lote", "movimentacoes_lote", ["id_lote_producao"])


def downgrade() -> None:
    op.drop_table("movimentacoes_lote")
    op.drop_table("lotes_producao")
    op.drop_table("genotipos")

    op.drop_constraint("fk_viveiro_layout_id_viveiro", "viveiro_layout", type_="foreignkey")
    op.drop_index("ix_viveiro_layout_id_viveiro", "viveiro_layout")
    op.drop_column("viveiro_layout", "id_viveiro")

    for table in reversed(("vendas", "semeaduras", "lotes_sementes", "arvores_matriz", "plantas", "canteiros")):
        op.drop_constraint(f"fk_{table}_id_viveiro", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_id_viveiro", table)
        op.drop_column(table, "id_viveiro")

    op.drop_table("funcionario_viveiros")
    op.drop_table("viveiros")
