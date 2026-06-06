from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import producao as crud_producao
from app.database import get_db
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.producao_pipeline import ProducaoResumoOut

router = APIRouter()


@router.get("/resumo", response_model=ProducaoResumoOut)
async def read_producao_resumo(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.view")),
):
    return await crud_producao.get_producao_resumo(db)
