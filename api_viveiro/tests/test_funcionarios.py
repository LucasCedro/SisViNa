import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.funcionarios import Funcionario
from app.auth.utils import gerar_senha_hash, verificar_senha
from tests.tenant_fixtures import DEFAULT_EMPRESA_ID, DEFAULT_VIVEIRO_ID

# Dados de teste
funcionario_test_data = {
    "nome": "João Silva",
    "cpf": "123.456.789-01",
    "rg": "12.345.678-9",
    "data_nascimento": "1990-01-01",
    "telefone": "(11) 98765-4321",
    "email": "joao.silva@exemplo.com",
    "endereco": "Rua das Flores, 123",
    "cargo": "Jardineiro",
    "data_contratacao": "2022-01-15",
    "salario": 2500.00,
    "usuario": "joaosilva",
    "senha": "Senha@123"
}

@pytest.mark.asyncio
async def test_create_funcionario(client: AsyncClient, auth_headers: dict):
    """
    Teste para criar um novo funcionário.
    """
    response = await client.post(
        "/api/v1/funcionarios/",
        json=funcionario_test_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == funcionario_test_data["nome"]
    assert data["cpf"] == funcionario_test_data["cpf"]
    assert data["usuario"] == funcionario_test_data["usuario"]
    assert "id" in data
    assert "data_cadastro" in data
    assert "senha" not in data  # A senha não deve ser retornada

@pytest.mark.asyncio
async def test_read_funcionario(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler um funcionário específico.
    """
    # Primeiro, criar um funcionário
    funcionario_dict = funcionario_test_data.copy()
    hashed_password = gerar_senha_hash(funcionario_dict.pop("senha"))
    db_funcionario = Funcionario(**funcionario_dict, senha=hashed_password, id_empresa=DEFAULT_EMPRESA_ID)
    db.add(db_funcionario)
    await db.commit()
    await db.refresh(db_funcionario)
    
    # Agora, ler o funcionário
    response = await client.get(
        f"/api/v1/funcionarios/{db_funcionario.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == funcionario_test_data["nome"]
    assert data["id"] == db_funcionario.id
    assert "senha" not in data  # A senha não deve ser retornada

@pytest.mark.asyncio
async def test_read_funcionarios(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler todos os funcionários.
    """
    # Criar funcionários
    funcionario1_dict = {
        "nome": "Ana Souza",
        "cpf": "111.222.333-44",
        "email": "ana@exemplo.com",
        "usuario": "anasouza",
        "senha": gerar_senha_hash("Senha@123"),
        "cargo": "Gerente"
    }
    
    funcionario2_dict = {
        "nome": "Carlos Lima",
        "cpf": "555.666.777-88",
        "email": "carlos@exemplo.com",
        "usuario": "carloslima",
        "senha": gerar_senha_hash("Senha@456"),
        "cargo": "Auxiliar"
    }
    
    db_funcionario1 = Funcionario(**funcionario1_dict, id_empresa=DEFAULT_EMPRESA_ID)
    db_funcionario2 = Funcionario(**funcionario2_dict, id_empresa=DEFAULT_EMPRESA_ID)
    
    db.add(db_funcionario1)
    db.add(db_funcionario2)
    await db.commit()
    
    # Ler todos os funcionários
    response = await client.get(
        "/api/v1/funcionarios/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # Inclui o funcionário de teste da fixture
    # Verificar se as senhas não são retornadas
    assert all("senha" not in item for item in data)

@pytest.mark.asyncio
async def test_update_funcionario(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para atualizar um funcionário.
    """
    # Criar um funcionário
    funcionario_dict = funcionario_test_data.copy()
    hashed_password = gerar_senha_hash(funcionario_dict.pop("senha"))
    db_funcionario = Funcionario(**funcionario_dict, senha=hashed_password, id_empresa=DEFAULT_EMPRESA_ID)
    db.add(db_funcionario)
    await db.commit()
    await db.refresh(db_funcionario)
    
    # Atualizar o funcionário
    update_data = {
        "telefone": "(11) 91234-5678",
        "endereco": "Avenida Central, 456",
        "salario": 2700.00
    }
    
    response = await client.put(
        f"/api/v1/funcionarios/{db_funcionario.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["telefone"] == update_data["telefone"]
    assert data["endereco"] == update_data["endereco"]
    assert data["salario"] == update_data["salario"]
    assert data["nome"] == funcionario_test_data["nome"]  # Não alterado

@pytest.mark.asyncio
async def test_update_funcionario_senha(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para atualizar a senha de um funcionário.
    """
    # Criar um funcionário
    funcionario_dict = funcionario_test_data.copy()
    hashed_password = gerar_senha_hash(funcionario_dict.pop("senha"))
    db_funcionario = Funcionario(**funcionario_dict, senha=hashed_password, id_empresa=DEFAULT_EMPRESA_ID)
    db.add(db_funcionario)
    await db.commit()
    await db.refresh(db_funcionario)
    
    # Atualizar a senha
    update_data = {
        "senha": "NovaSenha@789"
    }
    
    response = await client.put(
        f"/api/v1/funcionarios/{db_funcionario.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Buscar o funcionário atualizado no banco
    result = await db.execute(f"SELECT senha FROM funcionarios WHERE id = {db_funcionario.id}")
    senha_hash = result.scalar()
    
    # Verificar se a nova senha está correta
    assert verificar_senha("NovaSenha@789", senha_hash)
    assert not verificar_senha(funcionario_test_data["senha"], senha_hash)

@pytest.mark.asyncio
async def test_delete_funcionario(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para desativar um funcionário (soft delete).
    """
    # Criar um funcionário
    funcionario_dict = {
        "nome": "Funcionário para Desativar",
        "cpf": "999.888.777-66",
        "email": "desativar@exemplo.com",
        "usuario": "desativar",
        "senha": gerar_senha_hash("Senha@123"),
        "cargo": "Temporário",
        "ativo": True
    }
    
    db_funcionario = Funcionario(**funcionario_dict, id_empresa=DEFAULT_EMPRESA_ID)
    db.add(db_funcionario)
    await db.commit()
    await db.refresh(db_funcionario)
    
    # Desativar o funcionário (soft delete)
    response = await client.delete(
        f"/api/v1/funcionarios/{db_funcionario.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verificar se foi marcado como inativo
    result = await db.execute(f"SELECT ativo FROM funcionarios WHERE id = {db_funcionario.id}")
    is_active = result.scalar()
    assert is_active is False
    
    # O registro ainda deve existir
    check_response = await client.get(
        f"/api/v1/funcionarios/{db_funcionario.id}",
        headers=auth_headers
    )
    assert check_response.status_code == 200
    assert check_response.json()["ativo"] is False

@pytest.mark.asyncio
async def test_get_funcionario_me(client: AsyncClient, auth_headers: dict):
    """
    Teste para obter o funcionário logado.
    """
    response = await client.get(
        "/api/v1/funcionarios/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["usuario"] == "testuser"