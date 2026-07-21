"""Testes de isolamento e anti-escalação do contexto viveiro."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import gerar_senha_hash
from app.constants.viveiro_modo import MODO_FLORESTAL, MODO_NATIVO
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.models.funcionarios import Funcionario
from app.models.viveiros import Viveiro


@pytest.fixture
async def viveiros_seed(db: AsyncSession):
    nativo = Viveiro(id=1, nome="Teste Nativo", slug="teste-nativo", modo_operacao=MODO_NATIVO, ativo=True)
    florestal = Viveiro(
        id=2, nome="Teste Florestal", slug="teste-florestal", modo_operacao=MODO_FLORESTAL, ativo=True
    )
    db.add_all([nativo, florestal])
    await db.flush()
    return nativo, florestal


@pytest.fixture
async def users_viveiro(db: AsyncSession, viveiros_seed):
  senha = gerar_senha_hash("Senha!@#")
  admin = Funcionario(
      nome="Admin Test",
      cpf="100.000.000-01",
      usuario="test.admin.viveiro",
      senha=senha,
      email="admin.viveiro@test.local",
      perfis=["admin"],
      ativo=True,
  )
  campo = Funcionario(
      nome="Campo Test",
      cpf="100.000.000-02",
      usuario="test.campo.viveiro",
      senha=senha,
      email="campo.viveiro@test.local",
      perfis=["campo"],
      ativo=True,
  )
  db.add_all([admin, campo])
  await db.flush()
  db.add_all(
      [
          FuncionarioViveiro(id_funcionario=admin.id, id_viveiro=1),
          FuncionarioViveiro(id_funcionario=admin.id, id_viveiro=2),
          FuncionarioViveiro(id_funcionario=campo.id, id_viveiro=1),
      ]
  )
  await db.commit()
  return {"admin": admin, "campo": campo}


async def _token(client: AsyncClient, usuario: str) -> str:
    r = await client.post(
        "/api/v1/auth/login",
        data={"username": usuario, "password": "Senha!@#"},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_campo_nao_pode_enviar_header_viveiro(client: AsyncClient, users_viveiro):
    token = await _token(client, "test.campo.viveiro")
    r = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}", "X-Viveiro-Id": "2"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_admin_pode_trocar_contexto(client: AsyncClient, users_viveiro):
    token = await _token(client, "test.admin.viveiro")
    r = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}", "X-Viveiro-Id": "2"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["viveiro_ativo"]["modo_operacao"] == MODO_FLORESTAL
    assert "coleta" in body["modulos_nav_desabilitados"]


@pytest.mark.asyncio
async def test_florestal_bloqueado_em_viveiro_nativo(client: AsyncClient, users_viveiro):
    token = await _token(client, "test.admin.viveiro")
    r = await client.get(
        "/api/v1/florestal/resumo",
        headers={"Authorization": f"Bearer {token}", "X-Viveiro-Id": "1"},
    )
    assert r.status_code == 403
