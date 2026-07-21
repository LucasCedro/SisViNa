"""Composição do CMV de estoque por espécie (rastreabilidade do valor)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.estagios_producao import APTA_VENDA
from app.crud.plantas_estoque import VENDIDAS_OU_MORTAS, filtro_prontas_venda
from app.models.atividades import Atividade
from app.models.canteiros import Canteiro
from app.models.especies import Especie
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta
from app.models.semeaduras import Semeadura
from app.services.custeio import calcular_cif_unitario_parque

ESTAGIO_LABELS = {
    "em_desenvolvimento": "Em desenvolvimento",
    "apta_transferencia": "Apta transferência",
    "em_crescimento": "Em crescimento",
    "apta_rustificacao": "Apta rustificação",
    "em_rustificacao": "Em rustificação",
    "apta_venda": "Apta para venda",
}

ESCOPO_LABELS = {
    "comercial": "Aptas para venda na rustificação",
    "vivas": "Todas as mudas vivas da espécie",
}


def _filtro_plantas_especie(query, id_especie: int, escopo: str, id_viveiro: Optional[int] = None):
    query = (
        query.select_from(Planta)
        .join(Especie, Planta.id_especie == Especie.id)
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .outerjoin(Semeadura, Planta.id_semeadura == Semeadura.id)
        .outerjoin(LoteSementes, Planta.id_lote_sementes == LoteSementes.id)
        .where(
            Planta.id_especie == id_especie,
            Planta.status.notin_(VENDIDAS_OU_MORTAS),
        )
    )
    if id_viveiro is not None:
        query = query.where(Planta.id_viveiro == id_viveiro)
    if escopo == "comercial":
        query = filtro_prontas_venda(query)
    return query


async def montar_cmv_detalhe_especie(
    db: AsyncSession,
    id_especie: int,
    escopo: str = "comercial",
    id_viveiro: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    especie = await db.get(Especie, id_especie)
    if not especie:
        return None

    escopo = escopo if escopo in ESCOPO_LABELS else "comercial"
    cif_info = await calcular_cif_unitario_parque(db)
    parque_total = int(cif_info["parque_total"])
    cif_unitario = float(cif_info["cif_unitario"])

    q = _filtro_plantas_especie(
        select(
            Planta.id,
            Planta.custo_atual,
            Planta.custo_inicial,
            Planta.estagio_producao,
            Planta.status,
            Planta.id_semeadura,
            Canteiro.nome.label("canteiro_nome"),
            Canteiro.tipo_local,
            Semeadura.id.label("sem_id"),
            Semeadura.data_semeadura,
            Semeadura.quantidade_mudas_obtidas,
            Semeadura.quantidade_sementes_usadas,
            Semeadura.custo_sementes,
            Semeadura.custo_insumos,
            Semeadura.custo_indireto,
            Semeadura.custo_total,
            Semeadura.custo_unitario_muda,
            LoteSementes.codigo_lote,
            LoteSementes.id.label("id_lote"),
        ),
        id_especie,
        escopo,
        id_viveiro,
    )
    rows = (await db.execute(q)).all()
    if not rows:
        return {
            "id_especie": id_especie,
            "nome_popular": especie.nome_popular,
            "nome_cientifico": especie.nome_cientifico,
            "escopo": escopo,
            "escopo_label": ESCOPO_LABELS[escopo],
            "quantidade": 0,
            "valor_total": 0.0,
            "custo_medio": 0.0,
            "formula": "Σ custo_atual das mudas no escopo selecionado",
            "por_estagio": [],
            "por_semeadura": [],
            "composicao_agregada": [],
            "ajustes_pos_semeadura": {"atividades": 0.0, "outros": 0.0, "total": 0.0},
            "observacoes": ["Nenhuma muda neste escopo."],
            "parque_total": parque_total,
            "cif_unitario_parque": cif_unitario,
        }

    planta_ids = [int(r.id) for r in rows]
    custos = [float(r.custo_atual or 0) for r in rows]
    iniciais = [float(r.custo_inicial or 0) for r in rows]
    valor_total = round(sum(custos), 2)
    qtd = len(rows)
    custo_medio = round(valor_total / qtd, 2) if qtd else 0.0
    base_semeadura = round(sum(iniciais), 2)
    delta_total = round(valor_total - base_semeadura, 2)

    atividades_total = 0.0
    if planta_ids:
        atividades_total = float(
            (
                await db.execute(
                    select(func.coalesce(func.sum(Atividade.custo_atividade), 0)).where(
                        Atividade.id_planta.in_(planta_ids)
                    )
                )
            ).scalar()
            or 0
        )

    por_estagio: Dict[str, dict] = {}
    por_semeadura: Dict[int, dict] = {}
    direct_sementes_escopo = 0.0
    direct_insumos_escopo = 0.0

    for row in rows:
        est = row.estagio_producao or "—"
        ca = float(row.custo_atual or 0)
        ci = float(row.custo_inicial or 0)
        if est not in por_estagio:
            por_estagio[est] = {
                "estagio": est,
                "estagio_label": ESTAGIO_LABELS.get(est, est),
                "quantidade": 0,
                "valor_total": 0.0,
                "custo_medio": 0.0,
            }
        por_estagio[est]["quantidade"] += 1
        por_estagio[est]["valor_total"] += ca

        sem_id = int(row.sem_id) if row.sem_id else None
        if sem_id is None:
            continue

        if sem_id not in por_semeadura:
            qtd_sem = int(row.quantidade_mudas_obtidas or 0) or 1
            cu_sem = float(row.custo_unitario_muda or 0)
            cs = float(row.custo_sementes or 0)
            ci_ins = float(row.custo_insumos or 0)
            u_sem = round(cs / qtd_sem, 4)
            u_ins = round(ci_ins / qtd_sem, 4)
            por_semeadura[sem_id] = {
                "id_semeadura": sem_id,
                "data_semeadura": row.data_semeadura.isoformat() if row.data_semeadura else None,
                "codigo_lote": row.codigo_lote,
                "quantidade_no_escopo": 0,
                "quantidade_semeadura": qtd_sem,
                "custo_unitario_muda": cu_sem,
                "valor_total": 0.0,
                "composicao_unitario": {
                    "sementes": u_sem,
                    "insumos": u_ins,
                    "indireto": round(cif_unitario, 4),
                },
                "mudas_base_rateio": parque_total,
                "itens_custeio": [
                    {
                        "origem": "premissa",
                        "chave": item["chave"],
                        "descricao": item["descricao"],
                        "valor_unitario": item["unitario"],
                        "valor_total": 0.0,
                    }
                    for item in cif_info.get("itens") or []
                ],
            }
        por_semeadura[sem_id]["quantidade_no_escopo"] += 1
        por_semeadura[sem_id]["valor_total"] += ca
        u = por_semeadura[sem_id]["composicao_unitario"]
        direct_sementes_escopo += u["sementes"]
        direct_insumos_escopo += u["insumos"]

    for est in por_estagio.values():
        if est["quantidade"]:
            est["valor_total"] = round(est["valor_total"], 2)
            est["custo_medio"] = round(est["valor_total"] / est["quantidade"], 2)

    semeaduras_ordenadas = sorted(por_semeadura.values(), key=lambda x: x["id_semeadura"])
    for bloco in semeaduras_ordenadas:
        bloco["valor_total"] = round(bloco["valor_total"], 2)
        q_esc = bloco["quantidade_no_escopo"]
        u = bloco["composicao_unitario"]
        bloco["composicao_total_escopo"] = {
            "sementes": round(u["sementes"] * q_esc, 2),
            "insumos": round(u["insumos"] * q_esc, 2),
            "indireto": round(u["indireto"] * q_esc, 2),
        }
        for item in bloco["itens_custeio"]:
            item["valor_total"] = round(float(item["valor_unitario"]) * q_esc, 2)

    composicao_agregada: List[dict] = []
    if direct_sementes_escopo > 0:
        composicao_agregada.append(
            {
                "chave": "sementes",
                "origem": "sementes",
                "descricao": "Sementes (custo direto da semeadura)",
                "valor_total": round(direct_sementes_escopo, 2),
                "valor_unitario_medio": round(direct_sementes_escopo / qtd, 4),
            }
        )
    if direct_insumos_escopo > 0:
        composicao_agregada.append(
            {
                "chave": "insumos",
                "origem": "insumos",
                "descricao": "Insumos diretos (substrato, hidrogel…)",
                "valor_total": round(direct_insumos_escopo, 2),
                "valor_unitario_medio": round(direct_insumos_escopo / qtd, 4),
            }
        )
    for item in cif_info.get("itens") or []:
        unit = float(item["unitario"])
        composicao_agregada.append(
            {
                "chave": item["chave"],
                "origem": "premissa",
                "descricao": item["descricao"],
                "valor_total": round(unit * qtd, 2),
                "valor_unitario_medio": unit,
            }
        )
    composicao_agregada.sort(key=lambda x: -x["valor_total"])

    outros_delta = round(delta_total - atividades_total, 2)
    observacoes: List[str] = []
    if escopo == "comercial":
        observacoes.append(
            "Estoque comercial = mudas com estágio apta_venda na área de rustificação "
            "(Σ custo_atual de cada unidade)."
        )
    else:
        observacoes.append("Estoque = todas as mudas vivas da espécie (Σ custo_atual).")
    observacoes.append(
        f"CIF mensal (água, energia, MO…) rateado pelo parque inteiro: "
        f"R$ {cif_info['cif_mensal_total']:.2f}/mês ÷ {parque_total} mudas vivas "
        f"= R$ {cif_unitario:.4f}/muda (igual para todas as espécies)."
    )
    if any(float(r.custo_sementes or 0) == 0 for r in rows if r.sem_id):
        observacoes.append(
            "Sementes com valor zero no lote — informe custo na entrada do armazém para compor o CMV."
        )
    if atividades_total <= 0 and outros_delta <= 0:
        observacoes.append(
            "Sem ajustes pós-semeadura (atividades/fitossanidade) nas mudas deste escopo."
        )

    return {
        "id_especie": id_especie,
        "nome_popular": especie.nome_popular,
        "nome_cientifico": especie.nome_cientifico,
        "escopo": escopo,
        "escopo_label": ESCOPO_LABELS[escopo],
        "quantidade": qtd,
        "valor_total": valor_total,
        "custo_medio": custo_medio,
        "formula": f"{qtd} × custo médio {custo_medio:.2f} = {valor_total:.2f}"
        if qtd
        else "Σ custo_atual",
        "resumo_calculo": {
            "custo_base_semeadura": base_semeadura,
            "ajustes_pos_semeadura": delta_total,
            "valor_total": valor_total,
        },
        "por_estagio": sorted(por_estagio.values(), key=lambda x: -x["valor_total"]),
        "por_semeadura": semeaduras_ordenadas,
        "composicao_agregada": composicao_agregada,
        "ajustes_pos_semeadura": {
            "atividades": round(atividades_total, 2),
            "outros": outros_delta,
            "total": delta_total,
        },
        "observacoes": observacoes,
        "parque_total": parque_total,
        "cif_unitario_parque": cif_unitario,
    }
