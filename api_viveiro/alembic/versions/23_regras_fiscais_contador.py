"""Regras fiscais — parâmetros definidos pelo contador (cockpit)

Revision ID: 23_regras_fiscais_contador
Revises: 22_nfe_fiscal
"""

from alembic import op
import sqlalchemy as sa

revision = "23_regras_fiscais_contador"
down_revision = "22_nfe_fiscal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("regras_fiscais", sa.Column("nome", sa.String(120), nullable=True))
    op.add_column(
        "regras_fiscais",
        sa.Column("ajustar_cfop_por_uf", sa.Boolean(), server_default=sa.text("true")),
    )
    op.add_column(
        "regras_fiscais",
        sa.Column("isento_icms", sa.Boolean(), server_default=sa.text("false")),
    )
    op.add_column("regras_fiscais", sa.Column("reducao_bc_icms_percent", sa.Numeric(5, 2)))
    op.add_column("regras_fiscais", sa.Column("fundamento_legal", sa.Text()))
    op.add_column("regras_fiscais", sa.Column("informacoes_complementares", sa.Text()))
    op.add_column("regras_fiscais", sa.Column("pis_situacao_tributaria", sa.String(3)))
    op.add_column("regras_fiscais", sa.Column("cofins_situacao_tributaria", sa.String(3)))
    op.add_column("regras_fiscais", sa.Column("local_destino", sa.Integer()))
    op.add_column("regras_fiscais", sa.Column("cbenef", sa.String(10)))

    # Exemplo GO — INATIVO até o contador validar (não é parecer fiscal do sistema)
    op.execute(
        """
        INSERT INTO regras_fiscais (
          nome, ncm, uf_origem, uf_destino, tipo_cliente, cfop_base, csosn,
          descricao_produto, natureza_operacao, ajustar_cfop_por_uf,
          isento_icms, reducao_bc_icms_percent, fundamento_legal,
          informacoes_complementares, ativo, ordem
        ) VALUES (
          'GO interno — muda (exemplo contador)',
          '06029090', 'GO', 'GO', 'ANY', '5101', '400',
          'Muda de planta', 'Venda de mudas', true,
          true, NULL,
          'RCTE-GO Anexo IX Art. 7º h) — isenção (validar vigência e requisitos com contador)',
          'Benefício fiscal configurado pelo contador. Não substitui parecer.',
          false, 10
        ),
        (
          'GO interestadual — muda (exemplo contador)',
          '06029090', 'GO', '*', 'ANY', '6101', '400',
          'Muda de planta', 'Venda de mudas', true,
          false, 60.00,
          'Conv. ICMS 100/97 cl. 1 VIII — redução 60%% BC interestadual (validar com contador)',
          'Redução de BC conforme parametrização do contador.',
          false, 11
        )
        """
    )
    op.execute(
        """
        UPDATE regras_fiscais SET ativo = false, observacao = COALESCE(observacao, '')
          || ' [desativada — usar regras do contador]'
        WHERE nome IS NULL
        """
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM regras_fiscais WHERE nome LIKE 'GO % — muda (exemplo contador)'"
    )
    op.drop_column("regras_fiscais", "cbenef")
    op.drop_column("regras_fiscais", "local_destino")
    op.drop_column("regras_fiscais", "cofins_situacao_tributaria")
    op.drop_column("regras_fiscais", "pis_situacao_tributaria")
    op.drop_column("regras_fiscais", "informacoes_complementares")
    op.drop_column("regras_fiscais", "fundamento_legal")
    op.drop_column("regras_fiscais", "reducao_bc_icms_percent")
    op.drop_column("regras_fiscais", "isento_icms")
    op.drop_column("regras_fiscais", "ajustar_cfop_por_uf")
    op.drop_column("regras_fiscais", "nome")
