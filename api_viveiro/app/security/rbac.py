"""
RBAC estático do SisViNa — Single Source of Truth (backend).

Perfis (JSON no banco) agrupam permissões `modulo.acao`.
Rotas checam permissões via Depends(require_permission(...)).
"""

from __future__ import annotations

import logging
from typing import Callable, FrozenSet, Iterable, Set

from fastapi import Depends, HTTPException, status

from app.auth.jwt import get_current_user
from app.schemas.funcionarios import FuncionarioOut

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Catálogo canônico
# ---------------------------------------------------------------------------

ALL_PERMISSIONS: FrozenSet[str] = frozenset(
    {
        "users.view",
        "users.create",
        "users.edit",
        "users.delete",
        "config.profile.edit",
        "configuracoes.view",
        "home.view",
        "coleta.view",
        "coleta.create",
        "coleta.edit",
        "coleta.delete",
        "producao.view",
        "producao.create",
        "producao.transfer",
        "producao.edit",
        "viveiro.view",
        "viveiro.edit",
        "fitossanidade.view",
        "fitossanidade.create",
        "fitossanidade.edit",
        "fertilizacao.view",
        "fertilizacao.create",
        "fertilizacao.edit",
        "estoques.view",
        "estoques.edit",
        "vendas.view",
        "vendas.create",
        "vendas.edit",
        "vendas.approve",
        "financeiro.view",
        "financeiro.create",
        "financeiro.edit",
        "financeiro.delete",
        "fiscal.view",
        "fiscal.emit",
        "fiscal.edit",
        "contabilidade.view",
        "contabilidade.edit",
        "biblioteca.view",
        "biblioteca.edit",
        "prescricao.view",
        "prescricao.create",
        "florestal.view",
        "florestal.create",
        "florestal.edit",
        "florestal.transfer",
        "admin.godmode.view",
        "admin.godmode.manage",
        "empresa.users.manage",
    }
)

VALID_ROLE_IDS = frozenset(
    {"platform_admin", "empresa_admin", "admin", "gestor", "campo", "financeiro", "consulta", "rh"}
)

_VIEW_PERMISSIONS: FrozenSet[str] = frozenset(p for p in ALL_PERMISSIONS if p.endswith(".view"))
_CONSULTA_VIEW: FrozenSet[str] = _VIEW_PERMISSIONS - frozenset({"users.view"})

# Fail-closed: sem perfis → home + configurações + editar próprio perfil
BASELINE_AUTHENTICATED_PERMISSIONS: FrozenSet[str] = frozenset(
    {"config.profile.edit", "home.view", "configuracoes.view"}
)


def _perms(*names: str) -> FrozenSet[str]:
    unknown = set(names) - set(ALL_PERMISSIONS)
    if unknown:
        raise ValueError(f"Permissões desconhecidas no mapa RBAC: {sorted(unknown)}")
    return frozenset(names)


def _module_all(prefix: str, actions: Iterable[str]) -> FrozenSet[str]:
    return _perms(*(f"{prefix}.{action}" for action in actions))


_UI = _perms("config.profile.edit", "home.view", "configuracoes.view")
_COLETA_ALL = _module_all("coleta", ("view", "create", "edit", "delete"))
_PRODUCAO_ALL = _module_all("producao", ("view", "create", "transfer", "edit"))
_VIVEIRO_ALL = _module_all("viveiro", ("view", "edit"))
_FITO_ALL = _module_all("fitossanidade", ("view", "create", "edit"))
_FERT_ALL = _module_all("fertilizacao", ("view", "create", "edit"))
_ESTOQUES_ALL = _module_all("estoques", ("view", "edit"))
_VENDAS_GESTOR = _perms("vendas.view", "vendas.create", "vendas.edit")
_VENDAS_FIN = _module_all("vendas", ("view", "approve"))
_FIN_ALL = _module_all("financeiro", ("view", "create", "edit", "delete"))
_FISCAL_ALL = _module_all("fiscal", ("view", "emit", "edit"))
_CONTAB_ALL = _module_all("contabilidade", ("view", "edit"))
_BIBLIOTECA_ALL = _module_all("biblioteca", ("view", "edit"))
_PRESCRICAO_ALL = _module_all("prescricao", ("view", "create"))
_FLORESTAL_ALL = _module_all("florestal", ("view", "create", "edit", "transfer"))
_GODMODE = _perms("admin.godmode.view", "admin.godmode.manage")
_EMPRESA_USERS = _perms("users.view", "users.create", "users.edit", "users.delete", "empresa.users.manage")
_EMPRESA_ADMIN_BASE = (
    _UI
    | _COLETA_ALL
    | _PRODUCAO_ALL
    | _VIVEIRO_ALL
    | _FITO_ALL
    | _FERT_ALL
    | _ESTOQUES_ALL
    | _VENDAS_GESTOR
    | _FIN_ALL
    | _FISCAL_ALL
    | _CONTAB_ALL
    | _BIBLIOTECA_ALL
    | _PRESCRICAO_ALL
    | _FLORESTAL_ALL
    | _EMPRESA_USERS
)

