from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import semeaduras as crud
from app.database import get_db
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.semeaduras import (
    RastreabilidadePlantaOut,
    SemeaduraCreate,
    SemeaduraLoteCreate,
    SemeaduraLoteOut,
    SemeaduraOut,
)

router = APIRouter()


@router.get("/", response_model=List[SemeaduraOut])
async def listar_semeaduras(
    skip: int = 0,
    limit: int = 2000,
    id_lote_sementes: Optional[int] = None,
    id_arvore_matriz: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.view")),
):
    return await crud.get_semeaduras(
        db,
        skip=skip,
        limit=limit,
        id_lote_sementes=id_lote_sementes,
        id_arvore_matriz=id_arvore_matriz,
    )


@router.post("/", response_model=SemeaduraOut, status_code=201)
async def criar_semeadura(
    payload: SemeaduraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.create")),
):
    try:
        return await crud.create_semeadura(db, payload, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail="Conflito ao criar plantas (código de rastreio duplicado). Tente novamente.",
        ) from e


@router.post("/lote", response_model=SemeaduraLoteOut, status_code=201)
async def criar_semeaduras_lote(
    payload: SemeaduraLoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.create")),
):
    try:
        return await crud.create_semeaduras_lote(db, payload, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail="Conflito ao criar plantas (código de rastreio duplicado). Tente novamente.",
        ) from e


@router.get("/rastreabilidade/planta/{planta_id}", response_model=RastreabilidadePlantaOut)
async def rastreabilidade_planta(
    planta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("producao.view")),
):
    dados = await crud.get_rastreabilidade_planta(db, planta_id)
    if not dados:
        raise HTTPException(status_code=404, detail="Planta não encontrada")
    return dados
