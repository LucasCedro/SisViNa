from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import coletas_sementes as crud
from app.database import get_db
from app.schemas.coletas_sementes import ColetaSementesCreate, ColetaSementesOut, ColetaSementesUpdate
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()


@router.get("/", response_model=List[ColetaSementesOut])
async def listar_coletas(
    skip: int = 0,
    limit: int = 2000,
    id_arvore_matriz: Optional[int] = None,
    id_especie: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    return await crud.get_coletas(
        db,
        skip=skip,
        limit=limit,
        id_arvore_matriz=id_arvore_matriz,
        id_especie=id_especie,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get("/{coleta_id}", response_model=ColetaSementesOut)
async def obter_coleta(
    coleta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    coleta = await crud.get_coleta_out(db, coleta_id)
    if not coleta:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    return coleta


@router.post("/", response_model=ColetaSementesOut, status_code=201)
async def criar_coleta(
    payload: ColetaSementesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.create")),
):
    try:
        return await crud.create_coleta(db, payload, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{coleta_id}", response_model=ColetaSementesOut)
async def atualizar_coleta(
    coleta_id: int,
    payload: ColetaSementesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.edit")),
):
    coleta = await crud.update_coleta(db, coleta_id, payload)
    if not coleta:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    return coleta


@router.delete("/{coleta_id}", response_model=ColetaSementesOut)
async def excluir_coleta(
    coleta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.delete")),
):
    coleta = await crud.delete_coleta(db, coleta_id)
    if not coleta:
        raise HTTPException(status_code=404, detail="Coleta não encontrada")
    return coleta
