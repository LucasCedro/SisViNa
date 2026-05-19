# app/crud/especies.py
from typing import List, Optional, Dict, Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.especies import Especie
from app.models.plantas import Planta
from app.schemas.especies import EspecieCreate, EspecieUpdate

async def get_especie(db: AsyncSession, especie_id: int) -> Optional[Especie]:
    result = await db.execute(select(Especie).where(Especie.id == especie_id))
    return result.scalars().first()

async def get_especie_by_nome(db: AsyncSession, nome_cientifico: str) -> Optional[Especie]:
    result = await db.execute(select(Especie).where(Especie.nome_cientifico == nome_cientifico))
    return result.scalars().first()

async def get_especies(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Especie]:
    result = await db.execute(select(Especie).offset(skip).limit(limit))
    return result.scalars().all()

async def get_especies_with_plantas_count(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    query = select(
        Especie,
        func.count(Planta.id).label("total_plantas")
    ).outerjoin(
        Planta, Especie.id == Planta.id_especie
    ).group_by(
        Especie.id
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    especies_with_count = []
    for row in result:
        especie_dict = row[0].__dict__
        especie_dict["total_plantas"] = row[1]
        # Remover atributos SQLAlchemy
        if "_sa_instance_state" in especie_dict:
            del especie_dict["_sa_instance_state"]
        especies_with_count.append(especie_dict)
    
    return especies_with_count

async def create_especie(db: AsyncSession, especie: EspecieCreate) -> Especie:
    db_especie = Especie(**especie.dict())
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    return db_especie

async def update_especie(
    db: AsyncSession, especie_id: int, especie_update: EspecieUpdate
) -> Optional[Especie]:
    db_especie = await get_especie(db, especie_id)
    if not db_especie:
        return None
    
    update_data = especie_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_especie, field, value)
    
    await db.commit()
    await db.refresh(db_especie)
    return db_especie

async def delete_especie(db: AsyncSession, especie_id: int) -> Optional[Especie]:
    db_especie = await get_especie(db, especie_id)
    if not db_especie:
        return None
    
    await db.delete(db_especie)
    await db.commit()
    return db_especie