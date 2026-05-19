import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.vendas import Venda, ItemVenda
from app.models.compradores import Comprador
from app.models.funcionarios import Funcionario
from app.models.plantas import Planta
from app.models.especies import Especie
from app.auth.utils import gerar_senha_hash

# Dados de teste
comprador_test_data = {
    "tipo": "PF",
    "nome": "Cliente Teste",
    "cpf_cnpj": "111.222.333-44",
    "telefone": "(11) 95555-4444",
    "email": "cliente@teste.com",
    "endereco": "Rua dos Testes, 123",
    "cidade": "Testópolis",
    "estado": "TS",
    "ativo": True
}

venda_test_data = {
    "data_venda": datetime.now().isoformat(),
    "forma_pagamento": "PIX",
    "status": "PENDENTE",
    "observacoes": "Venda de teste"
}

@pytest.mark.asyncio
async def test_create_venda(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para criar uma nova venda com itens.
    """
    # Criar dados necessários
    # 1. Comprador
    db_comprador = Comprador(**comprador_test_data)
    db.add(db_comprador)
    
    # 2. Espécie
    db_especie = Especie(nome_cientifico="Espécie Venda", nome_popular="Venda Teste")
    db.add(db_especie)
    
    await db.commit()
    await db.refresh(db_comprador)
    await db.refresh(db_especie)
    
    # 3. Plantas
    planta1 = Planta(
        id_especie=db_especie.id, 
        codigo_rastreio="PL-VENDA-1", 
        status="ADULTA",
        preco_venda=50.0
    )
    planta2 = Planta(
        id_especie=db_especie.id, 
        codigo_rastreio="PL-VENDA-2", 
        status="ADULTA",
        preco_venda=75.0
    )
    
    db.add(planta1)
    db.add(planta2)
    await db.commit()
    await db.refresh(planta1)
    await db.refresh(planta2)
    
    # Dados para a venda
    venda_data = {
        **venda_test_data,
        "id_comprador": db_comprador.id,
        "id_funcionario": test_user["user"].id,
        "itens": [
            {
                "id_planta": planta1.id,
                "quantidade": 2,
                "valor_unitario": 50.0,
                "desconto": 5.0
            },
            {
                "id_planta": planta2.id,
                "quantidade": 1,
                "valor_unitario": 75.0,
                "desconto": 0.0
            }
        ]
    }
    
    # Criar a venda
    response = await client.post(
        "/api/v1/vendas/",
        json=venda_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar dados da venda
    assert data["id_comprador"] == db_comprador.id
    assert data["id_funcionario"] == test_user["user"].id
    assert data["status"] == venda_test_data["status"]
    assert "valor_total" in data
    assert data["valor_total"] == (2 * 50.0 - 5.0) + (1 * 75.0)  # 95.0 + 75.0 = 170.0
    assert "id" in data
    
    # Verificar itens da venda
    assert "itens" in data
    assert len(data["itens"]) == 2
    
    # Verificar se o status das plantas foi alterado para VENDIDA
    for planta_id in [planta1.id, planta2.id]:
        query = f"SELECT status FROM plantas WHERE id = {planta_id}"
        result = await db.execute(query)
        status = result.scalar()
        assert status == "VENDIDA"

@pytest.mark.asyncio
async def test_read_venda(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para ler uma venda específica.
    """
    # Criar dados necessários
    # 1. Comprador
    db_comprador = Comprador(
        tipo="PJ",
        nome="Empresa Teste",
        cpf_cnpj="12.345.678/0001-90",
        email="empresa@teste.com"
    )
    db.add(db_comprador)
    
    # 2. Espécie
    db_especie = Especie(nome_cientifico="Espécie Leitura", nome_popular="Leitura Teste")
    db.add(db_especie)
    
    await db.commit()
    await db.refresh(db_comprador)
    await db.refresh(db_especie)
    
    # 3. Planta
    db_planta = Planta(
        id_especie=db_especie.id, 
        codigo_rastreio="PL-LEITURA", 
        status="ADULTA",
        preco_venda=100.0
    )
    db.add(db_planta)
    await db.commit()
    await db.refresh(db_planta)
    
    # 4. Venda
    db_venda = Venda(
        id_comprador=db_comprador.id,
        id_funcionario=test_user["user"].id,
        data_venda=datetime.now(),
        valor_total=100.0,
        forma_pagamento="CARTÃO",
        status="PAGO"
    )
    db.add(db_venda)
    await db.commit()
    await db.refresh(db_venda)
    
    # 5. Item de venda
    db_item = ItemVenda(
        id_venda=db_venda.id,
        id_planta=db_planta.id,
        quantidade=1,
        valor_unitario=100.0,
        valor_total=100.0,
        desconto=0.0
    )
    db.add(db_item)
    await db.commit()
    
    # Ler a venda
    response = await client.get(
        f"/api/v1/vendas/{db_venda.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == db_venda.id
    assert data["id_comprador"] == db_comprador.id
    assert data["comprador_nome"] == "Empresa Teste"
    assert data["valor_total"] == 100.0
    assert "itens" in data
    assert len(data["itens"]) == 1
    assert data["itens"][0]["id_planta"] == db_planta.id
    assert data["itens"][0]["valor_total"] == 100.0

@pytest.mark.asyncio
async def test_update_status_venda(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para atualizar o status de uma venda.
    """
    # Criar dados necessários
    # 1. Comprador
    db_comprador = Comprador(
        tipo="PF",
        nome="Atualizar Status",
        cpf_cnpj="555.666.777-88",
        email="status@teste.com"
    )
    db.add(db_comprador)
    await db.commit()
    
    # 2. Venda
    db_venda = Venda(
        id_comprador=db_comprador.id,
        id_funcionario=test_user["user"].id,
        data_venda=datetime.now(),
        valor_total=200.0,
        forma_pagamento="BOLETO",
        status="PENDENTE"
    )
    db.add(db_venda)
    await db.commit()
    await db.refresh(db_venda)
    
    # Atualizar o status da venda
    update_data = {
        "status": "PAGO",
        "observacoes": "Pagamento recebido"
    }
    
    response = await client.put(
        f"/api/v1/vendas/{db_venda.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PAGO"
    assert data["observacoes"] == "Pagamento recebido"
    assert data["valor_total"] == 200.0  # Valor não alterado

@pytest.mark.asyncio
async def test_cancel_venda(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para cancelar uma venda e verificar se as plantas são restauradas ao status anterior.
    """
    # Criar dados necessários
    # 1. Comprador
    db_comprador = Comprador(
        tipo="PF",
        nome="Cancelamento Teste",
        cpf_cnpj="999.888.777-66",
        email="cancelar@teste.com"
    )
    db.add(db_comprador)
    
    # 2. Espécie
    db_especie = Especie(nome_cientifico="Espécie Cancelamento", nome_popular="Cancelar Teste")
    db.add(db_especie)
    
    await db.commit()
    await db.refresh(db_comprador)
    await db.refresh(db_especie)
    
    # 3. Plantas
    db_planta = Planta(
        id_especie=db_especie.id, 
        codigo_rastreio="PL-CANCELAR", 
        status="ADULTA",
        preco_venda=150.0
    )
    db.add(db_planta)
    await db.commit()
    await db.refresh(db_planta)
    
    # 4. Venda
    db_venda = Venda(
        id_comprador=db_comprador.id,
        id_funcionario=test_user["user"].id,
        data_venda=datetime.now(),
        valor_total=150.0,
        forma_pagamento="DINHEIRO",
        status="PENDENTE"
    )
    db.add(db_venda)
    await db.commit()
    await db.refresh(db_venda)
    
    # 5. Item de venda
    db_item = ItemVenda(
        id_venda=db_venda.id,
        id_planta=db_planta.id,
        quantidade=1,
        valor_unitario=150.0,
        valor_total=150.0,
        desconto=0.0
    )
    db.add(db_item)
    await db.commit()
    
    # Atualizar o status da planta para VENDIDA
    await db.execute(f"UPDATE plantas SET status = 'VENDIDA' WHERE id = {db_planta.id}")
    await db.commit()
    
    # Cancelar a venda
    update_data = {
        "status": "CANCELADO",
        "observacoes": "Cliente desistiu da compra"
    }
    
    response = await client.put(
        f"/api/v1/vendas/{db_venda.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verificar se a planta voltou ao status ADULTA
    query = f"SELECT status FROM plantas WHERE id = {db_planta.id}"
    result = await db.execute(query)
    status = result.scalar()
    assert status == "ADULTA"

@pytest.mark.asyncio
async def test_delete_venda(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para deletar uma venda.
    """
    # Criar dados necessários
    # 1. Comprador
    db_comprador = Comprador(
        tipo="PF",
        nome="Deletar Teste",
        cpf_cnpj="123.321.456-78",
        email="deletar@teste.com"
    )
    db.add(db_comprador)
    
    # 2. Venda
    db_venda = Venda(
        id_comprador=db_comprador.id,
        id_funcionario=test_user["user"].id,
        data_venda=datetime.now(),
        valor_total=50.0,
        forma_pagamento="PIX",
        status="PENDENTE"
    )
    db.add(db_venda)
    await db.commit()
    await db.refresh(db_venda)
    
    # Deletar a venda
    response = await client.delete(
        f"/api/v1/vendas/{db_venda.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verificar se foi realmente deletado
    check_response = await client.get(
        f"/api/v1/vendas/{db_venda.id}",
        headers=auth_headers
    )
    assert check_response.status_code == 404

@pytest.mark.asyncio
async def test_update_item_venda(client: AsyncClient, db: AsyncSession, auth_headers: dict, test_user: dict):
    """
    Teste para atualizar um item de venda.
    """
    # Criar dados necessários
    # 1. Comprador
    db_comprador = Comprador(
        tipo="PF",
        nome="Item Teste",
        cpf_cnpj="987.654.321-00",
        email="item@teste.com"
    )
    db.add(db_comprador)
    
    # 2. Espécie e planta
    db_especie = Especie(nome_cientifico="Espécie Item", nome_popular="Item Teste")
    db.add(db_especie)
    await db.commit()
    
    db_planta = Planta(
        id_especie=db_especie.id, 
        codigo_rastreio="PL-ITEM", 
        status="ADULTA",
        preco_venda=80.0
    )
    db.add(db_planta)
    await db.commit()
    
    # 3. Venda e item
    db_venda = Venda(
        id_comprador=db_comprador.id,
        id_funcionario=test_user["user"].id,
        data_venda=datetime.now(),
        valor_total=80.0,
        status="PENDENTE"
    )
    db.add(db_venda)
    await db.commit()
    
    db_item = ItemVenda(
        id_venda=db_venda.id,
        id_planta=db_planta.id,
        quantidade=1,
        valor_unitario=80.0,
        valor_total=80.0,
        desconto=0.0
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    
    # Atualizar o item
    update_data = {
        "quantidade": 2,
        "desconto": 10.0
    }
    
    response = await client.put(
        f"/api/v1/vendas/itens/{db_item.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantidade"] == 2
    assert data["desconto"] == 10.0
    assert data["valor_total"] == (2 * 80.0) - 10.0  # 150.0
    
    # Verificar se o valor total da venda foi atualizado
    venda_query = f"SELECT valor_total FROM vendas WHERE id = {db_venda.id}"
    venda_result = await db.execute(venda_query)
    valor_total = float(venda_result.scalar())
    assert valor_total == (2 * 80.0) - 10.0  # 150.0