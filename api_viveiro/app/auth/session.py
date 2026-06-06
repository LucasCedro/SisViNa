"""Montagem de respostas de sessão (/auth/me)."""

from app.schemas.auth import AuthMeOut
from app.schemas.funcionarios import FuncionarioOut
from app.security.rbac import resolve_permissions


def build_auth_me(user: FuncionarioOut) -> AuthMeOut:
    """
    Calcula permissões a partir dos perfis persistidos no BD.

    Se perfis for NULL/vazio → apenas config.profile.edit (+ baseline interna).
    """
    permissions = sorted(resolve_permissions(user.perfis))
    return AuthMeOut(**user.dict(), permissions=permissions)
