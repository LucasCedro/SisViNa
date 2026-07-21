# app/routes/canteiros.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.canteiros import Canteiro, CanteiroCreate, CanteiroUpdate, CanteiroWithOcupacao
from app.crud import canteiros as crud_canteiros
from app.security.rbac import require_permission
from app.security.scope_context import ScopeContext, get_scope_context
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

@router.get("/", response_model=List[Canteiro])
async def read_canteiros(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    tipo_local: Optional[str] = Query(None, description="sementeira | canteiro | armazem"),
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view"))
):
    """
    Recupera todos os canteiros.
    """
    canteiros = await crud_canteiros.get_canteiros(
        db,
        skip=skip,
        limit=limit,
        ativo=ativo,
        tipo_local=tipo_local,
        id_viveiro=scope.viveiro.id,
    )
    return canteiros

@router.get("/with-ocupacao", response_model=List[CanteiroWithOcupacao])
async def read_canteiros_with_ocupacao(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view"))
):
    """
    Recupera todos os canteiros com informações de ocupação.
    """
    canteiros = await crud_canteiros.get_canteiros_with_ocupacao(
        db, skip=skip, limit=limit, ativo=ativo, id_viveiro=scope.viveiro.id
    )
    return canteiros

@router.get("/{canteiro_id}", response_model=Canteiro)
async def read_canteiro(
    canteiro_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view"))
):
    """
    Recupera um canteiro específico pelo ID.
    """
    db_canteiro = await crud_canteiros.get_canteiro(db, canteiro_id, ctx=scope.viveiro)
    if db_canteiro is None:
        raise HTTPException(status_code=404, detail="Canteiro não encontrado")
    return db_canteiro

@router.post("/", response_model=Canteiro)
async def create_canteiro(
    canteiro: CanteiroCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.edit"))
):
    """
    Cria um novo canteiro.
    """
    db_canteiro = await crud_canteiros.get_canteiro_by_nome(
        db, nome=canteiro.nome, id_viveiro=scope.viveiro.id
    )
    if db_canteiro:
        raise HTTPException(
            status_code=400,
            detail="Canteiro com este nome já registrado"
        )
    return await crud_canteiros.create_canteiro(
        db=db, canteiro=canteiro, id_viveiro=scope.viveiro.id
    )

@router.put("/{canteiro_id}", response_model=Canteiro)
async def update_canteiro(
    canteiro_id: int,
    canteiro: CanteiroUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.edit"))
):
    """
    Atualiza um canteiro existente.
    """
    existente = await crud_canteiros.get_canteiro(db, canteiro_id, ctx=scope.viveiro)
    if existente is None:
        raise HTTPException(status_code=404, detail="Canteiro não encontrado")

    if canteiro.nome:
        existing_canteiro = await crud_canteiros.get_canteiro_by_nome(
            db, canteiro.nome, id_viveiro=scope.viveiro.id
        )
        if existing_canteiro and existing_canteiro.id != canteiro_id:
            raise HTTPException(
                status_code=400,
                detail="Canteiro com este nome já registrado"
            )
    
    db_canteiro = await crud_canteiros.update_canteiro(db, canteiro_id, canteiro)
    if db_canteiro is None:
        raise HTTPException(status_code=404, detail="Canteiro não encontrado")
    return db_canteiro

@router.delete("/{canteiro_id}")
async def delete_canteiro(
    canteiro_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.edit"))
):
    """
    Remove o local do banco somente se não houver plantas ativas (nem sementes em produção).
    """
    existente = await crud_canteiros.get_canteiro(db, canteiro_id, ctx=scope.viveiro)
    if existente is None:
        raise HTTPException(status_code=404, detail="Canteiro não encontrado")

    total = await crud_canteiros.count_plantas_ativas_no_canteiro(db, canteiro_id)
    if total > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Não é possível excluir: há {total} planta(s) ativa(s) neste local.",
        )

    await crud_canteiros.delete_canteiro(db, canteiro_id)
    return {"deleted": True, "id": canteiro_id}
