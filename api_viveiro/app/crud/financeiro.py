"""Indicadores financeiros integrados (vendas, CMV, estoques, lançamentos)."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.especies import Especie
from app.models.insumos import Insumo
from app.models.insumo_movimentacao import InsumoMovimentacao
from app.models.lancamentos_financeiros import LancamentoFinanceiro
from app.models.plantas import Planta
from app.models.vendas import ItemVenda, Venda
from app.models.compradores import Comprador
from app.models.canteiros import Canteiro
from app.crud.plantas_estoque import filtro_aptas_venda_comercial
from app.services.custeio import estimar_despesas_periodo


MESES_PT = (
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
)

MES_TODOS = 0  # agregado anual (Jan–Dez ou YTD no ano corrente)

REGIME_CAIXA = "caixa"
REGIME_COMPETENCIA = "competencia"


def _data_referencia_caixa():
    """Data de recebimento — fallback data_venda para vendas antigas sem data_pagamento."""
    return func.coalesce(Venda.data_pagamento, Venda.data_venda)


def _filtro_vendas(regime: str, inicio: datetime, fim: datetime):
    """
    Caixa: só PAGO, período pela data de pagamento.
    Competência: PENDENTE + PAGO (fato gerador na data_venda / fornecimento).
    """
    if regime == REGIME_COMPETENCIA:
        return and_(
            Venda.status.in_(("PENDENTE", "PAGO")),
            Venda.data_venda >= inicio,
            Venda.data_venda < fim,
        )
    return and_(
        Venda.status == "PAGO",
        _data_referencia_caixa() >= inicio,
        _data_referencia_caixa() < fim,
    )


def _descricao_regime(regime: str) -> str:
    if regime == REGIME_COMPETENCIA:
        return "regime de competência (fato gerador na data da venda)"
    return "regime de caixa (recebimento na data de pagamento)"


def _data_pagamento_compra():
    """Data efetiva do pagamento — fallback data_movimento para compras antigas."""
    return func.coalesce(InsumoMovimentacao.data_pagamento, InsumoMovimentacao.data_movimento)


def _filtro_compras_insumos_caixa(inicio_d: date, fim_d: date):
    return and_(
        InsumoMovimentacao.tipo == "entrada",
        func.coalesce(InsumoMovimentacao.valor_total, 0) > 0,
        or_(
            InsumoMovimentacao.status_pagamento == "PAGO",
            InsumoMovimentacao.status_pagamento.is_(None),
        ),
        _data_pagamento_compra() >= inicio_d,
        _data_pagamento_compra() <= fim_d,
    )


def _filtro_compras_insumos_competencia(inicio_d: date, fim_d: date):
    return and_(
        InsumoMovimentacao.tipo == "entrada",
        func.coalesce(InsumoMovimentacao.valor_total, 0) > 0,
        InsumoMovimentacao.data_movimento >= inicio_d,
        InsumoMovimentacao.data_movimento <= fim_d,
    )


async def _total_compras_insumos(
    db: AsyncSession, mes: int, ano: int, regime: str = REGIME_CAIXA
) -> float:
    inicio_d, fim_d = _periodo_date(mes, ano)
    filtro = (
        _filtro_compras_insumos_competencia(inicio_d, fim_d)
        if regime == REGIME_COMPETENCIA
        else _filtro_compras_insumos_caixa(inicio_d, fim_d)
    )
    return float(
        (
            await db.execute(
                select(func.coalesce(func.sum(InsumoMovimentacao.valor_total), 0)).where(filtro)
            )
        ).scalar()
        or 0
    )


async def _detalhe_compras_insumos(
    db: AsyncSession,
    mes: int,
    ano: int,
    regime: str = REGIME_CAIXA,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    inicio_d, fim_d = _periodo_date(mes, ano)
    filtro = (
        _filtro_compras_insumos_competencia(inicio_d, fim_d)
        if regime == REGIME_COMPETENCIA
        else _filtro_compras_insumos_caixa(inicio_d, fim_d)
    )
    data_ordem = (
        InsumoMovimentacao.data_movimento
        if regime == REGIME_COMPETENCIA
        else _data_pagamento_compra()
    )
    rows = (
        await db.execute(
            select(InsumoMovimentacao, Insumo.nome.label("insumo_nome"))
            .join(Insumo, InsumoMovimentacao.id_insumo == Insumo.id)
            .where(filtro)
            .order_by(data_ordem.desc(), InsumoMovimentacao.id.desc())
            .limit(limit)
        )
    ).all()
    return [
        {
            "id": m.id,
            "id_insumo": m.id_insumo,
            "insumo_nome": nome,
            "data_movimento": m.data_movimento.isoformat() if m.data_movimento else "",
            "data_pagamento": m.data_pagamento.isoformat() if m.data_pagamento else "",
            "valor_total": float(m.valor_total or 0),
            "status_pagamento": m.status_pagamento or "PAGO",
            "quantidade": float(m.quantidade or 0),
            "observacao": m.observacao,
        }
        for m, nome in rows
    ]


def _resolver_mes_ano(
    mes: Optional[int], ano: Optional[int]
) -> Tuple[int, int]:
    hoje = date.today()
    return (hoje.month if mes is None else mes, ano or hoje.year)


def _meses_no_periodo(mes: int, ano: int) -> int:
    if mes != MES_TODOS:
        return 1
    hoje = date.today()
    if ano < hoje.year:
        return 12
    if ano > hoje.year:
        return 0
    return hoje.month


def _escala_despesas_periodo(desp: Dict[str, Any], mes: int, ano: int) -> Dict[str, Any]:
    n = _meses_no_periodo(mes, ano)
    fixas = round(desp["despesas_fixas_mes"] * n, 2)
    comissao = desp["comissao_estimada"]
    itens: List[Dict[str, Any]] = []
    for i in desp.get("itens", []):
        item = dict(i)
        if item.get("tipo") == "fixa" and n != 1:
            base = float(item.get("base_valor") or item.get("valor") or 0)
            item["valor"] = round(base * n, 2)
            item["formula"] = f"Premissa mensal R$ {base:.2f}/mês × {n} mes(es)"
        itens.append(item)
    return {
        "comissao_estimada": comissao,
        "despesas_fixas_mes": fixas,
        "total_despesas_estimadas": round(comissao + fixas, 2),
        "itens": itens,
    }


def _periodo_datetime(mes: int, ano: int) -> Tuple[datetime, datetime]:
    if mes == MES_TODOS:
        inicio = datetime(ano, 1, 1)
        hoje = date.today()
        if ano < hoje.year:
            return inicio, datetime(ano + 1, 1, 1)
        if ano > hoje.year:
            return inicio, inicio
        if hoje.month == 12:
            return inicio, datetime(ano + 1, 1, 1)
        return inicio, datetime(ano, hoje.month + 1, 1)
    inicio = datetime(ano, mes, 1)
    if mes == 12:
        fim = datetime(ano + 1, 1, 1)
    else:
        fim = datetime(ano, mes + 1, 1)
    return inicio, fim


def _periodo_date(mes: int, ano: int) -> Tuple[date, date]:
    if mes == MES_TODOS:
        hoje = date.today()
        inicio = date(ano, 1, 1)
        if ano < hoje.year:
            return inicio, date(ano, 12, 31)
        if ano > hoje.year:
            return inicio, inicio
        return inicio, hoje
    ultimo = monthrange(ano, mes)[1]
    return date(ano, mes, 1), date(ano, mes, ultimo)


def _label_periodo(mes: int, ano: int) -> str:
    if mes == MES_TODOS:
        hoje = date.today()
        if ano == hoje.year and hoje.month < 12:
            return f"Jan–{MESES_PT[hoje.month - 1]}/{ano}"
        return f"Ano {ano}"
    return f"{MESES_PT[mes - 1]}/{ano}"


def _custo_item_expr():
    return func.coalesce(ItemVenda.custo_unitario, Planta.custo_atual, 0) * ItemVenda.quantidade


def _margem_pct(receita: float, lucro: float) -> Optional[float]:
    if receita <= 0:
        return None
    return round((lucro / receita) * 100, 1)


async def _dre_periodo(
    db: AsyncSession, mes: int, ano: int, regime: str = REGIME_CAIXA
) -> Dict[str, Any]:
    inicio, fim = _periodo_datetime(mes, ano)
    filtro_venda = _filtro_vendas(regime, inicio, fim)

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

    desp = await estimar_despesas_periodo(db, faturamento)
    meses_periodo = _meses_no_periodo(mes, ano)
    opex_comissao = desp["comissao_estimada"]
    opex_fixo = round(desp["despesas_fixas_mes"] * meses_periodo, 2)
    opex = round(opex_comissao + opex_fixo, 2)

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

    compras_insumos = await _total_compras_insumos(db, mes, ano, regime)

    lucro_bruto = faturamento - cmv
    resultado = lucro_bruto - compras_insumos - opex
    ticket = faturamento / mudas_vendidas if mudas_vendidas else None

    return {
        "faturamento": faturamento,
        "cmv": cmv,
        "lucro_bruto": lucro_bruto,
        "margem_bruta_pct": _margem_pct(faturamento, lucro_bruto),
        "opex": opex,
        "opex_comissao": opex_comissao,
        "opex_fixo": opex_fixo,
        "compras_insumos": compras_insumos,
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

    q_comercial = (
        select(
            func.count(Planta.id),
            func.coalesce(func.sum(Planta.custo_atual), 0),
        )
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
    )
    q_comercial = filtro_aptas_venda_comercial(q_comercial)
    row_com = (await db.execute(q_comercial)).one()
    mudas_comercial = int(row_com[0] or 0)
    valor_comercial = float(row_com[1] or 0)

    return {
        "valor_mudas_vivas": valor_mudas,
        "mudas_vivas": mudas_vivas,
        "custo_medio_muda_viva": round(valor_mudas / mudas_vivas, 2) if mudas_vivas else 0,
        "valor_mudas_comercial": valor_comercial,
        "mudas_comercial": mudas_comercial,
        "custo_medio_muda_comercial": round(valor_comercial / mudas_comercial, 2) if mudas_comercial else 0,
        "valor_insumos": valor_insumos,
        "total_insumos": len(insumos),
        "valor_sementes": valor_sementes,
    }


async def _integridade_financeira(db: AsyncSession) -> Dict[str, Any]:
    from app.models.lotes_sementes import LoteSementes
    from app.models.coletas_sementes import ColetaSementes
    from app.services.custeio import obter_valor_hora_coleta_campo

    valor_hora = await obter_valor_hora_coleta_campo(db)
    filtro_lote_ativo = and_(
        LoteSementes.status == "ativo",
        LoteSementes.quantidade_disponivel > 0,
    )

    lotes_sem_custo = int(
        (
            await db.execute(
                select(func.count(LoteSementes.id)).where(
                    filtro_lote_ativo,
                    func.coalesce(LoteSementes.valor_total, 0) <= 0,
                )
            )
        ).scalar()
        or 0
    )

    coletas_sem_horas = int(
        (
            await db.execute(
                select(func.count(func.distinct(ColetaSementes.id)))
                .select_from(ColetaSementes)
                .join(LoteSementes, LoteSementes.id_coleta_sementes == ColetaSementes.id)
                .where(
                    filtro_lote_ativo,
                    or_(
                        ColetaSementes.horas_campo.is_(None),
                        ColetaSementes.horas_campo <= 0,
                    ),
                )
            )
        ).scalar()
        or 0
    )

    lotes_armazem_sem_coleta = int(
        (
            await db.execute(
                select(func.count(LoteSementes.id)).where(
                    filtro_lote_ativo,
                    LoteSementes.id_coleta_sementes.is_(None),
                    func.coalesce(LoteSementes.valor_total, 0) <= 0,
                )
            )
        ).scalar()
        or 0
    )

    mudas_sem_custo = int(
        (
            await db.execute(
                select(func.count(Planta.id)).where(
                    Planta.status.notin_(("VENDIDA", "MORTA")),
                    func.coalesce(Planta.custo_atual, 0) <= 0,
                )
            )
        ).scalar()
        or 0
    )

    return {
        "lotes_sementes_sem_custo": lotes_sem_custo,
        "coletas_sem_horas_campo": coletas_sem_horas,
        "lotes_armazem_sem_coleta": lotes_armazem_sem_coleta,
        "premissa_coleta_campo_ok": valor_hora > 0,
        "valor_hora_coleta_campo": round(valor_hora, 2),
        "mudas_vivas_sem_custo": mudas_sem_custo,
    }


async def _margem_especies(
    db: AsyncSession, mes: int, ano: int, regime: str = REGIME_CAIXA
) -> List[Dict[str, Any]]:
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
        .where(_filtro_vendas(regime, inicio, fim))
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


async def _avisos_financeiros(
    db: AsyncSession,
    mes: int,
    ano: int,
    integridade: Optional[Dict[str, Any]] = None,
    regime: str = REGIME_CAIXA,
) -> List[Dict[str, Any]]:
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
                _filtro_vendas(regime, inicio, fim),
                ItemVenda.valor_unitario < custo_u,
            )
            .limit(20)
        )
    ).all()

    avisos: List[Dict[str, Any]] = []

    integ = integridade or await _integridade_financeira(db)
    if not integ.get("premissa_coleta_campo_ok", True):
        avisos.append(
            {
                "tipo": "premissa_coleta_campo",
                "mensagem": (
                    "Premissa «Mão de obra de coleta» está zerada ou inativa — "
                    "horas de campo não geram custo até configurar R$/h em Financeiro → Premissas."
                ),
                "id_especie": None,
                "codigo_planta": None,
            }
        )
    if integ.get("lotes_sementes_sem_custo", 0) > 0:
        n = integ["lotes_sementes_sem_custo"]
        if integ.get("coletas_sem_horas_campo", 0) == 0 and integ.get("premissa_coleta_campo_ok"):
            msg = (
                f"{n} lote(s) ativo(s) com custo zero apesar das horas informadas — "
                "reabra e salve a coleta ou verifique a premissa homem-hora."
            )
        else:
            msg = (
                f"{n} lote(s) de sementes ativo(s) com custo zero — "
                "informe horas na coleta vinculada ou configure homem-hora em Premissas."
            )
        avisos.append(
            {
                "tipo": "sementes_sem_custo",
                "mensagem": msg,
                "id_especie": None,
                "codigo_planta": None,
            }
        )
    if integ.get("coletas_sem_horas_campo", 0) > 0:
        n = integ["coletas_sem_horas_campo"]
        avisos.append(
            {
                "tipo": "coletas_sem_horas",
                "mensagem": (
                    f"{n} coleta(s) com lote ativo no armazém ainda sem horas de campo — "
                    "edite em Coleta Sementes (horas ficam na coleta, não no lote)."
                ),
                "id_especie": None,
                "codigo_planta": None,
            }
        )
    if integ.get("lotes_armazem_sem_coleta", 0) > 0:
        n = integ["lotes_armazem_sem_coleta"]
        avisos.append(
            {
                "tipo": "lotes_armazem_sem_coleta",
                "mensagem": (
                    f"{n} lote(s) criado(s) direto no armazém (sem coleta) sem custo — "
                    "não recebem horas de campo; informe valor manualmente ou vincule a uma coleta."
                ),
                "id_especie": None,
                "codigo_planta": None,
            }
        )
    if integ.get("mudas_vivas_sem_custo", 0) > 0:
        n = integ["mudas_vivas_sem_custo"]
        avisos.append(
            {
                "tipo": "mudas_sem_custo",
                "mensagem": (
                    f"{n} muda(s) viva(s) com custo_atual zero — CMV de venda pode ficar subestimado."
                ),
                "id_especie": None,
                "codigo_planta": None,
            }
        )

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
                    "Resultado operacional negativo no período — despesas (compras de insumos + OPEX) superaram o lucro bruto."
                ),
                "id_especie": None,
                "codigo_planta": None,
            }
        )

    return avisos


async def _evolucao_mensal(
    db: AsyncSession,
    mes: int,
    ano: int,
    meses: int = 12,
    regime: str = REGIME_CAIXA,
) -> List[Dict[str, Any]]:
    if mes == MES_TODOS:
        hoje = date.today()
        ultimo = 12 if ano < hoje.year else (hoje.month if ano == hoje.year else 0)
        out: List[Dict[str, Any]] = []
        for m in range(1, ultimo + 1):
            dre = await _dre_periodo(db, m, ano, regime)
            out.append(
                {
                    "mes": m,
                    "ano": ano,
                    "label": _label_periodo(m, ano),
                    "faturamento": dre["faturamento"],
                    "cmv": dre["cmv"],
                    "lucro_bruto": dre["lucro_bruto"],
                }
            )
        return out

    out: List[Dict[str, Any]] = []
    m, a = mes, ano
    for _ in range(meses):
        dre = await _dre_periodo(db, m, a, regime)
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


async def _receitas_periodo(
    db: AsyncSession,
    mes: int,
    ano: int,
    limit: int = 50,
    regime: str = REGIME_CAIXA,
) -> List[Dict[str, Any]]:
    inicio, fim = _periodo_datetime(mes, ano)
    data_ordem = _data_referencia_caixa() if regime == REGIME_CAIXA else Venda.data_venda
    q = (
        select(
            Venda,
            Comprador.nome.label("comprador_nome"),
            func.count(ItemVenda.id).label("total_itens"),
        )
        .join(Comprador, Venda.id_comprador == Comprador.id)
        .outerjoin(ItemVenda, Venda.id == ItemVenda.id_venda)
        .where(_filtro_vendas(regime, inicio, fim))
        .group_by(Venda.id, Comprador.nome)
        .order_by(data_ordem.desc())
        .limit(limit)
    )
    rows = (await db.execute(q)).all()
    return [
        {
            "id": v.id,
            "data_venda": v.data_venda.isoformat() if v.data_venda else "",
            "data_pagamento": v.data_pagamento.isoformat() if v.data_pagamento else "",
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


async def _opex_distribuicao_premissas(db: AsyncSession, faturamento: float) -> List[Dict[str, Any]]:
    desp = await estimar_despesas_periodo(db, faturamento)
    itens = []
    for item in desp.get("itens", []):
        valor = float(item.get("valor") or 0)
        if valor > 0:
            itens.append({"categoria": item["nome"], "valor": valor})
    total = sum(i["valor"] for i in itens)
    out = []
    for i in itens:
        pct = round((i["valor"] / total) * 100, 1) if total else 0
        out.append({"categoria": i["categoria"], "valor": i["valor"], "porcentagem": pct})
    return out


async def _detalhe_cmv_vendas(
    db: AsyncSession,
    mes: int,
    ano: int,
    limit: int = 150,
    regime: str = REGIME_CAIXA,
) -> Dict[str, Any]:
    inicio, fim = _periodo_datetime(mes, ano)
    filtro_venda = _filtro_vendas(regime, inicio, fim)
    nome = func.coalesce(Especie.nome_popular, Especie.nome_cientifico)

    total_itens = int(
        (
            await db.execute(
                select(func.count(ItemVenda.id))
                .select_from(ItemVenda)
                .join(Venda, ItemVenda.id_venda == Venda.id)
                .where(filtro_venda)
            )
        ).scalar()
        or 0
    )

    rows = (
        await db.execute(
            select(
                ItemVenda.id.label("id_item"),
                ItemVenda.id_venda,
                ItemVenda.quantidade,
                ItemVenda.valor_total,
                ItemVenda.custo_unitario,
                Planta.custo_atual,
                Planta.codigo_rastreio,
                nome.label("especie_nome"),
                Venda.data_venda,
                Comprador.nome.label("comprador_nome"),
            )
            .select_from(ItemVenda)
            .join(Venda, ItemVenda.id_venda == Venda.id)
            .join(Planta, ItemVenda.id_planta == Planta.id)
            .join(Especie, Planta.id_especie == Especie.id)
            .join(Comprador, Venda.id_comprador == Comprador.id)
            .where(filtro_venda)
            .order_by(Venda.data_venda.desc(), ItemVenda.id.desc())
            .limit(limit)
        )
    ).all()

    itens: List[Dict[str, Any]] = []
    resumo_origem: Dict[str, int] = {"congelado": 0, "planta_atual": 0}
    for row in rows:
        custo_u = float(row.custo_unitario if row.custo_unitario is not None else row.custo_atual or 0)
        origem = "congelado" if row.custo_unitario is not None else "planta_atual"
        qtd = int(row.quantidade or 1)
        resumo_origem[origem] = resumo_origem.get(origem, 0) + qtd
        itens.append(
            {
                "id_item": row.id_item,
                "id_venda": row.id_venda,
                "data_venda": row.data_venda.isoformat() if row.data_venda else "",
                "comprador_nome": row.comprador_nome,
                "codigo_rastreio": row.codigo_rastreio,
                "especie_nome": row.especie_nome,
                "quantidade": qtd,
                "receita_linha": float(row.valor_total or 0),
                "custo_unitario": custo_u,
                "cmv_linha": round(custo_u * qtd, 2),
                "origem_custo": origem,
            }
        )

    cmv_total = round(sum(i["cmv_linha"] for i in itens), 2)
    return {
        "itens": itens,
        "total_itens": total_itens,
        "truncado": total_itens > len(itens),
        "resumo_origem": resumo_origem,
        "total_parcial": cmv_total,
    }


async def _detalhe_estoque_insumos(db: AsyncSession) -> List[Dict[str, Any]]:
    insumos = (await db.execute(select(Insumo).order_by(Insumo.valor_estoque.desc()))).scalars().all()
    return [
        {
            "id": i.id,
            "nome": i.nome,
            "tipo": i.tipo or "",
            "quantidade_estoque": float(i.quantidade_estoque or 0),
            "preco_unitario": float(i.preco_unitario or 0),
            "valor_estoque": float(i.valor_estoque or 0),
            "unidade_medida": i.unidade_medida,
        }
        for i in insumos
        if float(i.valor_estoque or 0) > 0 or float(i.quantidade_estoque or 0) > 0
    ]


async def _detalhe_estoque_sementes(db: AsyncSession) -> List[Dict[str, Any]]:
    from app.models.lotes_sementes import LoteSementes

    nome = func.coalesce(Especie.nome_popular, Especie.nome_cientifico)
    rows = (
        await db.execute(
            select(
                LoteSementes.id,
                LoteSementes.codigo_lote,
                LoteSementes.quantidade_disponivel,
                LoteSementes.valor_total,
                LoteSementes.custo_unitario,
                nome.label("especie_nome"),
            )
            .join(Especie, LoteSementes.id_especie == Especie.id)
            .where(
                LoteSementes.status == "ativo",
                LoteSementes.quantidade_disponivel > 0,
            )
            .order_by(LoteSementes.valor_total.desc())
        )
    ).all()
    return [
        {
            "id": r.id,
            "codigo_lote": r.codigo_lote,
            "especie_nome": r.especie_nome,
            "quantidade_disponivel": int(r.quantidade_disponivel or 0),
            "valor_total": float(r.valor_total or 0),
            "custo_unitario": float(r.custo_unitario) if r.custo_unitario is not None else None,
        }
        for r in rows
    ]


async def _detalhe_capex_lancamentos(db: AsyncSession, mes: int, ano: int) -> List[Dict[str, Any]]:
    inicio_d, fim_d = _periodo_date(mes, ano)
    rows = (
        await db.execute(
            select(LancamentoFinanceiro)
            .where(
                LancamentoFinanceiro.tipo == "CAPEX",
                LancamentoFinanceiro.data_lancamento >= inicio_d,
                LancamentoFinanceiro.data_lancamento <= fim_d,
            )
            .order_by(LancamentoFinanceiro.data_lancamento.desc())
        )
    ).scalars().all()
    return [
        {
            "id": r.id,
            "descricao": r.descricao or "",
            "categoria": r.categoria or "",
            "data_lancamento": r.data_lancamento.isoformat() if r.data_lancamento else "",
            "valor": float(r.valor or 0),
            "forma_pagamento": r.forma_pagamento,
        }
        for r in rows
    ]


def _estoque_detalhes_blocos(
    estoque: Dict[str, Any],
    insumos_itens: List[Dict[str, Any]],
    sementes_itens: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "parque": {
            "titulo": "Parque — todas as mudas vivas",
            "formula": "Σ custo_atual das mudas com status ≠ VENDIDA/MORTA",
            "total": estoque["valor_mudas_vivas"],
            "explicacao": (
                f"{estoque['mudas_vivas']} mudas · "
                f"média R$ {estoque['custo_medio_muda_viva']:.2f}/muda"
            ),
            "passos": [
                {"label": "Total parque", "valor": estoque["valor_mudas_vivas"], "operador": "="},
            ],
        },
        "comercial": {
            "titulo": "Estoque comercial — aptas para venda",
            "formula": "Σ custo_atual · estagio apta_venda · canteiro rustificação",
            "total": estoque["valor_mudas_comercial"],
            "explicacao": (
                f"{estoque['mudas_comercial']} mudas · "
                f"média R$ {estoque['custo_medio_muda_comercial']:.2f}/muda"
            ),
            "passos": [
                {
                    "label": "Subconjunto do parque liberado para venda",
                    "valor": estoque["valor_mudas_comercial"],
                    "operador": "=",
                },
            ],
        },
        "insumos": {
            "titulo": "Insumos em estoque",
            "formula": "Σ valor_estoque (quantidade × preço médio móvel por insumo)",
            "total": estoque["valor_insumos"],
            "explicacao": f"{estoque['total_insumos']} item(ns) cadastrados",
            "passos": [
                {"label": "Soma dos insumos listados abaixo", "valor": estoque["valor_insumos"], "operador": "="},
            ],
        },
        "insumos_itens": insumos_itens,
        "sementes": {
            "titulo": "Sementes em estoque",
            "formula": "Σ valor_total dos lotes ativos com saldo (horas de coleta × homem-hora rateado)",
            "total": estoque["valor_sementes"],
            "explicacao": "Custo de campo informado na coleta — não é comissão nem pagamento ao operador.",
            "passos": [
                {"label": "Soma dos lotes listados abaixo", "valor": estoque["valor_sementes"], "operador": "="},
            ],
        },
        "sementes_itens": sementes_itens,
    }


async def _montar_detalhes_financeiro(
    db: AsyncSession,
    mes: int,
    ano: int,
    dre: Dict[str, Any],
    desp: Dict[str, Any],
    receitas: List[Dict[str, Any]],
    estoque: Dict[str, Any],
    regime: str = REGIME_CAIXA,
) -> Dict[str, Any]:
    cmv_raw = await _detalhe_cmv_vendas(db, mes, ano, regime=regime)
    compras_itens = await _detalhe_compras_insumos(db, mes, ano, regime=regime)
    insumos_itens = await _detalhe_estoque_insumos(db)
    sementes_itens = await _detalhe_estoque_sementes(db)
    capex_itens = await _detalhe_capex_lancamentos(db, mes, ano)

    fat = dre["faturamento"]
    cmv = dre["cmv"]
    lucro = dre["lucro_bruto"]
    compras = dre["compras_insumos"]
    opex = dre["opex"]
    resultado = dre["resultado_operacional"]

    opex_itens = [
        {
            "nome": i["nome"],
            "chave": i["chave"],
            "valor": i["valor"],
            "tipo": i["tipo"],
            "formula": i.get("formula"),
            "base_valor": i.get("base_valor"),
            "base_unidade": i.get("base_unidade"),
        }
        for i in desp.get("itens", [])
        if float(i.get("valor") or 0) > 0 or i.get("tipo") == "comissao"
    ]

    fat_label = (
        "Σ valor_total das vendas efetivadas (PENDENTE + PAGO) no período"
        if regime == REGIME_COMPETENCIA
        else "Σ valor_total das vendas pagas no período (data de recebimento)"
    )
    vendas_label = (
        f"{len(receitas)} venda(s) no período (inclui pendentes)"
        if regime == REGIME_COMPETENCIA
        else f"{len(receitas)} venda(s) pagas no período"
    )
    compras_label = (
        f"{len(compras_itens)} compra(s) no período (data da NF)"
        if regime == REGIME_COMPETENCIA
        else f"{len(compras_itens)} compra(s) pagas no período"
    )

    return {
        "faturamento": {
            "titulo": "Faturamento",
            "formula": fat_label,
            "total": fat,
            "explicacao": (
                f"{dre['mudas_vendidas']} muda(s) vendidas · "
                f"ticket médio R$ {dre['ticket_medio']:.2f}"
                if dre.get("ticket_medio")
                else f"{dre['mudas_vendidas']} muda(s) vendidas"
            ),
            "passos": [
                {"label": vendas_label, "valor": fat, "operador": "="},
            ],
        },
        "cmv": {
            "titulo": "CMV — custo das mudas vendidas",
            "formula": "Σ quantidade × custo_unitario (congelado na venda; senão custo_atual da planta)",
            "total": cmv,
            "explicacao": (
                f"{cmv_raw['total_itens']} item(ns) de venda · "
                f"{cmv_raw['resumo_origem'].get('congelado', 0)} com custo congelado na venda · "
                f"{cmv_raw['resumo_origem'].get('planta_atual', 0)} com custo_atual da planta"
            ),
            "passos": [],
            "itens": cmv_raw["itens"],
            "total_itens": cmv_raw["total_itens"],
            "truncado": cmv_raw["truncado"],
            "resumo_origem": cmv_raw["resumo_origem"],
        },
        "lucro_bruto": {
            "titulo": "Lucro bruto",
            "formula": "Faturamento − CMV",
            "total": lucro,
            "explicacao": (
                f"Margem bruta {dre['margem_bruta_pct']}%"
                if dre.get("margem_bruta_pct") is not None
                else None
            ),
            "passos": [
                {"label": "Faturamento", "valor": fat, "operador": None},
                {"label": "CMV", "valor": cmv, "operador": "−"},
                {"label": "Lucro bruto", "valor": lucro, "operador": "="},
            ],
        },
        "compras_insumos": {
            "titulo": "Compras de insumos",
            "formula": (
                "Σ valor_total das entradas de insumo no período (à vista + a prazo)"
                if regime == REGIME_COMPETENCIA
                else "Σ entradas de insumo pagas no período (data de pagamento)"
            ),
            "total": compras,
            "explicacao": "Cadastradas em Estoques → Insumos (entrada ou cadastro com NF).",
            "passos": [
                {"label": compras_label, "valor": compras, "operador": "="},
            ],
            "itens": compras_itens,
        },
        "opex": {
            "titulo": "OPEX — despesas operacionais",
            "formula": "Σ premissas DESPESA (comissão % sobre faturamento + despesas fixas mensais)",
            "total": opex,
            "faturamento_base": fat,
            "explicacao": "Calculado automaticamente pelas premissas em Financeiro → Premissas. Não usa lançamentos manuais.",
            "passos": [
                {"label": "Comissão (premissas % receita)", "valor": dre["opex_comissao"], "operador": "+"},
                {"label": "Despesas fixas mensais", "valor": dre["opex_fixo"], "operador": "="},
            ],
            "itens": opex_itens,
        },
        "resultado": {
            "titulo": "Resultado operacional",
            "formula": "Lucro bruto − Compras de insumos − OPEX",
            "total": resultado,
            "explicacao": "CAPEX não entra aqui — investimentos aparecem separadamente.",
            "passos": [
                {"label": "Lucro bruto", "valor": lucro, "operador": None},
                {"label": "Compras de insumos", "valor": compras, "operador": "−"},
                {"label": "OPEX", "valor": opex, "operador": "−"},
                {"label": "Resultado operacional", "valor": resultado, "operador": "="},
            ],
        },
        "estoque": _estoque_detalhes_blocos(estoque, insumos_itens, sementes_itens),
        "capex": {
            "titulo": "CAPEX — investimentos",
            "formula": "Σ lançamentos manuais tipo CAPEX no período",
            "total": dre["capex"],
            "explicacao": "Registrados em Gestão → CAPEX. Não compõe o resultado operacional.",
            "passos": [
                {"label": f"{len(capex_itens)} lançamento(s) no período", "valor": dre["capex"], "operador": "="},
            ],
            "itens": capex_itens,
        },
    }


async def _listar_vendas_pendentes(
    db: AsyncSession,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Vendas PENDENTE — todas ou só do período (data_venda)."""
    q = (
        select(
            Venda.id,
            Venda.data_venda,
            Venda.valor_total,
            Venda.forma_pagamento,
            Comprador.nome.label("comprador_nome"),
        )
        .join(Comprador, Venda.id_comprador == Comprador.id)
        .where(Venda.status == "PENDENTE")
    )
    if mes is not None and ano is not None:
        inicio, fim = _periodo_datetime(mes, ano)
        q = q.where(Venda.data_venda >= inicio, Venda.data_venda < fim)
    rows = (await db.execute(q.order_by(Venda.data_venda.desc()).limit(100))).all()
    return [
        {
            "id": r.id,
            "data_venda": r.data_venda.isoformat() if r.data_venda else "",
            "comprador_nome": r.comprador_nome,
            "valor_total": float(r.valor_total or 0),
            "forma_pagamento": r.forma_pagamento,
        }
        for r in rows
    ]


