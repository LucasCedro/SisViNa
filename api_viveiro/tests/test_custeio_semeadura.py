"""Rateio de CIF — parque inteiro, não por lote isolado."""

from app.models.financeiro_premissa import FinanceiroPremissa
from app.services.custeio import _base_rateio_mudas, _custo_premissa_item


def _prem_mensal(valor: float) -> FinanceiroPremissa:
    return FinanceiroPremissa(
        chave="cif_mo_producao_muda",
        nome="Mão de obra — produção",
        natureza="CUSTO",
        tipo_calculo="mensal_rateio",
        valor=valor,
        ativo=True,
    )


def test_base_rateio_usa_parque_total():
    assert _base_rateio_mudas(100, 200) == 300
    assert _base_rateio_mudas(0, 100) == 100


def test_mensal_rateio_parque_300_mudas():
    prem = _prem_mensal(19125.0)
    total, detalhe = _custo_premissa_item(prem, None, qtd_mudas=100, mudas_base_rateio=300)
    assert total == round(19125 / 300 * 100, 2)
    assert "÷ 300 mudas no parque" in detalhe
    assert "× 100" not in detalhe


def test_mensal_rateio_mesma_unidade_independente_especie():
    prem = _prem_mensal(19125.0)
    _, detalhe_angico = _custo_premissa_item(prem, None, qtd_mudas=100, mudas_base_rateio=300)
    _, detalhe_ipe = _custo_premissa_item(prem, None, qtd_mudas=200, mudas_base_rateio=300)
    assert "63.7500/muda" in detalhe_angico
    assert "63.7500/muda" in detalhe_ipe
