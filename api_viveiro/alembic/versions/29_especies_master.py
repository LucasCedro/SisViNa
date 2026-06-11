"""Tabela master imutável — referência taxonômica JBRJ (ETL, não editável pelo ERP)."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

revision = "29_especies_master"
down_revision = "28_reserva_teste_germ"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "especies_master",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("taxon_id_jbrj", sa.Integer(), nullable=True),
        sa.Column("nome_cientifico", sa.String(150), nullable=False),
        sa.Column("familia", sa.String(80), nullable=True),
        sa.Column("nomes_populares", ARRAY(sa.Text()), server_default="{}", nullable=False),
        sa.Column("biomas", ARRAY(sa.Text()), server_default="{}", nullable=False),
        sa.Column("estados_ocorrencia", ARRAY(sa.Text()), server_default="{}", nullable=False),
        sa.Column("status_ameaca", sa.String(120), nullable=True),
        sa.Column("meses_floracao", ARRAY(sa.Integer()), server_default="{}", nullable=False),
        sa.Column("meses_frutificacao", ARRAY(sa.Integer()), server_default="{}", nullable=False),
        sa.Column("forma_vida", ARRAY(sa.Text()), server_default="{}", nullable=False),
        sa.Column("habitat", ARRAY(sa.Text()), server_default="{}", nullable=False),
        sa.Column("notas_origem", sa.Text(), nullable=True),
        sa.Column("fonte", sa.String(40), server_default="JBRJ_FLORA", nullable=False),
        sa.Column("sincronizado_em", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_especies_master_taxon_jbrj", "especies_master", ["taxon_id_jbrj"], unique=True)
    op.create_index("ix_especies_master_nome_cientifico", "especies_master", ["nome_cientifico"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_especies_master_nome_cientifico", table_name="especies_master")
    op.drop_index("ix_especies_master_taxon_jbrj", table_name="especies_master")
    op.drop_table("especies_master")