async def _montar_detalhes_dfc(
    db: AsyncSession,
    mes: int,
    ano: int,
    dfc: Dict[str, Any],
    detalhes: Dict[str, Any],
) -> Dict[str, Any]:
    """Blocos explicativos da DFC — fórmula, passos e itens (regime caixa)."""
    ent = float(dfc["operacional"]["entradas"])
    comp = float(dfc["operacional"]["saidas"])
    op_sub = float(dfc["operacional"]["subtotal"])
    inv = float(dfc["investimento"]["saidas"])
    inv_sub = float(dfc["investimento"]["subtotal"])
    var = float(dfc["variacao_caixa"])
    qtd_rec = int(dfc.get("qtd_recebimentos") or 0)
    ticket = dfc.get("ticket_medio_recebido")

    entradas_itens = [
        {
            "id": e["id"],
            "data": e.get("data") or "",
            "descricao": e.get("descricao") or "",
            "valor": float(e.get("valor") or 0),
            "forma_pagamento": e.get("forma_pagamento"),
        }
        for e in dfc.get("entradas") or []
    ]
    compras_itens = detalhes.get("compras_insumos", {}).get("itens") or []
    capex_itens = detalhes.get("capex", {}).get("itens") or []

    pendentes_periodo = await _listar_vendas_pendentes(db, mes, ano)
    pendentes_aberto = await _listar_vendas_pendentes(db)

    a_rec_periodo = float(dfc.get("a_receber_periodo") or 0)
    a_rec_aberto = float(dfc.get("a_receber_aberto") or 0)

    ticket_txt = f"R$ {ticket:.2f}" if ticket is not None else "—"

    return {
        "recebimentos": {
            "titulo": "Recebimentos de clientes",
            "formula": "Σ valor_total das vendas com status PAGO no período, pela data de pagamento",
            "total": ent,
            "explicacao": (
                f"{qtd_rec} pagamento(s) · ticket médio {ticket_txt}. "
                "Aprovação do pagamento em Vendas define data_pagamento."
            ),
            "passos": [
                {"label": f"{len(entradas_itens)} recebimento(s) no período", "valor": ent, "operador": "="},
            ],
            "itens": entradas_itens,
        },
        "compras": detalhes.get("compras_insumos") or {
            "titulo": "Compras de insumo",
            "formula": "Σ entradas de insumo pagas no período (data de pagamento)",
            "total": comp,
            "explicacao": "Cadastradas em Compras e Estoques → Insumos.",
            "passos": [{"label": "Nenhuma compra paga", "valor": 0, "operador": "="}],
            "itens": [],
        },
        "operacional": {
            "titulo": "Caixa operacional",
            "formula": "Recebimentos − Compras de insumo pagas",
            "total": op_sub,
            "explicacao": "Atividades operacionais do período — entra e sai o que foi efetivamente pago.",
            "passos": [
                {"label": "Recebimentos de clientes", "valor": ent, "operador": None},
                {"label": "Compras de insumo", "valor": comp, "operador": "−"},
                {"label": "Caixa operacional", "valor": op_sub, "operador": "="},
            ],
        },
        "capex": detalhes.get("capex") or {
            "titulo": "CAPEX — investimentos",
            "formula": "Σ lançamentos manuais tipo CAPEX no período",
            "total": inv,
            "explicacao": "Registrados em Financeiro → Gestão.",
            "passos": [{"label": "Nenhum CAPEX", "valor": 0, "operador": "="}],
            "itens": [],
        },
        "investimento": {
            "titulo": "Caixa de investimento",
            "formula": "− Σ pagamentos CAPEX no período",
            "total": inv_sub,
            "explicacao": f"{len(capex_itens)} lançamento(s) CAPEX pago(s) no mês.",
            "passos": [
                {"label": "Pagamentos CAPEX", "valor": inv, "operador": "−"},
                {"label": "Caixa de investimento", "valor": inv_sub, "operador": "="},
            ],
        },
        "variacao": {
            "titulo": "Variação líquida de caixa",
            "formula": "Caixa operacional + Caixa de investimento",
            "total": var,
            "explicacao": "Saldo líquido de entradas e saídas no período (não é saldo de conta bancária acumulado).",
            "passos": [
                {"label": "Caixa operacional", "valor": op_sub, "operador": None},
                {"label": "Caixa de investimento", "valor": inv_sub, "operador": "+"},
                {"label": "Variação líquida de caixa", "valor": var, "operador": "="},
            ],
        },
        "a_receber_periodo": {
            "titulo": "A receber (período)",
            "formula": "Σ valor_total das vendas PENDENTE com data_venda no período",
            "total": a_rec_periodo,
            "explicacao": (
                f"{dfc.get('qtd_pendentes_periodo', 0)} venda(s) reconhecidas na DRE contábil, "
                "mas ainda sem recebimento no caixa."
            ),
            "passos": [
                {
                    "label": f"{len(pendentes_periodo)} venda(s) pendente(s) no período",
                    "valor": a_rec_periodo,
                    "operador": "=",
                },
            ],
            "itens": pendentes_periodo,
        },
        "a_receber_aberto": {
            "titulo": "A receber (em aberto)",
            "formula": "Σ valor_total de todas as vendas PENDENTE no sistema",
            "total": a_rec_aberto,
            "explicacao": (
                f"{dfc.get('qtd_vendas_pendentes', 0)} venda(s) na carteira — "
                "entram no caixa ao aprovar pagamento em Vendas."
            ),
            "passos": [
                {
                    "label": f"{len(pendentes_aberto)} venda(s) pendente(s) total",
                    "valor": a_rec_aberto,
                    "operador": "=",
                },
            ],
            "itens": pendentes_aberto,
        },
    }