ROLE_PERMISSIONS: dict[str, FrozenSet[str]] = {
    "admin": ALL_PERMISSIONS,
    "platform_admin": ALL_PERMISSIONS,
    "empresa_admin": _EMPRESA_ADMIN_BASE,
    "gestor": _UI
    | _COLETA_ALL
    | _PRODUCAO_ALL
    | _VIVEIRO_ALL
    | _FITO_ALL
    | _FERT_ALL
    | _ESTOQUES_ALL
    | _VENDAS_GESTOR
    | _BIBLIOTECA_ALL
    | _PRESCRICAO_ALL
    | _FLORESTAL_ALL
    | _perms("financeiro.view", "financeiro.create", "fiscal.view", "contabilidade.view"),
    "campo": _UI
    | _perms(
        "coleta.view",
        "coleta.create",
        "coleta.edit",
        "producao.view",
        "producao.create",
        "producao.transfer",
        "viveiro.view",
    )
    | _FITO_ALL
    | _FERT_ALL
    | _perms("estoques.view")
    | _BIBLIOTECA_ALL
    | _PRESCRICAO_ALL
    | _perms("florestal.view", "florestal.create", "florestal.transfer"),
    "financeiro": _UI
    | _perms("coleta.view", "producao.view", "viveiro.view", "estoques.view", "biblioteca.view")
    | _VENDAS_FIN
    | _FIN_ALL
    | _FISCAL_ALL
    | _CONTAB_ALL,
    "consulta": _UI | _CONSULTA_VIEW,
    "rh": _UI | _perms("users.view", "financeiro.view", "biblioteca.view"),
}


def normalize_role_ids(perfis: Iterable[str] | None) -> list[str]:
    if not perfis:
        return []
    seen: set[str] = set()
    ordered: list[str] = []
    for role in perfis:
        if role in VALID_ROLE_IDS and role not in seen:
            seen.add(role)
            ordered.append(role)
    return ordered


def is_platform_admin(perfis: Iterable[str] | None) -> bool:
    roles = normalize_role_ids(perfis)
    return "platform_admin" in roles or "admin" in roles


def is_empresa_admin(perfis: Iterable[str] | None) -> bool:
    roles = normalize_role_ids(perfis)
    return "empresa_admin" in roles or is_platform_admin(perfis)


def resolve_permissions(perfis: Iterable[str] | None) -> Set[str]:
    roles = normalize_role_ids(perfis)
    if not roles:
        return set(BASELINE_AUTHENTICATED_PERMISSIONS)
    merged: Set[str] = set()
    for role in roles:
        merged.update(ROLE_PERMISSIONS.get(role, frozenset()))
    return merged


def has_permission(perfis: Iterable[str] | None, permission: str) -> bool:
    if permission not in ALL_PERMISSIONS:
        return False
    return permission in resolve_permissions(perfis)


def require_permission(permission: str) -> Callable:
    if permission not in ALL_PERMISSIONS:
        raise ValueError(f"Permissão não registrada no catálogo RBAC: {permission}")

    async def _dependency(
        current_user: FuncionarioOut = Depends(get_current_user),
    ) -> FuncionarioOut:
        if not has_permission(current_user.perfis, permission):
            logger.warning(
                "RBAC negado usuario=%s id=%s permissao=%s perfis=%s",
                current_user.usuario,
                current_user.id,
                permission,
                current_user.perfis,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Permissão necessária: {permission}",
            )
        return current_user

    return _dependency


def require_godmode(permission: str) -> Callable:
    """
    Cockpit Admin (God Mode): exige platform_admin no BD **e** permissão exclusiva.
    empresa_admin NÃO acessa God Mode.
    """
    if permission not in ALL_PERMISSIONS:
        raise ValueError(f"Permissão God Mode não registrada: {permission}")

    async def _dependency(
        current_user: FuncionarioOut = Depends(get_current_user),
    ) -> FuncionarioOut:
        if not is_platform_admin(current_user.perfis):
            logger.warning(
                "God Mode negado usuario=%s id=%s — platform_admin ausente (perfis=%s)",
                current_user.usuario,
                current_user.id,
                current_user.perfis,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso exclusivo do administrador da plataforma Brotare.",
            )
        if not has_permission(current_user.perfis, permission):
            logger.warning(
                "God Mode negado usuario=%s id=%s permissao=%s perfis=%s",
                current_user.usuario,
                current_user.id,
                permission,
                current_user.perfis,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Permissão necessária: {permission}",
            )
        return current_user

    return _dependency


def require_empresa_user_manage() -> Callable:
    """Criação/edição de usuários: empresa_admin (própria empresa) ou platform_admin."""

    async def _dependency(
        current_user: FuncionarioOut = Depends(get_current_user),
    ) -> FuncionarioOut:
        if is_empresa_admin(current_user.perfis) and has_permission(
            current_user.perfis, "users.create"
        ):
            return current_user
        logger.warning(
            "Gestão usuários negada usuario=%s perfis=%s",
            current_user.usuario,
            current_user.perfis,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Permissão necessária para gerenciar usuários da empresa.",
        )

    return _dependency
