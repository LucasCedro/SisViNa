from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import plantas as crud_plantas
from app.crud.estoques_analytics import montar_analitico_mudas, verificar_integridade_cmv
from app.crud.estoques_timeline import montar_timeline_especies
from app.crud.lotes_sementes import get_lotes
from app.crud.plantas_estoque import contar_mudas_pipeline
from app.crud.viveiro_layout import get_layout
from app.models.insumo_movimentacao import InsumoMovimentacao
from app.models.insumos import Insumo
from app.models.plantas import Planta

_TIPO_CAMPO_CAPACIDADE = {
    "estoque": "armazem",
    "sementeira": "sementeira",
    "canteiro": "canteiro",
    "campo": "canteiro",
    "rustificacao": "rustificacao",
}


def _capacidade_campo_layout(campo: Dict[str, Any]) -> int:
    config = campo.get("config") or {}
    raw = config.get("capacidade")
    if raw is not None:
        try:
            return max(0, int(raw))
        except (TypeError, ValueError):
            pass
    if campo.get("tipo") in ("canteiro", "campo"):
        linhas = config.get("linhas")
        colunas = config.get("colunas")
        if linhas and colunas:
            try:
                return max(0, int(linhas) * int(colunas))
            except (TypeError, ValueError):
                pass
    return 0


async def capacidades_viveiro_layout(db: AsyncSession) -> Dict[str, int]:
    """Soma capacidades cadastradas no Viveiro Designer (planta baixa)."""
    layout = await get_layout(db)
    caps = {"armazem": 0, "sementeira": 0, "canteiro": 0, "rustificacao": 0}
    for campo in layout.get("campos") or []:
        seg = _TIPO_CAMPO_CAPACIDADE.get(campo.get("tipo") or "")
        if not seg:
            continue
        caps[seg] += _capacidade_campo_layout(campo)
    caps["desenvolvimento"] = caps["sementeira"] + caps["canteiro"]
    return caps


def _alerta_insumo(insumo: Insumo) -> Optional[str]:
    qtd = float(insumo.quantidade_estoque or 0)
    minimo = float(insumo.estoque_minimo or 0)
    maximo = float(insumo.estoque_maximo) if insumo.estoque_maximo is not None else None
    if minimo > 0 and qtd < minimo:
        return "abaixo_minimo"
    if maximo is not None and maximo > 0 and qtd > maximo:
        return "acima_maximo"
    return None


def _fmt_date(d) -> Optional[str]:
    if d is None:
        return None
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


async def _mapa_movimentacoes_insumo(db: AsyncSession) -> Dict[int, Dict[str, Any]]:
    rows = (
        await db.execute(
            select(
                InsumoMovimentacao.id_insumo,
                func.count(InsumoMovimentacao.id).label("qtd"),
                func.max(InsumoMovimentacao.data_movimento).label("ultima"),
            ).group_by(InsumoMovimentacao.id_insumo)
        )
    ).all()
    return {
        int(r.id_insumo): {"qtd_movimentacoes": int(r.qtd or 0), "ultima_movimentacao": r.ultima}
        for r in rows
    }


def _insumo_para_resumo(i: Insumo, mov: Optional[Dict[str, Any]] = None) -> dict:
    qtd = float(i.quantidade_estoque or 0)
    preco = float(i.preco_unitario) if i.preco_unitario is not None else None
    valor = float(i.valor_estoque or 0)
    if valor <= 0 and preco is not None:
        valor = qtd * preco
    mov = mov or {}
    return {
        "id": i.id,
        "nome": i.nome,
        "tipo": i.tipo,
        "descricao": i.descricao,
        "unidade_medida": i.unidade_medida,
        "quantidade_estoque": qtd,
        "preco_unitario": preco,
        "valor_estoque": valor,
        "estoque_minimo": float(i.estoque_minimo or 0),
        "estoque_maximo": float(i.estoque_maximo) if i.estoque_maximo is not None else None,
        "fornecedor": i.fornecedor,
        "data_ultima_compra": _fmt_date(i.data_ultima_compra),
        "ultima_movimentacao": _fmt_date(mov.get("ultima_movimentacao")),
        "qtd_movimentacoes": mov.get("qtd_movimentacoes", 0),
        "alerta_estoque": _alerta_insumo(i),
    }