async def get_painel_financeiro(
    db: AsyncSession,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    regime: str = REGIME_CAIXA,
) -> Dict[str, Any]:
    mes, ano = _resolver_mes_ano(mes, ano)

    dre = await _dre_periodo(db, mes, ano, regime)
    from app.crud.coletas_sementes import sanear_custos_coleta_campo_pendentes

    await sanear_custos_coleta_campo_pendentes(db)
    integridade = await _integridade_financeira(db)
    desp = await estimar_despesas_periodo(db, dre["faturamento"])
    desp_escalada = _escala_despesas_periodo(desp, mes, ano)
    estoque = await _estoque_financeiro(db)
    receitas = await _receitas_periodo(db, mes, ano, regime=regime)
    detalhes = await _montar_detalhes_financeiro(
        db, mes, ano, dre, desp_escalada, receitas, estoque, regime=regime
    )
    out = {
        "regime": regime,
        "regime_descricao": _descricao_regime(regime),
        "periodo": {"mes": mes, "ano": ano, "label": _label_periodo(mes, ano)},
        "dre": dre,
        "estoque": estoque,
        "integridade": integridade,
        "margem_especies": await _margem_especies(db, mes, ano, regime),
        "avisos": await _avisos_financeiros(db, mes, ano, integridade, regime),
        "evolucao_mensal": await _evolucao_mensal(db, mes, ano, regime=regime),
        "receitas": receitas,
        "opex_por_categoria": await _opex_distribuicao_premissas(db, dre["faturamento"]),
        "capex_por_categoria": await _distribuicao_categoria(db, mes, ano, "CAPEX"),
        "despesas_estimadas": {
            "comissao_estimada": desp_escalada["comissao_estimada"],
            "despesas_fixas_mes": desp_escalada["despesas_fixas_mes"],
            "total_despesas_estimadas": desp_escalada["total_despesas_estimadas"],
            "itens": [
                {
                    "nome": i["nome"],
                    "chave": i["chave"],
                    "valor": i["valor"],
                    "tipo": i["tipo"],
                    "formula": i.get("formula"),
                    "base_valor": i.get("base_valor"),
                    "base_unidade": i.get("base_unidade"),
                }
                for i in desp_escalada.get("itens", [])
            ],
        },
        "detalhes": detalhes,
        "detalhes_dfc": None,
        "dfc": None,
        "evolucao_caixa": [],
    }
    if regime == REGIME_CAIXA:
        out["dfc"] = await _dfc_periodo(db, mes, ano)
        out["evolucao_caixa"] = await _evolucao_caixa(db, mes, ano)
        out["detalhes_dfc"] = await _montar_detalhes_dfc(db, mes, ano, out["dfc"], detalhes)
        out["margem_especies"] = []
        out["avisos"] = [
            a
            for a in out["avisos"]
            if a.get("tipo")
            not in ("venda_abaixo_custo", "especie_prejuizo", "resultado_negativo")
        ]
    return out


