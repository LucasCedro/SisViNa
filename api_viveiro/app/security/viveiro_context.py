"""
Contexto de unidade viveiro — isolamento multi-tenant e anti-escalação.

Regras de segurança:
- Modo de operação vem SEMPRE do banco (viveiros.modo_operacao), nunca do cliente.
- Header X-Viveiro-Id só é honrado para perfil admin no BD.
- Não-admin que envia X-Viveiro-Id → 403 (tentativa de escalação horizontal).
- Toda mutação florestal valida id_viveiro do registro vs contexto ativo.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.constants.viveiro_modo import MODO_LABELS, VALID_MODOS_OPERACAO
from app.database import get_db
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.models.viveiros import Viveiro
from app.schemas.funcionarios import FuncionarioOut
from app.security.rbac import normalize_role_ids

logger = logging.getLogger(__name__)

VIVEIRO_HEADER = "X-Viveiro-Id"


@dataclass(frozen=True)
class ViveiroContext:
    id: int
    nome: str
    slug: str
    modo_operacao: str
    ativo: bool

    @property
    def modo_label(self) -> str:
        return MODO_LABELS.get(self.modo_operacao, self.modo_operacao)


def is_system_admin(user: FuncionarioOut) -> bool:
    return "admin" in normalize_role_ids(user.perfis)


async def list_viveiros_for_user(db: AsyncSession, user: FuncionarioOut) -> list[ViveiroContext]:
    if is_system_admin(user):
        result = await db.execute(
            select(Viveiro).where(Viveiro.ativo.is_(True)).order_by(Viveiro.id)
        )
    else:
        result = await db.execute(
            select(Viveiro)
            .join(FuncionarioViveiro, FuncionarioViveiro.id_viveiro == Viveiro.id)
            .where(
                FuncionarioViveiro.id_funcionario == user.id,
                Viveiro.ativo.is_(True),
            )
            .order_by(Viveiro.id)
        )
    return [_to_context(v) for v in result.scalars().all()]


async def user_has_viveiro_access(db: AsyncSession, user: FuncionarioOut, id_viveiro: int) -> bool:
    if is_system_admin(user):
        row = await db.get(Viveiro, id_viveiro)
        return row is not None and row.ativo
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
) -> ViveiroContext:
    allowed = await list_viveiros_for_user(db, user)
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

    if x_viveiro_id is not None:
        if not is_system_admin(user):
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
                detail="Administrador sem acesso a esta unidade.",
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
) -> ViveiroContext:
    return await resolve_viveiro_context(db, current_user, x_viveiro_id)


def _to_context(v: Viveiro) -> ViveiroContext:
    if v.modo_operacao not in VALID_MODOS_OPERACAO:
        raise ValueError(f"modo_operacao inválido no BD: {v.modo_operacao}")
    return ViveiroContext(
        id=v.id,
        nome=v.nome,
        slug=v.slug,
        modo_operacao=v.modo_operacao,
        ativo=bool(v.ativo),
    )
