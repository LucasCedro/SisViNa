"""CMV: água e MO por fatura/folha mensal (sem tarifa L nem salário médio)

Revision ID: 35_premissas_agua_mo_fatura_mes
Revises: 34_premissas_unidades_volume
"""

from alembic import op

revision = "35_premissas_agua_mo_fatura_mes"
down_revision = "34_premissas_unidades_volume"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE financeiro_premissas SET
            nome = 'Água — produção (irrigação)',
            descricao = 'Valor pago no mês com água das áreas produtivas (conta Saneago, poço ou caminhão-pipa). Rateio automático pelas mudas vivas — não use tarifa por litro (faixas e taxa mínima da concessionária). Opcional: litros/muda/mês só como referência operacional.',
            tipo_calculo = 'mensal_rateio',
            unidade = 'R$/mês',
            valor = COALESCE(valor, 0)
        WHERE chave = 'agua_muda_dia'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
            nome = 'Mão de obra — produção',
            descricao = 'Folha mensal total da equipe de campo (salários + encargos pagos no mês). Rateada automaticamente pelas mudas vivas.',
            tipo_calculo = 'mensal_rateio',
            unidade = 'R$/mês',
            quantidade = NULL,
            valor = CASE
                WHEN quantidade IS NOT NULL AND quantidade > 0 AND valor > 0
                    THEN quantidade * valor
                ELSE COALESCE(valor, 0)
            END
        WHERE chave = 'cif_mo_producao_muda'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
            descricao = 'Valor da fatura paga no mês (bombas, estufas, iluminação do viveiro). Rateio pelas mudas vivas. Não inclua escritório — use a despesa de administração na DRE.'
        WHERE chave = 'cif_energia_muda'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
            descricao = 'Valor pago no mês — escritório, refeitório e áreas comuns. Referência na DRE; não compõe CMV.'
        WHERE chave = 'energia_fatura_mes'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
            descricao = 'Valor pago no mês — consumo fora da produção de mudas (banheiros, escritório). Referência na DRE; não compõe CMV.'
        WHERE chave = 'agua_fatura_mes'
        """
    )
    op.execute(
        """
        UPDATE financeiro_premissas SET
            descricao = 'Folha mensal total paga à equipe administrativa (gestão, financeiro, vendas). Referência na DRE; não compõe CMV.'
        WHERE chave = 'salarios_admin_mes'
        """
    )


def downgrade() -> None:
    pass
