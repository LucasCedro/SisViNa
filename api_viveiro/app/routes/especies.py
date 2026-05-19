# app/routes/especies.py
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.especies import Especie, EspecieCreate, EspecieUpdate, EspecieWithPlantasCount
from app.crud import especies as crud_especies
from app.auth.jwt import get_current_user
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

@router.get("/", response_model=List[Especie])
async def read_especies(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera todas as espécies.
    """
    especies = await crud_especies.get_especies(db, skip=skip, limit=limit)
    return especies

@router.get("/with-plantas-count", response_model=List[EspecieWithPlantasCount])
async def read_especies_with_plantas_count(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera todas as espécies com contagem de plantas.
    """
    especies = await crud_especies.get_especies_with_plantas_count(db, skip=skip, limit=limit)
    return especies

@router.get("/{especie_id}", response_model=Especie)
async def read_especie(
    especie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera uma espécie específica pelo ID.
    """
    db_especie = await crud_especies.get_especie(db, especie_id)
    if db_especie is None:
        raise HTTPException(status_code=404, detail="Espécie não encontrada")
    return db_especie

@router.post("/", response_model=Especie)
async def create_especie(
    especie: EspecieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Cria uma nova espécie.
    """
    db_especie = await crud_especies.get_especie_by_nome(db, nome_cientifico=especie.nome_cientifico)
    if db_especie:
        raise HTTPException(
            status_code=400,
            detail="Espécie com este nome científico já registrada"
        )
    return await crud_especies.create_especie(db=db, especie=especie)

@router.put("/{especie_id}", response_model=Especie)
async def update_especie(
    especie_id: int,
    especie: EspecieUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Atualiza uma espécie existente.
    """
    db_especie = await crud_especies.update_especie(db, especie_id, especie)
    if db_especie is None:
        raise HTTPException(status_code=404, detail="Espécie não encontrada")
    return db_especie

@router.delete("/{especie_id}", response_model=Especie)
async def delete_especie(
    especie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Deleta uma espécie.
    """
    db_especie = await crud_especies.delete_especie(db, especie_id)
    if db_especie is None:
        raise HTTPException(status_code=404, detail="Espécie não encontrada")
    return db_especie