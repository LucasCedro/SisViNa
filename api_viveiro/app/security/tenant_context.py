"""
Contexto de empresa (tenant SaaS) — isolamento multi-cliente.

Regras:
- Usuário comum: empresa = funcionarios.id_empresa (fixo).
- empresa_admin: mesma regra; gerencia usuários só da própria empresa.
- platform_admin: pode trocar empresa via header X-Empresa-Id.
- Header X-Empresa-Id bloqueado para não-platform_admin (anti-escalação).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.database import get_db
from app.models.empresas import Empresa
from app.models.funcionarios import Funcionario
from app.schemas.funcionarios import FuncionarioOut
from app.security.rbac import is_empresa_admin, is_platform_admin, normalize_role_ids

logger = logging.getLogger(__name__)

EMPRESA_HEADER = "X-Empresa-Id"

PLATFORM_ONLY_PROFILES = frozenset({"admin", "platform_admin"})


@dataclass(frozen=True)
class TenantContext:
    id: int
    razao_social: str
    nome_fantasia: str
    slug: str
    ativo: bool
    is_platform_scope: bool = False


async def get_user_empresa_id(db: AsyncSession, user: FuncionarioOut) -> int:
    row = await db.get(Funcionario, user.id)
    if row is None or row.id_empresa is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário sem empresa vinculada.",
        )
    return int(row.id_empresa)


async def list_empresas_for_user(db: AsyncSession, user: FuncionarioOut) -> list[TenantContext]:
    if is_platform_admin(user.perfis):
        result = await db.execute(select(Empresa).where(Empresa.ativo.is_(True)).order_by(Empresa.id))
        return [_to_context(e, is_platform_scope=True) for e in result.scalars().all()]
    empresa_id = await get_user_empresa_id(db, user)
    row = await db.get(Empresa, empresa_id)
    if row is None or not row.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Empresa inativa ou inexistente.")
    return [_to_context(row)]


async def resolve_tenant_context(
    db: AsyncSession,
    user: FuncionarioOut,
    x_empresa_id: Optional[int],
    *,
    ip_origem: Optional[str] = None,
) -> TenantContext:
    from app.services.auditoria import registrar_auditoria

    user_empresa_id = await get_user_empresa_id(db, user)

    if x_empresa_id is not None:
        if not is_platform_admin(user.perfis):
            await registrar_auditoria(
                db,
                acao="tenant.header_bloqueado",
                user=user,
                id_empresa_origem=user_empresa_id,
                id_empresa_alvo=x_empresa_id,
                bloqueado=True,
                ip_origem=ip_origem,
                commit=True,
            )
            logger.warning(
                "Escalação tenant bloqueada usuario=%s header_empresa=%s",
                user.usuario,
                x_empresa_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seleção de empresa é exclusiva do administrador da plataforma.",
            )
        row = await db.get(Empresa, x_empresa_id)
        if row is None or not row.ativo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")
        if x_empresa_id != user_empresa_id:
            await registrar_auditoria(
                db,
                acao="tenant.switch_empresa",
                user=user,
                id_empresa_origem=user_empresa_id,
                id_empresa_alvo=x_empresa_id,
                ip_origem=ip_origem,
                commit=True,
            )
        return _to_context(row, is_platform_scope=True)

    row = await db.get(Empresa, user_empresa_id)
    if row is None or not row.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Empresa inativa ou inexistente.")
    return _to_context(row)


def assert_record_belongs_to_empresa(record_empresa_id: int, ctx: TenantContext, entity: str = "registro") -> None:
    if record_empresa_id != ctx.id:
        logger.warning(
            "Cross-tenant empresa bloqueado ctx=%s record=%s entity=%s",
            ctx.id,
            record_empresa_id,
            entity,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registro pertence a outra empresa.",
        )


def assert_can_manage_user_profiles(actor: FuncionarioOut, target_perfis: list[str] | None) -> None:
    """empresa_admin não pode promover a platform_admin/admin."""
    if is_platform_admin(actor.perfis):
        return
    if not is_empresa_admin(actor.perfis):
        return
    if not target_perfis:
        return
    roles = set(normalize_role_ids(target_perfis))
    forbidden = roles & PLATFORM_ONLY_PROFILES
    if forbidden:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Perfis de plataforma só podem ser atribuídos pelo administrador Brotare.",
        )


async def get_tenant_context(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user),
    x_empresa_id: Optional[int] = Header(None, alias=EMPRESA_HEADER),
) -> TenantContext:
    return await resolve_tenant_context(db, current_user, x_empresa_id)


def _to_context(e: Empresa, is_platform_scope: bool = False) -> TenantContext:
    return TenantContext(
        id=e.id,
        razao_social=e.razao_social,
        nome_fantasia=e.nome_fantasia,
        slug=e.slug,
        ativo=bool(e.ativo),
        is_platform_scope=is_platform_scope,
    )
