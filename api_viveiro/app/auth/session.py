"""Montagem de respostas de sessão (/auth/me)."""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.pipelines.registry import get_pipeline
from app.schemas.auth import AuthMeOut, ViveiroAtivoOut
from app.schemas.funcionarios import FuncionarioOut
from app.security.rbac import resolve_permissions
from app.security.viveiro_context import ViveiroContext, is_system_admin, list_viveiros_for_user


def build_auth_me(user: FuncionarioOut) -> AuthMeOut:
    """
    Legado síncrono — sem contexto viveiro.
    Preferir build_auth_me_async nas rotas com acesso ao BD.
    """
    permissions = sorted(resolve_permissions(user.perfis))
    return AuthMeOut(**user.dict(), permissions=permissions)


async def build_auth_me_async(
    db: AsyncSession,
    user: FuncionarioOut,
    ctx: ViveiroContext,
) -> AuthMeOut:
    permissions = sorted(resolve_permissions(user.perfis))
    pipeline = get_pipeline(ctx)
    viveiros = await list_viveiros_for_user(db, user)
    viveiro_ativo = ViveiroAtivoOut(
        id=ctx.id,
        nome=ctx.nome,
        slug=ctx.slug,
        modo_operacao=ctx.modo_operacao,
        modo_label=ctx.modo_label,
    )
    viveiros_out = [
        ViveiroAtivoOut(
            id=v.id,
            nome=v.nome,
            slug=v.slug,
            modo_operacao=v.modo_operacao,
            modo_label=v.modo_label,
        )
        for v in viveiros
    ]
    return AuthMeOut(
        **user.dict(),
        permissions=permissions,
        viveiro_ativo=viveiro_ativo,
        viveiros=viveiros_out,
        modulos_habilitados=sorted(pipeline.modulos_habilitados()),
        modulos_nav_desabilitados=sorted(pipeline.modulos_nav_desabilitados()),
        pode_selecionar_viveiro=is_system_admin(user) and len(viveiros) > 1,
    )
