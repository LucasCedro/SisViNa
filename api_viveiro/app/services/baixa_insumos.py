"""Baixa de insumos ligada a eventos operacionais (ex.: transferência para canteiro)."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.insumos import registrar_movimentacao
from app.models.financeiro_premissa import FinanceiroPremissa
from app.models.insumos import Insumo
from app.schemas.insumos import InsumoMovimentacaoCreate
from app.services.custeio import CHAVE_RECIPIENTE_SEMEADURA, CHAVE_SUBSTRATO
from app.services.unidades_insumo import consumo_substrato_por_muda


async def _obter_recipiente_semeadura(db: AsyncSession) -> str:
    result = await db.execute(
        select(FinanceiroPremissa.unidade).where(
            FinanceiroPremissa.chave == CHAVE_RECIPIENTE_SEMEADURA,
            FinanceiroPremissa.ativo.is_(True),
        )
    )
    unidade = result.scalar_one_or_none()
    return "saquinho" if unidade == "saquinho" else "tubete"


async def baixa_substrato_transferencia_canteiro(
    db: AsyncSession,
    n_mudas: int,
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Saída agregada de substrato ao promover mudas sementeira → canteiro.
    Usa a premissa substrato_tubete (insumo + quantidade por recipiente).
    """
    avisos: List[str] = []
    if n_mudas <= 0:
        return None, avisos

    result = await db.execute(
        select(FinanceiroPremissa).where(
            FinanceiroPremissa.chave == CHAVE_SUBSTRATO,
            FinanceiroPremissa.ativo.is_(True),
        )
    )
    prem = result.scalars().first()
    if not prem or not prem.id_insumo:
        avisos.append(
            "Substrato não baixado: configure o insumo na premissa "
            "Financeiro → Material por recipiente."
        )
        return None, avisos

    qtd_ref = float(prem.quantidade or 0)
    if qtd_ref <= 0:
        avisos.append(
            "Substrato não baixado: informe a quantidade por recipiente "
            "na premissa de substrato (Financeiro)."
        )
        return None, avisos

    insumo = await db.get(Insumo, prem.id_insumo)
    if not insumo:
        avisos.append("Substrato não baixado: insumo vinculado à premissa não encontrado.")
        return None, avisos

    recipiente = await _obter_recipiente_semeadura(db)
    por_muda, det = consumo_substrato_por_muda(qtd_ref, recipiente, insumo)
    if por_muda <= 0:
        avisos.append(f"Substrato não baixado: {det}")
        return None, avisos

    total = round(por_muda * n_mudas, 4)
    saldo = float(insumo.quantidade_estoque or 0)
    unidade = insumo.unidade_medida or "un"
    if total > saldo:
        raise ValueError(
            f"Estoque insuficiente de {insumo.nome}: necessário {total} {unidade}, "
            f"disponível {saldo}. Registre entrada em Estoques ou ajuste a premissa."
        )

    await registrar_movimentacao(
        db,
        insumo.id,
        InsumoMovimentacaoCreate(
            tipo="saida",
            quantidade=total,
            data_movimento=date.today(),
            observacao=(
                f"Transferência sementeira→canteiro — {n_mudas} muda(s) × {det}/muda"
            ),
        ),
    )

    return {
        "insumo_id": insumo.id,
        "insumo_nome": insumo.nome,
        "quantidade": total,
        "unidade": unidade,
        "por_muda": por_muda,
        "detalhe": det,
    }, avisos
