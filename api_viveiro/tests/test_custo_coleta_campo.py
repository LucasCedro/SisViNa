"""Custo de campo na coleta — rateio no lote de sementes."""

from types import SimpleNamespace

from app.services.custeio import aplicar_custo_campo_no_lote, calcular_custo_coleta_campo


def _lote(inicial: int, disp: int):
    return SimpleNamespace(
        quantidade_inicial=inicial,
        quantidade_disponivel=disp,
        valor_total=None,
        custo_unitario=None,
    )


def test_calcular_custo_coleta_campo():
    total, unit = calcular_custo_coleta_campo(4, 50, 1000)
    assert total == 200
    assert unit == 0.2


def test_aplicar_custo_lote_saldo_integral():
    lote = _lote(500, 500)
    aplicar_custo_campo_no_lote(lote, 200, 500)
    assert lote.valor_total == 200
    assert lote.custo_unitario == 0.4


def test_aplicar_custo_lote_com_consumo_parcial():
    lote = _lote(500, 300)
    aplicar_custo_campo_no_lote(lote, 200, 500)
    assert lote.custo_unitario == 0.4
    assert lote.valor_total == 120.0


def test_aplicar_custo_lote_zera_sem_horas():
    lote = _lote(500, 500)
    lote.valor_total = 99
    lote.custo_unitario = 0.1
    aplicar_custo_campo_no_lote(lote, 0, 500)
    assert lote.valor_total is None
    assert lote.custo_unitario is None
