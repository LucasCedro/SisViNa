import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insumos import Insumo
from app.models.atividades import InsumoAtividade, Atividade
from app.models.funcionarios import Funcionario
from app.models.plantas import Planta
from app.models.especies import Especie
from app.models.tipos_atividades import TipoAtividade
from tests.tenant_fixtures import DEFAULT_EMPRESA_ID, DEFAULT_VIVEIRO_ID

# Dados de teste
insumo_test_data = {
    "nome": "Adubo Orgânico",
    "tipo": "Fertilizante",
    "descricao": "Adubo para enriquecimento do solo",
    "unidade_medida": "kg",
    "quantidade_estoque": 100.0,
    "preco_unitario": 15.50,
    "fornecedor": "Fornecedor Teste"
}

@pytest.mark.asyncio
async def test_create_insumo(client: AsyncClient, auth_headers: dict):
    """
    Teste para criar um novo insumo.
    """
    response = await client.post(
        "/api/v1/insumos/",
        json=insumo_test_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == insumo_test_data["nome"]
    assert data["tipo"] == insumo_test_data["tipo"]
    assert data["quantidade_estoque"] == insumo_test_data["quantidade_estoque"]
    assert "id" in data
    assert "data_cadastro" in data

@pytest.mark.asyncio
async def test_read_insumo(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler um insumo específico.
    """
    # Primeiro, criar um insumo
    db_insumo = Insumo(**insumo_test_data)
    db.add(db_insumo)
    await db.commit()
    await db.refresh(db_insumo)
    
    # Agora, ler o insumo
    response = await client.get(
        f"/api/v1/insumos/{db_insumo.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == insumo_test_data["nome"]
    assert data["id"] == db_insumo.id

@pytest.mark.asyncio
async def test_read_insumos(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler todos os insumos.
    """
    # Criar insumos
    insumo1 = Insumo(nome="Substrato", tipo="Solo", quantidade_estoque=50.0, preco_unitario=12.0)
    insumo2 = Insumo(nome="Irrigador", tipo="Equipamento", quantidade_estoque=10.0, preco_unitario=35.0)
    
    db.add(insumo1)
    db.add(insumo2)
    await db.commit()
    
    # Ler todos os insumos
    response = await client.get(
        "/api/v1/insumos/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

@pytest.mark.asyncio
async def test_update_insumo(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para atualizar um insumo.
    """
    # Criar um insumo
    db_insumo = Insumo(**insumo_test_data)
    db.add(db_insumo)
    await db.commit()
    await db.refresh(db_insumo)
    
    # Atualizar o insumo
    update_data = {
        "quantidade_estoque": 85.0,
        "preco_unitario": 16.75,
        "descricao": "Adubo orgânico de alta qualidade"
    }
    
    response = await client.put(
        f"/api/v1/insumos/{db_insumo.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantidade_estoque"] == update_data["quantidade_estoque"]
    assert data["preco_unitario"] == update_data["preco_unitario"]
    assert data["descricao"] == update_data["descricao"]
    assert data["nome"] == insumo_test_data["nome"]  # Não alterado

@pytest.mark.asyncio
async def test_delete_insumo(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para deletar um insumo.
    """
    # Criar um insumo
    db_insumo = Insumo(nome="Insumo para Deletar", tipo="Teste", quantidade_estoque=1.0)
    db.add(db_insumo)
    await db.commit()
    await db.refresh(db_insumo)
    
    # Deletar o insumo
    response = await client.delete(
        f"/api/v1/insumos/{db_insumo.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verificar se foi realmente deletado
    check_response = await client.get(
        f"/api/v1/insumos/{db_insumo.id}",
        headers=auth_headers
    )
    assert check_response.status_code == 404

@pytest.mark.asyncio
async def test_atualizar_estoque_insumo(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para atualizar o estoque de um insumo.
    """
    # Criar um insumo
    db_insumo = Insumo(**insumo_test_data)
    db.add(db_insumo)
    await db.commit()
    await db.refresh(db_insumo)
    
    estoque_inicial = float(db_insumo.quantidade_estoque)
    
    # Adicionar ao estoque
    response = await client.post(
        f"/api/v1/insumos/{db_insumo.id}/estoque",
        json={
            "quantidade": 25.0,
            "data_compra": "2023-05-15"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantidade_estoque"] == estoque_inicial + 25.0
    
    # Reduzir do estoque
    response = await client.post(
        f"/api/v1/insumos/{db_insumo.id}/estoque",
        json={
            "quantidade": -10.0
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantidade_estoque"] == estoque_inicial + 25.0 - 10.0

@pytest.mark.asyncio
async def test_get_insumos_com_usos(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para obter insumos com suas estatísticas de uso.
    """
    # Configuração: criar dados necessários
    # 1. Insumo
    db_insumo = Insumo(**insumo_test_data)
    db.add(db_insumo)
    
    # 2. Espécie e planta
    db_especie = Especie(nome_cientifico="Teste Especie", nome_popular="Espécie de Teste")
    db.add(db_especie)
    
    # 3. Planta
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=1, codigo_rastreio="PL-TESTE", status="MUDA")
    db.add(db_planta)
    
    # 4. Funcionário
    db_funcionario = Funcionario(
        id_empresa=DEFAULT_EMPRESA_ID,
        nome="Func Teste", 
        cpf="000.111.222-33", 
        usuario="functeste", 
        senha="hash_senha"
    )
    db.add(db_funcionario)
    
    # 5. Tipo de atividade
    db_tipo = TipoAtividade(nome="ADUBAÇÃO", gera_custo=True)
    db.add(db_tipo)
    
    await db.commit()
    await db.refresh(db_insumo)
    await db.refresh(db_especie)
    await db.refresh(db_planta)
    await db.refresh(db_funcionario)
    await db.refresh(db_tipo)
    
    # 6. Atividade
    db_atividade = Atividade(
        id_tipo_atividade=db_tipo.id,
        id_planta=db_planta.id,
        id_funcionario=db_funcionario.id,
        data_atividade="2023-01-15T10:00:00",
        custo_atividade=20.0
    )
    db.add(db_atividade)
    await db.commit()
    await db.refresh(db_atividade)
    
    # 7. Uso de insumo na atividade
    db_insumo_atividade = InsumoAtividade(
        id_atividade=db_atividade.id,
        id_insumo=db_insumo.id,
        quantidade_usada=2.0,
        custo_total=20.0
    )
    db.add(db_insumo_atividade)
    await db.commit()
    
    # Fazer a requisição
    response = await client.get(
        "/api/v1/insumos/com-usos",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Encontrar o insumo de teste nos resultados
    insumo_info = next((item for item in data if item["id"] == db_insumo.id), None)
    assert insumo_info is not None
    assert insumo_info["total_usos"] >= 1
    assert insumo_info["quantidade_total_usada"] >= 2.0
    assert insumo_info["valor_total_usado"] >= 20.0

@pytest.mark.asyncio
async def test_get_tipos_insumos(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para obter a lista de tipos de insumos.
    """
    # Criar insumos com diferentes tipos
    insumo1 = Insumo(nome="Insumo Tipo A", tipo="Fertilizante", quantidade_estoque=10.0)
    insumo2 = Insumo(nome="Insumo Tipo B", tipo="Solo", quantidade_estoque=10.0)
    insumo3 = Insumo(nome="Insumo Tipo C", tipo="Equipamento", quantidade_estoque=10.0)
    
    db.add(insumo1)
    db.add(insumo2)
    db.add(insumo3)
    await db.commit()
    
    # Obter a lista de tipos
    response = await client.get(
        "/api/v1/insumos/tipos",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "Fertilizante" in data
    assert "Solo" in data
    assert "Equipamento" in data