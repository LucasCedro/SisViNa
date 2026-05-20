from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.crud import estoques as crud_estoques
from app.crud import lotes_sementes as crud_lotes
from app.database import get_db
from app.schemas.estoques import EstoqueResumoGeral
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.lotes_sementes import LoteSementesEntradaArmazem, LoteSementesOut

router = APIRouter()


@router.get("/resumo", response_model=EstoqueResumoGeral)
async def resumo_estoques(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user),
):
    return await crud_estoques.get_resumo_estoques(db)


@router.post("/entrada-sementes", response_model=LoteSementesOut, status_code=201)
async def entrada_sementes_armazem(
    payload: LoteSementesEntradaArmazem,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(get_current_user),
):
    try:
        return await crud_lotes.criar_lote_armazem(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
