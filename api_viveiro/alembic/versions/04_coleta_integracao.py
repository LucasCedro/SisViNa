"""integração coleta: lotes, testes, semeadura, procedência

Revision ID: 004_coleta_integracao
Revises: 003_coletas_sementes
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = "004_coleta_integracao"
down_revision = "003_coletas_sementes"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("arvores_matriz", sa.Column("municipio", sa.String(100), nullable=True))
    op.add_column("arvores_matriz", sa.Column("imovel_nome", sa.String(200), nullable=True))
    op.add_column("arvores_matriz", sa.Column("tipo_origem", sa.String(50), nullable=True))
    op.add_column("arvores_matriz", sa.Column("numero_autorizacao", sa.String(120), nullable=True))
    op.add_column("arvores_matriz", sa.Column("observacoes_legais", sa.Text(), nullable=True))
    op.add_column("arvores_matriz", sa.Column("mes_inicio_frutificacao", sa.SmallInteger(), nullable=True))
    op.add_column("arvores_matriz", sa.Column("mes_fim_frutificacao", sa.SmallInteger(), nullable=True))
    op.add_column("arvores_matriz", sa.Column("estagio_frutificacao", sa.String(80), nullable=True))
    op.add_column("arvores_matriz", sa.Column("fenologia_observacoes", sa.Text(), nullable=True))

    op.create_table(
        "lotes_sementes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo_lote", sa.String(50), nullable=False),
        sa.Column("id_coleta_sementes", sa.Integer(), nullable=False),
        sa.Column("id_arvore_matriz", sa.Integer(), nullable=False),
        sa.Column("id_especie", sa.Integer(), nullable=False),
        sa.Column("quantidade_inicial", sa.Integer(), nullable=False),
        sa.Column("quantidade_disponivel", sa.Integer(), nullable=False),
        sa.Column("data_formacao_lote", sa.Date(), nullable=False),
        sa.Column("beneficiamento", sa.Text(), nullable=True),
        sa.Column("condicoes_armazenamento", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="ativo", nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("data_registro", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["id_coleta_sementes"], ["coletas_sementes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_arvore_matriz"], ["arvores_matriz.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_especie"], ["especies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo_lote"),
    )
    op.create_index("ix_lotes_sementes_matriz", "lotes_sementes", ["id_arvore_matriz"])
    op.create_index("ix_lotes_sementes_coleta", "lotes_sementes", ["id_coleta_sementes"])

    op.create_table(
        "testes_sementes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_lote_sementes", sa.Integer(), nullable=False),
        sa.Column("data_teste", sa.Date(), nullable=False),
        sa.Column("tipo_teste", sa.String(40), nullable=False),
        sa.Column("metodologia", sa.Text(), nullable=True),
        sa.Column("repeticoes", sa.Integer(), server_default="1", nullable=True),
        sa.Column("sementes_avaliadas", sa.Integer(), nullable=True),
        sa.Column("percentual_resultado", sa.Numeric(5, 2), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("id_funcionario", sa.Integer(), nullable=False),
        sa.Column("data_registro", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["id_lote_sementes"], ["lotes_sementes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_funcionario"], ["funcionarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "semeaduras",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_lote_sementes", sa.Integer(), nullable=False),
        sa.Column("id_canteiro", sa.Integer(), nullable=True),
        sa.Column("data_semeadura", sa.Date(), nullable=False),
        sa.Column("quantidade_sementes_usadas", sa.Integer(), nullable=False),
        sa.Column("quantidade_mudas_obtidas", sa.Integer(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("id_funcionario", sa.Integer(), nullable=False),
        sa.Column("data_registro", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["id_lote_sementes"], ["lotes_sementes.id"]),
        sa.ForeignKeyConstraint(["id_canteiro"], ["canteiros.id"]),
        sa.ForeignKeyConstraint(["id_funcionario"], ["funcionarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("plantas", sa.Column("id_lote_sementes", sa.Integer(), nullable=True))
    op.add_column("plantas", sa.Column("id_semeadura", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_plantas_lote", "plantas", "lotes_sementes", ["id_lote_sementes"], ["id"])
    op.create_foreign_key("fk_plantas_semeadura", "plantas", "semeaduras", ["id_semeadura"], ["id"])

    op.execute(
        """
        CREATE OR REPLACE VIEW vw_rastreabilidade_muda AS
        SELECT
            p.id AS id_planta,
            p.codigo_rastreio,
            p.status AS status_planta,
            p.data_plantio,
            e.id AS id_especie,
            COALESCE(e.nome_popular, e.nome_cientifico) AS especie_nome,
            ls.codigo_lote,
            ls.id AS id_lote,
            c.id AS id_coleta,
            c.data_coleta,
            m.id AS id_arvore_matriz,
            m.nome AS matriz_nome,
            m.imovel_nome,
            m.municipio,
            m.tipo_origem,
            m.numero_autorizacao,
            s.id AS id_semeadura,
            s.data_semeadura,
            s.quantidade_sementes_usadas
        FROM plantas p
        LEFT JOIN semeaduras s ON p.id_semeadura = s.id
        LEFT JOIN lotes_sementes ls ON COALESCE(p.id_lote_sementes, s.id_lote_sementes) = ls.id
        LEFT JOIN coletas_sementes c ON ls.id_coleta_sementes = c.id
        LEFT JOIN arvores_matriz m ON ls.id_arvore_matriz = m.id
        LEFT JOIN especies e ON p.id_especie = e.id
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW vw_cadeia_semente_muda_venda AS
        SELECT
            p.id AS id_planta,
            p.codigo_rastreio,
            p.status AS status_planta,
            p.data_plantio,
            ls.codigo_lote,
            m.nome AS matriz_nome,
            c.data_coleta,
            s.data_semeadura,
            iv.id AS id_item_venda,
            iv.quantidade AS qtd_vendida,
            iv.valor_unitario,
            v.id AS id_venda,
            v.data_venda,
            v.status AS status_venda,
            comp.nome AS comprador_nome
        FROM plantas p
        LEFT JOIN semeaduras s ON p.id_semeadura = s.id
        LEFT JOIN lotes_sementes ls ON COALESCE(p.id_lote_sementes, s.id_lote_sementes) = ls.id
        LEFT JOIN coletas_sementes c ON ls.id_coleta_sementes = c.id
        LEFT JOIN arvores_matriz m ON ls.id_arvore_matriz = m.id
        LEFT JOIN itens_venda iv ON iv.id_planta = p.id
        LEFT JOIN vendas v ON v.id = iv.id_venda
        LEFT JOIN compradores comp ON comp.id = v.id_comprador
        """
    )


def downgrade():
    op.execute("DROP VIEW IF EXISTS vw_cadeia_semente_muda_venda")
    op.execute("DROP VIEW IF EXISTS vw_rastreabilidade_muda")
    op.drop_constraint("fk_plantas_semeadura", "plantas", type_="foreignkey")
    op.drop_constraint("fk_plantas_lote", "plantas", type_="foreignkey")
    op.drop_column("plantas", "id_semeadura")
    op.drop_column("plantas", "id_lote_sementes")
    op.drop_table("semeaduras")
    op.drop_table("testes_sementes")
    op.drop_index("ix_lotes_sementes_coleta", table_name="lotes_sementes")
    op.drop_index("ix_lotes_sementes_matriz", table_name="lotes_sementes")
    op.drop_table("lotes_sementes")
    for col in (
        "fenologia_observacoes",
        "estagio_frutificacao",
        "mes_fim_frutificacao",
        "mes_inicio_frutificacao",
        "observacoes_legais",
        "numero_autorizacao",
        "tipo_origem",
        "imovel_nome",
        "municipio",
    ):
        op.drop_column("arvores_matriz", col)
