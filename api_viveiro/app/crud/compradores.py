# app/crud/compradores.py
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.compradores import Comprador
from app.models.vendas import Venda
from app.schemas.compradores import CompradorCreate, CompradorUpdate
from app.auth.utils import gerar_senha_hash

async def get_comprador(db: AsyncSession, comprador_id: int) -> Optional[Comprador]:
    result = await db.execute(select(Comprador).where(Comprador.id == comprador_id))
    return result.scalars().first()

async def get_comprador_by_usuario(db: AsyncSession, usuario: str) -> Optional[Comprador]:
    if not usuario:
        return None
    result = await db.execute(select(Comprador).where(Comprador.usuario == usuario))
    return result.scalars().first()

async def get_comprador_by_cpf_cnpj(db: AsyncSession, cpf_cnpj: str) -> Optional[Comprador]:
    result = await db.execute(select(Comprador).where(Comprador.cpf_cnpj == cpf_cnpj))
    return result.scalars().first()

async def get_compradores(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    ativo: Optional[bool] = None,
    tipo: Optional[str] = None
) -> List[Comprador]:
    query = select(Comprador)
    
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
    tipo: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = select(
        Comprador,
        func.count(Venda.id).label("total_vendas"),
        func.sum(Venda.valor_total).label("valor_total_compras")
    ).outerjoin(
        Venda, Comprador.id == Venda.id_comprador
    )
    
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

async def create_comprador(db: AsyncSession, comprador: CompradorCreate) -> Comprador:
    comprador_dict = comprador.dict()
    
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