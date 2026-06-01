"""Premissas — labels e tipos práticos para o gerente

Revision ID: 20_premissas_praticas
Revises: 19_custeio_lote
"""

from alembic import op

revision = "20_premissas_praticas"
down_revision = "19_custeio_lote"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Substrato por tubete',
          descricao = 'Quantidade por tubete — o preço vem do estoque (média móvel)',
          unidade = 'g/tubete',
          tipo_calculo = 'insumo_medio'
        WHERE chave = 'substrato_tubete'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Água de irrigação',
          descricao = 'Litros por muda por dia — preço do insumo ou tarifa R$/L',
          unidade = 'L/muda/dia',
          tipo_calculo = 'insumo_medio'
        WHERE chave = 'agua_muda_dia'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Energia elétrica (produção)',
          descricao = 'Tarifa kWh × consumo por muda — entra no custo do lote',
          unidade = 'R$/kWh · kWh/muda',
          tipo_calculo = 'unitario_x_quantidade'
        WHERE chave = 'cif_energia_muda'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Mão de obra produtiva',
          descricao = 'Nº funcionários × salário — rateado pelas mudas vivas',
          unidade = 'pessoas · R$/salário',
          tipo_calculo = 'pessoas_x_salario_rateio'
        WHERE chave = 'cif_mo_producao_muda'
        """
    )


def downgrade() -> None:
    pass
