"""Schemas de autenticação / sessão."""

from typing import List

from pydantic import BaseModel

from app.schemas.funcionarios import FuncionarioOut


class AuthMeOut(FuncionarioOut):
    """
    Usuário logado + permissões efetivas (SSOT para o frontend).

    `permissions` é calculado no backend a partir de `perfis` — o cliente
    não deve inferir acesso por cargo nem reimplementar a matriz RBAC.
    """

    permissions: List[str] = []


class PermissionsOut(BaseModel):
    """Lista consolidada de permissões do usuário logado."""

    permissions: List[str]
