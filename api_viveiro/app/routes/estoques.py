from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.crud import estoques as crud_estoques
from app.crud.estoques_analytics import listar_detalhe_analitico
from app.crud.estoques_cmv_detalhe import montar_cmv_detalhe_especie
from app.crud.estoques_timeline import montar_timeline_especies
from app.crud import lotes_sementes as crud_lotes
from app.database import get_db
from app.schemas.estoques import (
    EstoqueAnaliticoDetalheOut,
    EstoqueCmvDetalheOut,
    EstoqueResumoGeral,
    EstoqueTimelineOut,
)
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.lotes_sementes import LoteSementesEntradaArmazem, LoteSementesOut

router = APIRouter()


@router.get("/resumo", response_model=EstoqueResumoGeral)
async def resumo_estoques(
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    return await crud_estoques.get_resumo_estoques(db)


@router.get("/analitico/detalhe", response_model=EstoqueAnaliticoDetalheOut)
async def detalhe_analitico_estoque(
    metrica_idade: str = Query("viveiro", regex="^(viveiro|rustificacao)$"),
    id_especie: Optional[int] = None,
    faixa: Optional[str] = None,
    agrupar: str = Query("muda", regex="^(muda|lote)$"),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    data = await listar_detalhe_analitico(
        db,
        metrica_idade=metrica_idade,
        id_especie=id_especie,
        faixa=faixa,
        agrupar=agrupar,
    )
    partes = []
    if id_especie and data["itens_muda"]:
        p0 = data["itens_muda"][0]
        partes.append(p0.get("nome_popular") or p0.get("nome_cientifico") or f"Espécie #{id_especie}")
    if faixa:
        partes.append(faixa)
    data["titulo_filtro"] = " · ".join(partes) if partes else "Todas as mudas vivas"
    return data


@router.get("/timeline", response_model=EstoqueTimelineOut)
async def timeline_especies_estoque(
    id_especie: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    return await montar_timeline_especies(db, id_especie=id_especie)


@router.get("/especie/{id_especie}/cmv-detalhe", response_model=EstoqueCmvDetalheOut)
async def cmv_detalhe_especie(
    id_especie: int,
    escopo: str = Query("comercial", regex="^(comercial|vivas)$"),
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("estoques.view")),
):
    data = await montar_cmv_detalhe_especie(db, id_especie, escopo=escopo)
    if not data:
        raise HTTPException(status_code=404, detail="Espécie não encontrada")
    return data


@router.post("/entrada-sementes", response_model=LoteSementesOut, status_code=201)
async def entrada_sementes_armazem(
    payload: LoteSementesEntradaArmazem,
    db: AsyncSession = Depends(get_db),
    current_user: FuncionarioOut = Depends(require_permission("estoques.edit")),
):
    try:
        return await crud_lotes.criar_lote_armazem(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