async def _dfc_periodo(db: AsyncSession, mes: int, ano: int) -> Dict[str, Any]:
    lc = await get_livro_caixa(db, mes, ano)
    inicio, fim = _periodo_datetime(mes, ano)

    a_receber_aberto = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(Venda.valor_total), 0)).where(Venda.status == "PENDENTE")
            )
        ).scalar()
        or 0
    )
    qtd_pendentes = int(
        (await db.execute(select(func.count(Venda.id)).where(Venda.status == "PENDENTE"))).scalar() or 0
    )

    a_receber_periodo = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(Venda.valor_total), 0)).where(
                    Venda.status == "PENDENTE",
                    Venda.data_venda >= inicio,
                    Venda.data_venda < fim,
                )
            )
        ).scalar()
        or 0
    )
    qtd_pendentes_periodo = int(
        (
            await db.execute(
                select(func.count(Venda.id)).where(
                    Venda.status == "PENDENTE",
                    Venda.data_venda >= inicio,
                    Venda.data_venda < fim,
                )
            )
        ).scalar()
        or 0
    )

    entradas_op = lc["total_entradas"]
    saidas_op = lc["total_saidas_operacionais"]
    saidas_inv = lc["total_saidas_investimento"]
    qtd_rec = len(lc["entradas"])
    qtd_compras = len(lc["saidas_operacionais"])
    ticket = round(entradas_op / qtd_rec, 2) if qtd_rec else None

    inicio_d, fim_d = _periodo_date(mes, ano)
    a_pagar_aberto = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(InsumoMovimentacao.valor_total), 0)).where(
                    InsumoMovimentacao.tipo == "entrada",
                    InsumoMovimentacao.status_pagamento == "PENDENTE",
                    func.coalesce(InsumoMovimentacao.valor_total, 0) > 0,
                )
            )
        ).scalar()
        or 0
    )
    qtd_compras_pendentes = int(
        (
            await db.execute(
                select(func.count(InsumoMovimentacao.id)).where(
                    InsumoMovimentacao.tipo == "entrada",
                    InsumoMovimentacao.status_pagamento == "PENDENTE",
                    func.coalesce(InsumoMovimentacao.valor_total, 0) > 0,
                )
            )
        ).scalar()
        or 0
    )
    a_pagar_periodo = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(InsumoMovimentacao.valor_total), 0)).where(
                    InsumoMovimentacao.tipo == "entrada",
                    InsumoMovimentacao.status_pagamento == "PENDENTE",
                    func.coalesce(InsumoMovimentacao.valor_total, 0) > 0,
                    InsumoMovimentacao.data_movimento >= inicio_d,
                    InsumoMovimentacao.data_movimento <= fim_d,
                )
            )
        ).scalar()
        or 0
    )
    qtd_pendentes_compras_periodo = int(
        (
            await db.execute(
                select(func.count(InsumoMovimentacao.id)).where(
                    InsumoMovimentacao.tipo == "entrada",
                    InsumoMovimentacao.status_pagamento == "PENDENTE",
                    func.coalesce(InsumoMovimentacao.valor_total, 0) > 0,
                    InsumoMovimentacao.data_movimento >= inicio_d,
                    InsumoMovimentacao.data_movimento <= fim_d,
                )
            )
        ).scalar()
        or 0
    )

    return {
        "operacional": {
            "entradas": entradas_op,
            "saidas": saidas_op,
            "subtotal": round(entradas_op - saidas_op, 2),
        },
        "investimento": {
            "entradas": 0.0,
            "saidas": saidas_inv,
            "subtotal": round(-saidas_inv, 2),
        },
        "variacao_caixa": lc["saldo_periodo"],
        "qtd_recebimentos": qtd_rec,
        "qtd_compras": qtd_compras,
        "ticket_medio_recebido": ticket,
        "a_receber_aberto": a_receber_aberto,
        "qtd_vendas_pendentes": qtd_pendentes,
        "a_receber_periodo": a_receber_periodo,
        "qtd_pendentes_periodo": qtd_pendentes_periodo,
        "a_pagar_aberto": a_pagar_aberto,
        "qtd_compras_pendentes": qtd_compras_pendentes,
        "a_pagar_periodo": a_pagar_periodo,
        "qtd_pendentes_compras_periodo": qtd_pendentes_compras_periodo,
        "entradas": lc["entradas"],
        "saidas_operacionais": lc["saidas_operacionais"],
        "saidas": lc["saidas"],
    }


