"""Montagem de respostas de sessão (/auth/me)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.pipelines.registry import get_pipeline
from app.schemas.auth import AuthMeOut, EmpresaAtivaOut, ViveiroAtivoOut
from app.schemas.funcionarios import FuncionarioOut
from app.security.rbac import is_platform_admin, resolve_permissions
from app.security.tenant_context import TenantContext, list_empresas_for_user
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
    tenant: TenantContext,
    viveiro: ViveiroContext,
) -> AuthMeOut:
    permissions = sorted(resolve_permissions(user.perfis))
    pipeline = get_pipeline(viveiro)
    viveiros = await list_viveiros_for_user(db, user, tenant=tenant)
    empresas_ctx = await list_empresas_for_user(db, user)
    empresas_out = [
        EmpresaAtivaOut(
            id=e.id,
            razao_social=e.razao_social,
            nome_fantasia=e.nome_fantasia,
            slug=e.slug,
        )
        for e in empresas_ctx
    ]
    empresa_ativa = EmpresaAtivaOut(
        id=tenant.id,
        razao_social=tenant.razao_social,
        nome_fantasia=tenant.nome_fantasia,
        slug=tenant.slug,
    )
    viveiro_ativo = ViveiroAtivoOut(
        id=viveiro.id,
        nome=viveiro.nome,
        slug=viveiro.slug,
        modo_operacao=viveiro.modo_operacao,
        modo_label=viveiro.modo_label,
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
    platform = is_platform_admin(user.perfis)
    return AuthMeOut(
        **user.dict(),
        permissions=permissions,
        empresa_ativa=empresa_ativa,
        empresas=empresas_out,
        viveiro_ativo=viveiro_ativo,
        viveiros=viveiros_out,
        modulos_habilitados=sorted(pipeline.modulos_habilitados()),
        modulos_nav_desabilitados=sorted(pipeline.modulos_nav_desabilitados()),
        pode_selecionar_viveiro=is_system_admin(user) and len(viveiros) > 1,
        pode_selecionar_empresa=platform,
        is_platform_admin=platform,
    )
