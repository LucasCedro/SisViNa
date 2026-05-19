# app/routes/canteiros.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.canteiros import Canteiro, CanteiroCreate, CanteiroUpdate, CanteiroWithOcupacao
from app.crud import canteiros as crud_canteiros
from app.auth.jwt import get_current_user
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

@router.get("/", response_model=List[Canteiro])
async def read_canteiros(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera todos os canteiros.
    """
    canteiros = await crud_canteiros.get_canteiros(db, skip=skip, limit=limit, ativo=ativo)
    return canteiros

@router.get("/with-ocupacao", response_model=List[CanteiroWithOcupacao])
async def read_canteiros_with_ocupacao(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera todos os canteiros com informações de ocupação.
    """
    canteiros = await crud_canteiros.get_canteiros_with_ocupacao(
        db, skip=skip, limit=limit, ativo=ativo
    )
    return canteiros

@router.get("/{canteiro_id}", response_model=Canteiro)
async def read_canteiro(
    canteiro_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera um canteiro específico pelo ID.
    """
    db_canteiro = await crud_canteiros.get_canteiro(db, canteiro_id)
    if db_canteiro is None:
        raise HTTPException(status_code=404, detail="Canteiro não encontrado")
    return db_canteiro

@router.post("/", response_model=Canteiro)
async def create_canteiro(
    canteiro: CanteiroCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Cria um novo canteiro.
    """
    db_canteiro = await crud_canteiros.get_canteiro_by_nome(db, nome=canteiro.nome)
    if db_canteiro:
        raise HTTPException(
            status_code=400,
            detail="Canteiro com este nome já registrado"
        )
    return await crud_canteiros.create_canteiro(db=db, canteiro=canteiro)

@router.put("/{canteiro_id}", response_model=Canteiro)
async def update_canteiro(
    canteiro_id: int,
    canteiro: CanteiroUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Atualiza um canteiro existente.
    """
    # Verificar se o nome já existe
    if canteiro.nome:
        existing_canteiro = await crud_canteiros.get_canteiro_by_nome(db, canteiro.nome)
        if existing_canteiro and existing_canteiro.id != canteiro_id:
            raise HTTPException(
                status_code=400,
                detail="Canteiro com este nome já registrado"
            )
    
    db_canteiro = await crud_canteiros.update_canteiro(db, canteiro_id, canteiro)
    if db_canteiro is None:
        raise HTTPException(status_code=404, detail="Canteiro não encontrado")
    return db_canteiro

@router.delete("/{canteiro_id}", response_model=Canteiro)
async def delete_canteiro(
    canteiro_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Deleta um canteiro. Se houver plantas associadas, apenas desativa o canteiro.
    """
    db_canteiro = await crud_canteiros.delete_canteiro(db, canteiro_id)
    if db_canteiro is None:
        raise HTTPException(status_code=404, detail="Canteiro não encontrado")
    return db_canteiro