from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.arvores_matriz import ArvoreMatriz
from app.models.coletas_sementes import ColetaSementes
from app.models.especies import Especie
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta
from app.models.vendas import Venda
from app.models.atividades import Atividade
from app.models.pragas import CombateRealizado
from app.models.canteiros import Canteiro


async def get_dashboard_resumo(db: AsyncSession) -> Dict[str, Any]:
    especies = (await db.execute(select(func.count(Especie.id)))).scalar() or 0
    matrizes = (await db.execute(select(func.count(ArvoreMatriz.id)))).scalar() or 0
    coletas = (await db.execute(select(func.count(ColetaSementes.id)))).scalar() or 0
    mudas_ativas = (
        await db.execute(
            select(func.count(Planta.id)).where(Planta.status.notin_(["VENDIDA", "MORTA"]))
        )
    ).scalar() or 0
    lotes_ativos = (
        await db.execute(select(func.count(LoteSementes.id)).where(LoteSementes.status == "ativo"))
    ).scalar() or 0

    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    vendas_mes = (
        await db.execute(
            select(func.coalesce(func.sum(Venda.valor_total), 0)).where(
                Venda.status == "PAGO", Venda.data_venda >= inicio_mes
            )
        )
    ).scalar() or 0

    receita_total = (
        await db.execute(
            select(func.coalesce(func.sum(Venda.valor_total), 0)).where(Venda.status == "PAGO")
        )
    ).scalar() or 0

    custo_atividades = (
        await db.execute(select(func.coalesce(func.sum(Atividade.custo_atividade), 0)))
    ).scalar() or 0
    custo_combates = (
        await db.execute(select(func.coalesce(func.sum(CombateRealizado.custo_total), 0)))
    ).scalar() or 0
    custo_operacional = float(custo_atividades) + float(custo_combates)

    por_especie_q = (
        select(
            Especie.id,
            func.coalesce(Especie.nome_popular, Especie.nome_cientifico).label("nome"),
            func.count(Planta.id).label("quantidade"),
        )
        .join(Planta, Planta.id_especie == Especie.id)
        .where(Planta.status.notin_(["VENDIDA", "MORTA"]))
        .group_by(Especie.id, Especie.nome_popular, Especie.nome_cientifico)
        .order_by(func.count(Planta.id).desc())
        .limit(15)
    )
    plantas_por_especie = [
        {"especie": row.nome, "quantidade": int(row.quantidade)}
        for row in (await db.execute(por_especie_q)).all()
    ]

    ocupacao: List[dict] = []
    try:
        result = await db.execute(text("SELECT * FROM vw_ocupacao_canteiros ORDER BY nome"))
        for row in result.mappings().all():
            ocupacao.append(dict(row))
    except Exception:
        canteiros = (await db.execute(select(Canteiro).where(Canteiro.ativo == True))).scalars().all()
        for c in canteiros:
            total = (
                await db.execute(
                    select(func.count(Planta.id)).where(
                        Planta.id_canteiro == c.id,
                        Planta.status.notin_(["VENDIDA", "MORTA"]),
                    )
                )
            ).scalar() or 0
            ocupacao.append({"id_canteiro": c.id, "nome": c.nome, "total_plantas": total})

    return {
        "especies": int(especies),
        "matrizes": int(matrizes),
        "coletas": int(coletas),
        "mudas_ativas": int(mudas_ativas),
        "lotes_ativos": int(lotes_ativos),
        "vendas_mes": float(vendas_mes),
        "receita_total_paga": float(receita_total),
        "custo_operacional": float(custo_operacional),
        "plantas_por_especie": plantas_por_especie,
        "ocupacao_canteiros": ocupacao,
    }


async def get_resumo_financeiro(db: AsyncSession) -> Dict[str, float]:
    try:
        row = (await db.execute(text("SELECT * FROM vw_resumo_financeiro"))).mappings().first()
        if row:
            data = dict(row)
            custo_op = float(data.get("custo_atividades") or 0) + float(data.get("custo_fitossanidade") or 0)
            mudas = int(data.get("mudas_ativas") or 0)
            custo_estoque = float(data.get("custo_estoque_mudas") or 0)
            receita = float(data.get("receita_vendas_paga") or 0)
            return {
                "total_capex": float(data.get("total_capex") or 0),
                "total_opex": float(data.get("total_opex") or 0),
                "receita_vendas_paga": receita,
                "receita_mes_atual": float(data.get("receita_mes_atual") or 0),
                "custo_atividades": float(data.get("custo_atividades") or 0),
                "custo_fitossanidade": float(data.get("custo_fitossanidade") or 0),
                "custo_estoque_mudas": custo_estoque,
                "custo_operacional_total": custo_op,
                "mudas_ativas": mudas,
                "custo_por_muda": custo_estoque / mudas if mudas else 0,
                "resultado_liquido": receita - custo_op - float(data.get("total_opex") or 0),
            }
    except Exception:
        pass

    dash = await get_dashboard_resumo(db)
    return {
        "total_capex": 0,
        "total_opex": 0,
        "receita_vendas_paga": dash["receita_total_paga"],
        "receita_mes_atual": dash["vendas_mes"],
        "custo_atividades": 0,
        "custo_fitossanidade": 0,
        "custo_estoque_mudas": 0,
        "custo_operacional_total": dash["custo_operacional"],
        "mudas_ativas": dash["mudas_ativas"],
        "custo_por_muda": 0,
        "resultado_liquido": dash["receita_total_paga"] - dash["custo_operacional"],
    }
