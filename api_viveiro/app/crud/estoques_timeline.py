"""Timeline média por espécie: armazém → sementeira → canteiro → rustificação."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.plantas_estoque import VENDIDAS_OU_MORTAS
from app.models.canteiros import Canteiro
from app.models.coletas_sementes import ColetaSementes
from app.models.especies import Especie
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta
from app.models.semeaduras import Semeadura
from app.models.transferencias_plantas import TransferenciaPlanta

ETAPAS = ("armazem", "sementeira", "canteiro", "rustificacao")
ETAPA_LABELS = {
    "armazem": "Armazém",
    "sementeira": "Sementeira",
    "canteiro": "Canteiro",
    "rustificacao": "Rustificação",
}
ETAPA_CORES = {
    "armazem": "#8B6914",
    "sementeira": "#E67E22",
    "canteiro": "#4A8F3C",
    "rustificacao": "#D4A017",
}


def _to_date(val) -> Optional[date]:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    return None


def _media(vals: List[int]) -> Optional[float]:
    if not vals:
        return None
    return round(sum(vals) / len(vals), 1)


def _segmento_etapa(tipo_local: Optional[str]) -> Optional[str]:
    if not tipo_local:
        return None
    if tipo_local == "sementeira":
        return "sementeira"
    if tipo_local == "canteiro":
        return "canteiro"
    if tipo_local == "rustificacao":
        return "rustificacao"
    return None


def _calcular_dwell_planta(
    planta: Planta,
    transfers: List[TransferenciaPlanta],
    hoje: date,
) -> Tuple[Dict[str, int], Optional[int]]:
    """Retorna dias por etapa (pós-armazém) e dias no armazém (lote→semeadura)."""
    dwell: Dict[str, int] = {e: 0 for e in ETAPAS if e != "armazem"}
    dias_armazem: Optional[int] = None

    sem = planta.semeadura
    lote = planta.lote_sementes
    if sem and lote:
        ref_arm = None
        if lote.coleta and lote.coleta.data_coleta:
            ref_arm = lote.coleta.data_coleta
        elif lote.data_formacao_lote:
            ref_arm = lote.data_formacao_lote
        if ref_arm and sem.data_semeadura:
            dias_armazem = max(0, (sem.data_semeadura - ref_arm).days)

    inicio = _to_date(planta.data_plantio) or (sem.data_semeadura if sem else None) or hoje
    canteiro_atual = planta.canteiro
    loc_atual = _segmento_etapa(canteiro_atual.tipo_local if canteiro_atual else None)

    ordenadas = sorted(
        transfers,
        key=lambda t: t.data_transferencia or datetime.min,
    )

    if not ordenadas:
        if loc_atual and inicio:
            dwell[loc_atual] = max(0, (hoje - inicio).days)
        return dwell, dias_armazem

    cursor = inicio
    loc = loc_atual
    if ordenadas and ordenadas[0].canteiro_origem:
        loc = _segmento_etapa(ordenadas[0].canteiro_origem.tipo_local) or loc

    for tr in ordenadas:
        dt = _to_date(tr.data_transferencia) or hoje
        orig = _segmento_etapa(
            tr.canteiro_origem.tipo_local if tr.canteiro_origem else None
        )
        dest = _segmento_etapa(
            tr.canteiro_destino.tipo_local if tr.canteiro_destino else None
        )
        etapa = orig or loc
        if etapa and cursor:
            dwell[etapa] = dwell.get(etapa, 0) + max(0, (dt - cursor).days)
        loc = dest or loc
        cursor = dt

    if loc and cursor:
        dwell[loc] = dwell.get(loc, 0) + max(0, (hoje - cursor).days)

    return dwell, dias_armazem


async def _armazem_por_especie(db: AsyncSession) -> Dict[int, Dict[str, Any]]:
    """Sementes ainda no armazém (lotes ativos) — tempo médio ponderado por qtd."""
    ref_data = func.coalesce(ColetaSementes.data_coleta, LoteSementes.data_formacao_lote)
    rows = (
        await db.execute(
            select(
                LoteSementes.id_especie,
                LoteSementes.quantidade_disponivel,
                (func.current_date() - ref_data).label("dias"),
            )
            .outerjoin(ColetaSementes, LoteSementes.id_coleta_sementes == ColetaSementes.id)
            .where(
                LoteSementes.status == "ativo",
                LoteSementes.quantidade_disponivel > 0,
            )
        )
    ).all()

    agg: Dict[int, Dict[str, Any]] = defaultdict(
        lambda: {"dias": [], "qtd_sementes": 0, "lotes": 0}
    )
    for row in rows:
        eid = int(row.id_especie)
        qtd = int(row.quantidade_disponivel or 0)
        dias = int(row.dias or 0)
        agg[eid]["qtd_sementes"] += qtd
        agg[eid]["lotes"] += 1
        for _ in range(min(qtd, 500)):
            agg[eid]["dias"].append(dias)
        if qtd > 500:
            agg[eid]["dias"].extend([dias] * (qtd - 500))

    out: Dict[int, Dict[str, Any]] = {}
    for eid, data in agg.items():
        out[eid] = {
            "dias_medio": _media(data["dias"]),
            "amostras": len(data["dias"]),
            "quantidade_sementes": data["qtd_sementes"],
            "lotes_ativos": data["lotes"],
        }
    return out


async def montar_timeline_especies(
    db: AsyncSession,
    *,
    id_especie: Optional[int] = None,
) -> Dict[str, Any]:
    hoje = date.today()

    q = (
        select(Planta)
        .options(
            selectinload(Planta.canteiro),
            selectinload(Planta.especie),
            selectinload(Planta.semeadura),
            selectinload(Planta.lote_sementes).selectinload(LoteSementes.coleta),
            selectinload(Planta.transferencias)
            .selectinload(TransferenciaPlanta.canteiro_origem),
            selectinload(Planta.transferencias)
            .selectinload(TransferenciaPlanta.canteiro_destino),
        )
        .where(Planta.status.notin_(VENDIDAS_OU_MORTAS))
    )
    if id_especie is not None:
        q = q.where(Planta.id_especie == id_especie)

    plantas = (await db.execute(q)).scalars().unique().all()
    armazem_lotes = await _armazem_por_especie(db)

    por_esp: Dict[int, Dict[str, Any]] = {}

    def _ensure(eid: int, pop, cient) -> Dict[str, Any]:
        if eid not in por_esp:
            por_esp[eid] = {
                "id_especie": eid,
                "nome_popular": pop,
                "nome_cientifico": cient,
                "quantidade_plantas": 0,
                "onde_agora": {e: 0 for e in ETAPAS},
                "armazem_sementes": armazem_lotes.get(eid, {}),
                "dias_armazem": [],
                "dias_sementeira": [],
                "dias_canteiro": [],
                "dias_rustificacao": [],
            }
        return por_esp[eid]

    for p in plantas:
        esp = p.especie
        agg = _ensure(
            p.id_especie,
            esp.nome_popular if esp else None,
            esp.nome_cientifico if esp else "",
        )
        agg["quantidade_plantas"] += 1

        tipo = p.canteiro.tipo_local if p.canteiro else None
        seg = _segmento_etapa(tipo)
        if seg:
            agg["onde_agora"][seg] += 1

        dwell, dias_arm = _calcular_dwell_planta(p, list(p.transferencias or []), hoje)
        if dias_arm is not None:
            agg["dias_armazem"].append(dias_arm)
        if dwell.get("sementeira"):
            agg["dias_sementeira"].append(dwell["sementeira"])
        if dwell.get("canteiro"):
            agg["dias_canteiro"].append(dwell["canteiro"])
        if dwell.get("rustificacao"):
            agg["dias_rustificacao"].append(dwell["rustificacao"])

    for eid, arm in armazem_lotes.items():
        if eid not in por_esp:
            esp_row = await db.get(Especie, eid)
            if esp_row:
                _ensure(eid, esp_row.nome_popular, esp_row.nome_cientifico)
        if eid in por_esp:
            por_esp[eid]["armazem_sementes"] = arm
            por_esp[eid]["onde_agora"]["armazem"] = arm.get("quantidade_sementes", 0)

    especies_out: List[Dict[str, Any]] = []
    global_dias: Dict[str, List[int]] = {e: [] for e in ETAPAS}

    for agg in sorted(por_esp.values(), key=lambda x: -x["quantidade_plantas"]):
        arm_lote = agg.get("armazem_sementes") or {}
        arm_plantas = agg["dias_armazem"]
        arm_medio = arm_lote.get("dias_medio")
        if arm_plantas:
            global_dias["armazem"].extend(arm_plantas)
            m_pl = _media(arm_plantas)
            if arm_medio is not None and m_pl is not None:
                arm_medio = round((arm_medio + m_pl) / 2, 1)
            elif m_pl is not None:
                arm_medio = m_pl
        elif arm_medio is not None:
            global_dias["armazem"].append(int(round(arm_medio)))

        global_dias["sementeira"].extend(agg["dias_sementeira"])
        global_dias["canteiro"].extend(agg["dias_canteiro"])
        global_dias["rustificacao"].extend(agg["dias_rustificacao"])

        etapas = {}
        for key, lista, arm_extra in (
            ("armazem", arm_plantas, arm_lote),
            ("sementeira", agg["dias_sementeira"], None),
            ("canteiro", agg["dias_canteiro"], None),
            ("rustificacao", agg["dias_rustificacao"], None),
        ):
            if key == "armazem":
                medio = arm_medio
                n = len(arm_plantas) + (arm_extra.get("amostras") or 0)
                if arm_extra.get("dias_medio") and arm_plantas:
                    n = max(n, 1)
            else:
                medio = _media(lista)
                n = len(lista)
            etapas[key] = {
                "dias_medio": medio,
                "amostras": n,
                "label": ETAPA_LABELS[key],
                "cor": ETAPA_CORES[key],
            }
            if medio is not None and n > 0:
                pass

        total_medio = sum(e["dias_medio"] or 0 for e in etapas.values())
        for e in etapas.values():
            d = e["dias_medio"] or 0
            e["percentual_timeline"] = round(100 * d / total_medio, 1) if total_medio > 0 else 0

        especies_out.append(
            {
                "id_especie": agg["id_especie"],
                "nome_popular": agg["nome_popular"],
                "nome_cientifico": agg["nome_cientifico"],
                "quantidade_plantas": agg["quantidade_plantas"],
                "onde_agora": agg["onde_agora"],
                "etapas": etapas,
                "ciclo_total_medio": round(total_medio, 1) if total_medio > 0 else None,
            }
        )

    global_etapas = {}
    total_g = 0
    for key in ETAPAS:
        m = _media(global_dias[key])
        global_etapas[key] = {
            "dias_medio": m,
            "amostras": len(global_dias[key]),
            "label": ETAPA_LABELS[key],
            "cor": ETAPA_CORES[key],
        }
        if m:
            total_g += m
    for key in ETAPAS:
        d = global_etapas[key]["dias_medio"] or 0
        global_etapas[key]["percentual_timeline"] = (
            round(100 * d / total_g, 1) if total_g > 0 else 0
        )

    return {
        "etapas_ordem": list(ETAPAS),
        "filtro_id_especie": id_especie,
        "resumo_global": {
            "etapas": global_etapas,
            "ciclo_total_medio": round(total_g, 1) if total_g > 0 else None,
            "quantidade_especies": len(especies_out),
        },
        "especies": especies_out,
    }
