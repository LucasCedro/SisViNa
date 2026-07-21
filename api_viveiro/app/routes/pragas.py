# app/routes/pragas.py
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.pragas import (
    TipoPraga, TipoPragaCreate, TipoPragaUpdate,
    MetodoCombate, MetodoCombateCreate, MetodoCombateUpdate,
    PragaPlanta, PragaPlantaCreate, PragaPlantaUpdate, PragaPlantaDetalhe,
    CombateRealizado, CombateRealizadoCreate, CombateRealizadoUpdate, CombateRealizadoDetalhe
)
from app.crud import pragas as crud_pragas
from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.security.scope_context import ScopeContext, get_scope_context
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

# Rotas para TipoPraga
@router.get("/tipos", response_model=List[TipoPraga])
async def read_tipos_pragas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.view")),
):
    """
    Recupera todos os tipos de pragas.
    """
    tipos = await crud_pragas.get_tipos_pragas(db, skip=skip, limit=limit, id_empresa=scope.tenant.id)
    return tipos

@router.get("/tipos/{tipo_id}", response_model=TipoPraga)
async def read_tipo_praga(
    tipo_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.view")),
):
    """
    Recupera um tipo de praga específico pelo ID.
    """
    db_tipo = await crud_pragas.get_tipo_praga(db, tipo_id, id_empresa=scope.tenant.id)
    if db_tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de praga não encontrado")
    return db_tipo

@router.post("/tipos", response_model=TipoPraga)
async def create_tipo_praga(
    tipo: TipoPragaCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.create")),
):
    """
    Cria um novo tipo de praga.
    """
    db_tipo = await crud_pragas.get_tipo_praga_by_nome(db, nome=tipo.nome, id_empresa=scope.tenant.id)
    if db_tipo:
        raise HTTPException(
            status_code=400,
            detail="Tipo de praga com este nome já registrado"
        )
    return await crud_pragas.create_tipo_praga(db=db, tipo_praga=tipo, id_empresa=scope.tenant.id)

@router.put("/tipos/{tipo_id}", response_model=TipoPraga)
async def update_tipo_praga(
    tipo_id: int,
    tipo: TipoPragaUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.edit")),
):
    """
    Atualiza um tipo de praga existente.
    """
    if tipo.nome:
        existing_tipo = await crud_pragas.get_tipo_praga_by_nome(db, tipo.nome, id_empresa=scope.tenant.id)
        if existing_tipo and existing_tipo.id != tipo_id:
            raise HTTPException(
                status_code=400,
                detail="Tipo de praga com este nome já registrado"
            )
    
    db_tipo = await crud_pragas.update_tipo_praga(db, tipo_id, tipo, id_empresa=scope.tenant.id)
    if db_tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de praga não encontrado")
    return db_tipo

@router.delete("/tipos/{tipo_id}", response_model=TipoPraga)
async def delete_tipo_praga(
    tipo_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.edit")),
):
    """
    Deleta um tipo de praga. Não é possível deletar se houver pragas associadas.
    """
    db_tipo = await crud_pragas.delete_tipo_praga(db, tipo_id, id_empresa=scope.tenant.id)
    if db_tipo is None:
        raise HTTPException(
            status_code=404, 
            detail="Tipo de praga não encontrado ou possui pragas associadas"
        )
    return db_tipo

# Rotas para MetodoCombate
@router.get("/metodos", response_model=List[MetodoCombate])
async def read_metodos_combate(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.view")),
):
    """
    Recupera todos os métodos de combate.
    """
    metodos = await crud_pragas.get_metodos_combate(db, skip=skip, limit=limit, id_empresa=scope.tenant.id)
    return metodos

@router.get("/metodos/{metodo_id}", response_model=MetodoCombate)
async def read_metodo_combate(
    metodo_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.view")),
):
    """
    Recupera um método de combate específico pelo ID.
    """
    db_metodo = await crud_pragas.get_metodo_combate(db, metodo_id, id_empresa=scope.tenant.id)
    if db_metodo is None:
        raise HTTPException(status_code=404, detail="Método de combate não encontrado")
    return db_metodo

@router.post("/metodos", response_model=MetodoCombate)
async def create_metodo_combate(
    metodo: MetodoCombateCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.create")),
):
    """
    Cria um novo método de combate.
    """
    return await crud_pragas.create_metodo_combate(db=db, metodo_combate=metodo, id_empresa=scope.tenant.id)

@router.put("/metodos/{metodo_id}", response_model=MetodoCombate)
async def update_metodo_combate(
    metodo_id: int,
    metodo: MetodoCombateUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.edit")),
):
    """
    Atualiza um método de combate existente.
    """
    db_metodo = await crud_pragas.update_metodo_combate(db, metodo_id, metodo, id_empresa=scope.tenant.id)
    if db_metodo is None:
        raise HTTPException(status_code=404, detail="Método de combate não encontrado")
    return db_metodo

@router.delete("/metodos/{metodo_id}", response_model=MetodoCombate)
async def delete_metodo_combate(
    metodo_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.edit")),
):
    """
    Deleta um método de combate. Não é possível deletar se houver combates associados.
    """
    db_metodo = await crud_pragas.delete_metodo_combate(db, metodo_id, id_empresa=scope.tenant.id)
    if db_metodo is None:
        raise HTTPException(
            status_code=404, 
            detail="Método de combate não encontrado ou possui combates associados"
        )
    return db_metodo