async def _evolucao_caixa(db: AsyncSession, mes: int, ano: int, meses: int = 12) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    m, a = mes, ano
    for _ in range(meses):
        lc = await get_livro_caixa(db, m, a)
        out.append(
            {
                "mes": m,
                "ano": a,
                "label": _label_periodo(m, a),
                "entradas": lc["total_entradas"],
                "saidas": lc["total_saidas"],
                "saldo": lc["saldo_periodo"],
            }
        )
        m -= 1
        if m < 1:
            m = 12
            a -= 1
    out.reverse()
    return out


async def _listar_vendas_pendentes_ate(
    db: AsyncSession,
    fim_dt: datetime,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    rows = (
        await db.execute(
            select(
                Venda.id,
                Venda.data_venda,
                Venda.valor_total,
                Venda.forma_pagamento,
                Comprador.nome.label("comprador_nome"),
            )
            .join(Comprador, Venda.id_comprador == Comprador.id)
            .where(Venda.status == "PENDENTE", Venda.data_venda <= fim_dt)
            .order_by(Venda.data_venda.desc())
            .limit(limit)
        )
    ).all()
    return [
        {
            "id": r.id,
            "data_venda": r.data_venda.isoformat() if r.data_venda else "",
            "comprador_nome": r.comprador_nome,
            "valor_total": float(r.valor_total or 0),
            "forma_pagamento": r.forma_pagamento,
        }
        for r in rows
    ]


async def _listar_compras_pendentes_ate(
    db: AsyncSession,
    fim_d: date,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    rows = (
        await db.execute(
            select(InsumoMovimentacao, Insumo.nome.label("insumo_nome"))
            .join(Insumo, InsumoMovimentacao.id_insumo == Insumo.id)
            .where(
                InsumoMovimentacao.tipo == "entrada",
                InsumoMovimentacao.status_pagamento == "PENDENTE",
                func.coalesce(InsumoMovimentacao.valor_total, 0) > 0,
                InsumoMovimentacao.data_movimento <= fim_d,
            )
            .order_by(InsumoMovimentacao.data_movimento.desc(), InsumoMovimentacao.id.desc())
            .limit(limit)
        )
    ).all()
    return [
        {
            "id": m.id,
            "data_movimento": m.data_movimento.isoformat() if m.data_movimento else "",
            "insumo_nome": nome,
            "quantidade": float(m.quantidade or 0),
            "valor_total": float(m.valor_total or 0),
            "status_pagamento": m.status_pagamento,
        }
        for m, nome in rows
    ]


async def _montar_detalhes_livro_caixa(
    db: AsyncSession,
    mes: int,
    ano: int,
    lc: Dict[str, Any],
) -> Dict[str, Any]:
    compras_itens = await _detalhe_compras_insumos(db, mes, ano, REGIME_CAIXA)
    capex_itens = await _detalhe_capex_lancamentos(db, mes, ano)
    ent = float(lc["total_entradas"])
    comp = float(lc["total_saidas_operacionais"])
    inv = float(lc["total_saidas_investimento"])
    saldo = float(lc["saldo_periodo"])
    qtd_rec = len(lc.get("entradas") or [])
    ticket = round(ent / qtd_rec, 2) if qtd_rec else None
    ticket_txt = f"R$ {ticket:.2f}" if ticket is not None else "—"

    entradas_itens = [
        {
            "id": e["id"],
            "data": e.get("data") or "",
            "descricao": e.get("descricao") or "",
            "valor": float(e.get("valor") or 0),
            "forma_pagamento": e.get("forma_pagamento"),
        }
        for e in lc.get("entradas") or []
    ]

    return {
        "entradas": {
            "titulo": "Entradas — recebimentos",
            "formula": "Σ valor_total das vendas PAGO no período, pela data de pagamento",
            "total": ent,
            "explicacao": f"{qtd_rec} recebimento(s) · ticket médio {ticket_txt}.",
            "passos": [{"label": f"{qtd_rec} recebimento(s) no período", "valor": ent, "operador": "="}],
            "itens": entradas_itens,
        },
        "saidas_operacionais": {
            "titulo": "Saídas operacionais — compras de insumo",
            "formula": "Σ entradas de insumo pagas no período (data de pagamento)",
            "total": comp,
            "explicacao": f"{len(compras_itens)} compra(s) quitada(s) no período.",
            "passos": [{"label": f"{len(compras_itens)} compra(s) pagas", "valor": comp, "operador": "="}],
            "itens": compras_itens,
        },
        "saidas_investimento": {
            "titulo": "Saídas de investimento — CAPEX",
            "formula": "Σ lançamentos manuais tipo CAPEX no período",
            "total": inv,
            "explicacao": f"{len(capex_itens)} lançamento(s) CAPEX.",
            "passos": [{"label": f"{len(capex_itens)} lançamento(s)", "valor": inv, "operador": "="}],
            "itens": [
                {
                    "id": s["id"],
                    "data_lancamento": s.get("data_lancamento") or "",
                    "descricao": s.get("descricao") or "",
                    "categoria": s.get("categoria"),
                    "valor": float(s.get("valor") or 0),
                    "forma_pagamento": s.get("forma_pagamento"),
                }
                for s in capex_itens
            ],
        },
        "saldo": {
            "titulo": "Saldo do período",
            "formula": "Entradas − Saídas operacionais − Saídas CAPEX",
            "total": saldo,
            "explicacao": "Livro caixa contábil — regime de caixa (movimentação efetiva).",
            "passos": [
                {"label": "Entradas", "valor": ent, "operador": None},
                {"label": "Saídas operacionais", "valor": comp, "operador": "−"},
                {"label": "Saídas CAPEX", "valor": inv, "operador": "−"},
                {"label": "Saldo do período", "valor": saldo, "operador": "="},
            ],
        },
    }


async def _caixa_equivalentes_ate(db: AsyncSession, fim_d: date, fim_dt: datetime) -> Dict[str, float]:
    """Saldo de caixa acumulado (regime caixa) até a data de referência do BP."""
    recebimentos = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(Venda.valor_total), 0)).where(
                    Venda.status == "PAGO",
                    _data_referencia_caixa() <= fim_dt,
                )
            )
        ).scalar()
        or 0
    )
    pagamentos_insumos = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(InsumoMovimentacao.valor_total), 0)).where(
                    InsumoMovimentacao.tipo == "entrada",
                    func.coalesce(InsumoMovimentacao.valor_total, 0) > 0,
                    or_(
                        InsumoMovimentacao.status_pagamento == "PAGO",
                        InsumoMovimentacao.status_pagamento.is_(None),
                    ),
                    _data_pagamento_compra() <= fim_d,
                )
            )
        ).scalar()
        or 0
    )
    pagamentos_capex = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(LancamentoFinanceiro.valor), 0)).where(
                    LancamentoFinanceiro.tipo == "CAPEX",
                    LancamentoFinanceiro.data_lancamento <= fim_d,
                )
            )
        ).scalar()
        or 0
    )
    saldo = round(recebimentos - pagamentos_insumos - pagamentos_capex, 2)
    return {
        "recebimentos": round(recebimentos, 2),
        "pagamentos_insumos": round(pagamentos_insumos, 2),
        "pagamentos_capex": round(pagamentos_capex, 2),
        "saldo": saldo,
    }


