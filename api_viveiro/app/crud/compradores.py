# app/crud/compradores.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compradores import Comprador
from app.models.vendas import Venda, ItemVenda
from app.schemas.compradores import CompradorCreate, CompradorUpdate
from app.auth.utils import gerar_senha_hash

VENDA_ATIVA = Venda.status != "CANCELADO"


def _classificar_relacionamento(
    vendas_historico: int,
    vendas_periodo: int,
    dias_desde_ultima: Optional[int],
) -> str:
    if vendas_historico == 0 or dias_desde_ultima is None:
        return "lead"
    if vendas_historico == 1 and dias_desde_ultima <= 90:
        return "novo"
    if dias_desde_ultima <= 90:
        if vendas_periodo >= 3 or vendas_historico >= 5:
            return "recorrente"
        return "ativo"
    if dias_desde_ultima <= 180:
        return "dormindo"
    return "inativo"


def _pct(receita: float, lucro: float) -> Optional[float]:
    if receita <= 0:
        return None
    return round((lucro / receita) * 100, 1)


async def get_compradores_analitico(
    db: AsyncSession,
    meses: int = 12,
    id_empresa: Optional[int] = None,
) -> Dict[str, Any]:
    now = datetime.now()
    if meses and meses > 0:
        data_inicio = now - timedelta(days=meses * 30)
        periodo_label = f"Últimos {meses} meses"
    else:
        data_inicio = None
        periodo_label = "Todo o período"

    periodo_cond = (
        and_(VENDA_ATIVA, Venda.data_venda >= data_inicio)
        if data_inicio
        else VENDA_ATIVA
    )
    custo_expr = func.coalesce(ItemVenda.custo_unitario, 0) * ItemVenda.quantidade

    q = (
        select(
            Comprador.id,
            Comprador.nome,
            Comprador.tipo,
            Comprador.cidade,
            Comprador.estado,
            Comprador.telefone,
            Comprador.email,
            func.count(func.distinct(case((periodo_cond, Venda.id)))).label("vendas_periodo"),
            func.count(func.distinct(case((VENDA_ATIVA, Venda.id)))).label("vendas_historico"),
            func.coalesce(func.sum(case((periodo_cond, ItemVenda.valor_total), else_=0)), 0).label(
                "receita_periodo"
            ),
            func.coalesce(func.sum(case((periodo_cond, custo_expr), else_=0)), 0).label("custo_periodo"),
            func.coalesce(func.sum(case((periodo_cond, ItemVenda.quantidade), else_=0)), 0).label(
                "mudas_periodo"
            ),
            func.max(case((VENDA_ATIVA, Venda.data_venda))).label("ultima_compra"),
            func.min(case((VENDA_ATIVA, Venda.data_venda))).label("primeira_compra"),
            func.coalesce(
                func.sum(
                    case(
                        (and_(VENDA_ATIVA, Venda.status == "PENDENTE"), Venda.valor_total),
                        else_=0,
                    )
                ),
                0,
            ).label("receita_pendente"),
        )
        .select_from(Comprador)
        .outerjoin(Venda, Comprador.id == Venda.id_comprador)
        .outerjoin(ItemVenda, Venda.id == ItemVenda.id_venda)
        .where(Comprador.ativo == True)
    )
    if id_empresa is not None:
        q = q.where(Comprador.id_empresa == id_empresa)
    q = q.group_by(
        Comprador.id,
        Comprador.nome,
        Comprador.tipo,
        Comprador.cidade,
        Comprador.estado,
        Comprador.telefone,
        Comprador.email,
    ).order_by(Comprador.nome)

    result = await db.execute(q)
    rows = result.all()

    total_cadastro = len(rows)
    clientes: List[Dict[str, Any]] = []

    for row in rows:
        receita = float(row.receita_periodo or 0)
        custo = float(row.custo_periodo or 0)
        lucro = receita - custo
        vendas_periodo = int(row.vendas_periodo or 0)
        vendas_historico = int(row.vendas_historico or 0)
        mudas = int(row.mudas_periodo or 0)
        ultima = row.ultima_compra
        dias_ultima = (now - ultima).days if ultima else None
        ticket = round(receita / vendas_periodo, 2) if vendas_periodo > 0 else None

        clientes.append(
            {
                "id": row.id,
                "nome": row.nome,
                "tipo": row.tipo,
                "cidade": row.cidade,
                "estado": row.estado,
                "telefone": row.telefone,
                "email": row.email,
                "vendas_periodo": vendas_periodo,
                "vendas_historico": vendas_historico,
                "receita_periodo": round(receita, 2),
                "custo_periodo": round(custo, 2),
                "lucro_periodo": round(lucro, 2),
                "margem_pct": _pct(receita, lucro),
                "mudas_periodo": mudas,
                "ticket_medio": ticket,
                "receita_pendente": float(row.receita_pendente or 0),
                "ultima_compra": ultima,
                "primeira_compra": row.primeira_compra,
                "dias_desde_ultima": dias_ultima,
                "status_relacionamento": _classificar_relacionamento(
                    vendas_historico, vendas_periodo, dias_ultima
                ),
            }
        )

    com_compra = [c for c in clientes if c["vendas_historico"] > 0]
    com_compra_periodo = [c for c in clientes if c["vendas_periodo"] > 0]
    receita_total = sum(c["receita_periodo"] for c in clientes)
    custo_total = sum(c["custo_periodo"] for c in clientes)
    lucro_total = receita_total - custo_total
    mudas_total = sum(c["mudas_periodo"] for c in clientes)
    pendente_total = sum(c["receita_pendente"] for c in clientes)
    recorrentes = sum(1 for c in clientes if c["status_relacionamento"] == "recorrente")
    atencao = sum(1 for c in clientes if c["status_relacionamento"] in ("dormindo", "inativo"))

    vendas_periodo_total = sum(c["vendas_periodo"] for c in clientes)
    ticket_medio = (
        round(receita_total / vendas_periodo_total, 2) if vendas_periodo_total > 0 else None
    )

    def ranking(items, key, sec_key=None, sec_label=None, limit=8):
        ordered = sorted(items, key=lambda x: x[key], reverse=True)
        ordered = [c for c in ordered if c[key] > 0][:limit]
        out = []
        for c in ordered:
            item = {
                "id": c["id"],
                "nome": c["nome"],
                "tipo": c["tipo"],
                "cidade": c["cidade"],
                "estado": c["estado"],
                "valor": c[key],
            }
            if sec_key:
                item["valor_secundario"] = c.get(sec_key)
                item["label_secundario"] = sec_label
            out.append(item)
        return out

    por_uf_map: Dict[str, Dict[str, Any]] = {}
    por_cidade_map: Dict[str, Dict[str, Any]] = {}
    por_tipo_map: Dict[str, Dict[str, Any]] = {
        "PF": {"tipo": "PF", "clientes": 0, "receita": 0.0, "lucro": 0.0},
        "PJ": {"tipo": "PJ", "clientes": 0, "receita": 0.0, "lucro": 0.0},
    }

    for c in clientes:
        if c["receita_periodo"] <= 0 and c["vendas_historico"] == 0:
            continue
        uf = (c["estado"] or "—").upper()
        por_uf_map.setdefault(uf, {"chave": uf, "uf": uf, "clientes": 0, "receita": 0.0, "mudas": 0})
        if c["receita_periodo"] > 0:
            por_uf_map[uf]["clientes"] += 1
            por_uf_map[uf]["receita"] += c["receita_periodo"]
            por_uf_map[uf]["mudas"] += c["mudas_periodo"]

        cidade_chave = f"{c['cidade'] or '—'}/{uf}"
        por_cidade_map.setdefault(
            cidade_chave,
            {"chave": cidade_chave, "uf": uf, "clientes": 0, "receita": 0.0, "mudas": 0},
        )
        if c["receita_periodo"] > 0:
            por_cidade_map[cidade_chave]["clientes"] += 1
            por_cidade_map[cidade_chave]["receita"] += c["receita_periodo"]
            por_cidade_map[cidade_chave]["mudas"] += c["mudas_periodo"]

        tipo = c["tipo"] if c["tipo"] in por_tipo_map else "PF"
        if c["receita_periodo"] > 0:
            por_tipo_map[tipo]["clientes"] += 1
            por_tipo_map[tipo]["receita"] += c["receita_periodo"]
            por_tipo_map[tipo]["lucro"] += c["lucro_periodo"]

    por_uf = sorted(por_uf_map.values(), key=lambda x: x["receita"], reverse=True)
    por_cidade = sorted(por_cidade_map.values(), key=lambda x: x["receita"], reverse=True)[:12]
    por_tipo = [v for v in por_tipo_map.values() if v["clientes"] > 0]

    atencao_list = sorted(
        [
            c
            for c in clientes
            if c["status_relacionamento"] in ("dormindo", "inativo") and c["vendas_historico"] > 0
        ],
        key=lambda x: (x["receita_periodo"], x["vendas_historico"]),
        reverse=True,
    )[:8]

    return {
        "resumo": {
            "periodo_meses": meses,
            "periodo_label": periodo_label,
            "total_clientes_cadastro": total_cadastro,
            "clientes_com_compra": len(com_compra),
            "clientes_com_compra_periodo": len(com_compra_periodo),
            "receita_periodo": round(receita_total, 2),
            "custo_periodo": round(custo_total, 2),
            "lucro_periodo": round(lucro_total, 2),
            "margem_media_pct": _pct(receita_total, lucro_total),
            "mudas_vendidas_periodo": mudas_total,
            "ticket_medio_periodo": ticket_medio,
            "receita_pendente": round(pendente_total, 2),
            "clientes_recorrentes": recorrentes,
            "clientes_atencao": atencao,
        },
        "rankings": {
            "por_lucro": ranking(com_compra_periodo, "lucro_periodo", "margem_pct", "margem %"),
            "por_receita": ranking(com_compra_periodo, "receita_periodo", "mudas_periodo", "mudas"),
            "por_fidelidade": ranking(
                com_compra_periodo,
                "vendas_periodo",
                "receita_periodo",
                "R$ faturado",
            ),
            "precisam_atencao": [
                {
                    "id": c["id"],
                    "nome": c["nome"],
                    "tipo": c["tipo"],
                    "cidade": c["cidade"],
                    "estado": c["estado"],
                    "valor": float(c["dias_desde_ultima"] or 0),
                    "valor_secundario": c["vendas_historico"],
                    "label_secundario": "compras históricas",
                }
                for c in atencao_list
            ],
        },
        "por_uf": por_uf,
        "por_cidade": por_cidade,
        "por_tipo": por_tipo,
        "clientes": clientes,
        "mostrar_resumo_financeiro": True,
    }


