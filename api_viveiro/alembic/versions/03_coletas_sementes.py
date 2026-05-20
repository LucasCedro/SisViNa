"""coletas de sementes por matriz

Revision ID: 003_coletas_sementes
Revises: 002_arvores_matriz
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = "003_coletas_sementes"
down_revision = "002_arvores_matriz"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "coletas_sementes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_arvore_matriz", sa.Integer(), nullable=False),
        sa.Column("id_funcionario", sa.Integer(), nullable=False),
        sa.Column("data_coleta", sa.Date(), nullable=False),
        sa.Column("quantidade_sementes", sa.Integer(), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("data_registro", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["id_arvore_matriz"], ["arvores_matriz.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_funcionario"], ["funcionarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_coletas_sementes_id", "coletas_sementes", ["id"])
    op.create_index("ix_coletas_sementes_matriz", "coletas_sementes", ["id_arvore_matriz"])
    op.create_index("ix_coletas_sementes_data", "coletas_sementes", ["data_coleta"])

    op.execute(
        """
        INSERT INTO coletas_sementes (id_arvore_matriz, id_funcionario, data_coleta, quantidade_sementes, observacoes)
        SELECT
            m.id,
            (SELECT f.id FROM funcionarios f WHERE f.ativo = true ORDER BY f.id LIMIT 1),
            m.data_ultima_coleta,
            m.sementes_coletadas,
            'Registro migrado do cadastro da matriz'
        FROM arvores_matriz m
        WHERE m.data_ultima_coleta IS NOT NULL
          AND COALESCE(m.sementes_coletadas, 0) > 0
          AND EXISTS (SELECT 1 FROM funcionarios f WHERE f.ativo = true)
        """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW vw_coletas_sementes_bi AS
        SELECT
            c.id,
            c.data_coleta,
            c.quantidade_sementes,
            c.observacoes,
            c.data_registro,
            m.id AS id_arvore_matriz,
            m.nome AS matriz_nome,
            m.cidade,
            m.estado,
            e.id AS id_especie,
            COALESCE(e.nome_popular, e.nome_cientifico) AS especie_nome,
            f.id AS id_funcionario,
            f.nome AS funcionario_nome
        FROM coletas_sementes c
        INNER JOIN arvores_matriz m ON c.id_arvore_matriz = m.id
        INNER JOIN especies e ON m.id_especie = e.id
        INNER JOIN funcionarios f ON c.id_funcionario = f.id
        """
    )


def downgrade():
    op.execute("DROP VIEW IF EXISTS vw_coletas_sementes_bi")
    op.drop_index("ix_coletas_sementes_data", table_name="coletas_sementes")
    op.drop_index("ix_coletas_sementes_matriz", table_name="coletas_sementes")
    op.drop_index("ix_coletas_sementes_id", table_name="coletas_sementes")
    op.drop_table("coletas_sementes")