async def _imobilizado_ate(db: AsyncSession, fim_d: date) -> float:
    """Custo histórico de CAPEX acumulado (sem depreciação — contador ajusta)."""
    return float(
        (
            await db.execute(
                select(func.coalesce(func.sum(LancamentoFinanceiro.valor), 0)).where(
                    LancamentoFinanceiro.tipo == "CAPEX",
                    LancamentoFinanceiro.data_lancamento <= fim_d,
                )
            )
        ).scalar()
        or 0
    )


async def _montar_detalhes_balanco(
    db: AsyncSession,
    bp: Dict[str, Any],
    estoque: Dict[str, Any],
    fim_d: date,
    fim_dt: datetime,
) -> Dict[str, Any]:
    insumos_itens = await _detalhe_estoque_insumos(db)
    sementes_itens = await _detalhe_estoque_sementes(db)
    est = _estoque_detalhes_blocos(estoque, insumos_itens, sementes_itens)

    circ = bp["ativo"]["circulante"]
    nao_circ = bp["ativo"]["nao_circulante"]
    pass_circ = bp["passivo"]["circulante"]
    pl_grupo = bp["patrimonio_liquido_grupo"]

    caixa = float(circ["caixa_equivalentes"])
    mudas = float(circ["estoques"]["mudas"])
    ins = float(circ["estoques"]["insumos"])
    sem = float(circ["estoques"]["sementes"])
    est_total = float(circ["estoques"]["total"])
    rec = float(circ["contas_receber"])
    fornec = float(pass_circ["fornecedores"])
    imob = float(nao_circ["imobilizado"])
    ativo_circ = float(circ["total"])
    ativo_total = float(bp["ativo"]["total"])
    passivo_total = float(bp["passivo"]["total"])
    pl = float(bp["patrimonio_liquido"])
    resultado = float(pl_grupo["resultado_exercicio"])
    acumulados = float(pl_grupo["lucros_acumulados"])

    caixa_comp = bp.get("_caixa_composicao") or {}
    pendentes_vendas = await _listar_vendas_pendentes_ate(db, fim_dt)
    pendentes_compras = await _listar_compras_pendentes_ate(db, fim_d)

    return {
        "caixa_equivalentes": {
            "titulo": "Caixa e equivalentes de caixa",
            "formula": "Recebimentos de vendas − Pagamentos de insumos − Pagamentos CAPEX (acumulado)",
            "total": caixa,
            "explicacao": (
                "Posição de caixa derivada dos fluxos registrados no sistema. "
                "OPEX estimado (premissas) não reduz o caixa aqui."
            ),
            "passos": [
                {"label": "Recebimentos (vendas pagas)", "valor": caixa_comp.get("recebimentos", 0), "operador": None},
                {"label": "Pagamentos de insumos", "valor": caixa_comp.get("pagamentos_insumos", 0), "operador": "−"},
                {"label": "Pagamentos CAPEX", "valor": caixa_comp.get("pagamentos_capex", 0), "operador": "−"},
                {"label": "Saldo em caixa", "valor": caixa, "operador": "="},
            ],
        },
        "estoque_mudas": {
            "titulo": "Estoques — mudas",
            "formula": est["parque"]["formula"],
            "total": mudas,
            "explicacao": est["parque"]["explicacao"],
            "passos": est["parque"]["passos"],
        },
        "estoque_insumos": {
            "titulo": "Estoques — insumos",
            "formula": est["insumos"]["formula"],
            "total": ins,
            "explicacao": est["insumos"]["explicacao"],
            "passos": est["insumos"]["passos"],
            "itens": insumos_itens,
        },
        "estoque_sementes": {
            "titulo": "Estoques — sementes",
            "formula": est["sementes"]["formula"],
            "total": sem,
            "explicacao": est["sementes"]["explicacao"],
            "passos": est["sementes"]["passos"],
            "itens": sementes_itens,
        },
        "estoques": {
            "titulo": "Estoques (ativo circulante)",
            "formula": "Mudas + insumos + sementes ao custo operacional",
            "total": est_total,
            "explicacao": "Agrupamento conforme CPC 16 / Lei 6.404 — estoques no circulante.",
            "passos": [
                {"label": "Mudas", "valor": mudas, "operador": None},
                {"label": "Insumos", "valor": ins, "operador": "+"},
                {"label": "Sementes", "valor": sem, "operador": "+"},
                {"label": "Total estoques", "valor": est_total, "operador": "="},
            ],
        },
        "contas_receber": {
            "titulo": "Contas a receber de clientes",
            "formula": "Σ valor_total das vendas PENDENTE com data_venda até a data de referência",
            "total": rec,
            "explicacao": f"{len(pendentes_vendas)} venda(s) ainda não recebidas no caixa.",
            "passos": [{"label": f"{len(pendentes_vendas)} título(s) em aberto", "valor": rec, "operador": "="}],
            "itens": pendentes_vendas,
        },
        "fornecedores": {
            "titulo": "Fornecedores",
            "formula": "Σ compras de insumo PENDENTE com data da NF até a data de referência",
            "total": fornec,
            "explicacao": f"{len(pendentes_compras)} compra(s) a prazo em aberto.",
            "passos": [{"label": f"{len(pendentes_compras)} título(s) em aberto", "valor": fornec, "operador": "="}],
            "itens": pendentes_compras,
        },
        "imobilizado": {
            "titulo": "Imobilizado",
            "formula": "Σ lançamentos CAPEX acumulados até a data de referência",
            "total": imob,
            "explicacao": (
                "Custo histórico dos investimentos registrados (terrenos, máquinas, instalações…). "
                "Depreciação/amortização deve ser aplicada pelo contador."
            ),
            "passos": [{"label": "CAPEX acumulado", "valor": imob, "operador": "="}],
        },
        "ativo_circulante": {
            "titulo": "Ativo circulante",
            "formula": "Caixa + Contas a receber + Estoques (+ despesas antecipadas quando houver)",
            "total": ativo_circ,
            "explicacao": f"Referência {fim_d.isoformat()} — estrutura Lei 6.404.",
            "passos": [
                {"label": "Caixa e equivalentes", "valor": caixa, "operador": None},
                {"label": "Contas a receber", "valor": rec, "operador": "+"},
                {"label": "Estoques", "valor": est_total, "operador": "+"},
                {"label": "Total circulante", "valor": ativo_circ, "operador": "="},
            ],
        },
        "ativo_total": {
            "titulo": "Total do ativo",
            "formula": "Ativo circulante + Ativo não circulante",
            "total": ativo_total,
            "explicacao": "Deve igualar Passivo + Patrimônio líquido.",
            "passos": [
                {"label": "Ativo circulante", "valor": ativo_circ, "operador": None},
                {"label": "Ativo não circulante", "valor": float(nao_circ["total"]), "operador": "+"},
                {"label": "Total do ativo", "valor": ativo_total, "operador": "="},
            ],
        },
        "resultado_exercicio": {
            "titulo": "Resultado do exercício",
            "formula": "Resultado operacional da DRE (competência) no período selecionado",
            "total": resultado,
            "explicacao": "Linha informativa do PL — reconhecida na DRE, não no caixa do BP.",
            "passos": [{"label": "Resultado operacional (DRE)", "valor": resultado, "operador": "="}],
        },
        "lucros_acumulados": {
            "titulo": "Lucros/prejuízos acumulados",
            "formula": "Patrimônio líquido total − Resultado do exercício",
            "total": acumulados,
            "explicacao": (
                "Saldo patrimonial residual (capital, reservas e exercícios anteriores não escriturados "
                "separadamente no sistema)."
            ),
            "passos": [
                {"label": "Patrimônio líquido", "valor": pl, "operador": None},
                {"label": "Resultado do exercício", "valor": resultado, "operador": "−"},
                {"label": "Lucros acumulados (ajuste)", "valor": acumulados, "operador": "="},
            ],
        },
        "patrimonio_liquido": {
            "titulo": "Patrimônio líquido",
            "formula": "Ativo total − Passivo total",
            "total": pl,
            "explicacao": "Equação fundamental: Ativo = Passivo + Patrimônio líquido.",
            "passos": [
                {"label": "Ativo total", "valor": ativo_total, "operador": None},
                {"label": "Passivo total", "valor": passivo_total, "operador": "−"},
                {"label": "Patrimônio líquido", "valor": pl, "operador": "="},
            ],
        },
    }


