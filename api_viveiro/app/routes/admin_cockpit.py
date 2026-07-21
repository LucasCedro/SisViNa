"""Rotas exclusivas do cockpit Admin (God Mode)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import admin_cockpit as crud_admin
from app.crud import funcionarios as crud_funcionarios
from app.database import get_db
from app.models.funcionarios import Funcionario
from app.schemas.admin_cockpit import (
    AdminAuditoriaOut,
    AdminFuncionarioListOut,
    AdminOverviewOut,
    AdminRbacOut,
)
from app.schemas.funcionarios import FuncionarioCreate, FuncionarioOut, FuncionarioUpdate
from app.schemas.viveiros import ViveiroCreate, ViveiroOut
from app.security.rbac import require_godmode
from app.crud import viveiros as crud_viveiros
from app.constants.viveiro_modo import MODO_LABELS

router = APIRouter()


@router.get("/overview", response_model=AdminOverviewOut)
async def read_admin_overview(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_godmode("admin.godmode.view")),
):
    """Panorama do sistema — somente Admin."""
    return await crud_admin.get_overview(db)


@router.get("/rbac", response_model=AdminRbacOut)
async def read_admin_rbac(
    _admin=Depends(require_godmode("admin.godmode.view")),
):
    """Matriz RBAC completa — somente Admin."""
    return crud_admin.get_rbac_matrix()


@router.post("/viveiros", response_model=ViveiroOut, status_code=201)
async def create_admin_viveiro(
    payload: ViveiroCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_godmode("admin.godmode.manage")),
):
    """Cria unidade viveiro — God Mode."""
    if await crud_viveiros.get_viveiro_by_slug(db, payload.slug, id_empresa=payload.id_empresa):
        raise HTTPException(status_code=400, detail="Slug já em uso nesta empresa.")
    row = await crud_viveiros.create_viveiro(db, payload, id_empresa=payload.id_empresa)
    await crud_viveiros.link_funcionario_viveiro(db, admin.id, row.id)
    await db.commit()
    await db.refresh(row)
    return ViveiroOut(
        id=row.id,
        nome=row.nome,
        slug=row.slug,
        modo_operacao=row.modo_operacao,
        modo_label=MODO_LABELS.get(row.modo_operacao, row.modo_operacao),
        ativo=bool(row.ativo),
        data_cadastro=row.data_cadastro,
    )


@router.get("/auditoria", response_model=List[AdminAuditoriaOut])
async def list_admin_auditoria(
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_godmode("admin.godmode.view")),
):
    """Log cross-tenant — somente platform_admin."""
    return await crud_admin.list_auditoria(db, limit=limit)


@router.get("/funcionarios", response_model=AdminFuncionarioListOut)
async def list_admin_funcionarios(
    skip: int = 0,
    limit: int = Query(100, le=500),
    ativo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_godmode("admin.godmode.manage")),
):
    count_stmt = select(func.count()).select_from(Funcionario)
    if ativo is not None:
        count_stmt = count_stmt.where(Funcionario.ativo == ativo)
    total = int(await db.scalar(count_stmt) or 0)
    items = await crud_funcionarios.get_funcionarios(db, skip=skip, limit=limit, ativo=ativo)
    return AdminFuncionarioListOut(items=items, total=total)


@router.post("/funcionarios", response_model=FuncionarioOut)
async def create_admin_funcionario(
    funcionario: FuncionarioCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_godmode("admin.godmode.manage")),
):
    empresa_id = funcionario.id_empresa or 1
    if await crud_funcionarios.get_funcionario_by_usuario(db, funcionario.usuario):
        raise HTTPException(status_code=400, detail="Usuário já registrado no sistema")
    if await crud_funcionarios.get_funcionario_by_cpf(db, funcionario.cpf, id_empresa=empresa_id):
        raise HTTPException(status_code=400, detail="CPF já registrado no sistema")
    return await crud_funcionarios.create_funcionario(db, funcionario, id_empresa=empresa_id)


@router.put("/funcionarios/{funcionario_id}", response_model=FuncionarioOut)
async def update_admin_funcionario(
    funcionario_id: int,
    funcionario: FuncionarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_godmode("admin.godmode.manage")),
):
    db_funcionario = await crud_funcionarios.get_funcionario(db, funcionario_id)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    if funcionario.usuario:
        existing = await crud_funcionarios.get_funcionario_by_usuario(db, funcionario.usuario)
        if existing and existing.id != funcionario_id:
            raise HTTPException(status_code=400, detail="Usuário já registrado por outro funcionário")

    if funcionario.cpf:
        existing_cpf = await crud_funcionarios.get_funcionario_by_cpf(
            db, funcionario.cpf, id_empresa=db_funcionario.id_empresa
        )
        if existing_cpf and existing_cpf.id != funcionario_id:
            raise HTTPException(status_code=400, detail="CPF já registrado por outro funcionário")

    # Impede auto-remoção do perfil admin
    if funcionario_id == current_admin.id and funcionario.perfis is not None:
        if "admin" not in funcionario.perfis:
            raise HTTPException(
                status_code=400,
                detail="Você não pode remover seu próprio perfil administrador.",
            )

    updated = await crud_funcionarios.update_funcionario(db, funcionario_id, funcionario)
    if updated is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return updated


@router.delete("/funcionarios/{funcionario_id}", response_model=FuncionarioOut)
async def deactivate_admin_funcionario(
    funcionario_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(require_godmode("admin.godmode.manage")),
):
    if funcionario_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta.")
    db_funcionario = await crud_funcionarios.delete_funcionario(db, funcionario_id)
    if db_funcionario is None:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return db_funcionario
