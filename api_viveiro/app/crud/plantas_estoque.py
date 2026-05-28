"""Filtros de estoque de mudas (desenvolvimento vs prontas para venda)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

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


def filtro_prontas_venda(
    query: Select,
    *,
    dias_minimos_rustificacao: int = RUSTIFICACAO_DIAS_MINIMO,
) -> Select:
    limite = date.today() - timedelta(days=dias_minimos_rustificacao)
    entrada_rust = (
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
    return (
        query.outerjoin(entrada_rust, entrada_rust.c.id_planta == Planta.id)
        .where(
            Planta.status.in_(DISPONIVEIS_VENDA),
            Planta.estagio_producao == APTA_VENDA,
            Canteiro.tipo_local == "rustificacao",
            func.coalesce(
                entrada_rust.c.data_entrada,
                Planta.data_inicio_estagio_atual,
                Planta.data_plantio,
                func.current_date(),
            )
            <= limite,
        )
    )


async def contar_mudas_pipeline(db: AsyncSession, dias_minimos: Optional[int] = None) -> dict:
    dias = dias_minimos if dias_minimos is not None else RUSTIFICACAO_DIAS_MINIMO
    limite = date.today() - timedelta(days=dias)

    base_viva = Planta.status.notin_(VENDIDAS_OU_MORTAS)

    q_sementeira = (
        select(func.count(Planta.id))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            base_viva,
            Canteiro.tipo_local == "sementeira",
            Planta.estagio_producao.in_((EM_DESENVOLVIMENTO, "semente")),
        )
    )
    q_canteiro = (
        select(func.count(Planta.id))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            base_viva,
            Canteiro.tipo_local == "canteiro",
            Planta.estagio_producao.in_((EM_DESENVOLVIMENTO, EM_RUSTIFICACAO, "em_crescimento")),
        )
    )

    entrada_rust = (
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
    data_ref = func.coalesce(
        entrada_rust.c.data_entrada,
        Planta.data_inicio_estagio_atual,
        Planta.data_plantio,
        func.current_date(),
    )

    q_rust_total = (
        select(func.count(Planta.id))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .outerjoin(entrada_rust, entrada_rust.c.id_planta == Planta.id)
        .where(
            base_viva,
            Canteiro.tipo_local == "rustificacao",
        )
    )

    q_prontas = (
        select(func.count(Planta.id))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .outerjoin(entrada_rust, entrada_rust.c.id_planta == Planta.id)
        .where(
            base_viva,
            Canteiro.tipo_local == "rustificacao",
            Planta.status.in_(DISPONIVEIS_VENDA),
            Planta.estagio_producao == APTA_VENDA,
            data_ref <= limite,
        )
    )

    q_aguardando = (
        select(func.count(Planta.id))
        .select_from(Planta)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .outerjoin(entrada_rust, entrada_rust.c.id_planta == Planta.id)
        .where(
            base_viva,
            Canteiro.tipo_local == "rustificacao",
            Planta.estagio_producao == APTA_VENDA,
            data_ref > limite,
        )
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
