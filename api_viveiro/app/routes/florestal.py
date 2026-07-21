"""API do módulo florestal — mudas plantadas por lote."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.viveiro_modo import MODO_FLORESTAL
from app.crud import florestal as crud_florestal
from app.database import get_db
from app.schemas.florestal import (
    FlorestalResumoOut,
    GenotipoCreate,
    GenotipoOut,
    GenotipoUpdate,
    LotePerdaRequest,
    LoteProducaoCreate,
    LoteProducaoOut,
    LoteTransferenciaRequest,
    MovimentacaoLoteOut,
)
from app.schemas.funcionarios import FuncionarioOut
from app.security.rbac import require_permission
from app.security.viveiro_context import ViveiroContext, get_viveiro_context

router = APIRouter()


def _assert_florestal(ctx: ViveiroContext) -> None:
    if ctx.modo_operacao != MODO_FLORESTAL:
        raise HTTPException(
            status_code=403,
            detail="Módulo florestal não habilitado para esta unidade viveiro.",
        )


@router.get("/resumo", response_model=FlorestalResumoOut)
async def resumo(
    db: AsyncSession = Depends(get_db),
    ctx: ViveiroContext = Depends(get_viveiro_context),
    _user: FuncionarioOut = Depends(require_permission("florestal.view")),
):
    _assert_florestal(ctx)
    return await crud_florestal.resumo_florestal(db, ctx)


@router.get("/genotipos", response_model=List[GenotipoOut])
async def list_genotipos(
    ativo: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    ctx: ViveiroContext = Depends(get_viveiro_context),
    _user: FuncionarioOut = Depends(require_permission("florestal.view")),
):
    _assert_florestal(ctx)
    return await crud_florestal.list_genotipos(db, ctx, ativo=ativo)


@router.post("/genotipos", response_model=GenotipoOut, status_code=201)
async def create_genotipo(
    payload: GenotipoCreate,
    db: AsyncSession = Depends(get_db),
    ctx: ViveiroContext = Depends(get_viveiro_context),
    _user: FuncionarioOut = Depends(require_permission("florestal.create")),
):
    _assert_florestal(ctx)
    try:
        row = await crud_florestal.create_genotipo(db, ctx, payload)
        await db.commit()
        return row
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/genotipos/{genotipo_id}", response_model=GenotipoOut)
async def update_genotipo(
    genotipo_id: int,
    payload: GenotipoUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: ViveiroContext = Depends(get_viveiro_context),
    _user: FuncionarioOut = Depends(require_permission("florestal.edit")),
):
    _assert_florestal(ctx)
    row = await crud_florestal.update_genotipo(db, ctx, genotipo_id, payload)
    if row is None:
        raise HTTPException(status_code=404, detail="Genótipo não encontrado.")
    await db.commit()
    return row


@router.get("/lotes", response_model=List[LoteProducaoOut])
async def list_lotes(
    estagio: Optional[str] = Query(None),
    id_genotipo: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    ctx: ViveiroContext = Depends(get_viveiro_context),
    _user: FuncionarioOut = Depends(require_permission("florestal.view")),
):
    _assert_florestal(ctx)
    return await crud_florestal.list_lotes(db, ctx, estagio=estagio, id_genotipo=id_genotipo)


@router.post("/lotes", response_model=LoteProducaoOut, status_code=201)
async def create_lote(
    payload: LoteProducaoCreate,
    db: AsyncSession = Depends(get_db),
    ctx: ViveiroContext = Depends(get_viveiro_context),
    user: FuncionarioOut = Depends(require_permission("florestal.create")),
):
    _assert_florestal(ctx)
    try:
        row = await crud_florestal.create_lote(db, ctx, payload, user.id)
        await db.commit()
        return row
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/lotes/{lote_id}/transferir", response_model=LoteProducaoOut)
async def transferir_lote(
    lote_id: int,
    payload: LoteTransferenciaRequest,
    db: AsyncSession = Depends(get_db),
    ctx: ViveiroContext = Depends(get_viveiro_context),
    user: FuncionarioOut = Depends(require_permission("florestal.transfer")),
):
    _assert_florestal(ctx)
    try:
        row = await crud_florestal.transferir_lote(db, ctx, lote_id, payload, user.id)
        await db.commit()
        return row
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/lotes/{lote_id}/perda", response_model=LoteProducaoOut)
async def registrar_perda(
    lote_id: int,
    payload: LotePerdaRequest,
    db: AsyncSession = Depends(get_db),
    ctx: ViveiroContext = Depends(get_viveiro_context),
    user: FuncionarioOut = Depends(require_permission("florestal.edit")),
):
    _assert_florestal(ctx)
    try:
        row = await crud_florestal.registrar_perda(db, ctx, lote_id, payload, user.id)
        await db.commit()
        return row
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/lotes/{lote_id}/movimentacoes", response_model=List[MovimentacaoLoteOut])
async def list_movimentacoes(
    lote_id: int,
    db: AsyncSession = Depends(get_db),
    ctx: ViveiroContext = Depends(get_viveiro_context),
    _user: FuncionarioOut = Depends(require_permission("florestal.view")),
):
    _assert_florestal(ctx)
    return await crud_florestal.list_movimentacoes(db, ctx, lote_id)
