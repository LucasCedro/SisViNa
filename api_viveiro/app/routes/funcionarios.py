# app/routes/funcionarios.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.funcionarios import (
    FuncionarioOut,
    FuncionarioCreate,
    FuncionarioUpdate,
    FuncionarioWithStats,
    FuncionarioSimpleOut,
)
from app.crud import funcionarios as crud_funcionarios
from app.auth.jwt import get_current_user
from app.security.rbac import require_permission
from app.security.scope_context import ScopeContext, get_scope_context
from app.security.tenant_context import assert_record_belongs_to_empresa

router = APIRouter()


@router.get("/", response_model=List[FuncionarioOut])
async def read_funcionarios(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    _user: FuncionarioOut = Depends(require_permission("users.view")),
):
    """Lista funcionários da empresa ativa."""
    return await crud_funcionarios.get_funcionarios(
        db, skip=skip, limit=limit, ativo=ativo, id_empresa=scope.tenant.id
    )


@router.get("/with-stats", response_model=List[FuncionarioWithStats])
async def read_funcionarios_with_stats(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    _user: FuncionarioOut = Depends(require_permission("users.view")),
):
    return await crud_funcionarios.get_funcionarios_with_stats(
        db, skip=skip, limit=limit, ativo=ativo, id_empresa=scope.tenant.id
    )


@router.get("/simples", response_model=List[FuncionarioSimpleOut])
async def read_funcionarios_simples(
    db: AsyncSession = Depends(get_db),
    ativo: Optional[bool] = True,
    scope: ScopeContext = Depends(get_scope_context),
    _user: FuncionarioOut = Depends(get_current_user),
):
    funcionarios = await crud_funcionarios.get_funcionarios(
        db, skip=0, limit=500, ativo=ativo, id_empresa=scope.tenant.id
    )
    return funcionarios


@router.get("/me", response_model=FuncionarioOut)
async def read_funcionario_me(
    current_user: FuncionarioOut = Depends(get_current_user),
):
    return current_user


@router.get("/{funcionario_id}", response_model=FuncionarioOut)
async def read_funcionario(
    funcionario_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    _user: FuncionarioOut = Depends(require_permission("users.view")),
):
    db_funcionario = await crud_funcionarios.get_funcionario(
        db, funcionario_id, id_empresa=scope.tenant.id
    )
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return db_funcionario


@router.post("/", response_model=FuncionarioOut)
async def create_funcionario(
    funcionario: FuncionarioCreate,
    db: AsyncSession = Depends(get_db),
):
    """Use POST /empresa/usuarios para criar usuários (empresa_admin)."""
    raise HTTPException(
        status_code=403,
        detail="Criação de usuários via /funcionarios desativada. Use Gestão de Usuários em Configurações.",
    )


@router.put("/{funcionario_id}", response_model=FuncionarioOut)
async def update_funcionario(
    funcionario_id: int,
    funcionario: FuncionarioUpdate,
    db: AsyncSession = Depends(get_db),
):
    raise HTTPException(
        status_code=403,
        detail="Edição de usuários via /funcionarios desativada. Use Gestão de Usuários em Configurações.",
    )


@router.delete("/{funcionario_id}", response_model=FuncionarioOut)
async def delete_funcionario(
    funcionario_id: int,
    db: AsyncSession = Depends(get_db),
):
    raise HTTPException(
        status_code=403,
        detail="Desativação via /funcionarios desativada. Use Gestão de Usuários em Configurações.",
    )
