"""Filtros de estoque de mudas (desenvolvimento vs aptas para venda)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.constants.estagios_producao import APTA_VENDA, EM_DESENVOLVIMENTO, EM_RUSTIFICACAO
from app.constants.referencia_embrapa_viveiro import RUSTIFICACAO_DIAS_MINIMO
from app.models.canteiros import Canteiro
from app.models.plantas import Planta
from app.models.transferencias_plantas import TransferenciaPlanta

DISPONIVEIS_VENDA = ("MUDA", "JOVEM", "ADULTA")
VENDIDAS_OU_MORTAS = ("VENDIDA", "MORTA")


def _subquery_entrada_rustificacao():
    return (
        select(
            TransferenciaPlanta.id_planta.label("id_planta"),
            func.max(func.date(TransferenciaPlanta.data_transferencia)).label("data_entrada"),
        )
        .select_from(TransferenciaPlanta)
        .join(Canteiro, TransferenciaPlanta.id_canteiro_destino == Canteiro.id)
        .where(Canteiro.tipo_local == "rustificacao")
        .group_by(TransferenciaPlanta.id_planta)
        .subquery()
    )


def _join_entrada_rustificacao(query: Select) -> Tuple[Select, object]:
    entrada_rust = _subquery_entrada_rustificacao()
    return query.outerjoin(entrada_rust, entrada_rust.c.id_planta == Planta.id), entrada_rust


def data_ref_rustificacao(entrada_rust):
    """Data de referência para calcular dias na rustificação."""
    return func.coalesce(
        entrada_rust.c.data_entrada,
        Planta.data_inicio_estagio_atual,
        Planta.data_plantio,
        func.current_date(),
    )


def filtro_aptas_venda_comercial(query: Select) -> Select:
    """Mudas liberadas para venda na área de rustificação (sem exigir prazo mínimo)."""
    return query.where(
        Planta.status.in_(DISPONIVEIS_VENDA),
        Planta.estagio_producao == APTA_VENDA,
        Canteiro.tipo_local == "rustificacao",
    )


def filtro_prontas_venda(
    query: Select,
    *,
    dias_minimos_rustificacao: int = RUSTIFICACAO_DIAS_MINIMO,
    exigir_prazo_minimo: bool = False,
) -> Select:
    """Estoque comercial / vendas. Por padrão inclui todas aptas; prazo é só recomendação."""
    query, entrada_rust = _join_entrada_rustificacao(query)
    query = filtro_aptas_venda_comercial(query)
    if exigir_prazo_minimo:
        limite = date.today() - timedelta(days=dias_minimos_rustificacao)
        query = query.where(data_ref_rustificacao(entrada_rust) <= limite)
    return query


def filtro_abaixo_prazo_rustificacao_recomendado(
    query: Select,
    *,
    dias_minimos_rustificacao: int = RUSTIFICACAO_DIAS_MINIMO,
) -> Select:
    """Aptas para venda, porém ainda abaixo do prazo recomendado de rustificação."""
    query, entrada_rust = _join_entrada_rustificacao(query)
    limite = date.today() - timedelta(days=dias_minimos_rustificacao)
    return filtro_aptas_venda_comercial(query).where(
        data_ref_rustificacao(entrada_rust) > limite
    )


def _filtro_viveiro(query, id_viveiro: Optional[int]):
    if id_viveiro is not None:
        return query.where(Planta.id_viveiro == id_viveiro)
    return query


async def contar_mudas_pipeline(
    db: AsyncSession,
    dias_minimos: Optional[int] = None,
    id_viveiro: Optional[int] = None,
) -> dict:
    dias = dias_minimos if dias_minimos is not None else RUSTIFICACAO_DIAS_MINIMO

    base_viva = Planta.status.notin_(VENDIDAS_OU_MORTAS)

    q_sementeira = _filtro_viveiro(
        select(func.count(Planta.id))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            base_viva,
            Canteiro.tipo_local == "sementeira",
            Planta.estagio_producao.in_((EM_DESENVOLVIMENTO, "semente")),
        ),
        id_viveiro,
    )
    q_canteiro = _filtro_viveiro(
        select(func.count(Planta.id))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            base_viva,
            Canteiro.tipo_local == "canteiro",
            Planta.estagio_producao.in_((EM_DESENVOLVIMENTO, EM_RUSTIFICACAO, "em_crescimento")),
        ),
        id_viveiro,
    )

    entrada_rust = _subquery_entrada_rustificacao()
    data_ref = data_ref_rustificacao(entrada_rust)

    q_rust_total = _filtro_viveiro(
        select(func.count(Planta.id))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .outerjoin(entrada_rust, entrada_rust.c.id_planta == Planta.id)
        .where(
            base_viva,
            Canteiro.tipo_local == "rustificacao",
        ),
        id_viveiro,
    )

    q_prontas = _filtro_viveiro(
        select(func.count(Planta.id))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            base_viva,
            Canteiro.tipo_local == "rustificacao",
            Planta.status.in_(DISPONIVEIS_VENDA),
            Planta.estagio_producao == APTA_VENDA,
        ),
        id_viveiro,
    )

    q_aguardando = _filtro_viveiro(
        filtro_abaixo_prazo_rustificacao_recomendado(
            select(func.count(Planta.id))
            .select_from(Planta)
            .join(Canteiro, Planta.id_canteiro == Canteiro.id),
            dias_minimos_rustificacao=dias,
        ),
        id_viveiro,
    )

    sementeira = int((await db.execute(q_sementeira)).scalar() or 0)
    canteiro = int((await db.execute(q_canteiro)).scalar() or 0)
    rustificacao = int((await db.execute(q_rust_total)).scalar() or 0)
    prontas = int((await db.execute(q_prontas)).scalar() or 0)
    aguardando = int((await db.execute(q_aguardando)).scalar() or 0)

    return {
        "dias_minimos_rustificacao": dias,
        "em_desenvolvimento_sementeira": sementeira,
        "em_desenvolvimento_canteiro": canteiro,
        "em_desenvolvimento_total": sementeira + canteiro,
        "em_rustificacao": rustificacao,
        "aptas_venda_aguardando_tempo": aguardando,
        "prontas_para_venda": prontas,
    }
