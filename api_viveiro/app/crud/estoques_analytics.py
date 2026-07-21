"""Visões analíticas de estoque de mudas (espécie, idade, cruzamento)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.estagios_producao import APTA_VENDA, EM_DESENVOLVIMENTO
from app.constants.referencia_embrapa_viveiro import RUSTIFICACAO_DIAS_MINIMO
from app.crud.plantas_estoque import (
    VENDIDAS_OU_MORTAS,
    _subquery_entrada_rustificacao,
    data_ref_rustificacao,
)
from app.models.canteiros import Canteiro
from app.models.especies import Especie
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta

FAIXAS_IDADE: List[Tuple[int, Optional[int], str]] = [
    (0, 29, "0–29 dias"),
    (30, 59, "30–59 dias"),
    (60, 89, "60–89 dias"),
    (90, None, "90+ dias"),
]


def _faixa_idade(dias: int) -> str:
    for ini, fim, rotulo in FAIXAS_IDADE:
        if fim is None and dias >= ini:
            return rotulo
        if fim is not None and ini <= dias <= fim:
            return rotulo
    return FAIXAS_IDADE[0][2]


def _stats_valores(custos: List[float]) -> Dict[str, float]:
    if not custos:
        return {"custo_medio": 0.0, "valor_custo_total": 0.0}
    total = sum(custos)
    return {
        "custo_medio": round(total / len(custos), 4),
        "valor_custo_total": round(total, 2),
    }


async def _carregar_plantas_vivas(
    db: AsyncSession, id_viveiro: Optional[int] = None
) -> List[Dict[str, Any]]:
    entrada_rust = _subquery_entrada_rustificacao()
    data_rust = data_ref_rustificacao(entrada_rust)
    data_viveiro = func.coalesce(
        Planta.data_plantio,
        Planta.data_inicio_estagio_atual,
        func.current_date(),
    )

    q = (
        select(
            Planta.id,
            Planta.codigo_rastreio,
            Planta.id_lote_sementes,
            Planta.data_plantio,
            Planta.id_especie,
            Especie.nome_popular,
            Especie.nome_cientifico,
            Planta.estagio_producao,
            Planta.status,
            Canteiro.tipo_local,
            Canteiro.nome.label("canteiro_nome"),
            LoteSementes.codigo_lote,
            Planta.custo_atual,
            Planta.preco_venda,
            (func.current_date() - data_viveiro).label("dias_viveiro"),
            (func.current_date() - data_rust).label("dias_rustificacao"),
        )
        .select_from(Planta)
        .join(Especie, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .outerjoin(LoteSementes, Planta.id_lote_sementes == LoteSementes.id)
        .outerjoin(entrada_rust, entrada_rust.c.id_planta == Planta.id)
        .where(Planta.status.notin_(VENDIDAS_OU_MORTAS))
    )
    if id_viveiro is not None:
        q = q.where(Planta.id_viveiro == id_viveiro)
    rows = (await db.execute(q)).all()
    out: List[Dict[str, Any]] = []
    for row in rows:
        tipo_local = row.tipo_local or ""
        dias_rust = int(row.dias_rustificacao) if row.dias_rustificacao is not None else None
        if tipo_local != "rustificacao":
            dias_rust = None
        dias_viveiro = int(row.dias_viveiro or 0)
        custo = float(row.custo_atual or 0)
        comercial = (
            tipo_local == "rustificacao"
            and row.estagio_producao == APTA_VENDA
            and row.status in ("MUDA", "JOVEM", "ADULTA")
        )
        out.append(
            {
                "id": row.id,
                "codigo_rastreio": row.codigo_rastreio,
                "id_lote_sementes": row.id_lote_sementes,
                "codigo_lote": row.codigo_lote,
                "data_plantio": row.data_plantio.isoformat() if row.data_plantio else None,
                "id_especie": row.id_especie,
                "nome_popular": row.nome_popular,
                "nome_cientifico": row.nome_cientifico,
                "estagio_producao": row.estagio_producao,
                "tipo_local": tipo_local,
                "canteiro_nome": row.canteiro_nome,
                "custo_atual": custo,
                "preco_venda": float(row.preco_venda or 0),
                "dias_viveiro": dias_viveiro,
                "dias_rustificacao": dias_rust,
                "comercial": comercial,
                "desenvolvimento": row.estagio_producao in (
                    EM_DESENVOLVIMENTO,
                    "semente",
                    "em_crescimento",
                )
                or tipo_local in ("sementeira", "canteiro"),
            }
        )
    return out


async def montar_analitico_mudas(
    db: AsyncSession,
    *,
    metrica_idade: str = "viveiro",
    id_viveiro: Optional[int] = None,
) -> Dict[str, Any]:
    """
    metrica_idade: viveiro | rustificacao
    - viveiro: dias desde plantio/início
    - rustificacao: dias na área de rustificação (só plantas lá; demais ignoradas na visão por idade)
    """
    plantas = await _carregar_plantas_vivas(db, id_viveiro=id_viveiro)
    total_qtd = len(plantas)
    if total_qtd == 0:
        return {
            "metrica_idade": metrica_idade,
            "faixas": [f[2] for f in FAIXAS_IDADE],
            "totais": {
                "quantidade": 0,
                "valor_custo_total": 0.0,
                "dias_medio_viveiro": None,
                "dias_medio_rustificacao": None,
            },
            "por_especie": [],
            "por_idade": [],
            "especie_idade": [],
        }

    def dias_metrica(p: Dict[str, Any]) -> Optional[int]:
        if metrica_idade == "rustificacao":
            return p["dias_rustificacao"]
        return p["dias_viveiro"]

    # --- por espécie ---
    por_esp: Dict[int, Dict[str, Any]] = {}
    for p in plantas:
        eid = p["id_especie"]
        if eid not in por_esp:
            por_esp[eid] = {
                "id_especie": eid,
                "nome_popular": p["nome_popular"],
                "nome_cientifico": p["nome_cientifico"],
                "quantidade_total": 0,
                "quantidade_comercial": 0,
                "quantidade_desenvolvimento": 0,
                "quantidade_rustificacao": 0,
                "custos": [],
                "dias_viveiro": [],
                "dias_rustificacao": [],
            }
        agg = por_esp[eid]
        agg["quantidade_total"] += 1
        agg["custos"].append(p["custo_atual"])
        agg["dias_viveiro"].append(p["dias_viveiro"])
        if p["dias_rustificacao"] is not None:
            agg["dias_rustificacao"].append(p["dias_rustificacao"])
        if p["comercial"]:
            agg["quantidade_comercial"] += 1
        if p["desenvolvimento"]:
            agg["quantidade_desenvolvimento"] += 1
        if p["tipo_local"] == "rustificacao":
            agg["quantidade_rustificacao"] += 1

    por_especie: List[Dict[str, Any]] = []
    for agg in sorted(por_esp.values(), key=lambda x: -x["quantidade_total"]):
        st = _stats_valores(agg["custos"])
        dv = agg["dias_viveiro"]
        dr = agg["dias_rustificacao"]
        por_especie.append(
            {
                "id_especie": agg["id_especie"],
                "nome_popular": agg["nome_popular"],
                "nome_cientifico": agg["nome_cientifico"],
                "quantidade_total": agg["quantidade_total"],
                "quantidade_comercial": agg["quantidade_comercial"],
                "quantidade_desenvolvimento": agg["quantidade_desenvolvimento"],
                "quantidade_rustificacao": agg["quantidade_rustificacao"],
                "custo_medio": st["custo_medio"],
                "valor_custo_total": st["valor_custo_total"],
                "dias_viveiro_medio": round(sum(dv) / len(dv), 1) if dv else None,
                "dias_viveiro_min": min(dv) if dv else None,
                "dias_viveiro_max": max(dv) if dv else None,
                "dias_rustificacao_medio": round(sum(dr) / len(dr), 1) if dr else None,
                "dias_rustificacao_min": min(dr) if dr else None,
                "dias_rustificacao_max": max(dr) if dr else None,
            }
        )

    # --- por idade ---
    buckets: Dict[str, List[float]] = {f[2]: [] for f in FAIXAS_IDADE}
    for p in plantas:
        d = dias_metrica(p)
        if d is None:
            continue
        buckets[_faixa_idade(d)].append(p["custo_atual"])

    por_idade: List[Dict[str, Any]] = []
    for _, _, rotulo in FAIXAS_IDADE:
        custos = buckets[rotulo]
        qtd = len(custos)
        st = _stats_valores(custos)
        por_idade.append(
            {
                "faixa": rotulo,
                "quantidade": qtd,
                "percentual": round(100 * qtd / total_qtd, 1) if total_qtd else 0,
                "custo_medio": st["custo_medio"],
                "valor_custo_total": st["valor_custo_total"],
            }
        )

    # --- espécie × idade ---
    cruz: Dict[Tuple[int, str], List[float]] = defaultdict(list)
    nomes: Dict[int, Tuple[Optional[str], str]] = {}
    for p in plantas:
        d = dias_metrica(p)
        if d is None:
            continue
        faixa = _faixa_idade(d)
        cruz[(p["id_especie"], faixa)].append(p["custo_atual"])
        nomes[p["id_especie"]] = (p["nome_popular"], p["nome_cientifico"])

    especie_idade: List[Dict[str, Any]] = []
    for (eid, faixa), custos in sorted(
        cruz.items(), key=lambda x: (-len(x[1]), x[0][0], x[0][1])
    ):
        pop, cient = nomes[eid]
        st = _stats_valores(custos)
        especie_idade.append(
            {
                "id_especie": eid,
                "nome_popular": pop,
                "nome_cientifico": cient,
                "faixa": faixa,
                "quantidade": len(custos),
                "custo_medio": st["custo_medio"],
                "valor_custo_total": st["valor_custo_total"],
            }
        )

    dias_v = [p["dias_viveiro"] for p in plantas]
    dias_r = [p["dias_rustificacao"] for p in plantas if p["dias_rustificacao"] is not None]

    return {
        "metrica_idade": metrica_idade,
        "faixas": [f[2] for f in FAIXAS_IDADE],
        "totais": {
            "quantidade": total_qtd,
            "valor_custo_total": round(sum(p["custo_atual"] for p in plantas), 2),
            "dias_medio_viveiro": round(sum(dias_v) / len(dias_v), 1) if dias_v else None,
            "dias_medio_rustificacao": round(sum(dias_r) / len(dias_r), 1) if dias_r else None,
        },
        "por_especie": por_especie,
        "por_idade": por_idade,
        "especie_idade": especie_idade,
    }


async def verificar_integridade_cmv(
    db: AsyncSession, id_viveiro: Optional[int] = None
) -> Dict[str, Any]:
    """Alertas que podem distorcer CMV ou valor de estoque."""
    plantas = await _carregar_plantas_vivas(db, id_viveiro=id_viveiro)
    sem_custo = [p for p in plantas if (p["custo_atual"] or 0) <= 0]
    com_custo = [p for p in plantas if (p["custo_atual"] or 0) > 0]

    return {
        "insumos_metodo": "media_movel",
        "mudas_metodo": "custo_atual_acumulado",
        "sementes_metodo": "valor_total_lote_proporcional",
        "venda_cmv": "snapshot ItemVenda.custo_unitario = planta.custo_atual na venda",
        "plantas_vivas": len(plantas),
        "plantas_com_custo": len(com_custo),
        "plantas_sem_custo": len(sem_custo),
        "alertas": _montar_alertas_cmv(plantas, sem_custo),
    }


def _montar_alertas_cmv(
    plantas: List[Dict[str, Any]], sem_custo: List[Dict[str, Any]]
) -> List[str]:
    alertas: List[str] = []
    if sem_custo:
        alertas.append(
            f"{len(sem_custo)} muda(s) viva(s) com custo_atual zero — CMV de venda pode ficar subestimado."
        )
    com = [p for p in plantas if p["comercial"]]
    com_sem = [p for p in com if (p["custo_atual"] or 0) <= 0]
    if com_sem:
        alertas.append(
            f"{len(com_sem)} muda(s) apta(s) p/ venda sem custo registrado."
        )
    if not alertas:
        alertas.append(
            "CMV de insumos usa média móvel nas entradas; mudas acumulam semeadura + atividades + fitossanidade."
        )
    return alertas


def _planta_detalhe_item(p: Dict[str, Any], metrica_idade: str) -> Dict[str, Any]:
    d_v = p["dias_viveiro"]
    d_r = p["dias_rustificacao"]
    d_metrica = d_r if metrica_idade == "rustificacao" else d_v
    faixa = _faixa_idade(d_metrica) if d_metrica is not None else None
    return {
        "id": p["id"],
        "codigo_rastreio": p.get("codigo_rastreio"),
        "id_especie": p["id_especie"],
        "nome_popular": p.get("nome_popular"),
        "nome_cientifico": p.get("nome_cientifico"),
        "id_lote_sementes": p.get("id_lote_sementes"),
        "codigo_lote": p.get("codigo_lote"),
        "canteiro_nome": p.get("canteiro_nome"),
        "tipo_local": p.get("tipo_local"),
        "estagio_producao": p.get("estagio_producao"),
        "status": p.get("status"),
        "data_plantio": p.get("data_plantio"),
        "dias_viveiro": d_v,
        "dias_rustificacao": d_r,
        "dias_metrica": d_metrica,
        "faixa_idade": faixa,
        "custo_atual": p.get("custo_atual", 0),
        "preco_venda": p.get("preco_venda", 0),
        "comercial": p.get("comercial", False),
    }


async def listar_detalhe_analitico(
    db: AsyncSession,
    *,
    metrica_idade: str = "viveiro",
    id_especie: Optional[int] = None,
    faixa: Optional[str] = None,
    agrupar: str = "muda",
    id_viveiro: Optional[int] = None,
) -> Dict[str, Any]:
    """Detalhe muda a muda ou agrupado por lote de sementes."""
    plantas = await _carregar_plantas_vivas(db, id_viveiro=id_viveiro)

    if id_especie is not None:
        plantas = [p for p in plantas if p["id_especie"] == id_especie]

    def dias_metrica(p: Dict[str, Any]) -> Optional[int]:
        if metrica_idade == "rustificacao":
            return p["dias_rustificacao"]
        return p["dias_viveiro"]

    if faixa:
        plantas = [
            p for p in plantas
            if dias_metrica(p) is not None and _faixa_idade(dias_metrica(p)) == faixa
        ]

    if metrica_idade == "rustificacao":
        plantas = [p for p in plantas if p["dias_rustificacao"] is not None]

    itens_muda = [_planta_detalhe_item(p, metrica_idade) for p in plantas]
    itens_muda.sort(
        key=lambda x: (
            -(x["dias_metrica"] if x["dias_metrica"] is not None else -1),
            x.get("codigo_rastreio") or "",
        )
    )

    if agrupar == "lote":
        lotes: Dict[Optional[int], List[Dict[str, Any]]] = defaultdict(list)
        for item in itens_muda:
            lotes[item.get("id_lote_sementes")].append(item)

        agrupados: List[Dict[str, Any]] = []
        for id_lote, membros in sorted(
            lotes.items(), key=lambda x: (-len(x[1]), x[0] or 0)
        ):
            dias_m = [m["dias_metrica"] for m in membros if m["dias_metrica"] is not None]
            codigo = membros[0].get("codigo_lote") if membros else None
            agrupados.append(
                {
                    "id_lote_sementes": id_lote,
                    "codigo_lote": codigo or ("Sem lote" if id_lote is None else f"Lote #{id_lote}"),
                    "quantidade": len(membros),
                    "dias_metrica_min": min(dias_m) if dias_m else None,
                    "dias_metrica_max": max(dias_m) if dias_m else None,
                    "dias_metrica_medio": round(sum(dias_m) / len(dias_m), 1) if dias_m else None,
                    "valor_custo_total": round(sum(m["custo_atual"] for m in membros), 2),
                    "plantas": membros,
                }
            )
        return {
            "metrica_idade": metrica_idade,
            "agrupar": "lote",
            "total_mudas": len(itens_muda),
            "total_lotes": len(agrupados),
            "itens_lote": agrupados,
            "itens_muda": itens_muda,
        }

    return {
        "metrica_idade": metrica_idade,
        "agrupar": "muda",
        "total_mudas": len(itens_muda),
        "itens_muda": itens_muda,
    }
