# app/routes/plantas.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.plantas import Planta, PlantaCreate, PlantaUpdate, PlantaWithEspecie
from app.crud import plantas as crud_plantas
from app.auth.jwt import get_current_user
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

@router.get("/", response_model=List[Planta])
async def read_plantas(
    skip: int = 0,
    limit: int = 100,
    id_especie: Optional[int] = None,
    id_canteiro: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera todas as plantas com opção de filtrar por espécie, canteiro e status.
    """
    plantas = await crud_plantas.get_plantas(
        db, 
        skip=skip, 
        limit=limit, 
        id_especie=id_especie,
        id_canteiro=id_canteiro,
        status=status
    )
    return plantas

@router.get("/with-relations", response_model=List[PlantaWithEspecie])
async def read_plantas_with_relations(
    skip: int = 0,
    limit: int = 100,
    id_especie: Optional[int] = None,
    id_canteiro: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera todas as plantas com informações de espécie e canteiro.
    """
    plantas = await crud_plantas.get_plantas_with_relations(
        db, 
        skip=skip, 
        limit=limit, 
        id_especie=id_especie,
        id_canteiro=id_canteiro,
        status=status
    )
    return plantas

@router.get("/{planta_id}", response_model=Planta)
async def read_planta(
    planta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera uma planta específica pelo ID.
    """
    db_planta = await crud_plantas.get_planta(db, planta_id)
    if db_planta is None:
        raise HTTPException(status_code=404, detail="Planta não encontrada")
    return db_planta

@router.post("/", response_model=Planta)
async def create_planta(
    planta: PlantaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Cria uma nova planta.
    """
    return await crud_plantas.create_planta(db=db, planta=planta)

@router.post("/bulk", response_model=List[Planta])
async def create_plantas_bulk(
    planta: PlantaCreate,
    quantidade: int = Query(..., description="Quantidade de plantas a serem criadas", gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Cria múltiplas plantas de uma mesma espécie de uma vez.
    """
    if quantidade > 500:
        raise HTTPException(
            status_code=400, 
            detail="Número máximo de plantas por operação é 500"
        )
    
    return await crud_plantas.create_plantas_bulk(db=db, planta_base=planta, quantidade=quantidade)

@router.put("/{planta_id}", response_model=Planta)
async def update_planta(
    planta_id: int,
    planta: PlantaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Atualiza uma planta existente.
    """
    db_planta = await crud_plantas.update_planta(db, planta_id, planta)
    if db_planta is None:
        raise HTTPException(status_code=404, detail="Planta não encontrada")
    return db_planta

@router.delete("/{planta_id}", response_model=Planta)
async def delete_planta(
    planta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Deleta uma planta.
    """
    db_planta = await crud_plantas.delete_planta(db, planta_id)
    if db_planta is None:
        raise HTTPException(status_code=404, detail="Planta não encontrada")
    return db_planta