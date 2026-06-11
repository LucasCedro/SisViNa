import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financeiro_premissa import FinanceiroPremissa
from app.models.insumos import Insumo
from app.services.baixa_insumos import baixa_substrato_transferencia_canteiro


@pytest.mark.asyncio
async def test_baixa_substrato_transferencia_canteiro(db: AsyncSession):
    insumo = Insumo(
        nome="Substrato teste",
        tipo="Substrato",
        unidade_medida="L",
        quantidade_estoque=100.0,
        preco_unitario=2.0,
        valor_estoque=200.0,
    )
    db.add(insumo)
    await db.flush()

    db.add(
        FinanceiroPremissa(
            chave="recipiente_semeadura",
            nome="Recipiente",
            natureza="CUSTO",
            tipo_calculo="config",
            unidade="tubete",
            valor=0,
            ativo=True,
        )
    )
    db.add(
        FinanceiroPremissa(
            chave="substrato_tubete",
            nome="Substrato",
            natureza="CUSTO",
            tipo_calculo="insumo_medio",
            unidade="ml/tubete",
            valor=0,
            quantidade=30,
            id_insumo=insumo.id,
            ativo=True,
        )
    )
    await db.commit()

    resumo, avisos = await baixa_substrato_transferencia_canteiro(db, n_mudas=10)
    assert not avisos
    assert resumo is not None
    assert resumo["quantidade"] == pytest.approx(0.3)
    assert resumo["por_muda"] == pytest.approx(0.03)

    await db.refresh(insumo)
    assert float(insumo.quantidade_estoque) == pytest.approx(99.7)


@pytest.mark.asyncio
async def test_baixa_substrato_sem_premissa_retorna_aviso(db: AsyncSession):
    resumo, avisos = await baixa_substrato_transferencia_canteiro(db, n_mudas=5)
    assert resumo is None
    assert len(avisos) == 1
