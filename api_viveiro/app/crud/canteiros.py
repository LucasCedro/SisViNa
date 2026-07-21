# app/crud/canteiros.py
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.canteiros import Canteiro
from app.models.plantas import Planta
from app.schemas.canteiros import CanteiroCreate, CanteiroUpdate
from app.security.viveiro_context import ViveiroContext, assert_record_belongs_to_viveiro

async def get_canteiro(
    db: AsyncSession, canteiro_id: int, ctx: Optional[ViveiroContext] = None
) -> Optional[Canteiro]:
    result = await db.execute(select(Canteiro).where(Canteiro.id == canteiro_id))
    row = result.scalars().first()
    if row and ctx is not None:
        assert_record_belongs_to_viveiro(row.id_viveiro, ctx, "canteiro")
    return row

async def get_canteiro_by_nome(
    db: AsyncSession, nome: str, id_viveiro: Optional[int] = None
) -> Optional[Canteiro]:
    query = select(Canteiro).where(Canteiro.nome == nome)
    if id_viveiro is not None:
        query = query.where(Canteiro.id_viveiro == id_viveiro)
    result = await db.execute(query)
    return result.scalars().first()

async def get_canteiros(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    tipo_local: Optional[str] = None,
    id_viveiro: Optional[int] = None,
) -> List[Canteiro]:
    query = select(Canteiro)

    if id_viveiro is not None:
        query = query.where(Canteiro.id_viveiro == id_viveiro)
    if ativo is not None:
        query = query.where(Canteiro.ativo == ativo)
    if tipo_local is not None:
        query = query.where(Canteiro.tipo_local == tipo_local)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_canteiros_with_ocupacao(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    id_viveiro: Optional[int] = None,
) -> List[Dict[str, Any]]:
    query = select(
        Canteiro,
        func.count(Planta.id).filter(
            Planta.status.notin_(['VENDIDA', 'MORTA'])
        ).label("total_plantas"),
        func.count(Planta.id).filter(
            Planta.status == 'SEMENTE'
        ).label("total_sementes"),
        func.count(Planta.id).filter(
            Planta.status == 'MUDA'
        ).label("total_mudas"),
        func.count(Planta.id).filter(
            Planta.status == 'JOVEM'
        ).label("total_jovens"),
        func.count(Planta.id).filter(
            Planta.status == 'ADULTA'
        ).label("total_adultas")
    ).outerjoin(
        Planta, Canteiro.id == Planta.id_canteiro
    )
    
    if id_viveiro is not None:
        query = query.where(Canteiro.id_viveiro == id_viveiro)
    if ativo is not None:
        query = query.where(Canteiro.ativo == ativo)

    query = query.group_by(
        Canteiro.id
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    canteiros_with_ocupacao = []
    for row in result:
        canteiro_dict = row[0].__dict__
        canteiro_dict["total_plantas"] = row[1] or 0
        canteiro_dict["total_sementes"] = row[2] or 0
        canteiro_dict["total_mudas"] = row[3] or 0
        canteiro_dict["total_jovens"] = row[4] or 0
        canteiro_dict["total_adultas"] = row[5] or 0
        
        # Calcular percentual de ocupação baseado na área total (se disponível)
        if canteiro_dict.get("area_total") and float(canteiro_dict["area_total"]) > 0:
            # Considerando uma média de área por planta (simplificação)
            area_media_planta = 0.25  # 0.25 m² por planta em média
            area_ocupada = canteiro_dict["total_plantas"] * area_media_planta
            canteiro_dict["percentual_ocupacao"] = min(100, (area_ocupada / float(canteiro_dict["area_total"])) * 100)
        else:
            canteiro_dict["percentual_ocupacao"] = 0
        
        # Remover _sa_instance_state
        if "_sa_instance_state" in canteiro_dict:
            del canteiro_dict["_sa_instance_state"]
        
        canteiros_with_ocupacao.append(canteiro_dict)
    
    return canteiros_with_ocupacao

async def create_canteiro(
    db: AsyncSession, canteiro: CanteiroCreate, id_viveiro: Optional[int] = None
) -> Canteiro:
    data = canteiro.dict()
    if id_viveiro is not None:
        data["id_viveiro"] = id_viveiro
    db_canteiro = Canteiro(**data)
    db.add(db_canteiro)
    await db.commit()
    await db.refresh(db_canteiro)
    return db_canteiro

async def update_canteiro(
    db: AsyncSession, canteiro_id: int, canteiro_update: CanteiroUpdate
) -> Optional[Canteiro]:
    db_canteiro = await get_canteiro(db, canteiro_id)
    if not db_canteiro:
        return None
    
    update_data = canteiro_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_canteiro, field, value)
    
    await db.commit()
    await db.refresh(db_canteiro)
    return db_canteiro

async def count_plantas_ativas_no_canteiro(db: AsyncSession, canteiro_id: int) -> int:
    query = select(func.count(Planta.id)).where(
        Planta.id_canteiro == canteiro_id,
        Planta.status.notin_(["VENDIDA", "MORTA"]),
    )
    result = await db.execute(query)
    return int(result.scalar_one() or 0)


async def delete_canteiro(db: AsyncSession, canteiro_id: int) -> Optional[Canteiro]:
    db_canteiro = await get_canteiro(db, canteiro_id)
    if not db_canteiro:
        return None

    count = await count_plantas_ativas_no_canteiro(db, canteiro_id)
    if count > 0:
        return None

    await db.delete(db_canteiro)
    await db.commit()
    return db_canteiro