# Rotas para PragaPlanta
@router.get("/plantas", response_model=List[PragaPlantaDetalhe])
async def read_pragas_plantas(
    skip: int = 0,
    limit: int = 100,
    id_planta: Optional[int] = None,
    id_tipo_praga: Optional[int] = None,
    nivel_infestacao: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.view")),
):
    """
    Recupera todas as ocorrências de pragas em plantas.
    """
    pragas = await crud_pragas.get_pragas_plantas(
        db, 
        skip=skip, 
        limit=limit, 
        id_planta=id_planta,
        id_tipo_praga=id_tipo_praga,
        nivel_infestacao=nivel_infestacao,
        id_viveiro=scope.viveiro.id,
    )
    return pragas

@router.get("/plantas/{praga_id}", response_model=PragaPlantaDetalhe)
async def read_praga_planta(
    praga_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.view")),
):
    """
    Recupera uma ocorrência específica de praga em planta pelo ID.
    """
    db_praga = await crud_pragas.get_praga_planta_detalhe(db, praga_id, id_viveiro=scope.viveiro.id)
    if db_praga is None:
        raise HTTPException(status_code=404, detail="Ocorrência de praga não encontrada")
    return db_praga

@router.post("/plantas", response_model=PragaPlanta)
async def create_praga_planta(
    praga: PragaPlantaCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.create")),
):
    """
    Registra uma nova ocorrência de praga em planta.
    """
    try:
        return await crud_pragas.create_praga_planta(
            db=db, praga_planta=praga, id_viveiro=scope.viveiro.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.put("/plantas/{praga_id}", response_model=PragaPlanta)
async def update_praga_planta(
    praga_id: int,
    praga: PragaPlantaUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.edit")),
):
    """
    Atualiza uma ocorrência de praga em planta existente.
    """
    db_praga = await crud_pragas.update_praga_planta(
        db, praga_id, praga, id_viveiro=scope.viveiro.id
    )
    if db_praga is None:
        raise HTTPException(status_code=404, detail="Ocorrência de praga não encontrada")
    return db_praga

@router.delete("/plantas/{praga_id}", response_model=PragaPlanta)
async def delete_praga_planta(
    praga_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.edit")),
):
    """
    Deleta uma ocorrência de praga em planta. Não é possível deletar se houver combates associados.
    """
    db_praga = await crud_pragas.delete_praga_planta(db, praga_id, id_viveiro=scope.viveiro.id)
    if db_praga is None:
        raise HTTPException(
            status_code=404, 
            detail="Ocorrência de praga não encontrada ou possui combates associados"
        )
    return db_praga

# Rotas para CombateRealizado
@router.get("/combates", response_model=List[CombateRealizadoDetalhe])
async def read_combates_realizados(
    skip: int = 0,
    limit: int = 100,
    id_praga_planta: Optional[int] = None,
    id_metodo_combate: Optional[int] = None,
    id_funcionario: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.view")),
):
    """
    Recupera todos os combates realizados.
    """
    combates = await crud_pragas.get_combates_realizados(
        db, 
        skip=skip, 
        limit=limit, 
        id_praga_planta=id_praga_planta,
        id_metodo_combate=id_metodo_combate,
        id_funcionario=id_funcionario,
        data_inicio=data_inicio,
        data_fim=data_fim,
        id_viveiro=scope.viveiro.id,
    )
    return combates

@router.get("/combates/{combate_id}", response_model=CombateRealizadoDetalhe)
async def read_combate_realizado(
    combate_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.view")),
):
    """
    Recupera um combate realizado específico pelo ID.
    """
    db_combate = await crud_pragas.get_combate_realizado_detalhe(
        db, combate_id, id_viveiro=scope.viveiro.id
    )
    if db_combate is None:
        raise HTTPException(status_code=404, detail="Combate realizado não encontrado")
    return db_combate

@router.post("/combates", response_model=CombateRealizado)
async def create_combate_realizado(
    combate: CombateRealizadoCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.create")),
):
    """
    Registra um novo combate realizado.
    """
    try:
        return await crud_pragas.create_combate_realizado(
            db=db, combate=combate, id_viveiro=scope.viveiro.id, id_empresa=scope.tenant.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.put("/combates/{combate_id}", response_model=CombateRealizado)
async def update_combate_realizado(
    combate_id: int,
    combate: CombateRealizadoUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.edit")),
):
    """
    Atualiza um combate realizado existente.
    """
    db_combate = await crud_pragas.update_combate_realizado(
        db, combate_id, combate, id_viveiro=scope.viveiro.id
    )
    if db_combate is None:
        raise HTTPException(status_code=404, detail="Combate realizado não encontrado")
    return db_combate

@router.delete("/combates/{combate_id}", response_model=CombateRealizadoDetalhe)
async def delete_combate_realizado(
    combate_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fitossanidade.edit")),
):
    """
    Deleta um combate realizado.
    """
    db_combate = await crud_pragas.delete_combate_realizado(
        db, combate_id, id_viveiro=scope.viveiro.id
    )
    if db_combate is None:
        raise HTTPException(status_code=404, detail="Combate realizado não encontrado")
    return db_combate
