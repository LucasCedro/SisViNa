from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import viveiro_layout as crud_layout
from app.database import get_db
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.viveiro_layout import ViveiroLayoutOut, ViveiroLayoutSave

router = APIRouter()


@router.get("/", response_model=ViveiroLayoutOut)
async def obter_layout(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view")),
):
    layout = await crud_layout.get_layout(db)
    return ViveiroLayoutOut(layout=layout or {})


@router.put("/", response_model=ViveiroLayoutOut)
async def salvar_layout(
    body: ViveiroLayoutSave,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.edit")),
):
    row = await crud_layout.save_layout(db, body.layout)
    return ViveiroLayoutOut(
        layout=body.layout,
        atualizado_em=row.atualizado_em,
    )
