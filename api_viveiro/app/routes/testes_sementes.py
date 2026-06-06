from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import testes_sementes as crud
from app.crud.testes_sementes import _para_resposta
from app.database import get_db
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.testes_sementes import TesteSementesCreate, TesteSementesOut, TesteSementesUpdate

router = APIRouter()


@router.get("/", response_model=List[TesteSementesOut])
async def listar_testes(
    skip: int = 0,
    limit: int = 2000,
    id_lote_sementes: Optional[int] = None,
    id_arvore_matriz: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    testes = await crud.get_testes(
        db,
        skip=skip,
        limit=limit,
        id_lote_sementes=id_lote_sementes,
        id_arvore_matriz=id_arvore_matriz,
    )
    return [_para_resposta(t) for t in testes]


@router.post("/", response_model=TesteSementesOut, status_code=201)
async def criar_teste(
    payload: TesteSementesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.create")),
):
    try:
        return await crud.create_teste(db, payload, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{teste_id}", response_model=TesteSementesOut)
async def atualizar_teste(
    teste_id: int,
    payload: TesteSementesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.edit")),
):
    teste = await crud.update_teste(db, teste_id, payload)
    if not teste:
        raise HTTPException(status_code=404, detail="Teste não encontrado")
    return teste


@router.delete("/{teste_id}", response_model=TesteSementesOut)
async def excluir_teste(
    teste_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("coleta.delete")),
):
    teste = await crud.delete_teste(db, teste_id)
    if not teste:
        raise HTTPException(status_code=404, detail="Teste não encontrado")
    return teste
