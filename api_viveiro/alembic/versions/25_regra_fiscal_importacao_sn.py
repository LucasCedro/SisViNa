"""Regras fiscais — importação SN + tipo operação; vendas tipo fiscal

Revision ID: 25_regra_fiscal_importacao_sn
Revises: 24_regra_fiscal_uf_destino_flex
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "25_regra_fiscal_importacao_sn"
down_revision = "24_regra_fiscal_uf_destino_flex"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "regras_fiscais",
        sa.Column("tipo_operacao", sa.String(20), server_default="domestica", nullable=False),
    )
    op.add_column(
        "regras_fiscais",
        sa.Column("icms_origem", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "regras_fiscais",
        sa.Column("aliquota_icms_importacao", sa.Numeric(5, 2), nullable=True),
    )
    op.add_column(
        "vendas",
        sa.Column("tipo_operacao_fiscal", sa.String(20), server_default="domestica", nullable=False),
    )
    op.add_column("notas_fiscais", sa.Column("importacao_snapshot", JSONB(), nullable=True))

    # Exemplo importação SN — INATIVO até contador validar
    op.execute(
        """
        INSERT INTO regras_fiscais (
          nome, ncm, uf_origem, uf_destino, tipo_cliente, tipo_operacao,
          cfop_base, csosn, descricao_produto, natureza_operacao,
          ajustar_cfop_por_uf, icms_origem, aliquota_icms_importacao,
          fundamento_legal, informacoes_complementares, ativo, ordem
        ) VALUES (
          'GO — mudas origem importada (exemplo SN)',
          '06029090', 'GO', 'INTERNA', 'ANY', 'importacao',
          '5101', '400', 'Muda de planta — origem estrangeira', 'Venda de mudas',
          true, 1, 4.00,
          'ICMS importação — Simples Nacional: recolhimento via guia/DAS conforme orientação contábil (validar vigência).',
          'Origem mercadoria estrangeira (icms_origem=1). Não substitui SPED/EFD.',
          false, 20
        )
        """
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM regras_fiscais WHERE nome = 'GO — mudas origem importada (exemplo SN)'"
    )
    op.drop_column("notas_fiscais", "importacao_snapshot")
    op.drop_column("vendas", "tipo_operacao_fiscal")
    op.drop_column("regras_fiscais", "aliquota_icms_importacao")
    op.drop_column("regras_fiscais", "icms_origem")
    op.drop_column("regras_fiscais", "tipo_operacao")
