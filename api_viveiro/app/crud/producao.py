from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.constants.estagios_producao import (
    APTA_TRANSFERENCIA,
    APTA_VENDA,
    APTA_RUSTIFICACAO,
    EM_CRESCIMENTO,
    EM_DESENVOLVIMENTO,
    EM_RUSTIFICACAO,
)
from app.models.canteiros import Canteiro
from app.models.especies import Especie
from app.models.coletas_sementes import ColetaSementes
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta
from app.models.vendas import ItemVenda, Venda


async def _sum_mudas_vendidas_desde(
    db: AsyncSession, desde: date, id_viveiro: Optional[int] = None
) -> int:
    """Soma quantidade de itens de venda não canceladas a partir de `desde` (data da venda)."""
    q = (
        select(func.coalesce(func.sum(ItemVenda.quantidade), 0))
        .select_from(ItemVenda)
        .join(Venda, ItemVenda.id_venda == Venda.id)
        .where(
            Venda.status != "CANCELADO",
            func.date(Venda.data_venda) >= desde,
        )
    )
    if id_viveiro is not None:
        q = q.where(Venda.id_viveiro == id_viveiro)
    total = (await db.execute(q)).scalar()
    return int(total or 0)


async def _contagem_por_especie(
    db: AsyncSession,
    *,
    statuses: Tuple[str, ...],
    tipo_canteiro: str,
    estagio_producao: Optional[str] = None,
    id_viveiro: Optional[int] = None,
) -> List[Dict[str, Any]]:
    q = (
        select(
            Especie.id,
            func.coalesce(Especie.nome_popular, Especie.nome_cientifico).label("nome"),
            func.count(Planta.id).label("qtd"),
        )
        .join(Planta, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(Planta.status.in_(statuses), Canteiro.tipo_local == tipo_canteiro)
    )
    if id_viveiro is not None:
        q = q.where(Planta.id_viveiro == id_viveiro)
    if estagio_producao:
        q = q.where(Planta.estagio_producao == estagio_producao)
    q = q.group_by(Especie.id, Especie.nome_popular, Especie.nome_cientifico).order_by(
        func.count(Planta.id).desc()
    )
    rows = (await db.execute(q)).all()
    return [
        {"id_especie": r[0], "especie": r[1], "quantidade": int(r[2] or 0)}
        for r in rows
    ]


async def _contar_plantas(
    db: AsyncSession,
    *,
    statuses: Tuple[str, ...],
    tipo_canteiro: Optional[str] = None,
    tipos_canteiro: Optional[Tuple[str, ...]] = None,
    estagio_producao: Optional[str] = None,
    id_viveiro: Optional[int] = None,
) -> int:
    q = select(func.count(Planta.id)).select_from(Planta)
    if tipo_canteiro or tipos_canteiro:
        q = q.join(Canteiro, Planta.id_canteiro == Canteiro.id)
        if tipos_canteiro:
            q = q.where(Canteiro.tipo_local.in_(tipos_canteiro))
        else:
            q = q.where(Canteiro.tipo_local == tipo_canteiro)
    q = q.where(Planta.status.in_(statuses))
    if id_viveiro is not None:
        q = q.where(Planta.id_viveiro == id_viveiro)
    if estagio_producao:
        q = q.where(Planta.estagio_producao == estagio_producao)
    return int((await db.execute(q)).scalar() or 0)


async def _contagem_por_especie_tipos(
    db: AsyncSession,
    *,
    statuses: Tuple[str, ...],
    tipos_canteiro: Tuple[str, ...],
    estagio_producao: Optional[str] = None,
    id_viveiro: Optional[int] = None,
) -> List[Dict[str, Any]]:
    q = (
        select(
            Especie.id,
            func.coalesce(Especie.nome_popular, Especie.nome_cientifico).label("nome"),
            func.count(Planta.id).label("qtd"),
        )
        .join(Planta, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            Planta.status.in_(statuses),
            Canteiro.tipo_local.in_(tipos_canteiro),
        )
    )
    if id_viveiro is not None:
        q = q.where(Planta.id_viveiro == id_viveiro)
    if estagio_producao:
        q = q.where(Planta.estagio_producao == estagio_producao)
    q = q.group_by(Especie.id, Especie.nome_popular, Especie.nome_cientifico).order_by(
        func.count(Planta.id).desc()
    )
    rows = (await db.execute(q)).all()
    return [
        {"id_especie": r[0], "especie": r[1], "quantidade": int(r[2] or 0)}
        for r in rows
    ]


async def get_producao_resumo(
    db: AsyncSession, id_viveiro: Optional[int] = None
) -> Dict[str, Any]:
    lote_where = [
        LoteSementes.status == "ativo",
        LoteSementes.quantidade_disponivel > 0,
    ]
    if id_viveiro is not None:
        lote_where.append(LoteSementes.id_viveiro == id_viveiro)

    sementes_armazem = (
        await db.execute(
            select(func.coalesce(func.sum(LoteSementes.quantidade_disponivel), 0)).where(
                *lote_where
            )
        )
    ).scalar() or 0

    lotes_com_estoque = (
        await db.execute(
            select(func.count(LoteSementes.id)).where(*lote_where)
        )
    ).scalar() or 0

    especies_armazem = (
        await db.execute(
            select(func.count(func.distinct(LoteSementes.id_especie))).where(*lote_where)
        )
    ).scalar() or 0

    na_sementeira = await _contar_plantas(
        db, statuses=("SEMENTE",), tipo_canteiro="sementeira", id_viveiro=id_viveiro
    )
    em_desenvolvimento_sementeira = await _contar_plantas(
        db,
        statuses=("SEMENTE",),
        tipo_canteiro="sementeira",
        estagio_producao=EM_DESENVOLVIMENTO,
        id_viveiro=id_viveiro,
    )
    aptas_transferencia = await _contar_plantas(
        db,
        statuses=("SEMENTE",),
        tipo_canteiro="sementeira",
        estagio_producao=APTA_TRANSFERENCIA,
        id_viveiro=id_viveiro,
    )

    nos_canteiros = await _contar_plantas(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipo_canteiro="canteiro",
        id_viveiro=id_viveiro,
    )
    em_crescimento_canteiro = await _contar_plantas(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipo_canteiro="canteiro",
        estagio_producao=EM_CRESCIMENTO,
        id_viveiro=id_viveiro,
    )
    aptas_rustificacao_canteiro = await _contar_plantas(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipo_canteiro="canteiro",
        estagio_producao=APTA_RUSTIFICACAO,
        id_viveiro=id_viveiro,
    )
    na_rustificacao = await _contar_plantas(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipo_canteiro="rustificacao",
        id_viveiro=id_viveiro,
    )
    em_rustificacao = await _contar_plantas(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipo_canteiro="rustificacao",
        estagio_producao=EM_RUSTIFICACAO,
        id_viveiro=id_viveiro,
    )
    # Regra operacional: só há aptos p/ venda na área de rustificação.
    prontas_venda_canteiro = 0
    prontas_venda_rustificacao = await _contar_plantas(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipo_canteiro="rustificacao",
        estagio_producao=APTA_VENDA,
        id_viveiro=id_viveiro,
    )
    prontas_venda = prontas_venda_canteiro + prontas_venda_rustificacao

    aguardando_transferencia = aptas_transferencia

    hoje = date.today()
    inicio_mes = date(hoje.year, hoje.month, 1)
    inicio_ano = date(hoje.year, 1, 1)
    vendidas_mtd = await _sum_mudas_vendidas_desde(db, inicio_mes, id_viveiro=id_viveiro)
    vendidas_ytd = await _sum_mudas_vendidas_desde(db, inicio_ano, id_viveiro=id_viveiro)

    # Armazém: usa data da coleta quando o lote veio de coleta (evita divergência com data_formacao_lote antiga).
    ref_data_armazem = func.coalesce(
        ColetaSementes.data_coleta,
        LoteSementes.data_formacao_lote,
    )
    dias_medios_armazem_raw = (
        await db.execute(
            select(
                (
                    func.sum(
                        LoteSementes.quantidade_disponivel
                        * (func.current_date() - ref_data_armazem)
                    )
                    / func.nullif(func.sum(LoteSementes.quantidade_disponivel), 0)
                )
            )
            .select_from(LoteSementes)
            .outerjoin(
                ColetaSementes,
                LoteSementes.id_coleta_sementes == ColetaSementes.id,
            )
            .where(
                LoteSementes.status == "ativo",
                LoteSementes.quantidade_disponivel > 0,
                *([] if id_viveiro is None else [LoteSementes.id_viveiro == id_viveiro]),
            )
        )
    ).scalar()

    dias_medios_armazem = float(dias_medios_armazem_raw) if dias_medios_armazem_raw is not None else None

    ref_dias_planta = func.coalesce(
        Planta.data_inicio_estagio_atual,
        Planta.data_plantio,
    )
    dias_medios_sementeira_q = (
        select(func.avg(func.current_date() - ref_dias_planta))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            Canteiro.tipo_local == "sementeira",
            Planta.status == "SEMENTE",
            ref_dias_planta.isnot(None),
        )
    )
    if id_viveiro is not None:
        dias_medios_sementeira_q = dias_medios_sementeira_q.where(Planta.id_viveiro == id_viveiro)
    dias_medios_sementeira_raw = (await db.execute(dias_medios_sementeira_q)).scalar()
    dias_medios_sementeira = (
        float(dias_medios_sementeira_raw) if dias_medios_sementeira_raw is not None else None
    )

    ref_dias_canteiro = func.coalesce(
        Planta.data_inicio_estagio_atual,
        Planta.data_germinacao,
        Planta.data_plantio,
    )
    dias_medios_canteiro_q = (
        select(func.avg(func.current_date() - ref_dias_canteiro))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            Canteiro.tipo_local == "canteiro",
            Planta.status.in_(("MUDA", "JOVEM", "ADULTA")),
            ref_dias_canteiro.isnot(None),
        )
    )
    if id_viveiro is not None:
        dias_medios_canteiro_q = dias_medios_canteiro_q.where(Planta.id_viveiro == id_viveiro)
    dias_medios_canteiro_raw = (await db.execute(dias_medios_canteiro_q)).scalar()
    dias_medios_canteiro = (
        float(dias_medios_canteiro_raw) if dias_medios_canteiro_raw is not None else None
    )

    ref_dias_rust = func.coalesce(
        Planta.data_inicio_estagio_atual,
        Planta.data_germinacao,
        Planta.data_plantio,
    )
    dias_medios_rustificacao_q = (
        select(func.avg(func.current_date() - ref_dias_rust))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            Canteiro.tipo_local == "rustificacao",
            Planta.status.in_(("MUDA", "JOVEM", "ADULTA")),
            ref_dias_rust.isnot(None),
        )
    )
    if id_viveiro is not None:
        dias_medios_rustificacao_q = dias_medios_rustificacao_q.where(Planta.id_viveiro == id_viveiro)
    dias_medios_rustificacao_raw = (await db.execute(dias_medios_rustificacao_q)).scalar()
    dias_medios_rustificacao = (
        float(dias_medios_rustificacao_raw) if dias_medios_rustificacao_raw is not None else None
    )

    por_especie_sementeira = await _contagem_por_especie(
        db, statuses=("SEMENTE",), tipo_canteiro="sementeira", id_viveiro=id_viveiro
    )
    por_especie_desenvolvimento = await _contagem_por_especie(
        db,
        statuses=("SEMENTE",),
        tipo_canteiro="sementeira",
        estagio_producao=EM_DESENVOLVIMENTO,
        id_viveiro=id_viveiro,
    )
    por_especie_aptas_transferencia = await _contagem_por_especie(
        db,
        statuses=("SEMENTE",),
        tipo_canteiro="sementeira",
        estagio_producao=APTA_TRANSFERENCIA,
        id_viveiro=id_viveiro,
    )
    por_especie_canteiro = await _contagem_por_especie(
        db, statuses=("MUDA", "JOVEM", "ADULTA"), tipo_canteiro="canteiro", id_viveiro=id_viveiro
    )
    por_especie_em_crescimento = await _contagem_por_especie(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipo_canteiro="canteiro",
        estagio_producao=EM_CRESCIMENTO,
        id_viveiro=id_viveiro,
    )
    por_especie_aptas_rustificacao = await _contagem_por_especie(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipo_canteiro="canteiro",
        estagio_producao=APTA_RUSTIFICACAO,
        id_viveiro=id_viveiro,
    )
    por_especie_rustificacao = await _contagem_por_especie(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipo_canteiro="rustificacao",
        estagio_producao=EM_RUSTIFICACAO,
        id_viveiro=id_viveiro,
    )
    por_especie_prontas_venda = await _contagem_por_especie_tipos(
        db,
        statuses=("MUDA", "JOVEM", "ADULTA"),
        tipos_canteiro=("rustificacao",),
        estagio_producao=APTA_VENDA,
        id_viveiro=id_viveiro,
    )

    vendas_q = (
        select(Venda)
        .options(joinedload(Venda.comprador), joinedload(Venda.itens))
        .order_by(Venda.data_venda.desc())
        .limit(8)
    )
    if id_viveiro is not None:
        vendas_q = vendas_q.where(Venda.id_viveiro == id_viveiro)
    vendas_rows = (await db.execute(vendas_q)).unique().scalars().all()
    vendas_recentes = []
    for v in vendas_rows:
        comprador_nome = v.comprador.nome if v.comprador else None
        total_itens = len(v.itens) if v.itens else 0
        vendas_recentes.append(
            {
                "id": v.id,
                "data_venda": v.data_venda,
                "comprador_nome": comprador_nome,
                "total_itens": total_itens,
                "status": v.status,
            }
        )

    return {
        "sementes_armazem": int(sementes_armazem),
        "lotes_com_estoque": int(lotes_com_estoque),
        "especies_armazem": int(especies_armazem),
        "na_sementeira": int(na_sementeira),
        "em_desenvolvimento_sementeira": int(em_desenvolvimento_sementeira),
        "aptas_transferencia": int(aptas_transferencia),
        "nos_canteiros": int(nos_canteiros),
        "em_crescimento_canteiro": int(em_crescimento_canteiro),
        "aptas_rustificacao_canteiro": int(aptas_rustificacao_canteiro),
        "na_rustificacao": int(na_rustificacao),
        "em_rustificacao": int(em_rustificacao),
        "prontas_venda": int(prontas_venda),
        "prontas_venda_canteiro": int(prontas_venda_canteiro),
        "prontas_venda_rustificacao": int(prontas_venda_rustificacao),
        "estoque_comercial_unidades": int(prontas_venda),
        "aguardando_transferencia": int(aguardando_transferencia),
        "vendidas_mtd": int(vendidas_mtd),
        "vendidas_ytd": int(vendidas_ytd),
        "dias_medios_armazem": dias_medios_armazem,
        "dias_medios_sementeira": dias_medios_sementeira,
        "dias_medios_canteiro": dias_medios_canteiro,
        "dias_medios_rustificacao": dias_medios_rustificacao,
        "por_especie_aptas_rustificacao": por_especie_aptas_rustificacao,
        "por_especie_sementeira": por_especie_sementeira,
        "por_especie_desenvolvimento": por_especie_desenvolvimento,
        "por_especie_aptas_transferencia": por_especie_aptas_transferencia,
        "por_especie_canteiro": por_especie_canteiro,
        "por_especie_em_crescimento": por_especie_em_crescimento,
        "por_especie_rustificacao": por_especie_rustificacao,
        "por_especie_prontas_venda": por_especie_prontas_venda,
        "vendas_recentes": vendas_recentes,
    }
