"""Schemas de autenticação / sessão."""

from typing import List, Optional

from pydantic import BaseModel

from app.schemas.funcionarios import FuncionarioOut


class EmpresaAtivaOut(BaseModel):
    id: int
    razao_social: str
    nome_fantasia: str
    slug: str


class ViveiroAtivoOut(BaseModel):
    id: int
    nome: str
    slug: str
    modo_operacao: str
    modo_label: str


class AuthMeOut(FuncionarioOut):
    """
    Usuário logado + permissões efetivas (SSOT para o frontend).

    `permissions` é calculado no backend a partir de `perfis` — o cliente
    não deve inferir acesso por cargo nem reimplementar a matriz RBAC.
    """

    permissions: List[str] = []
    empresa_ativa: Optional[EmpresaAtivaOut] = None
    empresas: List[EmpresaAtivaOut] = []
    viveiro_ativo: Optional[ViveiroAtivoOut] = None
    viveiros: List[ViveiroAtivoOut] = []
    modulos_habilitados: List[str] = []
    modulos_nav_desabilitados: List[str] = []
    pode_selecionar_viveiro: bool = False
    pode_selecionar_empresa: bool = False
    is_platform_admin: bool = False


class PermissionsOut(BaseModel):
    """Lista consolidada de permissões do usuário logado."""

    permissions: List[str]
