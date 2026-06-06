"""Schemas do cockpit Admin (God Mode)."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.schemas.funcionarios import FuncionarioOut


class AdminOverviewOut(BaseModel):
    funcionarios_total: int
    funcionarios_ativos: int
    funcionarios_inativos: int
    funcionarios_sem_perfis: int
    plantas_total: int
    vendas_total: int
    especies_total: int
    permissoes_catalogo: int
    perfis_rbac: int
    alembic_revision: Optional[str] = None
    por_perfil: Dict[str, int]


class AdminRbacRoleOut(BaseModel):
    id: str
    label: str
    permissoes: List[str]


class AdminRbacOut(BaseModel):
    roles: List[AdminRbacRoleOut]
    catalogo: List[str]


class AdminFuncionarioListOut(BaseModel):
    items: List[FuncionarioOut]
    total: int
