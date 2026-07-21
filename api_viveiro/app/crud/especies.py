# app/crud/especies.py
from typing import List, Optional, Dict, Any
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.especies import Especie
from app.models.especie_biblioteca import EspecieBiblioteca
from app.models.referencia_viveiro import EspecieFichaEmbrapa
from app.models.plantas import Planta
from app.schemas.especies import EspecieCreate, EspecieUpdate
from app.crud.especies_imagens import imagem_capa_biblioteca, total_fotos_biblioteca

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


async def get_especies_biblioteca(
    db: AsyncSession, skip: int = 0, limit: int = 500
) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(Especie, EspecieBiblioteca, EspecieFichaEmbrapa)
        .join(EspecieBiblioteca, EspecieBiblioteca.id_especie == Especie.id)
        .outerjoin(EspecieFichaEmbrapa, EspecieFichaEmbrapa.id_especie == Especie.id)
        .order_by(Especie.nome_popular.asc().nulls_last(), Especie.nome_cientifico.asc())
        .offset(skip)
        .limit(limit)
    )

    itens = []
    for especie, bib, ficha in result.all():
        ficha_out = None
        if ficha:
            ficha_out = {
                "mes_coleta_inicio": ficha.mes_coleta_inicio,
                "mes_coleta_fim": ficha.mes_coleta_fim,
                "armazenamento_tipo": ficha.armazenamento_tipo,
                "profundidade_semeadura_cm_min": float(ficha.profundidade_semeadura_cm_min)
                if ficha.profundidade_semeadura_cm_min is not None
                else None,
                "profundidade_semeadura_cm_max": float(ficha.profundidade_semeadura_cm_max)
                if ficha.profundidade_semeadura_cm_max is not None
                else None,
                "dias_inicio_germinacao": ficha.dias_inicio_germinacao,
                "pct_germinacao_tipico": float(ficha.pct_germinacao_tipico)
                if ficha.pct_germinacao_tipico is not None
                else None,
                "substrato_tipo": ficha.substrato_tipo,
                "conduz_pleno_sol": ficha.conduz_pleno_sol,
                "meses_permanencia_viveiro": ficha.meses_permanencia_viveiro,
                "meses_permanencia_viveiro_max": ficha.meses_permanencia_viveiro_max,
                "fitofisionomia": ficha.fitofisionomia,
            }
        itens.append(
            {
                "id": especie.id,
                "nome_cientifico": especie.nome_cientifico,
                "nome_popular": especie.nome_popular,
                "familia": especie.familia,
                "descricao": especie.descricao,
                "tempo_germinacao": especie.tempo_germinacao,
                "tempo_crescimento": especie.tempo_crescimento,
                "altura_maxima": float(especie.altura_maxima) if especie.altura_maxima is not None else None,
                "resumo_manejo": bib.resumo_manejo if bib else None,
                "imagem_arvore": bib.imagem_arvore if bib else None,
                "imagem_semente": bib.imagem_semente if bib else None,
                "imagem_folha": bib.imagem_folha if bib else None,
                "imagem_capa": imagem_capa_biblioteca(bib),
                "total_fotos": total_fotos_biblioteca(bib),
                "imagens_externas": [],
                "ficha_tecnica": ficha_out,
            }
        )
    return itens

async def get_especies_with_plantas_count(
    db: AsyncSession, skip: int = 0, limit: int = 100, id_viveiro: Optional[int] = None
) -> List[Dict[str, Any]]:
    join_cond = Especie.id == Planta.id_especie
    if id_viveiro is not None:
        join_cond = and_(join_cond, Planta.id_viveiro == id_viveiro)
    query = (
        select(Especie, func.count(Planta.id).label("total_plantas"))
        .outerjoin(Planta, join_cond)
        .group_by(Especie.id)
        .offset(skip)
        .limit(limit)
    )
    
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