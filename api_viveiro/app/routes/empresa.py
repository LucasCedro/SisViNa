"""Rotas de gestão da empresa (empresa_admin — sem God Mode)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import funcionarios as crud_funcionarios
from app.crud import viveiros as crud_viveiros
from app.database import get_db
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.models.funcionarios import Funcionario
from app.schemas.funcionarios import FuncionarioCreate, FuncionarioOut, FuncionarioUpdate
from app.security.rbac import require_empresa_user_manage, require_permission
from app.security.scope_context import ScopeContext, get_scope_context
from app.security.tenant_context import assert_can_manage_user_profiles, assert_record_belongs_to_empresa
from app.services.auditoria import registrar_auditoria

router = APIRouter()


async def _assert_funcionario_empresa(db: AsyncSession, funcionario_id: int, scope: ScopeContext) -> Funcionario:
    row = await crud_funcionarios.get_funcionario(db, funcionario_id, id_empresa=scope.tenant.id)
    if row is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    assert_record_belongs_to_empresa(row.id_empresa, scope.tenant, "funcionario")
    return row


@router.get("/usuarios", response_model=List[FuncionarioOut])
async def list_empresa_usuarios(
    skip: int = 0,
    limit: int = Query(100, le=500),
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    _user: FuncionarioOut = Depends(require_permission("users.view")),
):
    return await crud_funcionarios.get_funcionarios(
        db, skip=skip, limit=limit, ativo=ativo, id_empresa=scope.tenant.id
    )


@router.post("/usuarios", response_model=FuncionarioOut, status_code=201)
async def create_empresa_usuario(
    funcionario: FuncionarioCreate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    actor: FuncionarioOut = Depends(require_empresa_user_manage()),
):
    assert_can_manage_user_profiles(actor, funcionario.perfis)
    if await crud_funcionarios.get_funcionario_by_usuario(db, funcionario.usuario):
        raise HTTPException(status_code=400, detail="Usuário já registrado no sistema")
    if await crud_funcionarios.get_funcionario_by_cpf(db, funcionario.cpf, id_empresa=scope.tenant.id):
        raise HTTPException(status_code=400, detail="CPF já registrado no sistema")

    created = await crud_funcionarios.create_funcionario(
        db, funcionario, id_empresa=scope.tenant.id
    )
    viveiros = await crud_viveiros.list_viveiros(db, ativo=True, id_empresa=scope.tenant.id)
    for v in viveiros:
        await crud_viveiros.link_funcionario_viveiro(db, created.id, v.id)
    await db.commit()

    await registrar_auditoria(
        db,
        acao="empresa.usuario_criado",
        user=actor,
        id_empresa_origem=scope.tenant.id,
        id_empresa_alvo=scope.tenant.id,
        recurso_tipo="funcionario",
        recurso_id=created.id,
        detalhes={"usuario": created.usuario, "perfis": created.perfis},
    )
    return created


@router.put("/usuarios/{funcionario_id}", response_model=FuncionarioOut)
async def update_empresa_usuario(
    funcionario_id: int,
    funcionario: FuncionarioUpdate,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    actor: FuncionarioOut = Depends(require_empresa_user_manage()),
):
    db_funcionario = await _assert_funcionario_empresa(db, funcionario_id, scope)
    assert_can_manage_user_profiles(actor, funcionario.perfis)

    if funcionario.usuario:
        existing = await crud_funcionarios.get_funcionario_by_usuario(db, funcionario.usuario)
        if existing and existing.id != funcionario_id:
            raise HTTPException(status_code=400, detail="Usuário já registrado por outro funcionário")
    if funcionario.cpf:
        existing_cpf = await crud_funcionarios.get_funcionario_by_cpf(
            db, funcionario.cpf, id_empresa=scope.tenant.id
        )
        if existing_cpf and existing_cpf.id != funcionario_id:
            raise HTTPException(status_code=400, detail="CPF já registrado por outro funcionário")

    updated = await crud_funcionarios.update_funcionario(db, funcionario_id, funcionario)
    await registrar_auditoria(
        db,
        acao="empresa.usuario_atualizado",
        user=actor,
        id_empresa_origem=scope.tenant.id,
        recurso_tipo="funcionario",
        recurso_id=funcionario_id,
    )
    return updated


@router.delete("/usuarios/{funcionario_id}", response_model=FuncionarioOut)
async def deactivate_empresa_usuario(
    funcionario_id: int,
    db: AsyncSession = Depends(get_db),
    scope: ScopeContext = Depends(get_scope_context),
    actor: FuncionarioOut = Depends(require_empresa_user_manage()),
):
    if funcionario_id == actor.id:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta.")
    await _assert_funcionario_empresa(db, funcionario_id, scope)
    db_funcionario = await crud_funcionarios.delete_funcionario(db, funcionario_id)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    await registrar_auditoria(
        db,
        acao="empresa.usuario_desativado",
        user=actor,
        id_empresa_origem=scope.tenant.id,
        recurso_tipo="funcionario",
        recurso_id=funcionario_id,
    )
    return db_funcionario
