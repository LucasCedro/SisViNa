"""Remove espécies legado (fora da biblioteca) e colunas de origem/página.

Revision ID: 12_limpar_especies_legado
Revises: 11_biblioteca_enriquecer_manual
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa


revision = "12_limpar_especies_legado"
down_revision = "11_biblioteca_enriquecer_manual"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    ids_sql = "1, 2, 3"

    bind.execute(
        sa.text(
            f"""
            DELETE FROM coletas_sementes
            WHERE id_arvore_matriz IN (
                SELECT id FROM arvores_matriz WHERE id_especie IN ({ids_sql})
            )
            """
        )
    )
    bind.execute(
        sa.text(
            f"""
            DELETE FROM testes_sementes
            WHERE id_lote_sementes IN (
                SELECT id FROM lotes_sementes WHERE id_especie IN ({ids_sql})
            )
            """
        )
    )
    bind.execute(
        sa.text(
            f"""
            DELETE FROM semeaduras
            WHERE id_lote_sementes IN (
                SELECT id FROM lotes_sementes WHERE id_especie IN ({ids_sql})
            )
            """
        )
    )
    bind.execute(sa.text(f"DELETE FROM lotes_sementes WHERE id_especie IN ({ids_sql})"))
    bind.execute(sa.text(f"DELETE FROM arvores_matriz WHERE id_especie IN ({ids_sql})"))
    bind.execute(sa.text(f"DELETE FROM especies_ficha_embrapa WHERE id_especie IN ({ids_sql})"))
    bind.execute(sa.text(f"DELETE FROM especies WHERE id IN ({ids_sql})"))

    op.drop_column("especies_biblioteca", "pagina_manual")
    op.drop_column("especies_biblioteca", "origem_manual")

    bind.execute(sa.text("UPDATE viveiro_regras_globais SET fonte = 'SisViNa'"))
    bind.execute(sa.text("UPDATE especies_ficha_embrapa SET fonte = 'SisViNa'"))


def downgrade() -> None:
    op.add_column(
        "especies_biblioteca",
        sa.Column("pagina_manual", sa.Integer(), nullable=True),
    )
    op.add_column(
        "especies_biblioteca",
        sa.Column(
            "origem_manual",
            sa.String(200),
            nullable=False,
            server_default="SisViNa",
        ),
    )
