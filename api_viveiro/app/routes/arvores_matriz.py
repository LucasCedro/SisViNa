from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import arvores_matriz as crud
from app.database import get_db
from app.schemas.arvores_matriz import ArvoreMatrizCreate, ArvoreMatrizOut, ArvoreMatrizUpdate
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()


@router.get("/", response_model=List[ArvoreMatrizOut])
async def listar_arvores_matriz(
    skip: int = 0,
    limit: int = 500,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    return await crud.get_arvores_matriz(db, skip=skip, limit=limit)


@router.get("/{arvore_id}", response_model=ArvoreMatrizOut)
async def obter_arvore_matriz(
    arvore_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    arvore = await crud.get_arvore_matriz_out(db, arvore_id)
    if not arvore:
        raise HTTPException(status_code=404, detail="Árvore matriz não encontrada")
    return arvore


@router.post("/", response_model=ArvoreMatrizOut, status_code=201)
async def criar_arvore_matriz(
    payload: ArvoreMatrizCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.create")),
):
    return await crud.create_arvore_matriz(db, payload)


@router.put("/{arvore_id}", response_model=ArvoreMatrizOut)
async def atualizar_arvore_matriz(
    arvore_id: int,
    payload: ArvoreMatrizUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.edit")),
):
    arvore = await crud.update_arvore_matriz(db, arvore_id, payload)
    if not arvore:
        raise HTTPException(status_code=404, detail="Árvore matriz não encontrada")
    return arvore


@router.delete("/{arvore_id}", response_model=ArvoreMatrizOut)
async def excluir_arvore_matriz(
    arvore_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.delete")),
):
    arvore = await crud.get_arvore_matriz_out(db, arvore_id)
    if not arvore:
        raise HTTPException(status_code=404, detail="Árvore matriz não encontrada")
    await crud.delete_arvore_matriz(db, arvore_id)
    return arvore
