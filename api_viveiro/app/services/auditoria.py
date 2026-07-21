"""Registro de eventos cross-tenant (SaaS)."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auditoria import AuditoriaCrossTenant
from app.schemas.funcionarios import FuncionarioOut


async def registrar_auditoria(
    db: AsyncSession,
    *,
    acao: str,
    user: Optional[FuncionarioOut] = None,
    id_empresa_origem: Optional[int] = None,
    id_empresa_alvo: Optional[int] = None,
    id_viveiro_alvo: Optional[int] = None,
    recurso_tipo: Optional[str] = None,
    recurso_id: Optional[int] = None,
    detalhes: Optional[dict[str, Any]] = None,
    ip_origem: Optional[str] = None,
    bloqueado: bool = False,
    commit: bool = True,
) -> AuditoriaCrossTenant:
    row = AuditoriaCrossTenant(
        id_funcionario=user.id if user else None,
        usuario=user.usuario if user else None,
        id_empresa_origem=id_empresa_origem,
        id_empresa_alvo=id_empresa_alvo,
        id_viveiro_alvo=id_viveiro_alvo,
        acao=acao,
        recurso_tipo=recurso_tipo,
        recurso_id=recurso_id,
        detalhes=detalhes,
        ip_origem=ip_origem,
        bloqueado=bloqueado,
    )
    db.add(row)
    if commit:
        await db.commit()
        await db.refresh(row)
    return row
