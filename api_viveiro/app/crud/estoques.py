from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import plantas as crud_plantas
from app.crud.lotes_sementes import get_lotes
from app.crud.plantas_estoque import contar_mudas_pipeline
from app.models.insumos import Insumo
from app.models.plantas import Planta


def _alerta_insumo(insumo: Insumo) -> Optional[str]:
    qtd = float(insumo.quantidade_estoque or 0)
    minimo = float(insumo.estoque_minimo or 0)
    maximo = float(insumo.estoque_maximo) if insumo.estoque_maximo is not None else None
    if minimo > 0 and qtd < minimo:
        return "abaixo_minimo"
    if maximo is not None and maximo > 0 and qtd > maximo:
        return "acima_maximo"
    return None


def _insumo_para_resumo(i: Insumo) -> dict:
    qtd = float(i.quantidade_estoque or 0)
    preco = float(i.preco_unitario) if i.preco_unitario is not None else None
    valor = float(i.valor_estoque or 0)
    if valor <= 0 and preco is not None:
        valor = qtd * preco
    return {
        "id": i.id,
        "nome": i.nome,
        "tipo": i.tipo,
        "unidade_medida": i.unidade_medida,
        "quantidade_estoque": qtd,
        "preco_unitario": preco,
        "valor_estoque": valor,
        "estoque_minimo": float(i.estoque_minimo or 0),
        "estoque_maximo": float(i.estoque_maximo) if i.estoque_maximo is not None else None,
        "fornecedor": i.fornecedor,
        "alerta_estoque": _alerta_insumo(i),
    }


async def get_resumo_estoques(db: AsyncSession) -> Dict[str, Any]:
    lotes = await get_lotes(db, status="ativo", limit=500)
    lotes_ativos = [l for l in lotes if (l.get("quantidade_disponivel") or 0) > 0]

    ins_result = await db.execute(select(Insumo).order_by(Insumo.nome))
    insumos_db = ins_result.scalars().all()
    insumos = [_insumo_para_resumo(i) for i in insumos_db]
    valor_total_insumos = sum(i["valor_estoque"] for i in insumos)

    pipeline = await contar_mudas_pipeline(db)

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
        "valor_total_mudas": valor_mudas_vivas,
        "mudas_pipeline": pipeline,
        "estoque_comercial": estoque_comercial,
        "lotes_sementes": [
            {
                "id": l["id"],
                "codigo_lote": l["codigo_lote"],
                "origem_lote": l.get("origem_lote", "coleta"),
                "id_especie": l["id_especie"],
                "especie_nome": l.get("especie_nome"),
                "matriz_nome": l.get("matriz_nome"),
                "quantidade_disponivel": l["quantidade_disponivel"],
                "quantidade_inicial": l["quantidade_inicial"],
                "valor_total": l.get("valor_total"),
                "custo_unitario": l.get("custo_unitario"),
                "status": l["status"],
                "condicoes_armazenamento": l.get("condicoes_armazenamento"),
            }
            for l in lotes_ativos
        ],
        "insumos": insumos,
    }
