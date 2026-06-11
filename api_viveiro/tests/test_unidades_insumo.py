import pytest
from types import SimpleNamespace

from app.services.unidades_insumo import (
    consumo_substrato_por_muda,
    custo_insumo_peso,
    custo_insumo_volume,
    custo_substrato_por_recipiente,
    volume_substrato_litros,
)


def _insumo(unidade: str):
    return SimpleNamespace(unidade_medida=unidade, nome="Teste")


def test_volume_tubete_ml_para_litros():
    assert volume_substrato_litros(50, "tubete") == 0.05
    assert volume_substrato_litros(120, "tubete") == 0.12


def test_volume_saquinho_litros():
    assert volume_substrato_litros(0.3, "saquinho") == 0.3


def test_custo_substrato_estoque_em_litros():
    total, det = custo_insumo_volume(0.05, _insumo("L"), 10.0)
    assert total == 0.5
    assert "L ×" in det


def test_custo_substrato_estoque_em_kg_com_densidade():
    total, det = custo_insumo_volume(0.05, _insumo("kg"), 20.0, densidade_kg_l=0.2)
    assert total == 0.2
    assert "kg/L" in det


def test_custo_hidrogel_gramas():
    total, _ = custo_insumo_peso(5, _insumo("g"), 0.02)
    assert total == 0.1


def test_consumo_substrato_kg_em_gramas_premissa():
    qtd, det = consumo_substrato_por_muda(30, "tubete", _insumo("kg"))
    assert qtd == pytest.approx(0.03)
    assert "30" in det


def test_consumo_substrato_litros_tubete():
    qtd, det = consumo_substrato_por_muda(50, "tubete", _insumo("L"))
    assert qtd == 0.05
    assert "L" in det


def test_custo_substrato_kg_sem_densidade():
    total, det = custo_substrato_por_recipiente(30, "tubete", _insumo("kg"), 2.0)
    assert total == pytest.approx(0.06)
    assert "30" in det
