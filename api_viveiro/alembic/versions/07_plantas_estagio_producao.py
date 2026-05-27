"""estagio_producao em plantas

Revision ID: 07_plantas_estagio_producao
Revises: 06_funcionarios_perfis
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "07_plantas_estagio_producao"
down_revision = "06_funcionarios_perfis"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "plantas",
        sa.Column(
            "estagio_producao",
            sa.String(30),
            nullable=False,
            server_default="em_desenvolvimento",
        ),
    )
    op.create_index("ix_plantas_estagio_producao", "plantas", ["estagio_producao"])

    # SEMENTE na sementeira: em desenvolvimento (não assume aptidão)
    op.execute(
        """
        UPDATE plantas p
        SET estagio_producao = 'em_desenvolvimento'
        FROM canteiros c
        WHERE p.id_canteiro = c.id
          AND c.tipo_local = 'sementeira'
          AND p.status = 'SEMENTE'
        """
    )

    # Muda no canteiro: em crescimento (não assume pronta p/ venda)
    op.execute(
        """
        UPDATE plantas p
        SET estagio_producao = 'em_crescimento'
        FROM canteiros c
        WHERE p.id_canteiro = c.id
          AND c.tipo_local = 'canteiro'
          AND p.status IN ('MUDA', 'JOVEM', 'ADULTA')
        """
    )


def downgrade() -> None:
    op.drop_index("ix_plantas_estagio_producao", table_name="plantas")
    op.drop_column("plantas", "estagio_producao")
