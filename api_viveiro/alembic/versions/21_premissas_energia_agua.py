"""Premissas — energia rateada, irrigação vs hidrogel, labels claros

Revision ID: 21_premissas_energia_agua
Revises: 20_premissas_praticas
"""

from alembic import op

revision = "21_premissas_energia_agua"
down_revision = "20_premissas_praticas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Substrato por tubete',
          descricao = 'Material que vai em cada tubete na semeadura — preço médio vem do Estoques.',
          unidade = 'kg ou L / tubete',
          tipo_calculo = 'insumo_medio'
        WHERE chave = 'substrato_tubete'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Irrigação (água de produção)',
          descricao = 'Processo: litros irrigados por muda × tarifa da água (rede ou poço). Não use insumo de substrato aqui.',
          unidade = 'L/muda/dia · R$/L',
          tipo_calculo = 'unitario_x_quantidade',
          id_insumo = NULL
        WHERE chave = 'agua_muda_dia'
        """
    )
    op.execute(
        """
        INSERT INTO financeiro_premissas (chave, nome, descricao, natureza, tipo_calculo, unidade, valor, quantidade, ordem)
        VALUES (
          'hidrogel_tubete',
          'Hidrogel por tubete',
          'Insumo sólido aplicado no tubete — preço médio do item Hidrogel cadastrado em Estoques.',
          'CUSTO',
          'insumo_medio',
          'g ou un. / tubete',
          0,
          0,
          15
        )
        ON CONFLICT (chave) DO UPDATE SET
          nome = EXCLUDED.nome,
          descricao = EXCLUDED.descricao,
          tipo_calculo = EXCLUDED.tipo_calculo,
          unidade = EXCLUDED.unidade,
          ordem = EXCLUDED.ordem
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Energia elétrica — produção',
          descricao = 'Fatura das áreas produtivas (bombas, estufas, irrigação). O sistema divide pelas mudas vivas — não informe kWh por muda.',
          unidade = 'R$/mês',
          tipo_calculo = 'mensal_rateio',
          quantidade = NULL
        WHERE chave = 'cif_energia_muda'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Mão de obra — produção',
          descricao = 'Equipe de campo: número de pessoas × salário médio, rateado pelas mudas vivas.',
          unidade = 'pessoas · R$/mês',
          tipo_calculo = 'pessoas_x_salario_rateio'
        WHERE chave = 'cif_mo_producao_muda'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Energia elétrica — administração',
          descricao = 'Escritório, refeitório administrativo, áreas comuns. Referência na DRE — não entra no custo da muda.',
          unidade = 'R$/mês',
          tipo_calculo = 'mensal'
        WHERE chave = 'energia_fatura_mes'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
          nome = 'Água — administração',
          descricao = 'Fatura da concessionária fora da produção (banheiros, escritório). Referência na DRE.',
          unidade = 'R$/mês',
          tipo_calculo = 'mensal'
        WHERE chave = 'agua_fatura_mes'
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM financeiro_premissas WHERE chave = 'hidrogel_tubete'")
