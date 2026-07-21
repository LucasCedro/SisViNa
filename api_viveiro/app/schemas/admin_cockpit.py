"""Schemas do cockpit Admin (God Mode)."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.schemas.funcionarios import FuncionarioOut


class AdminViveiroResumoOut(BaseModel):
    id: int
    nome: str
    slug: str
    modo_operacao: str
    modo_label: str
    ativo: bool
    id_empresa: int
    funcionarios_vinculados: int = 0
    lotes_producao_ativos: int = 0


class AdminEmpresaResumoOut(BaseModel):
    id: int
    nome_fantasia: str
    razao_social: str
    slug: str
    ativo: bool
    viveiros_total: int = 0
    funcionarios_total: int = 0


class AdminOverviewOut(BaseModel):
    funcionarios_total: int
    funcionarios_ativos: int
    funcionarios_inativos: int
    funcionarios_sem_perfis: int
    plantas_total: int
    vendas_total: int
    especies_total: int
    empresas_total: int
    viveiros_total: int
    viveiros_florestal: int
    permissoes_catalogo: int
    perfis_rbac: int
    alembic_revision: Optional[str] = None
    por_perfil: Dict[str, int]
    empresas: List[AdminEmpresaResumoOut] = []
    viveiros: List[AdminViveiroResumoOut] = []


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


class AdminAuditoriaOut(BaseModel):
    id: int
    data_evento: Optional[str] = None
    usuario: Optional[str] = None
    id_empresa_origem: Optional[int] = None
    id_empresa_alvo: Optional[int] = None
    id_viveiro_alvo: Optional[int] = None
    acao: str
    recurso_tipo: Optional[str] = None
    recurso_id: Optional[int] = None
    detalhes: Optional[Dict[str, Any]] = None
    bloqueado: bool = False
