"""Indicadores financeiros integrados (vendas, CMV, estoques, lançamentos)."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.especies import Especie
from app.models.insumos import Insumo
from app.models.lancamentos_financeiros import LancamentoFinanceiro
from app.models.plantas import Planta
from app.models.vendas import ItemVenda, Venda
from app.models.compradores import Comprador


MESES_PT = (
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
)


def _periodo_datetime(mes: int, ano: int) -> Tuple[datetime, datetime]:
    inicio = datetime(ano, mes, 1)
    if mes == 12:
        fim = datetime(ano + 1, 1, 1)
    else:
        fim = datetime(ano, mes + 1, 1)
    return inicio, fim


def _periodo_date(mes: int, ano: int) -> Tuple[date, date]:
    ultimo = monthrange(ano, mes)[1]
    return date(ano, mes, 1), date(ano, mes, ultimo)


def _label_periodo(mes: int, ano: int) -> str:
    return f"{MESES_PT[mes - 1]}/{ano}"


def _custo_item_expr():
    return func.coalesce(ItemVenda.custo_unitario, Planta.custo_atual, 0) * ItemVenda.quantidade


def _margem_pct(receita: float, lucro: float) -> Optional[float]:
    if receita <= 0:
        return None
    return round((lucro / receita) * 100, 1)


async def _dre_periodo(db: AsyncSession, mes: int, ano: int) -> Dict[str, Any]:
    inicio, fim = _periodo_datetime(mes, ano)
    filtro_venda = and_(
        Venda.status == "PAGO",
        Venda.data_venda >= inicio,
        Venda.data_venda < fim,
    )

    faturamento = float(
        (await db.execute(select(func.coalesce(func.sum(Venda.valor_total), 0)).where(filtro_venda))).scalar()
        or 0
    )

    base_itens = (
        select(ItemVenda)
        .join(Venda, ItemVenda.id_venda == Venda.id)
        .join(Planta, ItemVenda.id_planta == Planta.id)
        .where(filtro_venda)
    )

    cmv = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(_custo_item_expr()), 0))
                .select_from(ItemVenda)
                .join(Venda, ItemVenda.id_venda == Venda.id)
                .join(Planta, ItemVenda.id_planta == Planta.id)
                .where(filtro_venda)
            )
        ).scalar()
        or 0
    )

    mudas_vendidas = int(
        (
            await db.execute(
                select(func.coalesce(func.sum(ItemVenda.quantidade), 0))
                .select_from(ItemVenda)
                .join(Venda, ItemVenda.id_venda == Venda.id)
                .where(filtro_venda)
            )
        ).scalar()
        or 0
    )

    inicio_d, fim_d = _periodo_date(mes, ano)
    opex = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(LancamentoFinanceiro.valor), 0)).where(
                    LancamentoFinanceiro.tipo == "OPEX",
                    LancamentoFinanceiro.data_lancamento >= inicio_d,
                    LancamentoFinanceiro.data_lancamento <= fim_d,
                )
            )
        ).scalar()
        or 0
    )
    capex = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(LancamentoFinanceiro.valor), 0)).where(
                    LancamentoFinanceiro.tipo == "CAPEX",
                    LancamentoFinanceiro.data_lancamento >= inicio_d,
                    LancamentoFinanceiro.data_lancamento <= fim_d,
                )
            )
        ).scalar()
        or 0
    )

    lucro_bruto = faturamento - cmv
    resultado = lucro_bruto - opex
    ticket = faturamento / mudas_vendidas if mudas_vendidas else None

    return {
        "faturamento": faturamento,
        "cmv": cmv,
        "lucro_bruto": lucro_bruto,
        "margem_bruta_pct": _margem_pct(faturamento, lucro_bruto),
        "opex": opex,
        "capex": capex,
        "resultado_operacional": resultado,
        "mudas_vendidas": mudas_vendidas,
        "ticket_medio": round(ticket, 2) if ticket is not None else None,
    }


async def _estoque_financeiro(db: AsyncSession) -> Dict[str, Any]:
    mudas_vivas = int(
        (
            await db.execute(
                select(func.count(Planta.id)).where(Planta.status.notin_(("VENDIDA", "MORTA")))
            )
        ).scalar()
        or 0
    )
    valor_mudas = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(Planta.custo_atual), 0)).where(
                    Planta.status.notin_(("VENDIDA", "MORTA"))
                )
            )
        ).scalar()
        or 0
    )
    insumos = (await db.execute(select(Insumo))).scalars().all()
    valor_insumos = sum(float(i.valor_estoque or 0) for i in insumos)

    from app.models.lotes_sementes import LoteSementes

    valor_sementes = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(LoteSementes.valor_total), 0)).where(
                    LoteSementes.status == "ativo",
                    LoteSementes.quantidade_disponivel > 0,
                )
            )
        ).scalar()
        or 0
    )

    return {
        "valor_mudas_vivas": valor_mudas,
        "mudas_vivas": mudas_vivas,
        "custo_medio_muda_viva": round(valor_mudas / mudas_vivas, 2) if mudas_vivas else 0,
        "valor_insumos": valor_insumos,
        "total_insumos": len(insumos),
        "valor_sementes": valor_sementes,
    }


async def _margem_especies(db: AsyncSession, mes: int, ano: int) -> List[Dict[str, Any]]:
    inicio, fim = _periodo_datetime(mes, ano)
    nome = func.coalesce(Especie.nome_popular, Especie.nome_cientifico)
    custo_expr = _custo_item_expr()

    q = (
        select(
            Especie.id.label("id_especie"),
            nome.label("nome"),
            func.coalesce(func.sum(ItemVenda.quantidade), 0).label("qtd"),
            func.coalesce(func.sum(ItemVenda.valor_total), 0).label("receita"),
            func.coalesce(func.sum(custo_expr), 0).label("cmv"),
        )
        .select_from(ItemVenda)
        .join(Venda, ItemVenda.id_venda == Venda.id)
        .join(Planta, ItemVenda.id_planta == Planta.id)
        .join(Especie, Planta.id_especie == Especie.id)
        .where(
            Venda.status == "PAGO",
            Venda.data_venda >= inicio,
            Venda.data_venda < fim,
        )
        .group_by(Especie.id, Especie.nome_popular, Especie.nome_cientifico)
        .order_by(func.sum(ItemVenda.valor_total).desc())
    )
    rows = (await db.execute(q)).all()
    out: List[Dict[str, Any]] = []
    for row in rows:
        receita = float(row.receita or 0)
        cmv = float(row.cmv or 0)
        qtd = int(row.qtd or 0)
        lucro = receita - cmv
        out.append(
            {
                "id_especie": row.id_especie,
                "nome": row.nome,
                "quantidade_vendida": qtd,
                "receita": receita,
                "cmv": cmv,
                "lucro_bruto": lucro,
                "margem_pct": _margem_pct(receita, lucro),
                "preco_medio": round(receita / qtd, 2) if qtd else None,
                "custo_medio": round(cmv / qtd, 2) if qtd else None,
            }
        )
    return out


async def _avisos_financeiros(db: AsyncSession, mes: int, ano: int) -> List[Dict[str, Any]]:
    inicio, fim = _periodo_datetime(mes, ano)
    custo_u = func.coalesce(ItemVenda.custo_unitario, Planta.custo_atual, 0)
    nome = func.coalesce(Especie.nome_popular, Especie.nome_cientifico)

    abaixo_custo = (
        await db.execute(
            select(
                Planta.codigo_rastreio,
                Planta.id_especie,
                nome,
                ItemVenda.valor_unitario,
                custo_u.label("custo"),
            )
            .select_from(ItemVenda)
            .join(Venda, ItemVenda.id_venda == Venda.id)
            .join(Planta, ItemVenda.id_planta == Planta.id)
            .join(Especie, Planta.id_especie == Especie.id)
            .where(
                Venda.status == "PAGO",
                Venda.data_venda >= inicio,
                Venda.data_venda < fim,
                ItemVenda.valor_unitario < custo_u,
            )
            .limit(20)
        )
    ).all()

    avisos: List[Dict[str, Any]] = []
    for row in abaixo_custo:
        avisos.append(
            {
                "tipo": "venda_abaixo_custo",
                "mensagem": (
                    f"{row.codigo_rastreio or 'Muda'} ({row.nome}): vendida a R$ {float(row.valor_unitario):.2f}, "
                    f"custo R$ {float(row.custo):.2f}"
                ),
                "id_especie": row.id_especie,
                "codigo_planta": row.codigo_rastreio,
            }
        )

    margens = await _margem_especies(db, mes, ano)
    for m in margens:
        if m["quantidade_vendida"] > 0 and m["margem_pct"] is not None and m["margem_pct"] < 0:
            avisos.append(
                {
                    "tipo": "especie_prejuizo",
                    "mensagem": (
                        f"{m['nome']}: margem negativa ({m['margem_pct']}%) "
                        f"no período — revisar preço ou custo de produção."
                    ),
                    "id_especie": m["id_especie"],
                    "codigo_planta": None,
                }
            )

    dre = await _dre_periodo(db, mes, ano)
    if dre["faturamento"] > 0 and dre["resultado_operacional"] < 0:
        avisos.append(
            {
                "tipo": "resultado_negativo",
                "mensagem": (
                    "Resultado operacional negativo no período — despesas (OPEX) superaram o lucro bruto."
                ),
                "id_especie": None,
                "codigo_planta": None,
            }
        )

    return avisos


async def _evolucao_mensal(db: AsyncSession, mes: int, ano: int, meses: int = 12) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    m, a = mes, ano
    for _ in range(meses):
        dre = await _dre_periodo(db, m, a)
        out.append(
            {
                "mes": m,
                "ano": a,
                "label": _label_periodo(m, a),
                "faturamento": dre["faturamento"],
                "cmv": dre["cmv"],
                "lucro_bruto": dre["lucro_bruto"],
            }
        )
        m -= 1
        if m < 1:
            m = 12
            a -= 1
    out.reverse()
    return out


async def _receitas_periodo(db: AsyncSession, mes: int, ano: int, limit: int = 50) -> List[Dict[str, Any]]:
    inicio, fim = _periodo_datetime(mes, ano)
    q = (
        select(
            Venda,
            Comprador.nome.label("comprador_nome"),
            func.count(ItemVenda.id).label("total_itens"),
        )
        .join(Comprador, Venda.id_comprador == Comprador.id)
        .outerjoin(ItemVenda, Venda.id == ItemVenda.id_venda)
        .where(
            Venda.status == "PAGO",
            Venda.data_venda >= inicio,
            Venda.data_venda < fim,
        )
        .group_by(Venda.id, Comprador.nome)
        .order_by(Venda.data_venda.desc())
        .limit(limit)
    )
    rows = (await db.execute(q)).all()
    return [
        {
            "id": v.id,
            "data_venda": v.data_venda.isoformat() if v.data_venda else "",
            "comprador_nome": comprador_nome,
            "total_itens": int(total_itens or 0),
            "valor_total": float(v.valor_total or 0),
            "status": v.status or "",
            "forma_pagamento": v.forma_pagamento,
        }
        for v, comprador_nome, total_itens in rows
    ]


async def _distribuicao_categoria(
    db: AsyncSession, mes: int, ano: int, tipo: str
) -> List[Dict[str, Any]]:
    inicio_d, fim_d = _periodo_date(mes, ano)
    rows = (
        await db.execute(
            select(
                LancamentoFinanceiro.categoria,
                func.coalesce(func.sum(LancamentoFinanceiro.valor), 0).label("valor"),
            )
            .where(
                LancamentoFinanceiro.tipo == tipo,
                LancamentoFinanceiro.data_lancamento >= inicio_d,
                LancamentoFinanceiro.data_lancamento <= fim_d,
            )
            .group_by(LancamentoFinanceiro.categoria)
            .order_by(func.sum(LancamentoFinanceiro.valor).desc())
        )
    ).all()
    total = sum(float(r.valor or 0) for r in rows)
    out = []
    for r in rows:
        valor = float(r.valor or 0)
        pct = round((valor / total) * 100, 1) if total else 0
        out.append({"categoria": r.categoria, "valor": valor, "porcentagem": pct})
    return out


async def get_painel_financeiro(
    db: AsyncSession,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
) -> Dict[str, Any]:
    hoje = date.today()
    mes = mes or hoje.month
    ano = ano or hoje.year

    dre = await _dre_periodo(db, mes, ano)
    from app.services.custeio import estimar_despesas_periodo

    desp = await estimar_despesas_periodo(db, dre["faturamento"])
    return {
        "periodo": {"mes": mes, "ano": ano, "label": _label_periodo(mes, ano)},
        "dre": dre,
        "estoque": await _estoque_financeiro(db),
        "margem_especies": await _margem_especies(db, mes, ano),
        "avisos": await _avisos_financeiros(db, mes, ano),
        "evolucao_mensal": await _evolucao_mensal(db, mes, ano),
        "receitas": await _receitas_periodo(db, mes, ano),
        "opex_por_categoria": await _distribuicao_categoria(db, mes, ano, "OPEX"),
        "capex_por_categoria": await _distribuicao_categoria(db, mes, ano, "CAPEX"),
        "despesas_estimadas": {
            "comissao_estimada": desp["comissao_estimada"],
            "despesas_fixas_mes": desp["despesas_fixas_mes"],
            "total_despesas_estimadas": round(
                desp["comissao_estimada"] + desp["despesas_fixas_mes"], 2
            ),
        },
    }
