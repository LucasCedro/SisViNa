from typing import Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lotes_sementes import LoteSementes
from app.models.insumos import Insumo
from app.models.plantas import Planta
from app.models.canteiros import Canteiro
from app.models.especies import Especie
from app.crud.lotes_sementes import get_lotes


async def get_resumo_estoques(db: AsyncSession) -> Dict[str, Any]:
    lotes = await get_lotes(db, status="ativo", limit=500)
    lotes_ativos = [l for l in lotes if (l.get("quantidade_disponivel") or 0) > 0]

    ins_result = await db.execute(select(Insumo).order_by(Insumo.nome))
    insumos_db = ins_result.scalars().all()
    insumos = [
        {
            "id": i.id,
            "nome": i.nome,
            "tipo": i.tipo,
            "unidade_medida": i.unidade_medida,
            "quantidade_estoque": float(i.quantidade_estoque or 0),
            "preco_unitario": float(i.preco_unitario) if i.preco_unitario else None,
            "fornecedor": i.fornecedor,
        }
        for i in insumos_db
    ]

    q_sementeira = (
        select(func.count(Planta.id))
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            Planta.status == "SEMENTE",
            Canteiro.tipo_local == "sementeira",
        )
    )
    q_canteiro = (
        select(func.count(Planta.id))
        .join(Canteiro, Planta.id_canteiro == Canteiro.id)
        .where(
            Planta.status.in_(("MUDA", "JOVEM", "ADULTA")),
            Canteiro.tipo_local == "canteiro",
        )
    )
    total_sementeira = (await db.execute(q_sementeira)).scalar() or 0
    total_canteiro = (await db.execute(q_canteiro)).scalar() or 0

    return {
        "total_lotes_sementes_ativos": len(lotes_ativos),
        "total_sementes_disponiveis": sum(
            l.get("quantidade_disponivel", 0) for l in lotes_ativos
        ),
        "total_plantas_sementeira": int(total_sementeira),
        "total_plantas_canteiro": int(total_canteiro),
        "total_insumos": len(insumos),
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
                "status": l["status"],
                "condicoes_armazenamento": l.get("condicoes_armazenamento"),
            }
            for l in lotes_ativos
        ],
        "insumos": insumos,
    }
