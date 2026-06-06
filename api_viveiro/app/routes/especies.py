# app/routes/especies.py
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.especies import (
    Especie,
    EspecieCreate,
    EspecieUpdate,
    EspecieWithPlantasCount,
    EspecieBibliotecaOut,
    ImagensExternasOut,
    SincronizarImagensExternasOut,
)
from app.crud import especies as crud_especies
from app.crud import especies_imagens as crud_imagens
from app.models.especie_biblioteca import EspecieBiblioteca
from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

@router.get("/", response_model=List[Especie])
async def read_especies(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view"))
):
    """
    Recupera todas as espécies.
    """
    especies = await crud_especies.get_especies(db, skip=skip, limit=limit)
    return especies

@router.get("/with-plantas-count", response_model=List[EspecieWithPlantasCount])
async def read_especies_with_plantas_count(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view"))
):
    """
    Recupera todas as espécies com contagem de plantas.
    """
    especies = await crud_especies.get_especies_with_plantas_count(db, skip=skip, limit=limit)
    return especies


@router.get("/biblioteca", response_model=List[EspecieBibliotecaOut])
async def read_especies_biblioteca(
    skip: int = 0,
    limit: int = 500,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("biblioteca.view"))
):
    """Lista espécies com dados da biblioteca técnica."""
    return await crud_especies.get_especies_biblioteca(db, skip=skip, limit=limit)


@router.post(
    "/biblioteca/sincronizar-imagens-externas",
    response_model=SincronizarImagensExternasOut,
)
async def sincronizar_imagens_externas_biblioteca(
    apenas_sem_cache: bool = Query(True),
    forcar: bool = Query(False),
    limite: int = Query(500, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("biblioteca.edit")),
):
    """Busca speciesLink e grava URLs no cache (JSON) da biblioteca."""
    return await crud_imagens.sincronizar_imagens_biblioteca(
        db,
        apenas_sem_cache=apenas_sem_cache,
        limite=limite,
        forcar=forcar,
    )


@router.get("/{especie_id}/imagens-externas", response_model=ImagensExternasOut)
async def read_imagens_externas_especie(
    especie_id: int,
    refresh: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("biblioteca.view")),
):
    especie = await crud_especies.get_especie(db, especie_id)
    if not especie:
        raise HTTPException(status_code=404, detail="Espécie não encontrada")
    urls = await crud_imagens.obter_imagens_externas(db, especie_id, refresh=refresh)
    bib = await db.get(EspecieBiblioteca, especie_id)
    locais = crud_imagens._urls_locais_biblioteca(bib) if bib else []
    todas: list[str] = []
    vistos: set[str] = set()
    for u in [*urls, *locais]:
        if u not in vistos:
            vistos.add(u)
            todas.append(u)
    return ImagensExternasOut(
        id_especie=especie_id,
        nome_cientifico=especie.nome_cientifico,
        urls=todas,
        cache_atualizado_em=bib.imagens_externas_atualizado_em if bib else None,
    )


@router.get("/{especie_id}", response_model=Especie)
async def read_especie(
    especie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("viveiro.view"))
):
    """
    Recupera uma espécie específica pelo ID.
    """
    db_especie = await crud_especies.get_especie(db, especie_id)
    if db_especie is None:
        raise HTTPException(status_code=404, detail="Espécie não encontrada")
    return db_especie

@router.post("/", response_model=Especie)
async def create_especie(
    especie: EspecieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("biblioteca.edit"))
):
    """
    Cria uma nova espécie.
    """
    db_especie = await crud_especies.get_especie_by_nome(db, nome_cientifico=especie.nome_cientifico)
    if db_especie:
        raise HTTPException(
            status_code=400,
            detail="Espécie com este nome científico já registrada"
        )
    return await crud_especies.create_especie(db=db, especie=especie)

@router.put("/{especie_id}", response_model=Especie)
async def update_especie(
    especie_id: int,
    especie: EspecieUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("biblioteca.edit"))
):
    """
    Atualiza uma espécie existente.
    """
    db_especie = await crud_especies.update_especie(db, especie_id, especie)
    if db_especie is None:
        raise HTTPException(status_code=404, detail="Espécie não encontrada")
    return db_especie

@router.delete("/{especie_id}", response_model=Especie)
async def delete_especie(
    especie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("biblioteca.edit"))
):
    """
    Deleta uma espécie.
    """
    db_especie = await crud_especies.delete_especie(db, especie_id)
    if db_especie is None:
        raise HTTPException(status_code=404, detail="Espécie não encontrada")
    return db_especie
