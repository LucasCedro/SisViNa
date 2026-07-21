"""Custeio por lote — premissas de CUSTO vs DESPESA (contabilidade gerencial)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financeiro_premissa import FinanceiroPremissa
from app.security.financeiro_scope import get_fin_scope

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
from app.models.semeaduras import Semeadura
from app.models.viveiros import Viveiro


def _resolve_id_empresa(id_empresa: Optional[int] = None) -> Optional[int]:
    if id_empresa is not None:
        return id_empresa
    scope = get_fin_scope()
    return scope.id_empresa if scope is not None else None


def _premissa_empresa_clause(id_empresa: Optional[int] = None):
    eid = _resolve_id_empresa(id_empresa)
    if eid is not None:
        return FinanceiroPremissa.id_empresa == eid
    return None


def _viveiros_empresa_clause(id_empresa: Optional[int] = None):
    eid = _resolve_id_empresa(id_empresa)
    if eid is not None:
        return Planta.id_viveiro.in_(select(Viveiro.id).where(Viveiro.id_empresa == eid))
    return None


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


async def obter_valor_hora_coleta_campo(
    db: AsyncSession, id_empresa: Optional[int] = None
) -> float:
    clauses = [
        FinanceiroPremissa.chave == CHAVE_PREMISSA_COLETA_CAMPO,
        FinanceiroPremissa.ativo.is_(True),
        FinanceiroPremissa.natureza == "CUSTO",
    ]
    ec = _premissa_empresa_clause(id_empresa)
    if ec is not None:
        clauses.append(ec)
    result = await db.execute(select(FinanceiroPremissa).where(*clauses))
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


def aplicar_custo_campo_no_lote(
    lote: LoteSementes,
    custo_total_coleta: float,
    qtd_sementes_rateio: int,
) -> None:
    """Rateia custo de campo da coleta no lote; valor_total reflete o saldo restante."""
    qtd_rateio = int(qtd_sementes_rateio or 0)
    disp = int(lote.quantidade_disponivel or 0)
    if custo_total_coleta <= 0 or qtd_rateio <= 0:
        lote.valor_total = None
        lote.custo_unitario = None
        return
    unit = float(custo_total_coleta) / qtd_rateio
    lote.custo_unitario = round(unit, 4)
    lote.valor_total = round(unit * disp, 2) if disp > 0 else 0.0


def definir_valor_lote_entrada(lote: LoteSementes, valor_total: Optional[float]) -> None:
    """Entrada manual de valor no lote (legado / cadastro direto)."""
    if valor_total is None or valor_total <= 0:
        lote.valor_total = None
        lote.custo_unitario = None
        return
    disp = int(lote.quantidade_disponivel or lote.quantidade_inicial or 0)
    aplicar_custo_campo_no_lote(
        lote,
        float(valor_total),
        int(lote.quantidade_inicial or disp or 0),
    )


async def _contar_mudas_vivas(db: AsyncSession, id_empresa: Optional[int] = None) -> int:
    clauses = [Planta.status.notin_(("VENDIDA", "MORTA"))]
    vc = _viveiros_empresa_clause(id_empresa)
    if vc is not None:
        clauses.append(vc)
    return int(
        (
            await db.execute(select(func.count(Planta.id)).where(*clauses))
        ).scalar()
        or 0
    )


async def _obter_recipiente_semeadura(db: AsyncSession, id_empresa: Optional[int] = None) -> str:
    clauses = [
        FinanceiroPremissa.chave == CHAVE_RECIPIENTE_SEMEADURA,
        FinanceiroPremissa.ativo.is_(True),
    ]
    ec = _premissa_empresa_clause(id_empresa)
    if ec is not None:
        clauses.append(ec)
    result = await db.execute(select(FinanceiroPremissa.unidade).where(*clauses))
    unidade = result.scalar_one_or_none()
    if unidade == "saquinho":
        return "saquinho"
    return "tubete"


async def _premissas_custo_ativas(
    db: AsyncSession, id_empresa: Optional[int] = None
) -> List[FinanceiroPremissa]:
    clauses = [FinanceiroPremissa.ativo.is_(True), FinanceiroPremissa.natureza == "CUSTO"]
    ec = _premissa_empresa_clause(id_empresa)
    if ec is not None:
        clauses.append(ec)
    result = await db.execute(
        select(FinanceiroPremissa)
        .where(*clauses)
        .order_by(FinanceiroPremissa.ordem, FinanceiroPremissa.id)
    )
    return list(result.scalars().all())


def _base_rateio_mudas(mudas_vivas: int, qtd_mudas: int) -> int:
    """Parque total para rateio mensal: todas as mudas vivas (inclui o lote novo)."""
    return max(int(mudas_vivas or 0) + max(int(qtd_mudas or 0), 0), 1)


def _mensal_premissa(prem: FinanceiroPremissa) -> float:
    tipo = (prem.tipo_calculo or "").lower()
    if tipo == "mensal_rateio":
        return float(prem.valor or 0)
    if tipo == "pessoas_x_salario_rateio":
        n = float(prem.quantidade or 0)
        sal = float(prem.valor or 0)
        if n <= 0 or sal <= 0:
            return 0.0
        return n * sal
    return 0.0


def _premissa_eh_cif_rateio(prem: FinanceiroPremissa) -> bool:
    return (prem.tipo_calculo or "").lower() in ("mensal_rateio", "pessoas_x_salario_rateio")


async def calcular_cif_unitario_parque(
    db: AsyncSession,
    *,
    parque_total: Optional[int] = None,
    id_empresa: Optional[int] = None,
) -> Dict[str, Any]:
    """CIF mensal (água, energia, MO…) rateado igualmente pelo parque inteiro."""
    if parque_total is None:
        parque_total = await _contar_mudas_vivas(db, id_empresa=id_empresa)
    parque = max(int(parque_total or 0), 1)

    unitario_total = 0.0
    itens: List[dict] = []
    for prem in await _premissas_custo_ativas(db, id_empresa=id_empresa):
        if not _premissa_eh_cif_rateio(prem):
            continue
        mensal = _mensal_premissa(prem)
        if mensal <= 0:
            continue
        unit = mensal / parque
        unitario_total += unit
        itens.append(
            {
                "chave": prem.chave,
                "nome": prem.nome,
                "mensal": round(mensal, 2),
                "unitario": round(unit, 4),
                "descricao": (
                    f"{prem.nome}: R$ {mensal:.2f}/mês ÷ {parque} mudas no parque "
                    f"= R$ {unit:.4f}/muda"
                ),
            }
        )

    return {
        "parque_total": parque,
        "cif_unitario": round(unitario_total, 4),
        "cif_mensal_total": round(sum(i["mensal"] for i in itens), 2),
        "itens": itens,
    }


async def _custo_atividades_planta(db: AsyncSession, planta_id: int) -> float:
    from app.models.atividades import Atividade

    return float(
        (
            await db.execute(
                select(func.coalesce(func.sum(Atividade.custo_atividade), 0)).where(
                    Atividade.id_planta == planta_id
                )
            )
        ).scalar()
        or 0
    )


def _custo_premissa_item(
    prem: FinanceiroPremissa,
    insumo: Optional[Insumo],
    qtd_mudas: int,
    mudas_base_rateio: int = 1,
    recipiente: str = "tubete",
) -> Tuple[float, str]:
    tipo = (prem.tipo_calculo or "").lower()
    qtd_mudas = max(qtd_mudas, 1)
    mudas_base_rateio = max(mudas_base_rateio, 1)

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
        por_muda = mensal / mudas_base_rateio
        total = round(por_muda * qtd_mudas, 2)
        return (
            total,
            f"{prem.nome}: R$ {mensal:.2f}/mês ÷ {mudas_base_rateio} mudas no parque "
            f"= R$ {por_muda:.4f}/muda",
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
        por_muda = mensal / mudas_base_rateio
        total = round(por_muda * qtd_mudas, 2)
        return (
            total,
            f"{prem.nome}: R$ {mensal:.2f}/mês ÷ {mudas_base_rateio} mudas no parque "
            f"= R$ {por_muda:.4f}/muda",
        )

    return 0.0, f"{prem.nome}: tipo não aplicável ao lote"


async def calcular_custo_lote_semeadura(
    db: AsyncSession,
    lote: LoteSementes,
    qtd_sementes: int,
    qtd_mudas: int,
    *,
    mudas_vivas_existentes: Optional[int] = None,
) -> Dict[str, Any]:
    """Custo do lote: direto (sementes/insumos) + CIF mensal ÷ parque total."""
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

    id_empresa = None
    if lote.id_viveiro:
        viveiro = await db.get(Viveiro, lote.id_viveiro)
        if viveiro:
            id_empresa = int(viveiro.id_empresa)

    if mudas_vivas_existentes is None:
        mudas_vivas = await _contar_mudas_vivas(db, id_empresa=id_empresa)
    else:
        mudas_vivas = int(mudas_vivas_existentes or 0)
    mudas_base_rateio = _base_rateio_mudas(mudas_vivas, qtd_mudas)
    recipiente = await _obter_recipiente_semeadura(db, id_empresa=id_empresa)
    premissas = await _premissas_custo_ativas(db, id_empresa=id_empresa)
    for prem in premissas:
        insumo = None
        if prem.id_insumo:
            insumo = await db.get(Insumo, prem.id_insumo)
        valor_item, detalhe = _custo_premissa_item(
            prem, insumo, qtd_mudas, mudas_base_rateio, recipiente
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
        "mudas_base_rateio": mudas_base_rateio,
    }


async def redistribuir_cif_parque(
    db: AsyncSession,
    *,
    commit: bool = True,
    id_empresa: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Recalcula o CIF mensal em TODAS as mudas vivas com o mesmo denominador (parque inteiro).
    Cada muda recebe: custo direto da semeadura + CIF/parque + atividades posteriores.
    """
    cif_info = await calcular_cif_unitario_parque(db, id_empresa=id_empresa)
    parque = cif_info["parque_total"]
    cif_unit = float(cif_info["cif_unitario"])

    sem_q = select(Semeadura)
    eid = _resolve_id_empresa(id_empresa)
    if eid is not None:
        sem_q = sem_q.where(
            Semeadura.id_viveiro.in_(select(Viveiro.id).where(Viveiro.id_empresa == eid))
        )
    semeaduras = list((await db.execute(sem_q)).scalars().all())
    direct_por_semeadura: Dict[int, float] = {}
    semeaduras_atualizadas = 0

    for sem in semeaduras:
        qtd = int(sem.quantidade_mudas_obtidas or 0)
        if qtd <= 0:
            qtd = int(
                (
                    await db.execute(
                        select(func.count(Planta.id)).where(Planta.id_semeadura == sem.id)
                    )
                ).scalar()
                or 0
            )
        if qtd <= 0:
            continue

        direct_total = float(sem.custo_sementes or 0) + float(sem.custo_insumos or 0)
        direct_unit = direct_total / qtd
        direct_por_semeadura[int(sem.id)] = direct_unit

        sem.custo_indireto = round(cif_unit * qtd, 2)
        sem.custo_total = round(direct_total + float(sem.custo_indireto), 2)
        sem.custo_unitario_muda = round(sem.custo_total / qtd, 2)
        if not sem.quantidade_mudas_obtidas:
            sem.quantidade_mudas_obtidas = qtd
        semeaduras_atualizadas += 1

    planta_q = select(Planta).where(Planta.status.notin_(("VENDIDA", "MORTA")))
    vc = _viveiros_empresa_clause(id_empresa)
    if vc is not None:
        planta_q = planta_q.where(vc)
    plantas = (await db.execute(planta_q)).scalars().all()
    plantas_atualizadas = 0
    for planta in plantas:
        direct = direct_por_semeadura.get(int(planta.id_semeadura or 0), 0.0)
        ativ = await _custo_atividades_planta(db, int(planta.id))
        ci = round(direct + cif_unit, 2)
        planta.custo_inicial = ci
        planta.custo_atual = round(ci + ativ, 2)
        plantas_atualizadas += 1

    if commit:
        await db.commit()

    return {
        "parque_total": parque,
        "cif_unitario": cif_unit,
        "cif_mensal_total": cif_info["cif_mensal_total"],
        "semeaduras_atualizadas": semeaduras_atualizadas,
        "plantas_atualizadas": plantas_atualizadas,
        "itens_cif": cif_info["itens"],
    }


