"""Helpers para filtrar queries por escopo empresa/viveiro."""

from __future__ import annotations

from typing import Any, Type

from sqlalchemy import Select

from app.security.tenant_context import TenantContext
from app.security.viveiro_context import ViveiroContext


def apply_viveiro_scope(stmt: Select, model: Type[Any], ctx: ViveiroContext) -> Select:
    if hasattr(model, "id_viveiro"):
        return stmt.where(model.id_viveiro == ctx.id)
    return stmt


def apply_empresa_scope(stmt: Select, model: Type[Any], ctx: TenantContext) -> Select:
    if hasattr(model, "id_empresa"):
        return stmt.where(model.id_empresa == ctx.id)
    return stmt
