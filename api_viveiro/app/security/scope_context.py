"""Contexto combinado empresa + viveiro para queries operacionais."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.database import get_db
from app.models.viveiros import Viveiro
from app.schemas.funcionarios import FuncionarioOut
from app.security.tenant_context import (
    EMPRESA_HEADER,
    TenantContext,
    get_tenant_context,
    resolve_tenant_context,
)
from app.security.viveiro_context import (
    VIVEIRO_HEADER,
    ViveiroContext,
    get_viveiro_context,
    resolve_viveiro_context,
)


@dataclass(frozen=True)
class ScopeContext:
    tenant: TenantContext
    viveiro: ViveiroContext


async def resolve_scope_context(
    db: AsyncSession,
    user: FuncionarioOut,
    x_empresa_id: Optional[int],
    x_viveiro_id: Optional[int],
    *,
    ip_origem: Optional[str] = None,
) -> ScopeContext:
    tenant = await resolve_tenant_context(db, user, x_empresa_id, ip_origem=ip_origem)
    viveiro = await resolve_viveiro_context(db, user, x_viveiro_id, tenant=tenant)
    row = await db.get(Viveiro, viveiro.id)
    if row is None or row.id_empresa != tenant.id:
        from app.services.auditoria import registrar_auditoria

        await registrar_auditoria(
            db,
            acao="viveiro.empresa_mismatch",
            user=user,
            id_empresa_origem=tenant.id,
            id_empresa_alvo=row.id_empresa if row else None,
            id_viveiro_alvo=viveiro.id,
            bloqueado=True,
            ip_origem=ip_origem,
            commit=True,
        )
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unidade viveiro não pertence à empresa ativa.",
        )
    return ScopeContext(tenant=tenant, viveiro=viveiro)


async def get_scope_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user),
    x_empresa_id: Optional[int] = Header(None, alias=EMPRESA_HEADER),
    x_viveiro_id: Optional[int] = Header(None, alias=VIVEIRO_HEADER),
) -> ScopeContext:
    ip = request.client.host if request.client else None
    return await resolve_scope_context(db, current_user, x_empresa_id, x_viveiro_id, ip_origem=ip)


# Atalhos para Depends em rotas que só precisam de um dos contextos
get_tenant_ctx = get_tenant_context
get_viveiro_ctx = get_viveiro_context
