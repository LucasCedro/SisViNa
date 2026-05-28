import pytest
from datetime import date, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.estagios_producao import APTA_VENDA, EM_DESENVOLVIMENTO
from app.models.canteiros import Canteiro
from app.models.especies import Especie
from app.models.insumos import Insumo
from app.models.plantas import Planta


@pytest.mark.asyncio
async def test_resumo_estoques_estrutura(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/estoques/resumo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "mudas_pipeline" in data
    assert "estoque_comercial" in data
    assert "valor_total_insumos" in data
    pipe = data["mudas_pipeline"]
    assert "prontas_para_venda" in pipe
    assert "dias_minimos_rustificacao" in pipe


@pytest.mark.asyncio
async def test_estoque_comercial_exige_rustificacao_30_dias(
    client: AsyncClient, db: AsyncSession, auth_headers: dict
):
    especie = Especie(nome_cientifico="Tabebuia sp", nome_popular="Ipê")
    rust = Canteiro(nome="Rust A", tipo_local="rustificacao", ativo=True)
    db.add(especie)
    db.add(rust)
    await db.commit()
    await db.refresh(especie)
    await db.refresh(rust)

    pronta = Planta(
        id_especie=especie.id,
        id_canteiro=rust.id,
        codigo_rastreio="M-PRONTA",
        status="MUDA",
        estagio_producao=APTA_VENDA,
        data_inicio_estagio_atual=date.today() - timedelta(days=35),
        preco_venda=5.0,
    )
    recente = Planta(
        id_especie=especie.id,
        id_canteiro=rust.id,
        codigo_rastreio="M-RECENTE",
        status="MUDA",
        estagio_producao=APTA_VENDA,
        data_inicio_estagio_atual=date.today() - timedelta(days=5),
        preco_venda=5.0,
    )
    db.add(pronta)
    db.add(recente)
    await db.commit()

    response = await client.get("/api/v1/estoques/resumo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["mudas_pipeline"]["prontas_para_venda"] == 1
    assert data["mudas_pipeline"]["aptas_venda_aguardando_tempo"] == 1
    assert data["total_mudas_aptas_venda"] == 1
    assert len(data["estoque_comercial"]) == 1
    assert data["estoque_comercial"][0]["quantidade"] == 1


@pytest.mark.asyncio
async def test_insumo_entrada_com_valor_cmv(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    insumo = Insumo(
        nome="NPK 10-10-10",
        tipo="Fertilizante",
        unidade_medida="kg",
        quantidade_estoque=0,
        preco_unitario=0,
        valor_estoque=0,
    )
    db.add(insumo)
    await db.commit()
    await db.refresh(insumo)

    response = await client.post(
        f"/api/v1/insumos/{insumo.id}/movimentacoes",
        json={
            "tipo": "entrada",
            "quantidade": 100,
            "valor_total": 1000,
            "data_movimento": str(date.today()),
        },
        headers=auth_headers,
    )
    assert response.status_code == 200

    get_resp = await client.get(f"/api/v1/insumos/{insumo.id}", headers=auth_headers)
    data = get_resp.json()
    assert data["quantidade_estoque"] == 100
    assert abs(data["preco_unitario"] - 10.0) < 0.01

    resumo = await client.get("/api/v1/estoques/resumo", headers=auth_headers)
    insumos = resumo.json()["insumos"]
    npk = next(i for i in insumos if i["id"] == insumo.id)
    assert npk["valor_estoque"] == 1000


@pytest.mark.asyncio
async def test_tipos_insumos_rota(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    db.add(Insumo(nome="Combustível", tipo="Combustivel", quantidade_estoque=50))
    await db.commit()

    response = await client.get("/api/v1/insumos/tipos", headers=auth_headers)
    assert response.status_code == 200
    assert "Combustivel" in response.json()
