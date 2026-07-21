import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.funcionarios import Funcionario
from app.auth.utils import gerar_senha_hash
from tests.tenant_fixtures import DEFAULT_EMPRESA_ID, DEFAULT_VIVEIRO_ID

# Dados de teste
user_test_data = {
    "nome": "Teste Auth",
    "cpf": "987.654.321-00",
    "email": "auth@teste.com",
    "usuario": "authuser",
    "senha": "Senha@123",
    "cargo": "Técnico",
    "ativo": True
}

@pytest.mark.asyncio
async def test_login(client: AsyncClient, db: AsyncSession):
    """
    Teste para o login e obtenção de token.
    """
    # Criar um usuário para teste
    hashed_password = gerar_senha_hash(user_test_data["senha"])
    db_user = Funcionario(
        nome=user_test_data["nome"],
        cpf=user_test_data["cpf"],
        email=user_test_data["email"],
        usuario=user_test_data["usuario"],
        senha=hashed_password,
        cargo=user_test_data["cargo"],
        ativo=user_test_data["ativo"]
    )
    db.add(db_user)
    await db.commit()
    
    # Tentar login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": user_test_data["usuario"],
            "password": user_test_data["senha"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_fail_wrong_password(client: AsyncClient, db: AsyncSession):
    """
    Teste para login com senha incorreta.
    """
    # Criar um usuário para teste
    hashed_password = gerar_senha_hash(user_test_data["senha"])
    db_user = Funcionario(
        nome=user_test_data["nome"],
        cpf=user_test_data["cpf"],
        email=user_test_data["email"],
        usuario=user_test_data["usuario"],
        senha=hashed_password,
        cargo=user_test_data["cargo"],
        ativo=user_test_data["ativo"]
    )
    db.add(db_user)
    await db.commit()
    
    # Tentar login com senha errada
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": user_test_data["usuario"],
            "password": "senha_errada"
        }
    )
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_fail_inactive_user(client: AsyncClient, db: AsyncSession):
    """
    Teste para login com usuário inativo.
    """
    # Criar um usuário inativo para teste
    hashed_password = gerar_senha_hash(user_test_data["senha"])
    db_user = Funcionario(
        nome=user_test_data["nome"],
        cpf=user_test_data["cpf"],
        email=user_test_data["email"],
        usuario=user_test_data["usuario"],
        senha=hashed_password,
        cargo=user_test_data["cargo"],
        ativo=False,
        id_empresa=DEFAULT_EMPRESA_ID,
    )
    db.add(db_user)
    await db.commit()
    
    # Tentar login com usuário inativo
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": user_test_data["usuario"],
            "password": user_test_data["senha"]
        }
    )
    
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict):
    """
    Teste para obter o usuário atual com permissões SSOT.
    """
    response = await client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["usuario"] == "testuser"
    assert "permissions" in data
    assert isinstance(data["permissions"], list)
    assert "users.edit" in data["permissions"]
    assert "config.profile.edit" in data["permissions"]


@pytest.mark.asyncio
async def test_get_permissions_endpoint(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/auth/permissions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "users.edit" in data["permissions"]


@pytest.mark.asyncio
async def test_me_empty_perfis_baseline_only(client: AsyncClient, db: AsyncSession):
    from app.auth.jwt import create_access_token

    user = Funcionario(
        nome="Sem Perfil",
        cpf="444.555.666-77",
        email="semperfil@teste.local",
        usuario="semperfil",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Temporário",
        perfis=None,
        ativo=True,
    )
    db.add(user)
    await db.commit()

    token = create_access_token(data={"sub": "semperfil"})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["permissions"] == sorted(["config.profile.edit", "home.view", "configuracoes.view"])
    assert data["perfis"] == []

@pytest.mark.asyncio
async def test_reset_password(client: AsyncClient, db: AsyncSession, test_user: dict, auth_headers: dict):
    """
    Teste para redefinir a senha do usuário.
    """
    # Tentar redefinir senha
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={
            "old_password": "Senha@123",  # Senha original definida no fixture
            "new_password": "NovaSenha@456"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verificar se a senha foi realmente alterada tentando login
    user_id = test_user["user"].id
    
    # Desconectar para limpar a sessão
    await db.close()
    
    # Tentar login com nova senha
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "NovaSenha@456"
        }
    )
    
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """
    Teste para acesso não autorizado.
    """
    response = await client.get("/api/v1/especies/")
    assert response.status_code == 401