"""Testes unitários e de integração do RBAC (Passo 1)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import gerar_senha_hash
from app.models.funcionarios import Funcionario
from app.security.rbac import (
    ALL_PERMISSIONS,
    ROLE_PERMISSIONS,
    has_permission,
    resolve_permissions,
)


def test_admin_has_users_edit():
    perms = resolve_permissions(["admin"])
    assert "users.edit" in perms
    assert "users.create" in perms
    assert perms == set(ALL_PERMISSIONS)


def test_gestor_cannot_edit_users():
    assert not has_permission(["gestor"], "users.edit")
    assert not has_permission(["gestor"], "users.create")
    assert not has_permission(["gestor"], "vendas.approve")
    assert has_permission(["gestor"], "vendas.create")
    assert has_permission(["gestor"], "coleta.create")


def test_campo_limited_write():
    assert has_permission(["campo"], "producao.transfer")
    assert not has_permission(["campo"], "vendas.create")
    assert not has_permission(["campo"], "viveiro.edit")
    assert has_permission(["campo"], "viveiro.view")


def test_financeiro_can_approve_vendas():
    assert has_permission(["financeiro"], "vendas.approve")
    assert has_permission(["financeiro"], "fiscal.emit")
    assert not has_permission(["financeiro"], "coleta.create")


def test_consulta_read_only():
    perms = resolve_permissions(["consulta"])
    assert "coleta.view" in perms
    assert "financeiro.view" in perms
    assert "users.view" not in perms
    assert all(
        p.endswith(".view") or p in {"config.profile.edit", "home.view"} for p in perms
    )
    assert "coleta.create" not in perms
    assert "users.edit" not in perms


def test_rh_view_users_not_edit_financeiro():
    assert has_permission(["rh"], "users.view")
    assert not has_permission(["rh"], "users.edit")
    assert has_permission(["rh"], "financeiro.view")
    assert not has_permission(["rh"], "financeiro.edit")


def test_multi_profile_union():
    # campo + consulta → permissões de escrita de campo prevalecem
    perms = resolve_permissions(["campo", "consulta"])
    assert "coleta.create" in perms
    assert "coleta.view" in perms


def test_empty_perfis_baseline_only():
    perms = resolve_permissions([])
    assert perms == {"config.profile.edit", "home.view", "configuracoes.view"}


def test_unknown_role_ignored():
    perms = resolve_permissions(["gestor", "hacker"])
    assert "coleta.view" in perms
    assert len(perms) == len(ROLE_PERMISSIONS["gestor"])


@pytest.mark.asyncio
async def test_privilege_escalation_blocked(
    client: AsyncClient, db: AsyncSession, auth_headers: dict
):
    """
    Usuário campo tentando PUT com perfis admin → 403.
    Mitigação da falha BOLA crítica.
    """
    campo = Funcionario(
        nome="Operador Campo",
        cpf="222.333.444-55",
        email="campo@teste.local",
        usuario="campouser",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Operador",
        perfis=["campo"],
        ativo=True,
    )
    db.add(campo)
    await db.commit()
    await db.refresh(campo)

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "campouser", "password": "Senha@123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    attack = await client.put(
        f"/api/v1/funcionarios/{campo.id}",
        json={"perfis": ["admin"]},
        headers=headers,
    )
    assert attack.status_code == 403
    assert "users.edit" in attack.json()["detail"]

    await db.refresh(campo)
    assert campo.perfis == ["campo"]


@pytest.mark.asyncio
async def test_admin_can_update_funcionario(
    client: AsyncClient, db: AsyncSession, auth_headers: dict
):
    alvo = Funcionario(
        nome="Alvo RH",
        cpf="333.444.555-66",
        email="alvo@teste.local",
        usuario="alvo",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Auxiliar",
        perfis=["consulta"],
        ativo=True,
    )
    db.add(alvo)
    await db.commit()
    await db.refresh(alvo)

    ok = await client.put(
        f"/api/v1/funcionarios/{alvo.id}",
        json={"perfis": ["campo", "consulta"], "telefone": "(11) 90000-0000"},
        headers=auth_headers,
    )
    assert ok.status_code == 200
    data = ok.json()
    assert set(data["perfis"]) == {"campo", "consulta"}
    assert data["telefone"] == "(11) 90000-0000"


@pytest.mark.asyncio
async def test_patch_me_cannot_change_perfis(client: AsyncClient, db: AsyncSession):
    """PATCH /me ignora perfis — mass assignment não altera o banco."""
    consulta = Funcionario(
        nome="Auditor Consulta",
        cpf="444.555.666-77",
        email="consulta@teste.local",
        usuario="consultauser",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Consultor",
        perfis=["consulta"],
        ativo=True,
    )
    db.add(consulta)
    await db.commit()
    await db.refresh(consulta)
    perfis_antes = list(consulta.perfis)

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "consultauser", "password": "Senha@123"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = await client.patch(
        "/api/v1/auth/me",
        json={"nome": "Nome Atualizado", "perfis": ["admin"]},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Nome Atualizado"

    await db.refresh(consulta)
    assert consulta.perfis == perfis_antes == ["consulta"]
    assert "admin" not in (consulta.perfis or [])


@pytest.mark.asyncio
async def test_consulta_forbidden_on_mutations(client: AsyncClient, db: AsyncSession):
    """Perfil consulta: leitura ok, escrita bloqueada (403)."""
    consulta = Funcionario(
        nome="Consulta RBAC",
        cpf="555.666.777-88",
        email="consulta2@teste.local",
        usuario="consulta2",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Consultor",
        perfis=["consulta"],
        ativo=True,
    )
    db.add(consulta)
    await db.commit()

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "consulta2", "password": "Senha@123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    blocked = [
        ("POST", "/api/v1/vendas/", {"id_comprador": 1, "itens": []}),
        ("POST", "/api/v1/insumos/", {"nome": "X", "tipo": "Fertilizante", "unidade": "kg"}),
        ("POST", "/api/v1/coletas-sementes/", {"id_arvore_matriz": 1, "quantidade": 1}),
        ("GET", "/api/v1/funcionarios/", None),
    ]
    for method, path, body in blocked:
        if method == "POST":
            r = await client.post(path, json=body, headers=headers)
        else:
            r = await client.get(path, headers=headers)
        assert r.status_code == 403, f"{method} {path} deveria retornar 403, got {r.status_code}"

    allowed = await client.get("/api/v1/vendas/", headers=headers)
    assert allowed.status_code == 200


@pytest.mark.asyncio
async def test_godmode_blocked_without_admin_profile(
    client: AsyncClient, db: AsyncSession
):
    """God Mode exige perfil admin — gestor puro recebe 403."""
    gestor = Funcionario(
        nome="Gestor Puro",
        cpf="666.777.888-99",
        email="gestor@teste.local",
        usuario="gestorpuro",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Gestor",
        perfis=["gestor"],
        ativo=True,
    )
    db.add(gestor)
    await db.commit()

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "gestorpuro", "password": "Senha@123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    r = await client.get("/api/v1/admin/cockpit/overview", headers=headers)
    assert r.status_code == 403
    assert "administrador" in r.json()["detail"].lower()
