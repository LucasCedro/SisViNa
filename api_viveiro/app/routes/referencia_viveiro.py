from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.constants.referencia_embrapa_viveiro import FONTE_SISTEMA
from app.crud import referencia_viveiro as crud_ref
from app.database import get_db
from app.schemas.referencia_viveiro import (
    EspecieFichaEmbrapaOut,
    ReferenciaViveiroResumoOut,
    RegraGlobalOut,
)

router = APIRouter()


@router.get("/regras", response_model=list[RegraGlobalOut])
async def listar_regras(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Parâmetros globais do viveiro (somente leitura)."""
    return await crud_ref.listar_regras_globais(db)


@router.get("/resumo", response_model=ReferenciaViveiroResumoOut)
async def resumo_referencia(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    regras = await crud_ref.listar_regras_globais(db)
    return ReferenciaViveiroResumoOut(fonte=FONTE_SISTEMA, regras_globais=regras)


@router.get("/especies/{id_especie}/ficha", response_model=EspecieFichaEmbrapaOut)
async def ficha_especie(
    id_especie: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    ficha = await crud_ref.get_ficha_especie(db, id_especie)
    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Espécie sem ficha técnica cadastrada.",
        )
    return ficha
