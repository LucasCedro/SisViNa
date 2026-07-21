from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.security.rbac import require_permission
from app.security.scope_context import ScopeContext, get_scope_context
from app.crud import lotes_sementes as crud
from app.database import get_db
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.lotes_sementes import (
    LoteSementesCreate,
    LoteSementesOut,
    LoteSementesUpdate,
    LoteSementesEntradaArmazem,
)

router = APIRouter()


@router.get("/", response_model=List[LoteSementesOut])
async def listar_lotes(
    skip: int = 0,
    limit: int = 2000,
    id_arvore_matriz: Optional[int] = None,
    id_coleta_sementes: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    return await crud.get_lotes(
        db,
        skip=skip,
        limit=limit,
        id_arvore_matriz=id_arvore_matriz,
        id_coleta_sementes=id_coleta_sementes,
        status=status,
        id_viveiro=scope.viveiro.id,
    )


@router.get("/{lote_id}", response_model=LoteSementesOut)
async def obter_lote(
    lote_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    lote = await crud.get_lote(db, lote_id, ctx=scope.viveiro)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    from app.crud.lotes_sementes import _para_resposta, _ultimo_teste_germinacao

    ultimo = await _ultimo_teste_germinacao(db, lote_id)
    return _para_resposta(lote, ultimo)


@router.post("/entrada-armazem", response_model=LoteSementesOut, status_code=201)
async def entrada_armazem(
    payload: LoteSementesEntradaArmazem,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.create")),
):
    try:
        return await crud.criar_lote_armazem(db, payload, id_viveiro=scope.viveiro.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/", response_model=LoteSementesOut, status_code=201)
async def criar_lote(
    payload: LoteSementesCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.create")),
):
    try:
        return await crud.create_lote(db, payload, id_viveiro=scope.viveiro.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{lote_id}", response_model=LoteSementesOut)
async def atualizar_lote(
    lote_id: int,
    payload: LoteSementesUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.edit")),
):
    existente = await crud.get_lote(db, lote_id, ctx=scope.viveiro)
    if not existente:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    lote = await crud.update_lote(db, lote_id, payload)
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return lote
