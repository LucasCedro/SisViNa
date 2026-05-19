import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.especies import Especie

# Dados de teste
especie_test_data = {
    "nome_cientifico": "Ocotea porosa",
    "nome_popular": "Imbuia",
    "familia": "Lauraceae",
    "descricao": "Árvore nativa da Mata Atlântica",
    "tempo_germinacao": 30,
    "tempo_crescimento": 365,
    "altura_maxima": 20.0
}

@pytest.mark.asyncio
async def test_create_especie(client: AsyncClient, auth_headers: dict):
    """
    Teste para criar uma nova espécie.
    """
    response = await client.post(
        "/api/v1/especies/",
        json=especie_test_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome_cientifico"] == especie_test_data["nome_cientifico"]
    assert data["nome_popular"] == especie_test_data["nome_popular"]
    assert "id" in data
    assert "data_cadastro" in data

@pytest.mark.asyncio
async def test_read_especie(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler uma espécie.
    """
    # Primeiro, criar uma espécie
    db_especie = Especie(**especie_test_data)
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    
    # Agora, ler a espécie
    response = await client.get(
        f"/api/v1/especies/{db_especie.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome_cientifico"] == especie_test_data["nome_cientifico"]
    assert data["id"] == db_especie.id

@pytest.mark.asyncio
async def test_read_especies(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler todas as espécies.
    """
    # Criar várias espécies
    especie1 = Especie(nome_cientifico="Espécie 1", nome_popular="Popular 1")
    especie2 = Especie(nome_cientifico="Espécie 2", nome_popular="Popular 2")
    
    db.add(especie1)
    db.add(especie2)
    await db.commit()
    
    # Ler todas as espécies
    response = await client.get(
        "/api/v1/especies/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

@pytest.mark.asyncio
async def test_update_especie(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para atualizar uma espécie.
    """
    # Criar uma espécie
    db_especie = Especie(**especie_test_data)
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    
    # Atualizar a espécie
    update_data = {
        "nome_popular": "Imbuia Atualizada",
        "descricao": "Descrição atualizada"
    }
    
    response = await client.put(
        f"/api/v1/especies/{db_especie.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome_popular"] == update_data["nome_popular"]
    assert data["descricao"] == update_data["descricao"]
    assert data["nome_cientifico"] == especie_test_data["nome_cientifico"]  # Não alterado

@pytest.mark.asyncio
async def test_delete_especie(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para deletar uma espécie.
    """
    # Criar uma espécie
    db_especie = Especie(**especie_test_data)
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    
    # Deletar a espécie
    response = await client.delete(
        f"/api/v1/especies/{db_especie.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verificar se foi realmente deletado
    check_response = await client.get(
        f"/api/v1/especies/{db_especie.id}",
        headers=auth_headers
    )
    assert check_response.status_code == 404