def _lote_para_resumo(l: dict) -> dict:
    hoje = date.today()
    df = l.get("data_formacao_lote")
    dias_arm = (hoje - df).days if df else None
    qi = l.get("quantidade_inicial") or 0
    qd = l.get("quantidade_disponivel") or 0
    pct_consumido = round(100 * (qi - qd) / qi, 1) if qi > 0 else None
    return {
        "id": l["id"],
        "codigo_lote": l["codigo_lote"],
        "origem_lote": l.get("origem_lote", "coleta"),
        "id_especie": l["id_especie"],
        "especie_nome": l.get("especie_nome"),
        "matriz_nome": l.get("matriz_nome"),
        "quantidade_disponivel": qd,
        "quantidade_inicial": qi,
        "valor_total": l.get("valor_total"),
        "custo_unitario": l.get("custo_unitario"),
        "status": l["status"],
        "condicoes_armazenamento": l.get("condicoes_armazenamento"),
        "data_formacao_lote": _fmt_date(df),
        "data_coleta": _fmt_date(l.get("data_coleta")),
        "dias_armazenamento": dias_arm,
        "percentual_consumido": pct_consumido,
        "ultimo_teste_germinacao": l.get("ultimo_teste_germinacao"),
        "beneficiamento": l.get("beneficiamento"),
        "observacoes": l.get("observacoes"),
    }


async def get_resumo_estoques(db: AsyncSession) -> Dict[str, Any]:
    lotes = await get_lotes(db, status="ativo", limit=500)
    lotes_ativos = [l for l in lotes if (l.get("quantidade_disponivel") or 0) > 0]
    lotes_resumo = [_lote_para_resumo(l) for l in lotes_ativos]
    valor_total_sementes = sum(float(l.get("valor_total") or 0) for l in lotes_ativos)

    mov_map = await _mapa_movimentacoes_insumo(db)
    ins_result = await db.execute(select(Insumo).order_by(Insumo.nome))
    insumos_db = ins_result.scalars().all()
    insumos = [_insumo_para_resumo(i, mov_map.get(i.id)) for i in insumos_db]
    valor_total_insumos = sum(i["valor_estoque"] for i in insumos)

    pipeline = await contar_mudas_pipeline(db)
    capacidades_viveiro = await capacidades_viveiro_layout(db)
    analitico_viveiro = await montar_analitico_mudas(db, metrica_idade="viveiro")
    analitico_rust = await montar_analitico_mudas(db, metrica_idade="rustificacao")
    cmv_integridade = await verificar_integridade_cmv(db)
    timeline_especies = await montar_timeline_especies(db)

    estoque_comercial_raw = await crud_plantas.get_estoque_resumo(db)
    estoque_comercial = [
        {
            "id_especie": e["id_especie"],
            "nome_popular": e.get("nome_popular"),
            "nome_cientifico": e["nome_cientifico"],
            "quantidade": e["quantidade"],
            "valor_unitario": e["valor_unitario"],
            "custo_medio": e.get("custo_medio", 0),
            "valor_estoque_especie": e.get("valor_estoque_especie", 0),
            "localizacao": e.get("localizacao"),
            "status_predominante": e.get("status_predominante"),
            "estagio_comercial": e.get("estagio_comercial", "apta_venda"),
        }
        for e in estoque_comercial_raw
    ]
    total_mudas_aptas_venda = sum(e["quantidade"] for e in estoque_comercial)
    valor_mudas_comercial = sum(e.get("valor_estoque_especie", 0) for e in estoque_comercial)

    valor_mudas_vivas = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(Planta.custo_atual), 0)).where(
                    Planta.status.notin_(("VENDIDA", "MORTA"))
                )
            )
        ).scalar()
        or 0
    )

    return {
        "total_lotes_sementes_ativos": len(lotes_ativos),
        "total_sementes_disponiveis": sum(
            l.get("quantidade_disponivel", 0) for l in lotes_ativos
        ),
        "total_plantas_sementeira": pipeline["em_desenvolvimento_sementeira"],
        "total_plantas_canteiro": pipeline["em_desenvolvimento_canteiro"],
        "total_insumos": len(insumos),
        "total_mudas_aptas_venda": int(total_mudas_aptas_venda),
        "valor_total_insumos": valor_total_insumos,
        "valor_total_sementes": round(valor_total_sementes, 2),
        "valor_total_mudas": valor_mudas_vivas,
        "valor_mudas_comercial": round(valor_mudas_comercial, 2),
        "mudas_pipeline": pipeline,
        "capacidades_viveiro": capacidades_viveiro,
        "estoque_comercial": estoque_comercial,
        "analitico_mudas": analitico_viveiro,
        "analitico_mudas_rustificacao": analitico_rust,
        "cmv_integridade": cmv_integridade,
        "timeline_especies": timeline_especies,
        "lotes_sementes": lotes_resumo,
        "insumos": insumos,
    }
