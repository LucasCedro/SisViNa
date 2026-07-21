from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.security.rbac import require_permission
from app.crud import dashboard as crud_dashboard
from app.database import get_db
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.lancamentos_financeiros import DashboardResumoOut, ResumoFinanceiroOut
from app.security.scope_context import ScopeContext, get_scope_context

router = APIRouter()


@router.get("/resumo", response_model=DashboardResumoOut)
async def read_dashboard_resumo(
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("producao.view")),
):
    return await crud_dashboard.get_dashboard_resumo(db, id_viveiro=scope.viveiro.id)


@router.get("/financeiro", response_model=ResumoFinanceiroOut)
async def read_resumo_financeiro(
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("financeiro.view")),
):
    return await crud_dashboard.get_resumo_financeiro(
        db, id_viveiro=scope.viveiro.id, id_empresa=scope.tenant.id
    )
