from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.crud import dashboard as crud_dashboard
from app.database import get_db
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.lancamentos_financeiros import DashboardResumoOut, ResumoFinanceiroOut

router = APIRouter()


@router.get("/resumo", response_model=DashboardResumoOut)
async def read_dashboard_resumo(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user),
):
    return await crud_dashboard.get_dashboard_resumo(db)


@router.get("/financeiro", response_model=ResumoFinanceiroOut)
async def read_resumo_financeiro(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user),
):
    return await crud_dashboard.get_resumo_financeiro(db)
