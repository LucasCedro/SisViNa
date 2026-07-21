import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime

from app.models.pragas import TipoPraga, MetodoCombate, PragaPlanta, CombateRealizado
from app.models.plantas import Planta
from app.models.especies import Especie
from app.models.funcionarios import Funcionario
from tests.tenant_fixtures import DEFAULT_EMPRESA_ID, DEFAULT_VIVEIRO_ID

# Dados de teste
tipo_praga_test_data = {
    "nome": "Cochonilha",
    "descricao": "Inseto que suga a seiva das plantas",
    "metodo_identificacao": "Manchas brancas nas folhas e caules"
}

metodo_combate_test_data = {
    "nome": "Calda de Fumo",
    "descricao": "Solução natural para combate de insetos",
    "produto": "Fumo de Corda",
    "dosagem": "100g para 1L de água",
    "metodo_aplicacao": "Pulverização foliar",
    "tempo_carencia": 7,
    "eficacia": "Média",
    "custo_unitario": 12.50
}

@pytest.mark.asyncio
async def test_create_tipo_praga(client: AsyncClient, auth_headers: dict):
    """
    Teste para criar um novo tipo de praga.
    """
    response = await client.post(
        "/api/v1/pragas/tipos",
        json=tipo_praga_test_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == tipo_praga_test_data["nome"]
    assert data["descricao"] == tipo_praga_test_data["descricao"]
    assert "id" in data
    assert "data_cadastro" in data

@pytest.mark.asyncio
async def test_read_tipo_praga(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler um tipo de praga específico.
    """
    # Criar um tipo de praga
    db_tipo_praga = TipoPraga(**tipo_praga_test_data)
    db.add(db_tipo_praga)
    await db.commit()
    await db.refresh(db_tipo_praga)
    
    # Ler o tipo de praga
    response = await client.get(
        f"/api/v1/pragas/tipos/{db_tipo_praga.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == tipo_praga_test_data["nome"]
    assert data["id"] == db_tipo_praga.id

@pytest.mark.asyncio
async def test_create_metodo_combate(client: AsyncClient, auth_headers: dict):
    """
    Teste para criar um novo método de combate.
    """
    response = await client.post(
        "/api/v1/pragas/metodos",
        json=metodo_combate_test_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == metodo_combate_test_data["nome"]
    assert data["dosagem"] == metodo_combate_test_data["dosagem"]
    assert data["custo_unitario"] == metodo_combate_test_data["custo_unitario"]
    assert "id" in data
    assert "data_cadastro" in data

@pytest.mark.asyncio
async def test_read_metodo_combate(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler um método de combate específico.
    """
    # Criar um método de combate
    db_metodo = MetodoCombate(**metodo_combate_test_data)
    db.add(db_metodo)
    await db.commit()
    await db.refresh(db_metodo)
    
    # Ler o método de combate
    response = await client.get(
        f"/api/v1/pragas/metodos/{db_metodo.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == metodo_combate_test_data["nome"]
    assert data["id"] == db_metodo.id

@pytest.mark.asyncio
async def test_registrar_praga_planta(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para registrar uma ocorrência de praga em uma planta.
    """
    # Criar dados necessários
    db_tipo_praga = TipoPraga(**tipo_praga_test_data)
    db.add(db_tipo_praga)
    
    db_especie = Especie(nome_cientifico="Teste Especie", nome_popular="Espécie de Teste")
    db.add(db_especie)
    
    await db.commit()
    await db.refresh(db_tipo_praga)
    await db.refresh(db_especie)
    
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-PRAGA", status="MUDA")
    db.add(db_planta)
    await db.commit()
    await db.refresh(db_planta)
    
    # Dados para registro de praga
    praga_data = {
        "id_planta": db_planta.id,
        "id_tipo_praga": db_tipo_praga.id,
        "data_identificacao": "2023-05-20",
        "nivel_infestacao": "MEDIO",
        "observacoes": "Identificado em estágio inicial"
    }
    
    # Registrar a praga
    response = await client.post(
        "/api/v1/pragas/plantas",
        json=praga_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id_planta"] == db_planta.id
    assert data["id_tipo_praga"] == db_tipo_praga.id
    assert data["nivel_infestacao"] == praga_data["nivel_infestacao"]
    assert "id" in data
    assert "data_registro" in data

@pytest.mark.asyncio
async def test_registrar_combate(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para registrar um combate a praga.
    """
    # Criar dados necessários
    db_tipo_praga = TipoPraga(nome="Pulgão", descricao="Inseto pequeno")
    db_metodo = MetodoCombate(**metodo_combate_test_data)
    db_especie = Especie(nome_cientifico="Espécie Teste", nome_popular="Teste")
    db_funcionario = Funcionario(
        nome="Func Combate", 
        cpf="222.333.444-55", 
        usuario="funccombate", 
        senha="hash_senha"
    )
    
    db.add(db_tipo_praga)
    db.add(db_metodo)
    db.add(db_especie)
    db.add(db_funcionario)
    await db.commit()
    
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-COMBATE", status="JOVEM")
    db.add(db_planta)
    await db.commit()
    
    db_praga_planta = PragaPlanta(
        id_planta=db_planta.id,
        id_tipo_praga=db_tipo_praga.id,
        data_identificacao=date.today(),
        nivel_infestacao="ALTO"
    )
    db.add(db_praga_planta)
    await db.commit()
    
    # Dados para registro de combate
    combate_data = {
        "id_praga_planta": db_praga_planta.id,
        "id_metodo_combate": db_metodo.id,
        "id_funcionario": db_funcionario.id,
        "data_aplicacao": datetime.now().isoformat(),
        "quantidade_aplicada": 0.5,
        "eficacia_observada": "BOA",
        "observacoes": "Aplicação realizada com sucesso"
    }
    
    # Registrar o combate
    response = await client.post(
        "/api/v1/pragas/combates",
        json=combate_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id_praga_planta"] == db_praga_planta.id
    assert data["id_metodo_combate"] == db_metodo.id
    assert data["id_funcionario"] == db_funcionario.id
    assert "custo_total" in data
    assert "id" in data
    assert "data_registro" in data

@pytest.mark.asyncio
async def test_get_pragas_plantas(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para obter as ocorrências de pragas em plantas.
    """
    # Criar dados necessários
    db_tipo_praga = TipoPraga(nome="Ferrugem", descricao="Doença fúngica")
    db_especie = Especie(nome_cientifico="Espécie Teste 2", nome_popular="Teste 2")
    
    db.add(db_tipo_praga)
    db.add(db_especie)
    await db.commit()
    
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-LISTAR", status="ADULTA")
    db.add(db_planta)
    await db.commit()
    
    db_praga_planta = PragaPlanta(
        id_planta=db_planta.id,
        id_tipo_praga=db_tipo_praga.id,
        data_identificacao=date.today(),
        nivel_infestacao="BAIXO"
    )
    db.add(db_praga_planta)
    await db.commit()
    
    # Obter a lista de pragas em plantas
    response = await client.get(
        "/api/v1/pragas/plantas",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Verificar se a praga criada está na lista
    praga_info = next((item for item in data if item["id"] == db_praga_planta.id), None)
    assert praga_info is not None
    assert "tipo_praga_nome" in praga_info
    assert "planta_codigo" in praga_info
    assert "especie_nome" in praga_info

@pytest.mark.asyncio
async def test_update_nivel_infestacao(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para atualizar o nível de infestação de uma praga.
    """
    # Criar dados necessários
    db_tipo_praga = TipoPraga(nome="Ácaro", descricao="Artrópode microscópico")
    db_especie = Especie(nome_cientifico="Espécie Teste 3", nome_popular="Teste 3")
    
    db.add(db_tipo_praga)
    db.add(db_especie)
    await db.commit()
    
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-UPDATE", status="ADULTA")
    db.add(db_planta)
    await db.commit()
    
    db_praga_planta = PragaPlanta(
        id_planta=db_planta.id,
        id_tipo_praga=db_tipo_praga.id,
        data_identificacao=date.today(),
        nivel_infestacao="BAIXO"
    )
    db.add(db_praga_planta)
    await db.commit()
    
    # Atualizar o nível de infestação
    update_data = {
        "nivel_infestacao": "CRITICO",
        "observacoes": "Infestação piorou muito"
    }
    
    response = await client.put(
        f"/api/v1/pragas/plantas/{db_praga_planta.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nivel_infestacao"] == "CRITICO"
    assert data["observacoes"] == "Infestação piorou muito"