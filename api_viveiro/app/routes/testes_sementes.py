from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.security.rbac import require_permission
from app.security.scope_context import ScopeContext, get_scope_context
from app.crud import testes_sementes as crud
from app.crud.testes_sementes import _para_resposta, calcular_taxa_germinacao_especie
from app.database import get_db
from app.models.lotes_sementes import LoteSementes
from app.schemas.funcionarios import FuncionarioOut
from app.schemas.testes_sementes import TesteSementesCreate, TesteSementesOut, TesteSementesUpdate

router = APIRouter()


@router.get("/", response_model=List[TesteSementesOut])
async def listar_testes(
    skip: int = 0,
    limit: int = 2000,
    id_lote_sementes: Optional[int] = None,
    id_arvore_matriz: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    testes = await crud.get_testes(
        db,
        skip=skip,
        limit=limit,
        id_lote_sementes=id_lote_sementes,
        id_arvore_matriz=id_arvore_matriz,
        id_viveiro=scope.viveiro.id,
    )
    return [_para_resposta(t) for t in testes]


@router.get("/kpi-especies")
async def kpi_germinacao_especies(
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.view")),
):
    """Média de germinação por espécie (último teste por lote)."""
    from app.models.especies import Especie
    from app.utils.especies_display import formatar_nome_popular

    result = await db.execute(
        select(LoteSementes.id_especie)
        .where(
            LoteSementes.id_especie.isnot(None),
            LoteSementes.id_viveiro == scope.viveiro.id,
        )
        .distinct()
    )
    ids = [row[0] for row in result.all()]
    saida = []
    for id_esp in ids:
        taxa = await calcular_taxa_germinacao_especie(db, id_esp, id_viveiro=scope.viveiro.id)
        if taxa is None:
            continue
        esp = await db.get(Especie, id_esp)
        nome = formatar_nome_popular(esp.nome_popular) if esp else None
        if esp and not nome:
            nome = esp.nome_cientifico
        saida.append(
            {
                "id_especie": id_esp,
                "especie_nome": nome or f"Espécie #{id_esp}",
                "taxa_germinacao_media": taxa,
            }
        )
    saida.sort(key=lambda x: x["especie_nome"])
    return saida


@router.post("/", response_model=TesteSementesOut, status_code=201)
async def criar_teste(
    payload: TesteSementesCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.create")),
):
    try:
        return await crud.create_teste(
            db, payload, current_user.id, id_viveiro=scope.viveiro.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{teste_id}", response_model=TesteSementesOut)
async def atualizar_teste(
    teste_id: int,
    payload: TesteSementesUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.edit")),
):
    teste = await crud.update_teste(db, teste_id, payload, id_viveiro=scope.viveiro.id)
    if not teste:
        raise HTTPException(status_code=404, detail="Teste não encontrado")
    return teste


@router.delete("/{teste_id}", response_model=TesteSementesOut)
async def excluir_teste(
    teste_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("coleta.delete")),
):
    teste = await crud.delete_teste(db, teste_id, id_viveiro=scope.viveiro.id)
    if not teste:
        raise HTTPException(status_code=404, detail="Teste não encontrado")
    return teste