ROLES_RESUMO_FINANCEIRO_CLIENTES = frozenset({"admin", "gestor", "financeiro"})


def usuario_ve_resumo_financeiro_clientes(perfis) -> bool:
    from app.security.rbac import normalize_role_ids

    return bool(set(normalize_role_ids(perfis)) & ROLES_RESUMO_FINANCEIRO_CLIENTES)


def aplicar_visibilidade_analitico(dados: Dict[str, Any], perfis) -> Dict[str, Any]:
    """Remove totais financeiros agregados para perfis operacionais (ex.: vendedor)."""
    if usuario_ve_resumo_financeiro_clientes(perfis):
        dados["mostrar_resumo_financeiro"] = True
        return dados

    out = {**dados, "mostrar_resumo_financeiro": False}
    resumo = {**out["resumo"]}
    resumo.update(
        {
            "receita_periodo": 0,
            "custo_periodo": 0,
            "lucro_periodo": 0,
            "margem_media_pct": None,
            "ticket_medio_periodo": None,
            "receita_pendente": 0,
        }
    )
    out["resumo"] = resumo

    rankings = dict(out.get("rankings") or {})
    out["rankings"] = rankings

    out["por_uf"] = [
        {**row, "receita": 0} for row in out.get("por_uf") or []
    ]
    out["por_cidade"] = [
        {**row, "receita": 0} for row in out.get("por_cidade") or []
    ]
    out["por_tipo"] = [
        {**row, "receita": 0, "lucro": 0} for row in out.get("por_tipo") or []
    ]

    return out


