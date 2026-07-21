"""Rotas de contexto de unidade viveiro."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.session import build_auth_me_async
from app.database import get_db
from app.domain.pipelines.registry import get_pipeline
from app.schemas.auth import AuthMeOut
from app.schemas.viveiros import ViveiroContextOut, ViveiroOut
from app.security.rbac import require_permission
from app.security.viveiro_context import (
    get_viveiro_context,
    is_system_admin,
    list_viveiros_for_user,
    resolve_viveiro_context,
    ViveiroContext,
)
from app.schemas.funcionarios import FuncionarioOut
from app.auth.jwt import get_current_user
from fastapi import Header
from typing import Optional

from app.crud import viveiros as crud_viveiros
from app.constants.viveiro_modo import MODO_LABELS

router = APIRouter()


def _viveiro_out_from_ctx(ctx: ViveiroContext) -> ViveiroOut:
    return ViveiroOut(
        id=ctx.id,
        nome=ctx.nome,
        slug=ctx.slug,
        modo_operacao=ctx.modo_operacao,
        modo_label=ctx.modo_label,
        ativo=ctx.ativo,
    )


@router.get("/contexto", response_model=ViveiroContextOut)
async def read_viveiro_contexto(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("home.view")),
    ctx: ViveiroContext = Depends(get_viveiro_context),
):
    """Contexto da unidade ativa + módulos habilitados pelo pipeline."""
    viveiros = await list_viveiros_for_user(db, current_user)
    pipeline = get_pipeline(ctx)
    return ViveiroContextOut(
        viveiro_ativo=_viveiro_out_from_ctx(ctx),
        viveiros=[
            ViveiroOut(
                id=v.id,
                nome=v.nome,
                slug=v.slug,
                modo_operacao=v.modo_operacao,
                modo_label=v.modo_label,
                ativo=v.ativo,
            )
            for v in viveiros
        ],
        modulos_habilitados=sorted(pipeline.modulos_habilitados()),
        modulos_nav_desabilitados=sorted(pipeline.modulos_nav_desabilitados()),
        pode_selecionar_viveiro=is_system_admin(current_user) and len(viveiros) > 1,
    )


@router.get("/me-contexto", response_model=AuthMeOut)
async def read_me_with_context(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user),
    x_viveiro_id: Optional[int] = Header(None, alias="X-Viveiro-Id"),
):
    """Auth/me enriquecido com contexto viveiro (usado no login/hydrate)."""
    ctx = await resolve_viveiro_context(db, current_user, x_viveiro_id)
    return await build_auth_me_async(db, current_user, ctx)


@router.get("/", response_model=list[ViveiroOut])
async def list_viveiros_route(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("home.view")),
):
    rows = await crud_viveiros.list_viveiros(db)
    if not is_system_admin(current_user):
        allowed_ids = {v.id for v in await list_viveiros_for_user(db, current_user)}
        rows = [r for r in rows if r.id in allowed_ids]
    return [
        ViveiroOut(
            id=r.id,
            nome=r.nome,
            slug=r.slug,
            modo_operacao=r.modo_operacao,
            modo_label=MODO_LABELS.get(r.modo_operacao, r.modo_operacao),
            ativo=bool(r.ativo),
            data_cadastro=r.data_cadastro,
        )
        for r in rows
        if r.ativo
    ]
