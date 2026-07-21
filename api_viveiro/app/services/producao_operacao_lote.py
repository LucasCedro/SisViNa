"""Resolução de plantas e operações em lote por espécie (produção em escala)."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.estagios_producao import (
    APTA_RUSTIFICACAO,
    APTA_TRANSFERENCIA,
    APTA_VENDA,
    EM_CRESCIMENTO,
    EM_DESENVOLVIMENTO,
    EM_RUSTIFICACAO,
)
from app.constants.referencia_embrapa_viveiro import RUSTIFICACAO_DIAS_MINIMO
from app.crud.plantas_estoque import _join_entrada_rustificacao, data_ref_rustificacao
from app.models.canteiros import Canteiro
from app.models.especies import Especie
from app.models.plantas import Planta
from app.schemas.producao import (
    AtualizarEstagioLoteRequest,
    AtualizarEstagioRequest,
    GrupoOperacaoLote,
    PromoverMudasLoteRequest,
    PromoverMudasRequest,
    TransferirRustificacaoLoteRequest,
    TransferirRustificacaoRequest,
)

_ETAPAS_RUSTIFICACAO_PRAZO = frozenset(
    {"rustificacao", "rustificacao_pronta_venda", "rustificacao_antes_prazo"}
)

_ETAPA_WHERE: Dict[str, Tuple] = {
    "sementeira_desenvolvimento": (
        Planta.status == "SEMENTE",
        Planta.estagio_producao == EM_DESENVOLVIMENTO,
        Canteiro.tipo_local == "sementeira",
    ),
    "sementeira_apta_transferencia": (
        Planta.status == "SEMENTE",
        Planta.estagio_producao == APTA_TRANSFERENCIA,
        Canteiro.tipo_local == "sementeira",
    ),
    "canteiro_crescimento": (
        Planta.status.in_(("MUDA", "JOVEM", "ADULTA")),
        Planta.estagio_producao == EM_CRESCIMENTO,
        Canteiro.tipo_local == "canteiro",
    ),
    "canteiro_apta_rustificacao": (
        Planta.status.in_(("MUDA", "JOVEM", "ADULTA")),
        Planta.estagio_producao == APTA_RUSTIFICACAO,
        Canteiro.tipo_local == "canteiro",
    ),
    "rustificacao": (
        Planta.status.in_(("MUDA", "JOVEM", "ADULTA")),
        Planta.estagio_producao == EM_RUSTIFICACAO,
        Canteiro.tipo_local == "rustificacao",
    ),
}


def _nome_especie_expr():
    return func.coalesce(Especie.nome_popular, Especie.nome_cientifico).label("especie_nome")


def _validar_etapa(etapa: str) -> None:
    if etapa not in _ETAPA_WHERE and etapa not in _ETAPAS_RUSTIFICACAO_PRAZO:
        raise ValueError(f"Etapa inválida: {etapa}")


def _base_query_etapa(etapa: str):
    _validar_etapa(etapa)
    q = (
        select(Planta)
        .join(Especie, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
    )
    if etapa in _ETAPA_WHERE:
        return q.where(*_ETAPA_WHERE[etapa])

    q = q.where(*_ETAPA_WHERE["rustificacao"])
    q, entrada_rust = _join_entrada_rustificacao(q)
    limite = date.today() - timedelta(days=RUSTIFICACAO_DIAS_MINIMO)
    data_ref = data_ref_rustificacao(entrada_rust)
    if etapa == "rustificacao_pronta_venda":
        return q.where(data_ref <= limite)
    if etapa == "rustificacao_antes_prazo":
        return q.where(data_ref > limite)
    return q


async def get_resumo_operacao_lote(
    db: AsyncSession,
    etapa: str,
    id_canteiro: Optional[int] = None,
) -> List[Dict[str, Any]]:
    _validar_etapa(etapa)

    query = (
        select(
            Planta.id_especie,
            _nome_especie_expr(),
            Planta.id_canteiro,
            Canteiro.nome.label("nome_canteiro"),
            func.count(Planta.id).label("disponivel"),
        )
        .join(Especie, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(*_ETAPA_WHERE["rustificacao" if etapa in _ETAPAS_RUSTIFICACAO_PRAZO else etapa])
        .group_by(
            Planta.id_especie,
            Especie.nome_popular,
            Especie.nome_cientifico,
            Planta.id_canteiro,
            Canteiro.nome,
        )
        .order_by(func.count(Planta.id).desc(), _nome_especie_expr())
    )
    if etapa in ("rustificacao_pronta_venda", "rustificacao_antes_prazo"):
        query, entrada_rust = _join_entrada_rustificacao(query)
        limite = date.today() - timedelta(days=RUSTIFICACAO_DIAS_MINIMO)
        data_ref = data_ref_rustificacao(entrada_rust)
        if etapa == "rustificacao_pronta_venda":
            query = query.where(data_ref <= limite)
        else:
            query = query.where(data_ref > limite)
    if id_canteiro:
        query = query.where(Planta.id_canteiro == id_canteiro)

    rows = (await db.execute(query)).all()
    return [
        {
            "id_especie": r[0],
            "especie_nome": r[1] or "",
            "id_canteiro": r[2],
            "nome_canteiro": r[3],
            "disponivel": int(r[4] or 0),
        }
        for r in rows
    ]


async def resolver_ids_grupos(
    db: AsyncSession,
    etapa: str,
    grupos: List[GrupoOperacaoLote],
) -> List[Dict[str, Any]]:
    """Resolve IDs de plantas por espécie/quantidade. Falha se faltar estoque."""
    saida = []
    for grupo in grupos:
        q = _base_query_etapa(etapa).where(Planta.id_especie == grupo.id_especie)
        if grupo.id_canteiro_origem:
            q = q.where(Planta.id_canteiro == grupo.id_canteiro_origem)
        q = q.order_by(Planta.data_plantio.asc(), Planta.id.asc()).limit(grupo.quantidade)
        rows = (await db.execute(q)).scalars().all()
        if len(rows) < grupo.quantidade:
            esp = await db.get(Especie, grupo.id_especie)
            nome = (esp.nome_popular or esp.nome_cientifico) if esp else str(grupo.id_especie)
            raise ValueError(
                f"{nome}: só {len(rows)} disponível(is), pediu {grupo.quantidade}."
            )
        ids = [p.id for p in rows]
        nome = None
        if rows:
            esp = await db.get(Especie, grupo.id_especie)
            nome = (esp.nome_popular or esp.nome_cientifico) if esp else None
        saida.append(
            {
                "id_especie": grupo.id_especie,
                "especie_nome": nome,
                "quantidade": grupo.quantidade,
                "ids_plantas": ids,
            }
        )
    return saida


def _montar_resposta_lote(itens: List[Dict[str, Any]], **extra) -> Dict[str, Any]:
    total = sum(i["quantidade"] for i in itens)
    return {
        "total": total,
        "itens": itens,
        **extra,
    }


async def atualizar_estagio_lote(
    db: AsyncSession,
    payload: AtualizarEstagioLoteRequest,
    *,
    etapa_origem: str,
    atualizar_fn,
) -> Dict[str, Any]:
    itens_resolvidos = await resolver_ids_grupos(db, etapa_origem, payload.grupos)
    todos_ids = [pid for item in itens_resolvidos for pid in item["ids_plantas"]]
    res = await atualizar_fn(
        db,
        AtualizarEstagioRequest(
            ids_plantas=todos_ids,
            estagio_producao=payload.estagio_producao,
        ),
    )
    return _montar_resposta_lote(
        [
            {
                "id_especie": i["id_especie"],
                "especie_nome": i["especie_nome"],
                "quantidade": i["quantidade"],
                "ids_plantas": i["ids_plantas"],
            }
            for i in itens_resolvidos
        ],
        avisos=res.get("avisos") or [],
    )


async def promover_mudas_lote(
    db: AsyncSession,
    payload: PromoverMudasLoteRequest,
    id_funcionario: Optional[int],
    promover_fn,
) -> Dict[str, Any]:
    itens_resolvidos = await resolver_ids_grupos(
        db, "sementeira_apta_transferencia", payload.grupos
    )
    todos_ids = [pid for item in itens_resolvidos for pid in item["ids_plantas"]]
    res = await promover_fn(
        db,
        PromoverMudasRequest(
            ids_plantas=todos_ids,
            id_canteiro_destino=payload.id_canteiro_destino,
            data_germinacao=payload.data_germinacao,
            observacoes=payload.observacoes,
        ),
        id_funcionario=id_funcionario,
    )
    return _montar_resposta_lote(
        [
            {
                "id_especie": i["id_especie"],
                "especie_nome": i["especie_nome"],
                "quantidade": i["quantidade"],
                "ids_plantas": i["ids_plantas"],
            }
            for i in itens_resolvidos
        ],
        avisos=res.get("avisos") or [],
        baixa_substrato=res.get("baixa_substrato"),
    )


async def transferir_rustificacao_lote(
    db: AsyncSession,
    payload: TransferirRustificacaoLoteRequest,
    id_funcionario: Optional[int],
    transferir_fn,
) -> Dict[str, Any]:
    itens_resolvidos = await resolver_ids_grupos(
        db, "canteiro_apta_rustificacao", payload.grupos
    )
    todos_ids = [pid for item in itens_resolvidos for pid in item["ids_plantas"]]
    res = await transferir_fn(
        db,
        TransferirRustificacaoRequest(
            ids_plantas=todos_ids,
            observacoes=payload.observacoes,
        ),
        id_funcionario=id_funcionario,
    )
    return _montar_resposta_lote(
        [
            {
                "id_especie": i["id_especie"],
                "especie_nome": i["especie_nome"],
                "quantidade": i["quantidade"],
                "ids_plantas": i["ids_plantas"],
            }
            for i in itens_resolvidos
        ],
        avisos=res.get("avisos") or [],
    )


# Mapeamento etapa → estágio destino (liberar)
_ETAPA_ESTAGIO_DESTINO = {
    "sementeira_desenvolvimento": "apta_transferencia",
    "canteiro_crescimento": "apta_rustificacao",
    "rustificacao": "apta_venda",
    "rustificacao_pronta_venda": "apta_venda",
    "rustificacao_antes_prazo": "apta_venda",
}
