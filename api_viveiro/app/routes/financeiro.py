from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import financeiro as crud_financeiro
from app.crud import premissas_financeiras as crud_premissas
from app.database import get_db
from app.schemas.financeiro import PainelFinanceiroOut
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.premissas_financeiras import PremissaCreate, PremissaOut, PremissaUpdate

router = APIRouter()


@router.get("/painel", response_model=PainelFinanceiroOut)
async def read_painel_financeiro(
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.view")),
):
    return await crud_financeiro.get_painel_financeiro(db, mes=mes, ano=ano)


@router.get("/premissas", response_model=List[PremissaOut])
async def list_premissas(
    natureza: Optional[str] = Query(None),
    apenas_ativas: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.view")),
):
    return await crud_premissas.list_premissas(db, natureza=natureza, apenas_ativas=apenas_ativas)


@router.post("/premissas", response_model=PremissaOut)
async def create_premissa(
    body: PremissaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.edit")),
):
    try:
        return await crud_premissas.create_premissa(db, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/premissas/{premissa_id}", response_model=PremissaOut)
async def update_premissa(
    premissa_id: int,
    body: PremissaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.edit")),
):
    out = await crud_premissas.update_premissa(db, premissa_id, body)
    if not out:
        raise HTTPException(status_code=404, detail="Premissa não encontrada")
    return out


@router.delete("/premissas/{premissa_id}")
async def delete_premissa(
    premissa_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.edit")),
):
    ok = await crud_premissas.delete_premissa(db, premissa_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Premissa não encontrada")
    return {"ok": True}
