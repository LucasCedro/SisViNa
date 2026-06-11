"""Custeio por lote — premissas de CUSTO vs DESPESA (contabilidade gerencial)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financeiro_premissa import FinanceiroPremissa

CHAVE_PREMISSA_COLETA_CAMPO = "coleta_campo"
CHAVE_RECIPIENTE_SEMEADURA = "recipiente_semeadura"
CHAVE_SUBSTRATO = "substrato_tubete"
CHAVE_HIDROGEL = "hidrogel_tubete"

from app.models.insumos import Insumo
from app.services.unidades_insumo import (
    custo_insumo_peso,
    custo_substrato_por_recipiente,
)
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta


def preco_medio_insumo(insumo: Insumo) -> float:
    qtd = float(insumo.quantidade_estoque or 0)
    valor = float(insumo.valor_estoque or 0)
    if qtd > 0 and valor > 0:
        return valor / qtd
    return float(insumo.preco_unitario or 0)


def calcular_custo_sementes_lote(lote: LoteSementes, qtd_usada: int) -> float:
    """Baixa proporcional do valor restante do lote (média por unidade disponível)."""
    disp = int(lote.quantidade_disponivel or 0)
    if disp <= 0 or qtd_usada <= 0:
        return 0.0
    valor_restante = float(lote.valor_total or 0)
    if valor_restante <= 0:
        cu = float(lote.custo_unitario or 0)
        return round(cu * qtd_usada, 2)
    cu = valor_restante / disp
    return round(cu * qtd_usada, 2)


def aplicar_baixa_valor_lote(lote: LoteSementes, qtd_usada: int, custo: float) -> None:
    if float(lote.valor_total or 0) > 0:
        lote.valor_total = max(0, float(lote.valor_total) - custo)
    disp_antes = int(lote.quantidade_disponivel or 0)
    if disp_antes > 0 and lote.valor_total and float(lote.valor_total) > 0:
        restante = int(lote.quantidade_disponivel or 0) - qtd_usada
        if restante > 0:
            lote.custo_unitario = float(lote.valor_total) / restante
        else:
            lote.custo_unitario = 0


async def obter_valor_hora_coleta_campo(db: AsyncSession) -> float:
    result = await db.execute(
        select(FinanceiroPremissa).where(
            FinanceiroPremissa.chave == CHAVE_PREMISSA_COLETA_CAMPO,
            FinanceiroPremissa.ativo.is_(True),
            FinanceiroPremissa.natureza == "CUSTO",
        )
    )
    prem = result.scalars().first()
    if not prem:
        return 0.0
    return float(prem.valor or 0)


def calcular_custo_coleta_campo(
    horas: Optional[float], valor_hora: float, qtd_sementes_lote: int
) -> Tuple[float, float]:
    """Retorna (custo_total, custo_unitario_semente). Rateio pelo lote comercial."""
    h = float(horas or 0)
    vh = float(valor_hora or 0)
    qtd = int(qtd_sementes_lote or 0)
    if h <= 0 or vh <= 0 or qtd <= 0:
        return 0.0, 0.0
    total = round(h * vh, 2)
    unit = round(total / qtd, 4)
    return total, unit


def definir_valor_lote_entrada(lote: LoteSementes, valor_total: Optional[float]) -> None:
    if valor_total is None or valor_total <= 0:
        return
    lote.valor_total = float(valor_total)
    qtd = int(lote.quantidade_inicial or 0)
    if qtd > 0:
        lote.custo_unitario = float(valor_total) / qtd


async def _contar_mudas_vivas(db: AsyncSession) -> int:
    return int(
        (
            await db.execute(
                select(func.count(Planta.id)).where(Planta.status.notin_(("VENDIDA", "MORTA")))
            )
        ).scalar()
        or 0
    )


async def _obter_recipiente_semeadura(db: AsyncSession) -> str:
    result = await db.execute(
        select(FinanceiroPremissa.unidade).where(
            FinanceiroPremissa.chave == CHAVE_RECIPIENTE_SEMEADURA,
            FinanceiroPremissa.ativo.is_(True),
        )
    )
    unidade = result.scalar_one_or_none()
    if unidade == "saquinho":
        return "saquinho"
    return "tubete"


async def _premissas_custo_ativas(db: AsyncSession) -> List[FinanceiroPremissa]:
    result = await db.execute(
        select(FinanceiroPremissa)
        .where(FinanceiroPremissa.ativo.is_(True), FinanceiroPremissa.natureza == "CUSTO")
        .order_by(FinanceiroPremissa.ordem, FinanceiroPremissa.id)
    )
    return list(result.scalars().all())


def _custo_premissa_item(
    prem: FinanceiroPremissa,
    insumo: Optional[Insumo],
    qtd_mudas: int,
    mudas_vivas: int = 1,
    recipiente: str = "tubete",
) -> Tuple[float, str]:
    tipo = (prem.tipo_calculo or "").lower()
    qtd_mudas = max(qtd_mudas, 1)
    mudas_vivas = max(mudas_vivas, 1)

    if tipo == "config":
        return 0.0, ""

    if tipo == "insumo_medio":
        chave = (prem.chave or "").lower()
        qtd_ref = float(prem.quantidade or 0)
        if qtd_ref <= 0:
            return 0.0, f"{prem.nome}: informe a quantidade por recipiente"

        if not insumo:
            return 0.0, f"{prem.nome}: selecione o insumo no estoque"

        pu = preco_medio_insumo(insumo)
        if pu <= 0:
            return 0.0, f"{prem.nome}: registre entrada do insumo em Estoques"

        if chave == CHAVE_SUBSTRATO:
            por_rec, det = custo_substrato_por_recipiente(qtd_ref, recipiente, insumo, pu)
            if por_rec <= 0:
                return 0.0, f"{prem.nome}: {det}"
            total = round(por_rec * qtd_mudas, 2)
            return total, f"{prem.nome}: {det} × {qtd_mudas} mudas"

        if chave == CHAVE_HIDROGEL:
            por_rec, det = custo_insumo_peso(qtd_ref, insumo, pu)
            if por_rec <= 0:
                return 0.0, f"{prem.nome}: {det or 'informe dosagem em gramas'}"
            total = round(por_rec * qtd_mudas, 2)
            return total, f"{prem.nome}: {det} × {qtd_mudas} mudas"

        total = round(qtd_ref * pu * qtd_mudas, 2)
        return total, f"{prem.nome}: {qtd_ref} × R$ {pu:.4f} × {qtd_mudas} mudas"

    if tipo == "unitario_x_quantidade":
        tarifa = float(prem.valor or 0)
        qtd_ref = float(prem.quantidade or 0)
        if tarifa <= 0 or qtd_ref <= 0:
            return 0.0, f"{prem.nome}: informe tarifa e quantidade por muda"
        por_muda = tarifa * qtd_ref
        total = round(por_muda * qtd_mudas, 2)
        return total, f"{prem.nome}: R$ {tarifa:.4f} × {qtd_ref} × {qtd_mudas} mudas"

    if tipo == "pessoas_x_salario_rateio":
        n = float(prem.quantidade or 0)
        sal = float(prem.valor or 0)
        if n <= 0 or sal <= 0:
            return 0.0, f"{prem.nome}: informe funcionários e salário"
        mensal = n * sal
        por_muda = mensal / mudas_vivas
        total = round(por_muda * qtd_mudas, 2)
        return (
            total,
            f"{prem.nome}: {n:.0f} × R$ {sal:.2f}/mês ÷ {mudas_vivas} mudas × {qtd_mudas}",
        )

    if tipo == "por_muda":
        vu = float(prem.valor or 0)
        total = round(vu * qtd_mudas, 2)
        return total, f"{prem.nome}: R$ {vu:.2f}/muda × {qtd_mudas}"

    if tipo == "por_lote":
        total = round(float(prem.valor or 0), 2)
        return total, f"{prem.nome}: R$ {total:.2f}/lote"

    if tipo == "mensal_rateio":
        mensal = float(prem.valor or 0)
        if mensal <= 0:
            return 0.0, f"{prem.nome}: informe a fatura mensal da produção"
        por_muda = mensal / mudas_vivas
        total = round(por_muda * qtd_mudas, 2)
        return (
            total,
            f"{prem.nome}: R$ {mensal:.2f}/mês ÷ {mudas_vivas} mudas × {qtd_mudas}",
        )

    return 0.0, f"{prem.nome}: tipo não aplicável ao lote"


async def calcular_custo_lote_semeadura(
    db: AsyncSession,
    lote: LoteSementes,
    qtd_sementes: int,
    qtd_mudas: int,
) -> Dict[str, Any]:
    """Custo total do lote de semeadura rateado por número de mudas."""
    qtd_mudas = max(int(qtd_mudas or 0), 0)
    if qtd_mudas <= 0:
        qtd_mudas = 1

    custo_sementes = calcular_custo_sementes_lote(lote, qtd_sementes)
    itens: List[dict] = [
        {
            "origem": "sementes",
            "descricao": f"Lote {lote.codigo_lote}",
            "valor": custo_sementes,
        }
    ]

    custo_insumos = 0.0
    custo_indireto = 0.0

    mudas_vivas = await _contar_mudas_vivas(db)
    recipiente = await _obter_recipiente_semeadura(db)
    premissas = await _premissas_custo_ativas(db)
    for prem in premissas:
        insumo = None
        if prem.id_insumo:
            insumo = await db.get(Insumo, prem.id_insumo)
        valor_item, detalhe = _custo_premissa_item(
            prem, insumo, qtd_mudas, mudas_vivas, recipiente
        )
        if valor_item <= 0:
            continue
        itens.append({"origem": "premissa", "chave": prem.chave, "descricao": detalhe, "valor": valor_item})
        chave = (prem.chave or "").lower()
        if prem.tipo_calculo in ("insumo_medio", "unitario_x_quantidade") or "substrato" in chave or "hidrogel" in chave:
            custo_insumos += valor_item
        else:
            custo_indireto += valor_item

    custo_total = round(custo_sementes + custo_insumos + custo_indireto, 2)
    custo_unitario = round(custo_total / qtd_mudas, 2) if qtd_mudas else None

    return {
        "custo_sementes": custo_sementes,
        "custo_insumos": custo_insumos,
        "custo_indireto": custo_indireto,
        "custo_total": custo_total,
        "custo_unitario_muda": custo_unitario,
        "itens_premissa": itens,
    }


async def estimar_despesas_periodo(
    db: AsyncSession,
    faturamento: float,
) -> Dict[str, Any]:
    result = await db.execute(
        select(FinanceiroPremissa)
        .where(FinanceiroPremissa.ativo.is_(True), FinanceiroPremissa.natureza == "DESPESA")
        .order_by(FinanceiroPremissa.ordem)
    )
    premissas = list(result.scalars().all())
    comissao = 0.0
    fixas = 0.0
    for p in premissas:
        if p.tipo_calculo == "percentual_receita":
            comissao += faturamento * (float(p.valor or 0) / 100)
        elif p.tipo_calculo == "mensal":
            fixas += float(p.valor or 0)
    return {
        "comissao_estimada": round(comissao, 2),
        "despesas_fixas_mes": round(fixas, 2),
        "premissas_despesa": premissas,
    }
