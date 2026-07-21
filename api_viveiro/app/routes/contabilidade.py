"""Demonstrações contábeis — regime de competência."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.security.rbac import require_permission
from app.security.financeiro_dep import bind_financeiro_scope
from app.crud import financeiro as crud_financeiro
from app.database import get_db
from app.schemas.contabilidade import (
    BalancoPatrimonialOut,
    LivroCaixaOut,
    LivroInventarioOut,
    NotasExplicativasOut,
)
from app.schemas.financeiro import PainelFinanceiroOut
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()


@router.get("/painel", response_model=PainelFinanceiroOut)
async def read_painel_contabil(
    mes: Optional[int] = Query(None, ge=0, le=12),
    ano: Optional[int] = Query(None, ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(bind_financeiro_scope),
    current_user: FuncionarioOut = Depends(require_permission("contabilidade.view")),
):
    """DRE e indicadores em regime de competência (fato gerador)."""
    return await crud_financeiro.get_painel_financeiro(
        db, mes=mes, ano=ano, regime=crud_financeiro.REGIME_COMPETENCIA
    )


@router.get("/balanco", response_model=BalancoPatrimonialOut)
async def read_balanco_patrimonial(
    mes: Optional[int] = Query(None, ge=0, le=12),
    ano: Optional[int] = Query(None, ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(bind_financeiro_scope),
    current_user: FuncionarioOut = Depends(require_permission("contabilidade.view")),
):
    return await crud_financeiro.get_balanco_patrimonial(db, mes=mes, ano=ano)


@router.get("/livro-caixa", response_model=LivroCaixaOut)
async def read_livro_caixa(
    mes: Optional[int] = Query(None, ge=0, le=12),
    ano: Optional[int] = Query(None, ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(bind_financeiro_scope),
    current_user: FuncionarioOut = Depends(require_permission("contabilidade.view")),
):
    return await crud_financeiro.get_livro_caixa(db, mes=mes, ano=ano)


@router.get("/inventario", response_model=LivroInventarioOut)
async def read_livro_inventario(
    mes: Optional[int] = Query(None, ge=0, le=12),
    ano: Optional[int] = Query(None, ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(bind_financeiro_scope),
    current_user: FuncionarioOut = Depends(require_permission("contabilidade.view")),
):
    return await crud_financeiro.get_livro_inventario(db, mes=mes, ano=ano)


@router.get("/notas-explicativas", response_model=NotasExplicativasOut)
async def read_notas_explicativas(
    mes: Optional[int] = Query(None, ge=0, le=12),
    ano: Optional[int] = Query(None, ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(bind_financeiro_scope),
    current_user: FuncionarioOut = Depends(require_permission("contabilidade.view")),
):
    return await crud_financeiro.get_notas_explicativas(db, mes=mes, ano=ano)