async def get_comprador(
    db: AsyncSession, comprador_id: int, id_empresa: Optional[int] = None
) -> Optional[Comprador]:
    query = select(Comprador).where(Comprador.id == comprador_id)
    if id_empresa is not None:
        query = query.where(Comprador.id_empresa == id_empresa)
    result = await db.execute(query)
    return result.scalars().first()

async def get_comprador_by_usuario(
    db: AsyncSession, usuario: str, id_empresa: Optional[int] = None
) -> Optional[Comprador]:
    if not usuario:
        return None
    query = select(Comprador).where(Comprador.usuario == usuario)
    if id_empresa is not None:
        query = query.where(Comprador.id_empresa == id_empresa)
    result = await db.execute(query)
    return result.scalars().first()

async def get_comprador_by_cpf_cnpj(
    db: AsyncSession, cpf_cnpj: str, id_empresa: Optional[int] = None
) -> Optional[Comprador]:
    query = select(Comprador).where(Comprador.cpf_cnpj == cpf_cnpj)
    if id_empresa is not None:
        query = query.where(Comprador.id_empresa == id_empresa)
    result = await db.execute(query)
    return result.scalars().first()

async def get_compradores(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    ativo: Optional[bool] = None,
    tipo: Optional[str] = None,
    id_empresa: Optional[int] = None,
) -> List[Comprador]:
    query = select(Comprador)

    if id_empresa is not None:
        query = query.where(Comprador.id_empresa == id_empresa)
    if ativo is not None:
        query = query.where(Comprador.ativo == ativo)
    
    if tipo is not None:
        query = query.where(Comprador.tipo == tipo)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_compradores_with_vendas(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    ativo: Optional[bool] = None,
    tipo: Optional[str] = None,
    id_empresa: Optional[int] = None,
) -> List[Dict[str, Any]]:
    query = select(
        Comprador,
        func.count(Venda.id).label("total_vendas"),
        func.sum(Venda.valor_total).label("valor_total_compras")
    ).outerjoin(
        Venda, Comprador.id == Venda.id_comprador
    )
    
    if id_empresa is not None:
        query = query.where(Comprador.id_empresa == id_empresa)
    if ativo is not None:
        query = query.where(Comprador.ativo == ativo)
    
    if tipo is not None:
        query = query.where(Comprador.tipo == tipo)
    
    query = query.group_by(
        Comprador.id
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    compradores_with_vendas = []
    for row in result:
        comprador_dict = row[0].__dict__
        comprador_dict["total_vendas"] = row[1] or 0
        comprador_dict["valor_total_compras"] = float(row[2] or 0)
        
        # Remover senha e _sa_instance_state
        if "senha" in comprador_dict:
            del comprador_dict["senha"]
        if "_sa_instance_state" in comprador_dict:
            del comprador_dict["_sa_instance_state"]
        
        compradores_with_vendas.append(comprador_dict)
    
    return compradores_with_vendas

async def create_comprador(
    db: AsyncSession, comprador: CompradorCreate, id_empresa: Optional[int] = None
) -> Comprador:
    comprador_dict = comprador.dict()
    if id_empresa is not None:
        comprador_dict["id_empresa"] = id_empresa
    
    # Hash da senha se ela for fornecida
    if comprador_dict.get("senha"):
        senha_hash = gerar_senha_hash(comprador_dict.pop("senha"))
        comprador_dict["senha"] = senha_hash
    
    db_comprador = Comprador(**comprador_dict)
    db.add(db_comprador)
    await db.commit()
    await db.refresh(db_comprador)
    return db_comprador

async def update_comprador(
    db: AsyncSession, comprador_id: int, comprador_update: CompradorUpdate
) -> Optional[Comprador]:
    db_comprador = await get_comprador(db, comprador_id)
    if not db_comprador:
        return None
    
    update_data = comprador_update.dict(exclude_unset=True)
    
    # Hash da senha se ela for atualizada
    if "senha" in update_data and update_data["senha"]:
        update_data["senha"] = gerar_senha_hash(update_data["senha"])
    
    for field, value in update_data.items():
        setattr(db_comprador, field, value)
    
    await db.commit()
    await db.refresh(db_comprador)
    return db_comprador

async def delete_comprador(db: AsyncSession, comprador_id: int) -> Optional[Comprador]:
    db_comprador = await get_comprador(db, comprador_id)
    if not db_comprador:
        return None
    
    # Verificar se há vendas para este comprador
    query = select(func.count(Venda.id)).where(Venda.id_comprador == comprador_id)
    result = await db.execute(query)
    count = result.scalar_one()
    
    if count > 0:
        # Se houver vendas, apenas desativa o comprador
        db_comprador.ativo = False
        await db.commit()
        await db.refresh(db_comprador)
        return db_comprador
    else:
        # Se não houver vendas, remove o comprador
        await db.delete(db_comprador)
        await db.commit()
        return db_comprador