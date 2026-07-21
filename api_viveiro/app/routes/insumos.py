# app/routes/insumos.py
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.insumos import (
    Insumo,
    InsumoCreate,
    InsumoUpdate,
    InsumoComUsos,
    InsumoMovimentacaoCreate,
    InsumoMovimentacaoOut,
)
from app.crud import insumos as crud_insumos
from app.security.rbac import require_permission
from app.security.scope_context import ScopeContext, get_scope_context
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
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    return await crud_insumos.get_insumos(
        db,
        skip=skip,
        limit=limit,
        tipo=tipo,
        fornecedor=fornecedor,
        estoque_minimo=estoque_minimo,
        id_empresa=scope.tenant.id,
    )


@router.get("/com-usos", response_model=List[InsumoComUsos])
async def read_insumos_com_usos(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    return await crud_insumos.get_insumos_com_usos(
        db, skip=skip, limit=limit, tipo=tipo, id_empresa=scope.tenant.id
    )


@router.get("/tipos", response_model=List[str])
async def get_tipos_insumos(
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    return await crud_insumos.get_tipos_insumos(db, id_empresa=scope.tenant.id)


@router.get("/fornecedores", response_model=List[str])
async def get_fornecedores(
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    return await crud_insumos.get_fornecedores(db, id_empresa=scope.tenant.id)


@router.get("/{insumo_id}", response_model=Insumo)
async def read_insumo(
    insumo_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    db_insumo = await crud_insumos.get_insumo(db, insumo_id, id_empresa=scope.tenant.id)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    return db_insumo


@router.get("/{insumo_id}/movimentacoes", response_model=List[InsumoMovimentacaoOut])
async def listar_movimentacoes_insumo(
    insumo_id: int,
    limit: int = 60,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    db_insumo = await crud_insumos.get_insumo(db, insumo_id, id_empresa=scope.tenant.id)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    return await crud_insumos.listar_movimentacoes(db, insumo_id, limit=limit)


@router.post("/", response_model=Insumo)
async def create_insumo(
    insumo: InsumoCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.edit")),
):
    db_insumo = await crud_insumos.get_insumo_by_nome(
        db, nome=insumo.nome, id_empresa=scope.tenant.id
    )
    if db_insumo:
        raise HTTPException(status_code=400, detail="Insumo com este nome já registrado")
    return await crud_insumos.create_insumo(db=db, insumo=insumo, id_empresa=scope.tenant.id)


@router.put("/{insumo_id}", response_model=Insumo)
async def update_insumo(
    insumo_id: int,
    insumo: InsumoUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.edit")),
):
    existing = await crud_insumos.get_insumo(db, insumo_id, id_empresa=scope.tenant.id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    if insumo.nome:
        existing_insumo = await crud_insumos.get_insumo_by_nome(
            db, insumo.nome, id_empresa=scope.tenant.id
        )
        if existing_insumo and existing_insumo.id != insumo_id:
            raise HTTPException(status_code=400, detail="Insumo com este nome já registrado")

    db_insumo = await crud_insumos.update_insumo(db, insumo_id, insumo, id_empresa=scope.tenant.id)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    return db_insumo


@router.delete("/{insumo_id}", response_model=Insumo)
async def delete_insumo(
    insumo_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.edit")),
):
    existing = await crud_insumos.get_insumo(db, insumo_id, id_empresa=scope.tenant.id)
    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Insumo não encontrado ou possui usos registrados",
        )
    db_insumo = await crud_insumos.delete_insumo(db, insumo_id, id_empresa=scope.tenant.id)
    if db_insumo is None:
        raise HTTPException(
            status_code=404,
            detail="Insumo não encontrado ou possui usos registrados",
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
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.edit")),
):
    existing = await crud_insumos.get_insumo(db, insumo_id, id_empresa=scope.tenant.id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    try:
        db_insumo = await crud_insumos.atualizar_estoque(
            db,
            insumo_id,
            estoque_data.quantidade,
            estoque_data.data_compra,
            id_empresa=scope.tenant.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    if float(db_insumo.quantidade_estoque or 0) < 0:
        raise HTTPException(
            status_code=400,
            detail="Operação resultaria em estoque negativo.",
        )
    return db_insumo


@router.post("/{insumo_id}/movimentacoes", response_model=InsumoMovimentacaoOut)
async def registrar_movimentacao_insumo(
    insumo_id: int,
    payload: InsumoMovimentacaoCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("estoques.edit")),
):
    existing = await crud_insumos.get_insumo(db, insumo_id, id_empresa=scope.tenant.id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    try:
        mov = await crud_insumos.registrar_movimentacao(
            db, insumo_id, payload, id_empresa=scope.tenant.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if mov is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    return mov