def _montar_detalhes_inventario(
    estoque: Dict[str, Any],
    insumos_itens: List[Dict[str, Any]],
    sementes_itens: List[Dict[str, Any]],
    resumo: Dict[str, Any],
) -> Dict[str, Any]:
    est = _estoque_detalhes_blocos(estoque, insumos_itens, sementes_itens)
    mv = resumo["mudas_vivas"]
    mc = resumo["mudas_comercial"]
    ins = resumo["insumos"]
    sem = resumo["sementes"]
    total = resumo["valor_total"]
    return {
        "mudas_vivas": est["parque"],
        "mudas_comercial": est["comercial"],
        "insumos": {**est["insumos"], "itens": insumos_itens},
        "sementes": {**est["sementes"], "itens": sementes_itens},
        "valor_total": {
            "titulo": "Valor total inventariado",
            "formula": "Mudas vivas + Insumos + Sementes",
            "total": total,
            "explicacao": "Mudas comercial é subconjunto do parque — não soma em duplicidade.",
            "passos": [
                {"label": f"Mudas vivas ({mv['quantidade']} un.)", "valor": mv["valor"], "operador": None},
                {"label": f"Insumos ({ins.get('itens', 0)} itens)", "valor": ins["valor"], "operador": "+"},
                {"label": "Sementes (lotes ativos)", "valor": sem["valor"], "operador": "+"},
                {"label": "Total inventariado", "valor": total, "operador": "="},
            ],
        },
    }


async def get_balanco_patrimonial(
    db: AsyncSession,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
) -> Dict[str, Any]:
    """BP em estrutura Lei 6.404 / CPC — snapshot na data de referência do período."""
    mes, ano = _resolver_mes_ano(mes, ano)
    _, fim_d = _periodo_date(mes, ano)
    fim_dt = datetime(fim_d.year, fim_d.month, fim_d.day, 23, 59, 59)

    estoque = await _estoque_financeiro(db)
    valor_mudas = float(estoque["valor_mudas_vivas"])
    valor_insumos = float(estoque["valor_insumos"])
    valor_sementes = float(estoque["valor_sementes"])
    valor_estoque = round(valor_mudas + valor_insumos + valor_sementes, 2)

    caixa_comp = await _caixa_equivalentes_ate(db, fim_d, fim_dt)
    caixa = caixa_comp["saldo"]
    imobilizado = round(await _imobilizado_ate(db, fim_d), 2)

    contas_receber = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(Venda.valor_total), 0)).where(
                    Venda.status == "PENDENTE",
                    Venda.data_venda <= fim_dt,
                )
            )
        ).scalar()
        or 0
    )

    fornecedores = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(InsumoMovimentacao.valor_total), 0)).where(
                    InsumoMovimentacao.tipo == "entrada",
                    InsumoMovimentacao.status_pagamento == "PENDENTE",
                    func.coalesce(InsumoMovimentacao.valor_total, 0) > 0,
                    InsumoMovimentacao.data_movimento <= fim_d,
                )
            )
        ).scalar()
        or 0
    )

    dre = await _dre_periodo(db, mes, ano, REGIME_COMPETENCIA)
    resultado_periodo = float(dre["resultado_operacional"])

    ativo_circulante = round(caixa + contas_receber + valor_estoque, 2)
    ativo_nao_circulante = round(imobilizado, 2)
    ativo_total = round(ativo_circulante + ativo_nao_circulante, 2)

    passivo_circulante = round(fornecedores, 2)
    passivo_nao_circulante = 0.0
    passivo_total = round(passivo_circulante + passivo_nao_circulante, 2)

    patrimonio_liquido = round(ativo_total - passivo_total, 2)
    lucros_acumulados = round(patrimonio_liquido - resultado_periodo, 2)

    bp = {
        "periodo": {"mes": mes, "ano": ano, "label": _label_periodo(mes, ano)},
        "data_referencia": fim_d.isoformat(),
        "ativo": {
            "circulante": {
                "caixa_equivalentes": caixa,
                "contas_receber": contas_receber,
                "estoques": {
                    "mudas": valor_mudas,
                    "insumos": valor_insumos,
                    "sementes": valor_sementes,
                    "total": valor_estoque,
                },
                "despesas_antecipadas": 0.0,
                "total": ativo_circulante,
            },
            "nao_circulante": {
                "realizavel_longo_prazo": 0.0,
                "investimentos": 0.0,
                "imobilizado": imobilizado,
                "intangivel": 0.0,
                "total": ativo_nao_circulante,
            },
            "total": ativo_total,
        },
        "passivo": {
            "circulante": {
                "fornecedores": fornecedores,
                "emprestimos_financiamentos": 0.0,
                "obrigacoes_fiscais": 0.0,
                "outras_obrigacoes": 0.0,
                "total": passivo_circulante,
            },
            "nao_circulante": {
                "emprestimos": 0.0,
                "outras_obrigacoes": 0.0,
                "total": passivo_nao_circulante,
            },
            "total": passivo_total,
        },
        "patrimonio_liquido_grupo": {
            "capital_social": 0.0,
            "reservas": 0.0,
            "lucros_acumulados": lucros_acumulados,
            "resultado_exercicio": resultado_periodo,
            "total": patrimonio_liquido,
        },
        "patrimonio_liquido": patrimonio_liquido,
        "resultado_periodo": resultado_periodo,
        "passivo_mais_pl": round(passivo_total + patrimonio_liquido, 2),
        "estoque_detalhe": estoque,
        "observacoes": [
            "Demonstração estruturada conforme Lei 6.404/76 e CPCs — posição na data de referência.",
            "SisViNa é sistema florestal de viveiro: linhas sem movimento aparecem zeradas (auxílio ao contador).",
            "Caixa: recebimentos de vendas − pagamentos de insumos e CAPEX registrados até a referência.",
            "Estoques ao custo operacional; contas a receber = vendas PENDENTE; fornecedores = compras PENDENTE.",
            "Imobilizado = CAPEX acumulado (custo histórico, sem depreciação). OPEX de premissas não entra no caixa.",
        ],
        "_caixa_composicao": caixa_comp,
    }
    bp["detalhes"] = await _montar_detalhes_balanco(db, bp, estoque, fim_d, fim_dt)
    del bp["_caixa_composicao"]
    return bp


