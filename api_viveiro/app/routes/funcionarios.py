# app/routes/funcionarios.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
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

router = APIRouter()


@router.get("/", response_model=List[FuncionarioOut])
async def read_funcionarios(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("users.view")),
):
    """Lista funcionários — exige users.view."""
    return await crud_funcionarios.get_funcionarios(db, skip=skip, limit=limit, ativo=ativo)


@router.get("/with-stats", response_model=List[FuncionarioWithStats])
async def read_funcionarios_with_stats(
    skip: int = 0,
    limit: int = 100,
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("users.view")),
):
    """Lista funcionários com estatísticas — exige users.view."""
    return await crud_funcionarios.get_funcionarios_with_stats(
        db, skip=skip, limit=limit, ativo=ativo
    )


@router.get("/simples", response_model=List[FuncionarioSimpleOut])
async def read_funcionarios_simples(
    db: AsyncSession = Depends(get_db),
    ativo: Optional[bool] = True,
    _user: FuncionarioOut = Depends(get_current_user),
):
    """
    Lista mínima {id, nome} para dropdowns operacionais.
    Qualquer usuário autenticado — sem expor perfis/salário.
    """
    funcionarios = await crud_funcionarios.get_funcionarios(db, skip=0, limit=500, ativo=ativo)
    return funcionarios


@router.get("/me", response_model=FuncionarioOut)
async def read_funcionario_me(
    current_user: FuncionarioOut = Depends(get_current_user),
):
    """Dados do usuário logado — autenticação básica (sem users.view)."""
    return current_user


@router.get("/{funcionario_id}", response_model=FuncionarioOut)
async def read_funcionario(
    funcionario_id: int,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("users.view")),
):
    """Detalhe de funcionário — exige users.view."""
    db_funcionario = await crud_funcionarios.get_funcionario(db, funcionario_id)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return db_funcionario


@router.post("/", response_model=FuncionarioOut)
async def create_funcionario(
    funcionario: FuncionarioCreate,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("users.create")),
):
    """Cria funcionário — exige users.create (impede auto-promoção via POST anônimo)."""
    db_funcionario = await crud_funcionarios.get_funcionario_by_usuario(db, funcionario.usuario)
    if db_funcionario:
        raise HTTPException(status_code=400, detail="Usuário já registrado no sistema")

    db_func_cpf = await crud_funcionarios.get_funcionario_by_cpf(db, funcionario.cpf)
    if db_func_cpf:
        raise HTTPException(status_code=400, detail="CPF já registrado no sistema")

    return await crud_funcionarios.create_funcionario(db=db, funcionario=funcionario)


@router.put("/{funcionario_id}", response_model=FuncionarioOut)
async def update_funcionario(
    funcionario_id: int,
    funcionario: FuncionarioUpdate,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("users.edit")),
):
    """
    Atualiza funcionário — exige users.edit.

    Mitigação BOLA/mass-assignment: sem users.edit, não dá para injetar
    `"perfis": ["admin"]` nem alterar cargo/salário de terceiros.
    Alteração do próprio perfil (sem perfis) → PATCH /auth/me.
    """
    db_funcionario = await crud_funcionarios.get_funcionario(db, funcionario_id)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    if funcionario.usuario:
        existing_user = await crud_funcionarios.get_funcionario_by_usuario(db, funcionario.usuario)
        if existing_user and existing_user.id != funcionario_id:
            raise HTTPException(
                status_code=400,
                detail="Usuário já registrado por outro funcionário",
            )

    if funcionario.cpf:
        existing_cpf = await crud_funcionarios.get_funcionario_by_cpf(db, funcionario.cpf)
        if existing_cpf and existing_cpf.id != funcionario_id:
            raise HTTPException(
                status_code=400,
                detail="CPF já registrado por outro funcionário",
            )

    return await crud_funcionarios.update_funcionario(db, funcionario_id, funcionario)


@router.delete("/{funcionario_id}", response_model=FuncionarioOut)
async def delete_funcionario(
    funcionario_id: int,
    db: AsyncSession = Depends(get_db),
    _user: FuncionarioOut = Depends(require_permission("users.delete")),
):
    """Desativa funcionário — exige users.delete."""
    db_funcionario = await crud_funcionarios.delete_funcionario(db, funcionario_id)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return db_funcionario
