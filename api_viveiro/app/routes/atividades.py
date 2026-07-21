# app/routes/atividades.py
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.atividades import (
    TipoAtividade, TipoAtividadeCreate, TipoAtividadeUpdate,
    Atividade, AtividadeCreate, AtividadeUpdate, AtividadeDetalhe, AtividadeCompleta
)
from app.crud import atividades as crud_atividades
from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.security.scope_context import ScopeContext, get_scope_context
from app.schemas.funcionarios import FuncionarioOut

router = APIRouter()

# Rotas para TipoAtividade
@router.get("/tipos", response_model=List[TipoAtividade])
async def read_tipos_atividades(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("producao.view"))
):
    """
    Recupera todos os tipos de atividades.
    """
    tipos = await crud_atividades.get_tipos_atividades(db, skip=skip, limit=limit, id_empresa=scope.tenant.id)
    return tipos

@router.get("/tipos/{tipo_id}", response_model=TipoAtividade)
async def read_tipo_atividade(
    tipo_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("producao.view"))
):
    """
    Recupera um tipo de atividade específico pelo ID.
    """
    db_tipo = await crud_atividades.get_tipo_atividade(db, tipo_id, id_empresa=scope.tenant.id)
    if db_tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de atividade não encontrado")
    return db_tipo

@router.post("/tipos", response_model=TipoAtividade)
async def create_tipo_atividade(
    tipo: TipoAtividadeCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fertilizacao.create"))
):
    """
    Cria um novo tipo de atividade.
    """
    db_tipo = await crud_atividades.get_tipo_atividade_by_nome(db, nome=tipo.nome, id_empresa=scope.tenant.id)
    if db_tipo:
        raise HTTPException(
            status_code=400,
            detail="Tipo de atividade com este nome já registrado"
        )
    return await crud_atividades.create_tipo_atividade(db=db, tipo_atividade=tipo, id_empresa=scope.tenant.id)

@router.put("/tipos/{tipo_id}", response_model=TipoAtividade)
async def update_tipo_atividade(
    tipo_id: int,
    tipo: TipoAtividadeUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fertilizacao.edit"))
):
    """
    Atualiza um tipo de atividade existente.
    """
    if tipo.nome:
        existing_tipo = await crud_atividades.get_tipo_atividade_by_nome(db, tipo.nome, id_empresa=scope.tenant.id)
        if existing_tipo and existing_tipo.id != tipo_id:
            raise HTTPException(
                status_code=400,
                detail="Tipo de atividade com este nome já registrado"
            )
    
    db_tipo = await crud_atividades.update_tipo_atividade(db, tipo_id, tipo, id_empresa=scope.tenant.id)
    if db_tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de atividade não encontrado")
    return db_tipo

@router.delete("/tipos/{tipo_id}", response_model=TipoAtividade)
async def delete_tipo_atividade(
    tipo_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fertilizacao.edit"))
):
    """
    Deleta um tipo de atividade. Não é possível deletar se houver atividades associadas.
    """
    db_tipo = await crud_atividades.delete_tipo_atividade(db, tipo_id, id_empresa=scope.tenant.id)
    if db_tipo is None:
        raise HTTPException(
            status_code=404, 
            detail="Tipo de atividade não encontrado ou possui atividades associadas"
        )
    return db_tipo


@router.get("/", response_model=List[AtividadeCompleta])
async def read_atividades(
    skip: int = 0,
    limit: int = 100,
    id_tipo_atividade: Optional[int] = None,
    id_planta: Optional[int] = None,
    id_funcionario: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("producao.view"))
):
    """
    Recupera todas as atividades com opção de filtrar por tipo, planta, funcionário e período.
    """
    atividades = await crud_atividades.get_atividades(
        db, 
        skip=skip, 
        limit=limit, 
        id_tipo_atividade=id_tipo_atividade,
        id_planta=id_planta,
        id_funcionario=id_funcionario,
        data_inicio=data_inicio,
        data_fim=data_fim,
        id_viveiro=scope.viveiro.id,
    )
    return atividades

@router.get("/{atividade_id}", response_model=AtividadeDetalhe)
async def read_atividade(
    atividade_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("producao.view"))
):
    """
    Recupera uma atividade específica pelo ID com detalhes.
    """
    db_atividade = await crud_atividades.get_atividade_detalhe(
        db, atividade_id, id_viveiro=scope.viveiro.id
    )
    if db_atividade is None:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return db_atividade

@router.post("/", response_model=AtividadeDetalhe)
async def create_atividade(
    atividade: AtividadeCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fertilizacao.create"))
):
    """
    Cria uma nova atividade com opção de adicionar insumos utilizados.
    """
    try:
        return await crud_atividades.create_atividade(
            db=db, atividade=atividade, id_viveiro=scope.viveiro.id, id_empresa=scope.tenant.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.put("/{atividade_id}", response_model=Atividade)
async def update_atividade(
    atividade_id: int,
    atividade: AtividadeUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fertilizacao.edit"))
):
    """
    Atualiza uma atividade existente.
    """
    db_atividade = await crud_atividades.update_atividade(
        db, atividade_id, atividade, id_viveiro=scope.viveiro.id
    )
    if db_atividade is None:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return db_atividade

@router.delete("/{atividade_id}", response_model=AtividadeDetalhe)
async def delete_atividade(
    atividade_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    current_user: FuncionarioOut = Depends(require_permission("fertilizacao.edit"))
):
    """
    Deleta uma atividade. Restaura o estoque dos insumos e remove o custo da planta.
    """
    db_atividade = await crud_atividades.delete_atividade(
        db, atividade_id, id_viveiro=scope.viveiro.id
    )
    if db_atividade is None:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return db_atividade
