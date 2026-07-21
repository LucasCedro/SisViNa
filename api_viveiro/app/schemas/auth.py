"""Schemas de autenticação / sessão."""

from typing import List, Optional

from pydantic import BaseModel

from app.schemas.funcionarios import FuncionarioOut


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
    viveiro_ativo: Optional[ViveiroAtivoOut] = None
    viveiros: List[ViveiroAtivoOut] = []
    modulos_habilitados: List[str] = []
    modulos_nav_desabilitados: List[str] = []
    pode_selecionar_viveiro: bool = False


class PermissionsOut(BaseModel):
    """Lista consolidada de permissões do usuário logado."""

    permissions: List[str]
