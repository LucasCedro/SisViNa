from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import lancamentos_financeiros as crud
from app.database import get_db
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.lancamentos_financeiros import (
    LancamentoFinanceiro,
    LancamentoFinanceiroCreate,
    LancamentoFinanceiroUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[LancamentoFinanceiro])
async def listar(
    skip: int = 0,
    limit: int = 500,
    tipo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.view")),
):
    return await crud.list_lancamentos(db, skip=skip, limit=limit, tipo=tipo)


@router.post("/", response_model=LancamentoFinanceiro)
async def criar(
    body: LancamentoFinanceiroCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.create")),
):
    return await crud.create_lancamento(db, body, current_user.id)


@router.put("/{lancamento_id}", response_model=LancamentoFinanceiro)
async def atualizar(
    lancamento_id: int,
    body: LancamentoFinanceiroUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.edit")),
):
    obj = await crud.update_lancamento(db, lancamento_id, body)
    if not obj:
        raise HTTPException(404, "Lançamento não encontrado")
    return obj


@router.delete("/{lancamento_id}", response_model=LancamentoFinanceiro)
async def excluir(
    lancamento_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.delete")),
):
    obj = await crud.delete_lancamento(db, lancamento_id)
    if not obj:
        raise HTTPException(404, "Lançamento não encontrado")
    return obj