async def recalcular_custos_semeaduras(db: AsyncSession) -> Dict[str, Any]:
    """Alias: redistribui CIF pelo parque inteiro e recalcula CMV de todas as mudas."""
    return await redistribuir_cif_parque(db, commit=True)


async def estimar_despesas_periodo(
    db: AsyncSession,
    faturamento: float,
    id_empresa: Optional[int] = None,
) -> Dict[str, Any]:
    clauses = [FinanceiroPremissa.ativo.is_(True), FinanceiroPremissa.natureza == "DESPESA"]
    ec = _premissa_empresa_clause(id_empresa)
    if ec is not None:
        clauses.append(ec)
    result = await db.execute(
        select(FinanceiroPremissa).where(*clauses).order_by(FinanceiroPremissa.ordem)
    )
    premissas = list(result.scalars().all())
    comissao = 0.0
    fixas = 0.0
    itens: List[Dict[str, Any]] = []
    for p in premissas:
        if p.tipo_calculo == "percentual_receita":
            val = round(faturamento * (float(p.valor or 0) / 100), 2)
            comissao += val
            pct = float(p.valor or 0)
            itens.append(
                {
                    "nome": p.nome,
                    "chave": p.chave,
                    "valor": val,
                    "tipo": "comissao",
                    "formula": f"Faturamento (R$ {faturamento:.2f}) × {pct:g}%",
                    "base_valor": pct,
                    "base_unidade": "%",
                }
            )
        elif p.tipo_calculo == "mensal":
            val = round(float(p.valor or 0), 2)
            fixas += val
            itens.append(
                {
                    "nome": p.nome,
                    "chave": p.chave,
                    "valor": val,
                    "tipo": "fixa",
                    "formula": f"Premissa mensal fixa: R$ {val:.2f}/mês",
                    "base_valor": val,
                    "base_unidade": "R$/mês",
                }
            )
    return {
        "comissao_estimada": round(comissao, 2),
        "despesas_fixas_mes": round(fixas, 2),
        "premissas_despesa": premissas,
        "itens": itens,
    }
