import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.tipos_atividades import TipoAtividade
from app.models.atividades import Atividade, InsumoAtividade
from app.models.plantas import Planta
from app.models.especies import Especie
from app.models.funcionarios import Funcionario
from app.models.insumos import Insumo
from tests.tenant_fixtures import DEFAULT_EMPRESA_ID, DEFAULT_VIVEIRO_ID

# Dados de teste
tipo_atividade_test_data = {
    "nome": "PODA",
    "descricao": "Poda das folhas e galhos",
    "gera_custo": True
}

atividade_test_data = {
    "data_atividade": datetime.now().isoformat(),
    "descricao": "Poda para estimular crescimento",
    "custo_atividade": 15.0,
    "observacoes": "Realizada com sucesso"
}

insumo_test_data = {
    "nome": "Tesoura de Poda",
    "tipo": "Equipamento",
    "unidade_medida": "un",
    "quantidade_estoque": 5.0,
    "preco_unitario": 45.0
}

@pytest.mark.asyncio
async def test_create_tipo_atividade(client: AsyncClient, auth_headers: dict):
    """
    Teste para criar um novo tipo de atividade.
    """
    response = await client.post(
        "/api/v1/atividades/tipos",
        json=tipo_atividade_test_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == tipo_atividade_test_data["nome"]
    assert data["gera_custo"] == tipo_atividade_test_data["gera_custo"]
    assert "id" in data

@pytest.mark.asyncio
async def test_read_tipos_atividades(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """
    Teste para ler todos os tipos de atividades.
    """
    # Criar tipos de atividades
    tipo1 = TipoAtividade(nome="PLANTIO", descricao="Plantio inicial", gera_custo=True)
    tipo2 = TipoAtividade(nome="INSPECAO", descricao="Inspeção de rotina", gera_custo=False)
    
    db.add(tipo1)
    db.add(tipo2)
    await db.commit()
    
    # Ler todos os tipos
    response = await client.get(
        "/api/v1/atividades/tipos",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert any(item["nome"] == "PLANTIO" for item in data)
    assert any(item["nome"] == "INSPECAO" for item in data)

@pytest.mark.asyncio
async def test_create_atividade(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para criar uma nova atividade.
    """
    # Criar dados necessários
    # 1. Tipo de atividade
    db_tipo = TipoAtividade(**tipo_atividade_test_data)
    db.add(db_tipo)
    
    # 2. Espécie
    db_especie = Especie(nome_cientifico="Teste Atividade", nome_popular="Atividade Teste")
    db.add(db_especie)
    
    await db.commit()
    await db.refresh(db_tipo)
    await db.refresh(db_especie)
    
    # 3. Planta
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-ATIV", status="MUDA")
    db.add(db_planta)
    await db.commit()
    await db.refresh(db_planta)
    
    # Dados para a atividade
    atividade_data = {
        **atividade_test_data,
        "id_tipo_atividade": db_tipo.id,
        "id_planta": db_planta.id,
        "id_funcionario": test_user["user"].id
    }
    
    # Criar a atividade
    response = await client.post(
        "/api/v1/atividades/",
        json=atividade_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id_tipo_atividade"] == db_tipo.id
    assert data["id_planta"] == db_planta.id
    assert data["id_funcionario"] == test_user["user"].id
    assert data["custo_atividade"] == atividade_test_data["custo_atividade"]
    assert "id" in data
    assert "data_registro" in data
    
    # Verificar se o custo foi adicionado à planta
    planta_query = f"SELECT custo_atual FROM plantas WHERE id = {db_planta.id}"
    planta_result = await db.execute(planta_query)
    custo_planta = float(planta_result.scalar())
    assert custo_planta == atividade_test_data["custo_atividade"]

@pytest.mark.asyncio
async def test_create_atividade_com_insumos(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para criar uma atividade com insumos.
    """
    # Criar dados necessários
    # 1. Tipo de atividade
    db_tipo = TipoAtividade(nome="FERTILIZACAO", descricao="Aplicação de fertilizantes", gera_custo=True)
    db.add(db_tipo)
    
    # 2. Espécie e planta
    db_especie = Especie(nome_cientifico="Espécie Insumo", nome_popular="Insumo Teste")
    db.add(db_especie)
    await db.commit()
    
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-INSUMO", status="JOVEM")
    db.add(db_planta)
    
    # 3. Insumo
    db_insumo = Insumo(**insumo_test_data)
    db.add(db_insumo)
    
    await db.commit()
    await db.refresh(db_tipo)
    await db.refresh(db_planta)
    await db.refresh(db_insumo)
    
    # Dados para a atividade com insumos
    atividade_data = {
        "id_tipo_atividade": db_tipo.id,
        "id_planta": db_planta.id,
        "id_funcionario": test_user["user"].id,
        "data_atividade": datetime.now().isoformat(),
        "descricao": "Fertilização trimestral",
        "custo_atividade": 0.0,  # Será calculado com base nos insumos
        "insumos": [
            {
                "id_insumo": db_insumo.id,
                "quantidade_usada": 2.0,
                "custo_total": 90.0  # 2 * 45.0
            }
        ]
    }
    
    # Criar a atividade
    response = await client.post(
        "/api/v1/atividades/",
        json=atividade_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id_tipo_atividade"] == db_tipo.id
    assert data["custo_atividade"] == 90.0
    assert "insumos_utilizados" in data
    assert len(data["insumos_utilizados"]) == 1
    assert data["insumos_utilizados"][0]["id_insumo"] == db_insumo.id
    
    # Verificar se o estoque do insumo foi atualizado
    insumo_query = f"SELECT quantidade_estoque FROM insumos WHERE id = {db_insumo.id}"
    insumo_result = await db.execute(insumo_query)
    estoque_atual = float(insumo_result.scalar())
    assert estoque_atual == 3.0  # 5.0 - 2.0
    
    # Verificar se o custo foi adicionado à planta
    planta_query = f"SELECT custo_atual FROM plantas WHERE id = {db_planta.id}"
    planta_result = await db.execute(planta_query)
    custo_planta = float(planta_result.scalar())
    assert custo_planta == 90.0

@pytest.mark.asyncio
async def test_read_atividade(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para ler uma atividade específica.
    """
    # Criar dados necessários
    # 1. Tipo de atividade
    db_tipo = TipoAtividade(nome="REGA", descricao="Rega das plantas", gera_custo=True)
    db.add(db_tipo)
    
    # 2. Espécie e planta
    db_especie = Especie(nome_cientifico="Espécie Leitura", nome_popular="Leitura Teste")
    db.add(db_especie)
    await db.commit()
    
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-LEITURA", status="MUDA")
    db.add(db_planta)
    await db.commit()
    
    # 3. Atividade
    db_atividade = Atividade(
        id_tipo_atividade=db_tipo.id,
        id_planta=db_planta.id,
        id_funcionario=test_user["user"].id,
        data_atividade=datetime.now(),
        descricao="Rega matinal",
        custo_atividade=5.0
    )
    db.add(db_atividade)
    await db.commit()
    await db.refresh(db_atividade)
    
    # Ler a atividade
    response = await client.get(
        f"/api/v1/atividades/{db_atividade.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == db_atividade.id
    assert data["descricao"] == "Rega matinal"
    assert data["custo_atividade"] == 5.0
    assert "tipo_atividade" in data
    assert data["tipo_atividade"]["nome"] == "REGA"

@pytest.mark.asyncio
async def test_read_atividades(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para ler todas as atividades.
    """
    # Criar dados necessários
    # 1. Tipo de atividade
    db_tipo = TipoAtividade(nome="MEDICACAO", descricao="Aplicação de medicamentos", gera_custo=True)
    db.add(db_tipo)
    
    # 2. Espécie e planta
    db_especie = Especie(nome_cientifico="Espécie Lista", nome_popular="Lista Teste")
    db.add(db_especie)
    await db.commit()
    
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-LISTA", status="JOVEM")
    db.add(db_planta)
    await db.commit()
    
    # 3. Atividades
    atividade1 = Atividade(
        id_tipo_atividade=db_tipo.id,
        id_planta=db_planta.id,
        id_funcionario=test_user["user"].id,
        data_atividade=datetime.now(),
        descricao="Aplicação 1",
        custo_atividade=10.0
    )
    
    atividade2 = Atividade(
        id_tipo_atividade=db_tipo.id,
        id_planta=db_planta.id,
        id_funcionario=test_user["user"].id,
        data_atividade=datetime.now(),
        descricao="Aplicação 2",
        custo_atividade=15.0
    )
    
    db.add(atividade1)
    db.add(atividade2)
    await db.commit()
    
    # Ler todas as atividades
    response = await client.get(
        "/api/v1/atividades/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    
    # Verificar se as atividades recém-criadas estão na lista
    assert any(item["descricao"] == "Aplicação 1" for item in data)
    assert any(item["descricao"] == "Aplicação 2" for item in data)
    
    # Verificar se os dados completos estão presentes
    for item in data:
        assert "tipo_atividade_nome" in item
        assert "funcionario_nome" in item
        assert "planta_codigo" in item
        assert "especie_nome" in item

@pytest.mark.asyncio
async def test_update_atividade(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para atualizar uma atividade.
    """
    # Criar dados necessários
    # 1. Tipo de atividade
    db_tipo = TipoAtividade(nome="TRANSPLANTE", descricao="Transplante de mudas", gera_custo=True)
    db.add(db_tipo)
    
    # 2. Espécie e planta
    db_especie = Especie(nome_cientifico="Espécie Update", nome_popular="Update Teste")
    db.add(db_especie)
    await db.commit()
    
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-UPDATE", status="MUDA")
    db.add(db_planta)
    await db.commit()
    
    # 3. Atividade
    db_atividade = Atividade(
        id_tipo_atividade=db_tipo.id,
        id_planta=db_planta.id,
        id_funcionario=test_user["user"].id,
        data_atividade=datetime.now(),
        descricao="Transplante inicial",
        custo_atividade=20.0
    )
    db.add(db_atividade)
    await db.commit()
    await db.refresh(db_atividade)
    
    # Registrar custo atual da planta
    planta_query = f"SELECT custo_atual FROM plantas WHERE id = {db_planta.id}"
    planta_result = await db.execute(planta_query)
    custo_inicial = float(planta_result.scalar())
    
    # Atualizar a atividade
    update_data = {
        "descricao": "Transplante corretivo",
        "custo_atividade": 30.0,  # Aumentou o custo
        "observacoes": "Transplante realizado com sucesso"
    }
    
    response = await client.put(
        f"/api/v1/atividades/{db_atividade.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["descricao"] == update_data["descricao"]
    assert data["custo_atividade"] == update_data["custo_atividade"]
    assert data["observacoes"] == update_data["observacoes"]
    
    # Verificar se o custo da planta foi atualizado
    planta_result = await db.execute(planta_query)
    custo_final = float(planta_result.scalar())
    assert custo_final == custo_inicial + (update_data["custo_atividade"] - 20.0)  # 30.0 - 20.0 = 10.0

@pytest.mark.asyncio
async def test_delete_atividade(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para deletar uma atividade.
    """
    # Criar dados necessários
    # 1. Tipo de atividade
    db_tipo = TipoAtividade(nome="REMOCAO", descricao="Remoção de folhas secas", gera_custo=True)
    db.add(db_tipo)
    
    # 2. Espécie e planta
    db_especie = Especie(nome_cientifico="Espécie Delete", nome_popular="Delete Teste")
    db.add(db_especie)
    await db.commit()
    
    db_planta = Planta(id_viveiro=DEFAULT_VIVEIRO_ID, id_especie=db_especie.id, codigo_rastreio="PL-DELETE", status="ADULTA")
    db.add(db_planta)
    await db.commit()
    
    # 3. Atividade
    db_atividade = Atividade(
        id_tipo_atividade=db_tipo.id,
        id_planta=db_planta.id,
        id_funcionario=test_user["user"].id,
        data_atividade=datetime.now(),
        descricao="Remoção folhas secas",
        custo_atividade=8.0
    )
    db.add(db_atividade)
    await db.commit()
    await db.refresh(db_atividade)
    
    # Atualizar o custo da planta
    await db.execute(f"UPDATE plantas SET custo_atual = 8.0 WHERE id = {db_planta.id}")
    await db.commit()
    
    # Deletar a atividade
    response = await client.delete(
        f"/api/v1/atividades/{db_atividade.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verificar se foi realmente deletado
    check_response = await client.get(
        f"/api/v1/atividades/{db_atividade.id}",
        headers=auth_headers
    )
    assert check_response.status_code == 404
    
    # Verificar se o custo foi removido da planta
    planta_query = f"SELECT custo_atual FROM plantas WHERE id = {db_planta.id}"
    planta_result = await db.execute(planta_query)
    custo_final = float(planta_result.scalar())
    assert custo_final == 0.0  # 8.0 - 8.0 = 0.0