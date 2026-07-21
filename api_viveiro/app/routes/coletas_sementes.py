from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.security.rbac import require_permission
from app.security.scope_context import ScopeContext, get_scope_context
from app.crud import arvores_matriz as crud_arvores
from app.crud import coletas_sementes as crud
from app.database import get_db
from app.models.arvores_matriz import ArvoreMatriz
from app.schemas.coletas_sementes import (
    ColetaSementesCreate,
    ColetaSementesOut,
    ColetaSementesUpdate,
    CustoCampoReferenciaOut,
)
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()


async def _filtrar_coletas_viveiro(db: AsyncSession, coletas: List[dict], scope: ScopeContext) -> List[dict]:
    if not coletas:
        return []
    ids_arvore = {c["id_arvore_matriz"] for c in coletas}
    result = await db.execute(
        select(ArvoreMatriz.id).where(
            ArvoreMatriz.id.in_(ids_arvore),
            ArvoreMatriz.id_viveiro == scope.viveiro.id,
        )
    )
    ids_viveiro = set(result.scalars().all())
    return [c for c in coletas if c["id_arvore_matriz"] in ids_viveiro]


@router.get("/", response_model=List[ColetaSementesOut])
async def listar_coletas(
    skip: int = 0,
    limit: int = 2000,
    id_arvore_matriz: Optional[int] = None,
    id_especie: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    if id_arvore_matriz is not None:
        arvore = await crud_arvores.get_arvore_matriz(
            db, id_arvore_matriz, ctx=scope.viveiro
        )
        if not arvore:
            return []
    coletas = await crud.get_coletas(
        db,
        skip=skip,
        limit=limit,
        id_arvore_matriz=id_arvore_matriz,
        id_especie=id_especie,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    return await _filtrar_coletas_viveiro(db, coletas, scope)


@router.get("/custo-campo-referencia", response_model=CustoCampoReferenciaOut)
async def custo_campo_referencia(
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    return await crud.get_custo_campo_referencia(db, id_empresa=scope.tenant.id)


@router.get("/{coleta_id}", response_model=ColetaSementesOut)
async def obter_coleta(
    coleta_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    coleta = await crud.get_coleta_out(db, coleta_id)
    if not coleta:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    arvore = await crud_arvores.get_arvore_matriz(
        db, coleta["id_arvore_matriz"], ctx=scope.viveiro
    )
    if not arvore:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    return coleta


@router.post("/", response_model=ColetaSementesOut, status_code=201)
async def criar_coleta(
    payload: ColetaSementesCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.create")),
):
    arvore = await crud_arvores.get_arvore_matriz(
        db, payload.id_arvore_matriz, ctx=scope.viveiro
    )
    if not arvore:
        raise HTTPException(status_code=404, detail="Árvore matriz não encontrada")
    try:
        return await crud.create_coleta(db, payload, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{coleta_id}", response_model=ColetaSementesOut)
async def atualizar_coleta(
    coleta_id: int,
    payload: ColetaSementesUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.edit")),
):
    existente = await crud.get_coleta(db, coleta_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    await crud_arvores.get_arvore_matriz(
        db, existente.id_arvore_matriz, ctx=scope.viveiro
    )
    coleta = await crud.update_coleta(db, coleta_id, payload)
    if not coleta:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    return coleta


@router.delete("/{coleta_id}", response_model=ColetaSementesOut)
async def excluir_coleta(
    coleta_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.delete")),
):
    existente = await crud.get_coleta(db, coleta_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    await crud_arvores.get_arvore_matriz(
        db, existente.id_arvore_matriz, ctx=scope.viveiro
    )
    coleta = await crud.delete_coleta(db, coleta_id)
    if not coleta:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    return coleta
