# app/crud/plantas.py
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.plantas import Planta
from app.models.especies import Especie
from app.models.canteiros import Canteiro
from app.schemas.plantas import PlantaCreate, PlantaUpdate
import uuid

async def get_planta(db: AsyncSession, planta_id: int) -> Optional[Planta]:
    result = await db.execute(select(Planta).where(Planta.id == planta_id))
    return result.scalars().first()

async def get_planta_by_codigo(db: AsyncSession, codigo_rastreio: str) -> Optional[Planta]:
    result = await db.execute(select(Planta).where(Planta.codigo_rastreio == codigo_rastreio))
    return result.scalars().first()

async def get_plantas(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    id_especie: Optional[int] = None,
    id_canteiro: Optional[int] = None,
    status: Optional[str] = None
) -> List[Planta]:
    query = select(Planta)
    
    # Adicionar filtros se fornecidos
    if id_especie is not None:
        query = query.where(Planta.id_especie == id_especie)
    
    if id_canteiro is not None:
        query = query.where(Planta.id_canteiro == id_canteiro)
    
    if status is not None:
        query = query.where(Planta.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_plantas_with_relations(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    id_especie: Optional[int] = None,
    id_canteiro: Optional[int] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = select(
        Planta, 
        Especie.nome_cientifico.label("especie_nome"),
        Canteiro.nome.label("nome_canteiro")
    ).join(
        Especie, Planta.id_especie == Especie.id
    ).outerjoin(
        Canteiro, Planta.id_canteiro == Canteiro.id
    )
    
    # Adicionar filtros se fornecidos
    if id_especie is not None:
        query = query.where(Planta.id_especie == id_especie)
    
    if id_canteiro is not None:
        query = query.where(Planta.id_canteiro == id_canteiro)
    
    if status is not None:
        query = query.where(Planta.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    
    plantas_with_relations = []
    for row in result:
        planta_dict = row[0].__dict__
        planta_dict["especie_nome"] = row[1]
        planta_dict["nome_canteiro"] = row[2]
        
        if "_sa_instance_state" in planta_dict:
            del planta_dict["_sa_instance_state"]
        
        plantas_with_relations.append(planta_dict)
    
    return plantas_with_relations

async def create_planta(db: AsyncSession, planta: PlantaCreate) -> Planta:
    # Gerar código de rastreio se não fornecido
    if not planta.codigo_rastreio:
        planta_dict = planta.dict()
        planta_dict["codigo_rastreio"] = f"PL-{uuid.uuid4().hex[:8].upper()}"
    else:
        planta_dict = planta.dict()
    
    db_planta = Planta(**planta_dict)
    db.add(db_planta)
    await db.commit()
    await db.refresh(db_planta)
    return db_planta

async def create_plantas_bulk(db: AsyncSession, planta_base: PlantaCreate, quantidade: int) -> List[Planta]:
    """Cria múltiplas plantas de uma mesma espécie de uma vez"""
    plantas = []
    
    planta_dict = planta_base.dict()
    for _ in range(quantidade):
        novo_planta_dict = planta_dict.copy()
        novo_planta_dict["codigo_rastreio"] = f"PL-{uuid.uuid4().hex[:8].upper()}"
        db_planta = Planta(**novo_planta_dict)
        db.add(db_planta)
        plantas.append(db_planta)
    
    await db.commit()
    
    for planta in plantas:
        await db.refresh(planta)
    
    return plantas

async def update_planta(
    db: AsyncSession, planta_id: int, planta_update: PlantaUpdate
) -> Optional[Planta]:
    db_planta = await get_planta(db, planta_id)
    if not db_planta:
        return None
    
    update_data = planta_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_planta, field, value)
    
    await db.commit()
    await db.refresh(db_planta)
    return db_planta

async def delete_planta(db: AsyncSession, planta_id: int) -> Optional[Planta]:
    db_planta = await get_planta(db, planta_id)
    if not db_planta:
        return None
    
    await db.delete(db_planta)
    await db.commit()
    return db_planta