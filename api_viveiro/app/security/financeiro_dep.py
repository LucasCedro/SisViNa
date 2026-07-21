"""Dependency que vincula escopo financeiro ao request."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends

from app.security.financeiro_scope import FinanceiroScope, reset_financeiro_scope, set_financeiro_scope
from app.security.scope_context import ScopeContext, get_scope_context


@asynccontextmanager
async def _financeiro_scope_manager(
    scope: ScopeContext,
) -> AsyncGenerator[None, None]:
    token = set_financeiro_scope(
        FinanceiroScope(id_viveiro=scope.viveiro.id, id_empresa=scope.tenant.id)
    )
    try:
        yield
    finally:
        reset_financeiro_scope(token)


async def bind_financeiro_scope(
    scope: ScopeContext = Depends(get_scope_context),
) -> AsyncGenerator[None, None]:
    async with _financeiro_scope_manager(scope):
        yield
