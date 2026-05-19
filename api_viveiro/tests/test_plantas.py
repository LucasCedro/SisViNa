import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.especies import Especie
from app.models.plantas import Planta
from app.models.canteiros import Canteiro

# Dados de teste
especie_test_data = {
    "nome_cientifico": "Araucaria angustifolia",
    "nome_popular": "Pinheiro-do-Paraná",
    "familia": "Araucariaceae"
}

canteiro_test_data = {
    "nome": "Canteiro A",
    "descricao": "Canteiro para plantas nativas",
    "area_total": 100.0,
    "tipo_solo": "Argiloso"
}

planta_test_data = {
    "codigo_rastreio": "PL-TEST001",
    "data_plantio": "2023-01-01",
    "altura_atual": 1.5,
    "diametro_caule": 2.0,
    "coordenada_x": 10.0,
    "coordenada_y": 15.0,
    "status": "MUDA",
    "observacoes": "Planta de teste",
    "preco_venda": 50.0
}

@pytest.mark.asyncio
async def test_create_planta(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para criar uma nova planta.
    """
    # Primeiro, criar uma espécie
    db_especie = Especie(**especie_test_data)
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    
    # Criar um canteiro
    db_canteiro = Canteiro(**canteiro_test_data)
    db.add(db_canteiro)
    await db.commit()
    await db.refresh(db_canteiro)
    
    # Dados da planta
    create_data = {
        **planta_test_data,
        "id_especie": db_especie.id,
        "id_canteiro": db_canteiro.id
    }
    
    # Criar a planta
    response = await client.post(
        "/api/v1/plantas/",
        json=create_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["codigo_rastreio"] == planta_test_data["codigo_rastreio"]
    assert data["id_especie"] == db_especie.id
    assert data["id_canteiro"] == db_canteiro.id
    assert "id" in data
    assert "data_cadastro" in data

@pytest.mark.asyncio
async def test_read_planta(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler uma planta específica.
    """
    # Criar espécie
    db_especie = Especie(**especie_test_data)
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    
    # Criar canteiro
    db_canteiro = Canteiro(**canteiro_test_data)
    db.add(db_canteiro)
    await db.commit()
    await db.refresh(db_canteiro)
    
    # Criar planta
    db_planta = Planta(**planta_test_data, id_especie=db_especie.id, id_canteiro=db_canteiro.id)
    db.add(db_planta)
    await db.commit()
    await db.refresh(db_planta)
    
    # Ler a planta
    response = await client.get(
        f"/api/v1/plantas/{db_planta.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["codigo_rastreio"] == planta_test_data["codigo_rastreio"]
    assert data["id"] == db_planta.id

@pytest.mark.asyncio
async def test_read_plantas(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler todas as plantas.
    """
    # Criar espécie
    db_especie = Especie(**especie_test_data)
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    
    # Criar plantas
    planta1 = Planta(codigo_rastreio="PL-TEST001", id_especie=db_especie.id, status="MUDA")
    planta2 = Planta(codigo_rastreio="PL-TEST002", id_especie=db_especie.id, status="JOVEM")
    
    db.add(planta1)
    db.add(planta2)
    await db.commit()
    
    # Ler todas as plantas
    response = await client.get(
        "/api/v1/plantas/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

@pytest.mark.asyncio
async def test_update_planta(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para atualizar uma planta.
    """
    # Criar espécie
    db_especie = Especie(**especie_test_data)
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    
    # Criar canteiro
    db_canteiro = Canteiro(**canteiro_test_data)
    db.add(db_canteiro)
    await db.commit()
    await db.refresh(db_canteiro)
    
    # Criar planta
    db_planta = Planta(**planta_test_data, id_especie=db_especie.id, id_canteiro=db_canteiro.id)
    db.add(db_planta)
    await db.commit()
    await db.refresh(db_planta)
    
    # Atualizar a planta
    update_data = {
        "altura_atual": 2.5,
        "status": "JOVEM",
        "observacoes": "Planta atualizada"
    }
    
    response = await client.put(
        f"/api/v1/plantas/{db_planta.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["altura_atual"] == 2.5
    assert data["status"] == "JOVEM"
    assert data["observacoes"] == "Planta atualizada"
    assert data["codigo_rastreio"] == planta_test_data["codigo_rastreio"]  # Não alterado

@pytest.mark.asyncio
async def test_delete_planta(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para deletar uma planta.
    """
    # Criar espécie
    db_especie = Especie(**especie_test_data)
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    
    # Criar planta
    db_planta = Planta(codigo_rastreio="PL-DELETAR", id_especie=db_especie.id, status="MUDA")
    db.add(db_planta)
    await db.commit()
    await db.refresh(db_planta)
    
    # Deletar a planta
    response = await client.delete(
        f"/api/v1/plantas/{db_planta.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verificar se foi realmente deletado
    check_response = await client.get(
        f"/api/v1/plantas/{db_planta.id}",
        headers=auth_headers
    )
    assert check_response.status_code == 404

@pytest.mark.asyncio
async def test_create_plantas_bulk(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para criar múltiplas plantas de uma vez.
    """
    # Criar espécie
    db_especie = Especie(**especie_test_data)
    db.add(db_especie)
    await db.commit()
    await db.refresh(db_especie)
    
    # Dados básicos para criação em massa
    bulk_data = {
        "id_especie": db_especie.id,
        "status": "SEMENTE",
    }
    
    # Criar múltiplas plantas
    response = await client.post(
        "/api/v1/plantas/bulk?quantidade=5",
        json=bulk_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    # Verificar se todas têm o mesmo id_especie
    assert all(item["id_especie"] == db_especie.id for item in data)
    # Verificar se todas têm códigos de rastreio únicos
    codigos = [item["codigo_rastreio"] for item in data]
    assert len(codigos) == len(set(codigos))  # Não há duplicatas