async def get_livro_caixa(
    db: AsyncSession,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
) -> Dict[str, Any]:
    """Livro caixa — entradas (recebimentos), saídas operacionais (compras) e CAPEX."""
    mes, ano = _resolver_mes_ano(mes, ano)
    inicio, fim = _periodo_datetime(mes, ano)
    inicio_d, fim_d = _periodo_date(mes, ano)

    entradas_rows = (
        await db.execute(
            select(Venda, Comprador.nome.label("comprador_nome"))
            .join(Comprador, Venda.id_comprador == Comprador.id)
            .where(_filtro_vendas(REGIME_CAIXA, inicio, fim))
            .order_by(_data_referencia_caixa().desc())
        )
    ).all()

    entradas = [
        {
            "id": v.id,
            "data": (v.data_pagamento or v.data_venda).isoformat() if (v.data_pagamento or v.data_venda) else "",
            "descricao": f"Venda #{v.id} — {comprador}",
            "valor": float(v.valor_total or 0),
            "forma_pagamento": v.forma_pagamento,
            "status": v.status,
        }
        for v, comprador in entradas_rows
    ]
    total_entradas = round(sum(e["valor"] for e in entradas), 2)

    compras_raw = await _detalhe_compras_insumos(db, mes, ano, REGIME_CAIXA)
    saidas_operacionais = [
        {
            "id": c["id"],
            "data": c["data_pagamento"] or c["data_movimento"],
            "descricao": f"Compra — {c['insumo_nome']}",
            "valor": c["valor_total"],
            "categoria": "compra_insumo",
            "status_pagamento": c["status_pagamento"],
        }
        for c in compras_raw
    ]
    total_saidas_operacionais = round(sum(s["valor"] for s in saidas_operacionais), 2)

    saidas_raw = await _detalhe_capex_lancamentos(db, mes, ano)
    saidas = [
        {
            "id": s["id"],
            "data": s["data_lancamento"],
            "descricao": s["descricao"] or s["categoria"] or "CAPEX",
            "valor": s["valor"],
            "categoria": s["categoria"],
            "forma_pagamento": s["forma_pagamento"],
        }
        for s in saidas_raw
    ]
    total_saidas_investimento = round(sum(s["valor"] for s in saidas), 2)
    total_saidas = round(total_saidas_operacionais + total_saidas_investimento, 2)
    saldo = round(total_entradas - total_saidas, 2)

    lc = {
        "periodo": {"mes": mes, "ano": ano, "label": _label_periodo(mes, ano)},
        "entradas": entradas,
        "saidas_operacionais": saidas_operacionais,
        "saidas": saidas,
        "total_entradas": total_entradas,
        "total_saidas_operacionais": total_saidas_operacionais,
        "total_saidas_investimento": total_saidas_investimento,
        "total_saidas": total_saidas,
        "saldo_periodo": saldo,
        "observacoes": [
            "Entradas: vendas com status PAGO pela data de pagamento.",
            "Saídas operacionais: compras de insumo pagas no período.",
            "Saídas de investimento: lançamentos CAPEX registrados manualmente.",
            "OPEX estimado (premissas) não aparece aqui — é despesa de competência na DRE.",
        ],
    }
    lc["detalhes"] = await _montar_detalhes_livro_caixa(db, mes, ano, lc)
    return lc


async def get_livro_inventario(
    db: AsyncSession,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
) -> Dict[str, Any]:
    """Livro de inventário — registro de estoques na data de referência."""
    mes, ano = _resolver_mes_ano(mes, ano)
    _, fim_d = _periodo_date(mes, ano)

    estoque = await _estoque_financeiro(db)
    insumos = await _detalhe_estoque_insumos(db)
    sementes = await _detalhe_estoque_sementes(db)

    resumo = {
            "mudas_vivas": {
                "quantidade": estoque["mudas_vivas"],
                "valor": estoque["valor_mudas_vivas"],
                "custo_medio": estoque["custo_medio_muda_viva"],
            },
            "mudas_comercial": {
                "quantidade": estoque["mudas_comercial"],
                "valor": estoque["valor_mudas_comercial"],
                "custo_medio": estoque["custo_medio_muda_comercial"],
            },
            "insumos": {
                "itens": estoque["total_insumos"],
                "valor": estoque["valor_insumos"],
            },
            "sementes": {
                "valor": estoque["valor_sementes"],
            },
            "valor_total": round(
                estoque["valor_mudas_vivas"]
                + estoque["valor_insumos"]
                + estoque["valor_sementes"],
                2,
            ),
        }

    inv = {
        "periodo": {"mes": mes, "ano": ano, "label": _label_periodo(mes, ano)},
        "data_referencia": fim_d.isoformat(),
        "resumo": resumo,
        "insumos": insumos,
        "sementes": sementes,
        "observacoes": [
            "Inventário físico-contábil com base nos saldos operacionais do sistema.",
            "Mudas comercial = subconjunto apto para venda (rustificação).",
            "Valores de sementes derivam de horas de coleta × homem-hora rateado.",
        ],
    }
    inv["detalhes"] = _montar_detalhes_inventario(estoque, insumos, sementes, resumo)
    return inv


async def get_notas_explicativas(
    db: AsyncSession,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
) -> Dict[str, Any]:
    """Notas explicativas — critérios contábeis e destaques do período."""
    mes, ano = _resolver_mes_ano(mes, ano)

    painel = await get_painel_financeiro(db, mes, ano, regime=REGIME_COMPETENCIA)
    balanco = await get_balanco_patrimonial(db, mes, ano)
    dre = painel["dre"]
    inicio, fim = _periodo_datetime(mes, ano)

    pendentes_periodo = int(
        (
            await db.execute(
                select(func.count(Venda.id)).where(
                    Venda.status == "PENDENTE",
                    Venda.data_venda >= inicio,
                    Venda.data_venda < fim,
                )
            )
        ).scalar()
        or 0
    )

    return {
        "periodo": painel["periodo"],
        "regime": REGIME_COMPETENCIA,
        "secoes": [
            {
                "titulo": "Regime de competência",
                "texto": (
                    "A DRE contábil reconhece receita e CMV no fato gerador — data da venda "
                    "(fornecimento da mercadoria), incluindo vendas com pagamento ainda PENDENTE. "
                    "O Financeiro gerencial usa regime de caixa (recebimento efetivo)."
                ),
            },
            {
                "titulo": "Critério de CMV",
                "texto": (
                    "Custo das mudas vendidas: custo_unitario congelado na venda quando disponível; "
                    "senão custo_atual da planta. Sementes e insumos seguem premissas e movimentações "
                    "operacionais descritas em Financeiro → Premissas."
                ),
            },
            {
                "titulo": "Compras de insumos",
                "texto": (
                    "Entradas de insumo em Estoques são tratadas como compra. Na competência entram na DRE "
                    "pela data da NF; no caixa só quando status PAGO (à vista ou quitação)."
                ),
            },
            {
                "titulo": "OPEX na DRE",
                "texto": (
                    "Despesas operacionais estimadas pelas premissas DESPESA (fixas mensais + comissão % "
                    "sobre faturamento do período). Não substituem escrituração fiscal nem SPED."
                ),
            },
            {
                "titulo": "Balanço patrimonial (Lei 6.404)",
                "texto": (
                    f"Ativo total R$ {balanco['ativo']['total']:.2f} "
                    f"(circulante R$ {balanco['ativo']['circulante']['total']:.2f} · "
                    f"não circulante R$ {balanco['ativo']['nao_circulante']['total']:.2f}). "
                    f"Passivo R$ {balanco['passivo']['total']:.2f} · "
                    f"PL R$ {balanco['patrimonio_liquido']:.2f}. "
                    "Linhas não escrituradas no sistema (capital, empréstimos, tributos) ficam zeradas."
                ),
            },
            {
                "titulo": "Destaques do período",
                "texto": (
                    f"Faturamento R$ {dre['faturamento']:.2f} · CMV R$ {dre['cmv']:.2f} · "
                    f"Resultado operacional R$ {dre['resultado_operacional']:.2f}. "
                    f"{pendentes_periodo} venda(s) pendente(s) de pagamento reconhecidas na competência."
                ),
            },
        ],
        "dre_resumo": dre,
        "balanco_resumo": {
            "ativo_total": balanco["ativo"]["total"],
            "patrimonio_liquido": balanco["patrimonio_liquido"],
            "contas_receber": balanco["ativo"]["circulante"]["contas_receber"],
        },
    }
