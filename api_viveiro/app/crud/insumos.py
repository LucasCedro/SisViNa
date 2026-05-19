# app/crud/insumos.py
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.insumos import Insumo
from app.models.atividades import InsumoAtividade
from app.schemas.insumos import InsumoCreate, InsumoUpdate

async def get_insumo(db: AsyncSession, insumo_id: int) -> Optional[Insumo]:
    """
    Obtém um insumo pelo ID
    """
    result = await db.execute(select(Insumo).where(Insumo.id == insumo_id))
    return result.scalars().first()

async def get_insumo_by_nome(db: AsyncSession, nome: str) -> Optional[Insumo]:
    """
    Obtém um insumo pelo nome
    """
    result = await db.execute(select(Insumo).where(Insumo.nome == nome))
    return result.scalars().first()

async def get_insumos(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    tipo: Optional[str] = None,
    fornecedor: Optional[str] = None,
    estoque_minimo: Optional[float] = None
) -> List[Insumo]:
    """
    Obtém lista de insumos com filtros opcionais
    """
    query = select(Insumo)
    
    if tipo:
        query = query.where(Insumo.tipo == tipo)
    
    if fornecedor:
        query = query.where(Insumo.fornecedor == fornecedor)
    
    if estoque_minimo is not None:
        query = query.where(Insumo.quantidade_estoque >= estoque_minimo)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_insumos_com_usos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Obtém insumos com informações de uso
    """
    query = select(
        Insumo,
        func.count(InsumoAtividade.id).label("total_usos"),
        func.sum(InsumoAtividade.quantidade_usada).label("quantidade_total_usada"),
        func.sum(InsumoAtividade.custo_total).label("valor_total_usado")
    ).outerjoin(
        InsumoAtividade, Insumo.id == InsumoAtividade.id_insumo
    )
    
    if tipo:
        query = query.where(Insumo.tipo == tipo)
    
    query = query.group_by(
        Insumo.id
    ).order_by(
        Insumo.nome
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    insumos_com_usos = []
    for row in result:
        insumo, total_usos, quantidade_total_usada, valor_total_usado = row
        
        insumo_dict = insumo.__dict__
        if "_sa_instance_state" in insumo_dict:
            del insumo_dict["_sa_instance_state"]
        
        # Converter Decimal para float
        if "quantidade_estoque" in insumo_dict and insumo_dict["quantidade_estoque"] is not None:
            insumo_dict["quantidade_estoque"] = float(insumo_dict["quantidade_estoque"])
        
        if "preco_unitario" in insumo_dict and insumo_dict["preco_unitario"] is not None:
            insumo_dict["preco_unitario"] = float(insumo_dict["preco_unitario"])
        
        insumos_com_usos.append({
            **insumo_dict,
            "total_usos": total_usos or 0,
            "quantidade_total_usada": float(quantidade_total_usada or 0),
            "valor_total_usado": float(valor_total_usado or 0)
        })
    
    return insumos_com_usos

async def create_insumo(db: AsyncSession, insumo: InsumoCreate) -> Insumo:
    """
    Cria um novo insumo
    """
    db_insumo = Insumo(**insumo.dict())
    db.add(db_insumo)
    await db.commit()
    await db.refresh(db_insumo)
    return db_insumo

async def update_insumo(
    db: AsyncSession, insumo_id: int, insumo_update: InsumoUpdate
) -> Optional[Insumo]:
    """
    Atualiza um insumo existente
    """
    db_insumo = await get_insumo(db, insumo_id)
    if not db_insumo:
        return None
    
    update_data = insumo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_insumo, field, value)
    
    await db.commit()
    await db.refresh(db_insumo)
    return db_insumo

async def delete_insumo(db: AsyncSession, insumo_id: int) -> Optional[Insumo]:
    """
    Deleta um insumo se não estiver em uso
    """
    db_insumo = await get_insumo(db, insumo_id)
    if not db_insumo:
        return None
    
    # Verificar se há usos do insumo
    query = select(func.count(InsumoAtividade.id)).where(InsumoAtividade.id_insumo == insumo_id)
    result = await db.execute(query)
    count = result.scalar_one()
    
    if count > 0:
        return None  # Não pode excluir insumos com usos registrados
    
    await db.delete(db_insumo)
    await db.commit()
    return db_insumo

async def atualizar_estoque(
    db: AsyncSession, insumo_id: int, quantidade: float, data_compra: Optional[date] = None
) -> Optional[Insumo]:
    """
    Atualiza o estoque de um insumo (adição ou subtração)
    """
    db_insumo = await get_insumo(db, insumo_id)
    if not db_insumo:
        return None
    
    # Atualizar estoque
    db_insumo.quantidade_estoque = db_insumo.quantidade_estoque + quantidade
    
    # Se for adição, atualizar data da última compra
    if quantidade > 0 and data_compra:
        db_insumo.data_ultima_compra = data_compra
    
    await db.commit()
    await db.refresh(db_insumo)
    return db_insumo