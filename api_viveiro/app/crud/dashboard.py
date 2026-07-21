from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.arvores_matriz import ArvoreMatriz
from app.models.coletas_sementes import ColetaSementes
from app.models.especies import Especie
from app.models.lancamentos_financeiros import LancamentoFinanceiro
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta
from app.models.vendas import Venda
from app.models.atividades import Atividade
from app.models.pragas import CombateRealizado, PragaPlanta
from app.models.canteiros import Canteiro


async def get_dashboard_resumo(
    db: AsyncSession, id_viveiro: Optional[int] = None
) -> Dict[str, Any]:
    especies = (await db.execute(select(func.count(Especie.id)))).scalar() or 0

    matrizes_q = select(func.count(ArvoreMatriz.id))
    if id_viveiro is not None:
        matrizes_q = matrizes_q.where(ArvoreMatriz.id_viveiro == id_viveiro)
    matrizes = (await db.execute(matrizes_q)).scalar() or 0

    coletas_q = select(func.count(ColetaSementes.id)).join(
        ArvoreMatriz, ColetaSementes.id_arvore_matriz == ArvoreMatriz.id
    )
    if id_viveiro is not None:
        coletas_q = coletas_q.where(ArvoreMatriz.id_viveiro == id_viveiro)
    coletas = (await db.execute(coletas_q)).scalar() or 0

    mudas_q = select(func.count(Planta.id)).where(Planta.status.notin_(["VENDIDA", "MORTA"]))
    if id_viveiro is not None:
        mudas_q = mudas_q.where(Planta.id_viveiro == id_viveiro)
    mudas_ativas = (await db.execute(mudas_q)).scalar() or 0

    lotes_q = select(func.count(LoteSementes.id)).where(LoteSementes.status == "ativo")
    if id_viveiro is not None:
        lotes_q = lotes_q.where(LoteSementes.id_viveiro == id_viveiro)
    lotes_ativos = (await db.execute(lotes_q)).scalar() or 0

    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    vendas_mes_q = select(func.coalesce(func.sum(Venda.valor_total), 0)).where(
        Venda.status == "PAGO", Venda.data_venda >= inicio_mes
    )
    if id_viveiro is not None:
        vendas_mes_q = vendas_mes_q.where(Venda.id_viveiro == id_viveiro)
    vendas_mes = (await db.execute(vendas_mes_q)).scalar() or 0

    receita_q = select(func.coalesce(func.sum(Venda.valor_total), 0)).where(Venda.status == "PAGO")
    if id_viveiro is not None:
        receita_q = receita_q.where(Venda.id_viveiro == id_viveiro)
    receita_total = (await db.execute(receita_q)).scalar() or 0

    custo_atividades_q = select(func.coalesce(func.sum(Atividade.custo_atividade), 0)).join(
        Planta, Atividade.id_planta == Planta.id
    )
    if id_viveiro is not None:
        custo_atividades_q = custo_atividades_q.where(Planta.id_viveiro == id_viveiro)
    custo_atividades = (await db.execute(custo_atividades_q)).scalar() or 0

    custo_combates_q = select(func.coalesce(func.sum(CombateRealizado.custo_total), 0)).join(
        PragaPlanta, CombateRealizado.id_praga_planta == PragaPlanta.id
    ).join(Planta, PragaPlanta.id_planta == Planta.id)
    if id_viveiro is not None:
        custo_combates_q = custo_combates_q.where(Planta.id_viveiro == id_viveiro)
    custo_combates = (await db.execute(custo_combates_q)).scalar() or 0
    custo_operacional = float(custo_atividades) + float(custo_combates)

    por_especie_q = (
        select(
            Especie.id,
            func.coalesce(Especie.nome_popular, Especie.nome_cientifico).label("nome"),
            func.count(Planta.id).label("quantidade"),
        )
        .join(Planta, Planta.id_especie == Especie.id)
        .where(Planta.status.notin_(["VENDIDA", "MORTA"]))
    )
    if id_viveiro is not None:
        por_especie_q = por_especie_q.where(Planta.id_viveiro == id_viveiro)
    por_especie_q = (
        por_especie_q.group_by(Especie.id, Especie.nome_popular, Especie.nome_cientifico)
        .order_by(func.count(Planta.id).desc())
        .limit(15)
    )
    plantas_por_especie = [
        {"especie": row.nome, "quantidade": int(row.quantidade)}
        for row in (await db.execute(por_especie_q)).all()
    ]

    ocupacao: List[dict] = []
    if id_viveiro is None:
        try:
            result = await db.execute(text("SELECT * FROM vw_ocupacao_canteiros ORDER BY nome"))
            for row in result.mappings().all():
                ocupacao.append(dict(row))
        except Exception:
            pass
    if not ocupacao:
        canteiros_q = select(Canteiro).where(Canteiro.ativo == True)
        if id_viveiro is not None:
            canteiros_q = canteiros_q.where(Canteiro.id_viveiro == id_viveiro)
        canteiros = (await db.execute(canteiros_q)).scalars().all()
        for c in canteiros:
            plantas_q = select(func.count(Planta.id)).where(
                Planta.id_canteiro == c.id,
                Planta.status.notin_(["VENDIDA", "MORTA"]),
            )
            if id_viveiro is not None:
                plantas_q = plantas_q.where(Planta.id_viveiro == id_viveiro)
            total = (await db.execute(plantas_q)).scalar() or 0
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


async def get_resumo_financeiro(
    db: AsyncSession,
    id_viveiro: Optional[int] = None,
    id_empresa: Optional[int] = None,
) -> Dict[str, float]:
    use_view = id_viveiro is None and id_empresa is None
    if use_view:
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

    dash = await get_dashboard_resumo(db, id_viveiro=id_viveiro)
    total_capex = 0.0
    total_opex = 0.0
    if id_empresa is not None:
        capex_q = select(func.coalesce(func.sum(LancamentoFinanceiro.valor), 0)).where(
            LancamentoFinanceiro.id_empresa == id_empresa,
            LancamentoFinanceiro.tipo == "capex",
        )
        opex_q = select(func.coalesce(func.sum(LancamentoFinanceiro.valor), 0)).where(
            LancamentoFinanceiro.id_empresa == id_empresa,
            LancamentoFinanceiro.tipo == "opex",
        )
        total_capex = float((await db.execute(capex_q)).scalar() or 0)
        total_opex = float((await db.execute(opex_q)).scalar() or 0)

    custo_estoque_q = select(func.coalesce(func.sum(Planta.custo_atual), 0)).where(
        Planta.status.notin_(["VENDIDA", "MORTA"])
    )
    if id_viveiro is not None:
        custo_estoque_q = custo_estoque_q.where(Planta.id_viveiro == id_viveiro)
    custo_estoque = float((await db.execute(custo_estoque_q)).scalar() or 0)
    mudas = int(dash["mudas_ativas"])

    return {
        "total_capex": total_capex,
        "total_opex": total_opex,
        "receita_vendas_paga": dash["receita_total_paga"],
        "receita_mes_atual": dash["vendas_mes"],
        "custo_atividades": 0,
        "custo_fitossanidade": 0,
        "custo_estoque_mudas": custo_estoque,
        "custo_operacional_total": dash["custo_operacional"],
        "mudas_ativas": mudas,
        "custo_por_muda": custo_estoque / mudas if mudas else 0,
        "resultado_liquido": dash["receita_total_paga"] - dash["custo_operacional"] - total_opex,
    }
