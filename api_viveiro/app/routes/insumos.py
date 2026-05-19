# app/routes/insumos.py
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.schemas.insumos import Insumo, InsumoCreate, InsumoUpdate, InsumoComUsos
from app.crud import insumos as crud_insumos
from app.auth.jwt import get_current_user
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

@router.get("/", response_model=List[Insumo])
async def read_insumos(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    fornecedor: Optional[str] = None,
    estoque_minimo: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera todos os insumos com filtros opcionais.
    """
    insumos = await crud_insumos.get_insumos(
        db, 
        skip=skip, 
        limit=limit, 
        tipo=tipo,
        fornecedor=fornecedor,
        estoque_minimo=estoque_minimo
    )
    return insumos

@router.get("/com-usos", response_model=List[InsumoComUsos])
async def read_insumos_com_usos(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera todos os insumos com informações de uso.
    """
    insumos = await crud_insumos.get_insumos_com_usos(
        db, skip=skip, limit=limit, tipo=tipo
    )
    return insumos

@router.get("/{insumo_id}", response_model=Insumo)
async def read_insumo(
    insumo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera um insumo específico pelo ID.
    """
    db_insumo = await crud_insumos.get_insumo(db, insumo_id)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    return db_insumo

@router.post("/", response_model=Insumo)
async def create_insumo(
    insumo: InsumoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Cria um novo insumo.
    """
    # Verificar se já existe insumo com o mesmo nome
    db_insumo = await crud_insumos.get_insumo_by_nome(db, nome=insumo.nome)
    if db_insumo:
        raise HTTPException(
            status_code=400,
            detail="Insumo com este nome já registrado"
        )
    return await crud_insumos.create_insumo(db=db, insumo=insumo)

@router.put("/{insumo_id}", response_model=Insumo)
async def update_insumo(
    insumo_id: int,
    insumo: InsumoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Atualiza um insumo existente.
    """
    # Verificar se o nome já existe
    if insumo.nome:
        existing_insumo = await crud_insumos.get_insumo_by_nome(db, insumo.nome)
        if existing_insumo and existing_insumo.id != insumo_id:
            raise HTTPException(
                status_code=400,
                detail="Insumo com este nome já registrado"
            )
    
    db_insumo = await crud_insumos.update_insumo(db, insumo_id, insumo)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    return db_insumo

@router.delete("/{insumo_id}", response_model=Insumo)
async def delete_insumo(
    insumo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Deleta um insumo. Não é possível deletar se houver usos registrados.
    """
    db_insumo = await crud_insumos.delete_insumo(db, insumo_id)
    if db_insumo is None:
        raise HTTPException(
            status_code=404, 
            detail="Insumo não encontrado ou possui usos registrados"
        )
    return db_insumo

class EstoqueUpdate(BaseModel):
    quantidade: float
    data_compra: Optional[date] = None


@router.post("/{insumo_id}/estoque", response_model=Insumo)
async def atualizar_estoque_insumo(
    insumo_id: int,
    estoque_data: EstoqueUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Atualiza o estoque de um insumo (adição ou remoção).
    """
    db_insumo = await crud_insumos.atualizar_estoque(
        db, 
        insumo_id, 
        estoque_data.quantidade, 
        estoque_data.data_compra
    )
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    
    # Verificar se o estoque ficou negativo
    if db_insumo.quantidade_estoque < 0:
        await crud_insumos.update_insumo(
            db, 
            insumo_id, 
            InsumoUpdate(quantidade_estoque=0)
        )
        raise HTTPException(
            status_code=400,
            detail=f"Operação resultaria em estoque negativo. Estoque zerado. Estoque atual: 0"
        )
    
    return db_insumo

@router.get("/tipos", response_model=List[str])
async def get_tipos_insumos(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Retorna a lista de tipos de insumos cadastrados.
    """
    query = "SELECT DISTINCT tipo FROM insumos ORDER BY tipo"
    result = await db.execute(query)
    tipos = [row[0] for row in result]
    return tipos

@router.get("/fornecedores", response_model=List[str])
async def get_fornecedores(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Retorna a lista de fornecedores cadastrados.
    """
    query = "SELECT DISTINCT fornecedor FROM insumos WHERE fornecedor IS NOT NULL ORDER BY fornecedor"
    result = await db.execute(query)
    fornecedores = [row[0] for row in result]
    return fornecedores