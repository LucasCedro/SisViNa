import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.compradores import Comprador
from app.models.vendas import Venda
from app.models.funcionarios import Funcionario
from app.auth.utils import gerar_senha_hash, verificar_senha

# Dados de teste
comprador_pf_test_data = {
    "tipo": "PF",
    "nome": "Maria Silva",
    "cpf_cnpj": "987.654.321-00",
    "telefone": "(11) 98765-4321",
    "email": "maria.silva@exemplo.com",
    "endereco": "Avenida Principal, 456",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "01234-567",
    "usuario": "mariasilva",
    "senha": "Senha@123",
    "ativo": True
}

comprador_pj_test_data = {
    "tipo": "PJ",
    "nome": "Empresa Teste LTDA",
    "cpf_cnpj": "12.345.678/0001-90",
    "telefone": "(11) 3456-7890",
    "email": "contato@empresa.com",
    "endereco": "Rua Empresarial, 789",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "04567-890",
    "usuario": "empresateste",
    "senha": "Senha@456",
    "ativo": True
}

@pytest.mark.asyncio
async def test_create_comprador_pf(client: AsyncClient, auth_headers: dict):
    """
    Teste para criar um novo comprador pessoa física.
    """
    response = await client.post(
        "/api/v1/compradores/",
        json=comprador_pf_test_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == comprador_pf_test_data["nome"]
    assert data["tipo"] == "PF"
    assert data["cpf_cnpj"] == comprador_pf_test_data["cpf_cnpj"]
    assert "id" in data
    assert "data_cadastro" in data
    assert "senha" not in data  # A senha não deve ser retornada

@pytest.mark.asyncio
async def test_create_comprador_pj(client: AsyncClient, auth_headers: dict):
    """
    Teste para criar um novo comprador pessoa jurídica.
    """
    response = await client.post(
        "/api/v1/compradores/",
        json=comprador_pj_test_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == comprador_pj_test_data["nome"]
    assert data["tipo"] == "PJ"
    assert data["cpf_cnpj"] == comprador_pj_test_data["cpf_cnpj"]
    assert "id" in data
    assert "data_cadastro" in data
    assert "senha" not in data  # A senha não deve ser retornada

@pytest.mark.asyncio
async def test_read_comprador(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler um comprador específico.
    """
    # Primeiro, criar um comprador
    comprador_dict = comprador_pf_test_data.copy()
    senha = comprador_dict.pop("senha")
    hashed_password = gerar_senha_hash(senha) if senha else None
    db_comprador = Comprador(**comprador_dict, senha=hashed_password)
    db.add(db_comprador)
    await db.commit()
    await db.refresh(db_comprador)
    
    # Agora, ler o comprador
    response = await client.get(
        f"/api/v1/compradores/{db_comprador.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == comprador_pf_test_data["nome"]
    assert data["id"] == db_comprador.id
    assert "senha" not in data  # A senha não deve ser retornada

@pytest.mark.asyncio
async def test_read_compradores(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler todos os compradores.
    """
    # Criar compradores
    comprador1_dict = {
        "tipo": "PF",
        "nome": "João Oliveira",
        "cpf_cnpj": "111.222.333-45",
        "email": "joao@exemplo.com",
        "usuario": "joaooliveira",
        "ativo": True
    }
    
    comprador2_dict = {
        "tipo": "PJ",
        "nome": "Negócios Inovadores S.A.",
        "cpf_cnpj": "98.765.432/0001-10",
        "email": "contato@negocios.com",
        "usuario": "negocios",
        "ativo": True
    }
    
    db_comprador1 = Comprador(**comprador1_dict)
    db_comprador2 = Comprador(**comprador2_dict)
    
    db.add(db_comprador1)
    db.add(db_comprador2)
    await db.commit()
    
    # Ler todos os compradores
    response = await client.get(
        "/api/v1/compradores/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    # Verificar se as senhas não são retornadas
    assert all("senha" not in item for item in data)

@pytest.mark.asyncio
async def test_read_compradores_com_filtro(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler compradores filtrados por tipo.
    """
    # Criar compradores
    comprador1_dict = {
        "tipo": "PF",
        "nome": "Ana Pereira",
        "cpf_cnpj": "555.666.777-88",
        "email": "ana@exemplo.com",
        "ativo": True
    }
    
    comprador2_dict = {
        "tipo": "PJ",
        "nome": "Tech Solutions LTDA",
        "cpf_cnpj": "11.222.333/0001-44",
        "email": "contato@tech.com",
        "ativo": True
    }
    
    db_comprador1 = Comprador(**comprador1_dict)
    db_comprador2 = Comprador(**comprador2_dict)
    
    db.add(db_comprador1)
    db.add(db_comprador2)
    await db.commit()
    
    # Ler compradores PF
    response_pf = await client.get(
        "/api/v1/compradores/?tipo=PF",
        headers=auth_headers
    )
    
    assert response_pf.status_code == 200
    data_pf = response_pf.json()
    assert isinstance(data_pf, list)
    assert all(item["tipo"] == "PF" for item in data_pf)
    
    # Ler compradores PJ
    response_pj = await client.get(
        "/api/v1/compradores/?tipo=PJ",
        headers=auth_headers
    )
    
    assert response_pj.status_code == 200
    data_pj = response_pj.json()
    assert isinstance(data_pj, list)
    assert all(item["tipo"] == "PJ" for item in data_pj)

@pytest.mark.asyncio
async def test_update_comprador(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para atualizar um comprador.
    """
    # Criar um comprador
    comprador_dict = comprador_pf_test_data.copy()
    senha = comprador_dict.pop("senha")
    hashed_password = gerar_senha_hash(senha) if senha else None
    db_comprador = Comprador(**comprador_dict, senha=hashed_password)
    db.add(db_comprador)
    await db.commit()
    await db.refresh(db_comprador)
    
    # Atualizar o comprador
    update_data = {
        "telefone": "(11) 91234-5678",
        "endereco": "Rua Nova, 789",
        "cep": "09876-543"
    }
    
    response = await client.put(
        f"/api/v1/compradores/{db_comprador.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["telefone"] == update_data["telefone"]
    assert data["endereco"] == update_data["endereco"]
    assert data["cep"] == update_data["cep"]
    assert data["nome"] == comprador_pf_test_data["nome"]  # Não alterado

@pytest.mark.asyncio
async def test_update_comprador_senha(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para atualizar a senha de um comprador.
    """
    # Criar um comprador
    comprador_dict = comprador_pf_test_data.copy()
    senha = comprador_dict.pop("senha")
    hashed_password = gerar_senha_hash(senha) if senha else None
    db_comprador = Comprador(**comprador_dict, senha=hashed_password)
    db.add(db_comprador)
    await db.commit()
    await db.refresh(db_comprador)
    
    # Atualizar a senha
    update_data = {
        "senha": "NovaSenha@789"
    }
    
    response = await client.put(
        f"/api/v1/compradores/{db_comprador.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Buscar o comprador atualizado no banco
    result = await db.execute(f"SELECT senha FROM compradores WHERE id = {db_comprador.id}")
    senha_hash = result.scalar()
    
    # Verificar se a nova senha está correta
    assert verificar_senha("NovaSenha@789", senha_hash)
    assert not verificar_senha(comprador_pf_test_data["senha"], senha_hash)

@pytest.mark.asyncio
async def test_delete_comprador(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para desativar um comprador (soft delete).
    """
    # Criar um comprador
    comprador_dict = {
        "tipo": "PF",
        "nome": "Comprador para Desativar",
        "cpf_cnpj": "123.456.789-99",
        "email": "desativar@exemplo.com",
        "ativo": True
    }
    
    db_comprador = Comprador(**comprador_dict)
    db.add(db_comprador)
    await db.commit()
    await db.refresh(db_comprador)
    
    # Desativar o comprador (soft delete)
    response = await client.delete(
        f"/api/v1/compradores/{db_comprador.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verificar se foi marcado como inativo
    result = await db.execute(f"SELECT ativo FROM compradores WHERE id = {db_comprador.id}")
    is_active = result.scalar()
    assert is_active is False
    
    # O registro ainda deve existir
    check_response = await client.get(
        f"/api/v1/compradores/{db_comprador.id}",
        headers=auth_headers
    )
    assert check_response.status_code == 200
    assert check_response.json()["ativo"] is False

@pytest.mark.asyncio
async def test_get_compradores_with_vendas(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para obter compradores com informações de vendas.
    """
    # Criar um comprador
    db_comprador = Comprador(
        tipo="PF",
        nome="Comprador Com Vendas",
        cpf_cnpj="444.555.666-77",
        email="vendas@exemplo.com",
        ativo=True
    )
    db.add(db_comprador)
    await db.commit()
    await db.refresh(db_comprador)
    
    # Criar algumas vendas para o comprador
    venda1 = Venda(
        id_comprador=db_comprador.id,
        id_funcionario=test_user["user"].id,
        data_venda=datetime.now(),
        valor_total=100.0,
        status="PAGO"
    )
    
    venda2 = Venda(
        id_comprador=db_comprador.id,
        id_funcionario=test_user["user"].id,
        data_venda=datetime.now(),
        valor_total=150.0,
        status="PENDENTE"
    )
    
    db.add(venda1)
    db.add(venda2)
    await db.commit()
    
    # Obter compradores com informações de vendas
    response = await client.get(
        "/api/v1/compradores/with-vendas",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Encontrar o comprador de teste na lista
    comprador_info = next((item for item in data if item["id"] == db_comprador.id), None)
    assert comprador_info is not None
    assert comprador_info["total_vendas"] == 2
    assert comprador_info["valor_total_compras"] == 250.0  # 100.0 + 150.0
    
    # Verificar se a senha não é retornada
    assert "senha" not in comprador_info