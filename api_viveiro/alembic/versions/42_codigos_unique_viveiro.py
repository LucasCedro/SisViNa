"""codigo_rastreio e codigo_lote únicos por viveiro."""

from alembic import op

revision = "42_codigos_unique_viveiro"
down_revision = "41_insumos_id_empresa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("plantas_codigo_rastreio_key", "plantas", type_="unique")
    op.create_unique_constraint(
        "uq_plantas_viveiro_codigo_rastreio", "plantas", ["id_viveiro", "codigo_rastreio"]
    )
    op.drop_constraint("lotes_sementes_codigo_lote_key", "lotes_sementes", type_="unique")
    op.create_unique_constraint(
        "uq_lotes_viveiro_codigo_lote", "lotes_sementes", ["id_viveiro", "codigo_lote"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_lotes_viveiro_codigo_lote", "lotes_sementes", type_="unique")
    op.create_unique_constraint("lotes_sementes_codigo_lote_key", "lotes_sementes", ["codigo_lote"])
    op.drop_constraint("uq_plantas_viveiro_codigo_rastreio", "plantas", type_="unique")
    op.create_unique_constraint("plantas_codigo_rastreio_key", "plantas", ["codigo_rastreio"])
