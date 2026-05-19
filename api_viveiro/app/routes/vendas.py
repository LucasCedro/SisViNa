# app/routes/vendas.py
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.vendas import (
    Venda, VendaCreate, VendaUpdate, VendaDetalhe,
    ItemVenda, ItemVendaUpdate, ItemVendaDetalhe
)
from app.crud import vendas as crud_vendas
from app.auth.jwt import get_current_user
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

@router.get("/", response_model=List[Venda])
async def read_vendas(
    skip: int = 0,
    limit: int = 100,
    id_comprador: Optional[int] = None,
    id_funcionario: Optional[int] = None,
    status: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera todas as vendas com opção de filtrar.
    """
    vendas = await crud_vendas.get_vendas(
        db, 
        skip=skip, 
        limit=limit, 
        id_comprador=id_comprador,
        id_funcionario=id_funcionario,
        status=status,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    return vendas

@router.get("/{venda_id}", response_model=VendaDetalhe)
async def read_venda(
    venda_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera uma venda específica pelo ID com detalhes.
    """
    db_venda = await crud_vendas.get_venda_detalhe(db, venda_id)
    if db_venda is None:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return db_venda

@router.post("/", response_model=VendaDetalhe)
async def create_venda(
    venda: VendaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Cria uma nova venda com seus itens.
    """
    try:
        return await crud_vendas.create_venda(db=db, venda=venda)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{venda_id}", response_model=Venda)
async def update_venda(
    venda_id: int,
    venda: VendaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Atualiza uma venda existente (apenas dados gerais, não itens).
    """
    db_venda = await crud_vendas.update_venda(db, venda_id, venda)
    if db_venda is None:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return db_venda

@router.delete("/{venda_id}", response_model=VendaDetalhe)
async def delete_venda(
    venda_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Deleta uma venda e seus itens, restaurando o status das plantas.
    """
    db_venda = await crud_vendas.delete_venda(db, venda_id)
    if db_venda is None:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return db_venda

# Rotas para ItemVenda
@router.get("/itens/{item_id}", response_model=ItemVendaDetalhe)
async def read_item_venda(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Recupera um item de venda específico pelo ID.
    """
    db_item = await crud_vendas.get_item_venda_detalhe(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item de venda não encontrado")
    return db_item

@router.put("/itens/{item_id}", response_model=ItemVenda)
async def update_item_venda(
    item_id: int,
    item: ItemVendaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Atualiza um item de venda existente.
    """
    db_item = await crud_vendas.update_item_venda(db, item_id, item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item de venda não encontrado")
    return db_item

@router.delete("/itens/{item_id}", response_model=ItemVendaDetalhe)
async def delete_item_venda(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user)
):
    """
    Deleta um item de venda, restaurando o status da planta.
    """
    db_item = await crud_vendas.delete_item_venda(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item de venda não encontrado")
    return db_item