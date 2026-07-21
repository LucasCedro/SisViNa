"""
Contexto de unidade viveiro — isolamento multi-tenant e anti-escalação.

Regras de segurança:
- Modo de operação vem SEMPRE do banco (viveiros.modo_operacao), nunca do cliente.
- Header X-Viveiro-Id honrado para platform_admin e empresa_admin (dentro da empresa).
- Não-admin que envia X-Viveiro-Id → 403 (tentativa de escalação horizontal).
- Toda mutação valida id_viveiro do registro vs contexto ativo.
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
from app.constants.viveiro_modo import MODO_LABELS, VALID_MODOS_OPERACAO
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.models.viveiros import Viveiro
from app.schemas.funcionarios import FuncionarioOut
from app.security.rbac import is_empresa_admin, is_platform_admin, normalize_role_ids
from app.security.tenant_context import EMPRESA_HEADER, TenantContext

logger = logging.getLogger(__name__)

VIVEIRO_HEADER = "X-Viveiro-Id"


@dataclass(frozen=True)
class ViveiroContext:
    id: int
    nome: str
    slug: str
    modo_operacao: str
    ativo: bool
    id_empresa: int

    @property
    def modo_label(self) -> str:
        return MODO_LABELS.get(self.modo_operacao, self.modo_operacao)


def is_system_admin(user: FuncionarioOut) -> bool:
    """Compat: admin de plataforma ou empresa."""
    return is_platform_admin(user.perfis) or is_empresa_admin(user.perfis)


async def list_viveiros_for_user(
    db: AsyncSession,
    user: FuncionarioOut,
    tenant: Optional[TenantContext] = None,
) -> list[ViveiroContext]:
    if is_platform_admin(user.perfis):
        stmt = select(Viveiro).where(Viveiro.ativo.is_(True))
        if tenant is not None:
            stmt = stmt.where(Viveiro.id_empresa == tenant.id)
        stmt = stmt.order_by(Viveiro.id)
        result = await db.execute(stmt)
        return [_to_context(v) for v in result.scalars().all()]

    if is_empresa_admin(user.perfis):
        empresa_id = tenant.id if tenant else await _user_empresa_id(db, user)
        result = await db.execute(
            select(Viveiro)
            .where(Viveiro.id_empresa == empresa_id, Viveiro.ativo.is_(True))
            .order_by(Viveiro.id)
        )
        return [_to_context(v) for v in result.scalars().all()]

    stmt = (
        select(Viveiro)
        .join(FuncionarioViveiro, FuncionarioViveiro.id_viveiro == Viveiro.id)
        .where(
            FuncionarioViveiro.id_funcionario == user.id,
            Viveiro.ativo.is_(True),
        )
    )
    if tenant is not None:
        stmt = stmt.where(Viveiro.id_empresa == tenant.id)
    stmt = stmt.order_by(Viveiro.id)
    result = await db.execute(stmt)
    return [_to_context(v) for v in result.scalars().all()]


async def user_has_viveiro_access(
    db: AsyncSession,
    user: FuncionarioOut,
    id_viveiro: int,
    tenant: Optional[TenantContext] = None,
) -> bool:
    row = await db.get(Viveiro, id_viveiro)
    if row is None or not row.ativo:
        return False
    if tenant is not None and row.id_empresa != tenant.id:
        return False
    if is_platform_admin(user.perfis) or is_empresa_admin(user.perfis):
        if tenant is not None:
            return row.id_empresa == tenant.id
        empresa_id = await _user_empresa_id(db, user)
        if is_empresa_admin(user.perfis) and row.id_empresa != empresa_id:
            return False
        return True
    result = await db.execute(
        select(FuncionarioViveiro.id_viveiro).where(
            FuncionarioViveiro.id_funcionario == user.id,
            FuncionarioViveiro.id_viveiro == id_viveiro,
        )
    )
    return result.scalar_one_or_none() is not None


async def resolve_viveiro_context(
    db: AsyncSession,
    user: FuncionarioOut,
    x_viveiro_id: Optional[int],
    tenant: Optional[TenantContext] = None,
) -> ViveiroContext:
    allowed = await list_viveiros_for_user(db, user, tenant=tenant)
    if not allowed:
        logger.warning(
            "Viveiro negado usuario=%s id=%s — sem vínculo com unidade",
            user.usuario,
            user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário sem vínculo com nenhuma unidade viveiro.",
        )

    can_select = is_platform_admin(user.perfis) or is_empresa_admin(user.perfis)

    if x_viveiro_id is not None:
        if not can_select:
            logger.warning(
                "Escalação horizontal bloqueada usuario=%s id=%s header_viveiro=%s",
                user.usuario,
                user.id,
                x_viveiro_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seleção de unidade viveiro é exclusiva do administrador.",
            )
        match = next((v for v in allowed if v.id == x_viveiro_id), None)
        if match is None:
            row = await db.get(Viveiro, x_viveiro_id)
            if row is None or not row.ativo:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade viveiro não encontrada.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a esta unidade viveiro.",
            )
        return match

    return allowed[0]


def assert_record_belongs_to_viveiro(record_viveiro_id: int, ctx: ViveiroContext, entity: str = "registro") -> None:
    if record_viveiro_id != ctx.id:
        logger.warning(
            "Cross-tenant bloqueado viveiro_ctx=%s record_viveiro=%s entity=%s",
            ctx.id,
            record_viveiro_id,
            entity,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registro pertence a outra unidade viveiro.",
        )


async def get_viveiro_context(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user),
    x_viveiro_id: Optional[int] = Header(None, alias=VIVEIRO_HEADER),
    x_empresa_id: Optional[int] = Header(None, alias=EMPRESA_HEADER),
) -> ViveiroContext:
    from app.security.tenant_context import resolve_tenant_context

    tenant = await resolve_tenant_context(db, current_user, x_empresa_id)
    return await resolve_viveiro_context(db, current_user, x_viveiro_id, tenant=tenant)


def _to_context(v: Viveiro) -> ViveiroContext:
    if v.modo_operacao not in VALID_MODOS_OPERACAO:
        raise ValueError(f"modo_operacao inválido no BD: {v.modo_operacao}")
    return ViveiroContext(
        id=v.id,
        nome=v.nome,
        slug=v.slug,
        modo_operacao=v.modo_operacao,
        ativo=bool(v.ativo),
        id_empresa=int(v.id_empresa),
    )


async def _user_empresa_id(db: AsyncSession, user: FuncionarioOut) -> int:
    from app.models.funcionarios import Funcionario

    row = await db.get(Funcionario, user.id)
    if row is None or row.id_empresa is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário sem empresa vinculada.")
    return int(row.id_empresa)
