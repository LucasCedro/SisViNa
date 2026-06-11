"""Reinsere premissas CMV/DRE ausentes (bancos sem seed da migration 19)

Revision ID: 32_reseed_financeiro_premissas
Revises: 31_coleta_custo_campo
"""

from alembic import op

revision = "32_reseed_financeiro_premissas"
down_revision = "31_coleta_custo_campo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO financeiro_premissas (chave, nome, descricao, natureza, tipo_calculo, unidade, valor, quantidade, ordem, ativo)
        VALUES
        (
            'coleta_campo',
            'Mão de obra de coleta',
            'Valor homem-hora (R$/h). Informe as horas em cada coleta; o custo total é rateado pelas sementes do lote.',
            'CUSTO', 'valor_hora', 'R$/h', 0, NULL, 5, TRUE
        ),
        (
            'substrato_tubete',
            'Substrato por tubete',
            'Material que vai em cada tubete na semeadura — preço médio vem do Estoques.',
            'CUSTO', 'insumo_medio', 'kg ou L / tubete', 0, 1, 10, TRUE
        ),
        (
            'hidrogel_tubete',
            'Hidrogel por tubete',
            'Insumo sólido aplicado no tubete — preço médio do item Hidrogel cadastrado em Estoques.',
            'CUSTO', 'insumo_medio', 'g ou un. / tubete', 0, 0, 15, TRUE
        ),
        (
            'agua_muda_dia',
            'Irrigação (água de produção)',
            'Processo: litros irrigados por muda × tarifa da água (rede ou poço). Não use insumo de substrato aqui.',
            'CUSTO', 'unitario_x_quantidade', 'L/muda/dia · R$/L', 0, 2, 20, TRUE
        ),
        (
            'cif_energia_muda',
            'Energia elétrica — produção',
            'Fatura das áreas produtivas (bombas, estufas, irrigação). O sistema divide pelas mudas vivas — não informe kWh por muda.',
            'CUSTO', 'mensal_rateio', 'R$/mês', 0, NULL, 30, TRUE
        ),
        (
            'cif_mo_producao_muda',
            'Mão de obra — produção',
            'Equipe de campo: número de pessoas × salário médio, rateado pelas mudas vivas.',
            'CUSTO', 'pessoas_x_salario_rateio', 'pessoas · R$/mês', 0, NULL, 40, TRUE
        ),
        (
            'energia_fatura_mes',
            'Energia elétrica — administração',
            'Escritório, refeitório administrativo, áreas comuns. Referência na DRE — não entra no custo da muda.',
            'DESPESA', 'mensal', 'R$/mês', 0, NULL, 100, TRUE
        ),
        (
            'agua_fatura_mes',
            'Água — administração',
            'Fatura da concessionária fora da produção (banheiros, escritório). Referência na DRE.',
            'DESPESA', 'mensal', 'R$/mês', 0, NULL, 110, TRUE
        ),
        (
            'salarios_admin_mes',
            'Salários administrativos',
            'Despesa — não compõe custo da muda',
            'DESPESA', 'mensal', 'R$/mês', 0, NULL, 120, TRUE
        ),
        (
            'comissao_vendas_pct',
            'Comissão de vendas',
            'Percentual sobre receita — despesa comercial na DRE',
            'DESPESA', 'percentual_receita', '%', 0, NULL, 130, TRUE
        )
        ON CONFLICT (chave) DO UPDATE SET
            nome = EXCLUDED.nome,
            descricao = EXCLUDED.descricao,
            natureza = EXCLUDED.natureza,
            tipo_calculo = EXCLUDED.tipo_calculo,
            unidade = EXCLUDED.unidade,
            ordem = EXCLUDED.ordem,
            ativo = EXCLUDED.ativo
        """
    )


def downgrade() -> None:
    pass
