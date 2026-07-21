"""Testes de isolamento operacional — estoques, financeiro, exports, BOLA."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.tenant_fixtures import DEFAULT_EMPRESA_ID, DEFAULT_VIVEIRO_ID
from app.auth.utils import gerar_senha_hash
from app.models.empresas import Empresa
from app.models.funcionarios import Funcionario
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.models.insumos import Insumo
from app.models.lotes_sementes import LoteSementes
from app.models.plantas import Planta
from app.models.viveiros import Viveiro


async def _login(client: AsyncClient, usuario: str, senha: str = "Senha@123") -> dict:
    r = await client.post(
        "/api/v1/auth/login",
        data={"username": usuario, "password": senha},
    )
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_estoques_resumo_isolado_por_viveiro(client: AsyncClient, db: AsyncSession):
    from app.models.especies import Especie

    esp = Especie(nome_cientifico="IsoEsp", nome_popular="Iso")
    db.add(esp)
    await db.flush()

    v2 = Viveiro(
        nome="Outro Viveiro",
        slug="outro-viveiro-iso",
        modo_operacao="nativo",
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(v2)
    await db.flush()

    db.add(
        Planta(
            id_especie=esp.id,
            id_viveiro=v2.id,
            codigo_rastreio="ISO-EST-001",
            status="MUDA",
            estagio_producao="em_crescimento",
            custo_atual=100,
        )
    )

    user = Funcionario(
        nome="Campo V1",
        cpf="111.222.333-44",
        usuario="campoestoque",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Campo",
        perfis=["campo"],
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(user)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=user.id, id_viveiro=DEFAULT_VIVEIRO_ID))
    await db.commit()

    headers = await _login(client, "campoestoque")
    r = await client.get("/api/v1/estoques/resumo", headers=headers)
    assert r.status_code == 200
    body = r.json()
    codigos = [p.get("codigo_rastreio") for p in body.get("mudas", [])]
    assert "ISO-EST-001" not in codigos
    assert float(body.get("valor_total_mudas", 0)) < 100


@pytest.mark.asyncio
async def test_catalogo_pragas_isolado_por_empresa(client: AsyncClient, db: AsyncSession):
    from app.models.pragas import TipoPraga

    empresa2 = Empresa(
        razao_social="Empresa Cat 2",
        nome_fantasia="Cat2",
        slug="emp-cat-2",
        ativo=True,
    )
    db.add(empresa2)
    await db.flush()
    db.add(TipoPraga(nome="Praga Secreta", descricao="x", id_empresa=empresa2.id))

    user = Funcionario(
        nome="Fitossanidade E1",
        cpf="222.333.444-55",
        usuario="fitoe1",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Campo",
        perfis=["campo"],
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(user)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=user.id, id_viveiro=DEFAULT_VIVEIRO_ID))
    await db.commit()

    headers = await _login(client, "fitoe1")
    r = await client.get("/api/v1/pragas/tipos", headers=headers)
    assert r.status_code == 200
    nomes = [t["nome"] for t in r.json()]
    assert "Praga Secreta" not in nomes


@pytest.mark.asyncio
async def test_insumos_isolados_por_empresa(client: AsyncClient, db: AsyncSession):
    empresa2 = Empresa(
        razao_social="Empresa 2",
        nome_fantasia="Emp2",
        slug="emp2-test",
        ativo=True,
    )
    db.add(empresa2)
    await db.flush()
    db.add(Insumo(nome="Insumo Secreto", tipo="fertilizante", id_empresa=empresa2.id))
    await db.flush()

    user = Funcionario(
        nome="Gestor E1",
        cpf="555.666.777-88",
        usuario="gestore1ins",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Gestor",
        perfis=["gestor"],
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(user)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=user.id, id_viveiro=DEFAULT_VIVEIRO_ID))
    await db.commit()

    headers = await _login(client, "gestore1ins")
    r = await client.get("/api/v1/insumos/", headers=headers)
    assert r.status_code == 200
    nomes = [i["nome"] for i in r.json()]
    assert "Insumo Secreto" not in nomes


@pytest.mark.asyncio
async def test_export_coletas_filtra_viveiro(client: AsyncClient, db: AsyncSession):
    from app.models.especies import Especie
    from app.models.arvores_matriz import ArvoreMatriz
    from app.models.coletas_sementes import ColetaSementes

    esp = Especie(nome_cientifico="ExpEsp", nome_popular="Exp")
    db.add(esp)
    await db.flush()

    v2 = Viveiro(
        nome="Viveiro Export",
        slug="viveiro-export-iso",
        modo_operacao="nativo",
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(v2)
    await db.flush()

    matriz = ArvoreMatriz(
        nome="Matriz Exp",
        id_especie=esp.id,
        id_viveiro=v2.id,
        latitude=-10.0,
        longitude=-50.0,
        tipo_coordenada="decimal",
    )
    db.add(matriz)
    await db.flush()

    user = Funcionario(
        nome="Campo Export",
        cpf="999.888.777-66",
        usuario="campoexport",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Campo",
        perfis=["campo"],
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(user)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=user.id, id_viveiro=DEFAULT_VIVEIRO_ID))
    await db.flush()

    coleta_v1 = ColetaSementes(
        id_arvore_matriz=matriz.id,
        id_funcionario=user.id,
        data_coleta=__import__("datetime").date.today(),
        quantidade_sementes=10,
    )
    db.add(coleta_v1)
    await db.commit()

    headers = await _login(client, "campoexport")
    r = await client.get("/api/v1/coleta-relatorios/export/coletas.csv", headers=headers)
    assert r.status_code == 200
    assert str(matriz.id) not in r.text


@pytest.mark.asyncio
async def test_bola_praga_outro_viveiro_404(client: AsyncClient, db: AsyncSession):
    """BOLA: acesso direto por ID a praga de outro viveiro retorna 404."""
    from app.models.especies import Especie
    from app.models.pragas import TipoPraga, PragaPlanta

    esp = Especie(nome_cientifico="PragaEsp", nome_popular="Praga")
    tipo = TipoPraga(nome="Lagarta ISO", descricao="teste", id_empresa=DEFAULT_EMPRESA_ID)
    db.add_all([esp, tipo])
    await db.flush()

    v2 = Viveiro(
        nome="Viveiro Praga",
        slug="viveiro-praga-iso",
        modo_operacao="nativo",
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(v2)
    await db.flush()

    planta = Planta(
        id_especie=esp.id,
        id_viveiro=v2.id,
        codigo_rastreio="PRAGA-ISO-01",
        status="MUDA",
        estagio_producao="em_crescimento",
    )
    db.add(planta)
    await db.flush()

    praga = PragaPlanta(
        id_planta=planta.id,
        id_tipo_praga=tipo.id,
        nivel_infestacao="baixo",
        data_identificacao=__import__("datetime").date.today(),
    )
    db.add(praga)
    await db.flush()

    user = Funcionario(
        nome="Campo Praga",
        cpf="444.333.222-11",
        usuario="campopraga",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Campo",
        perfis=["campo"],
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(user)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=user.id, id_viveiro=DEFAULT_VIVEIRO_ID))
    await db.commit()

    headers = await _login(client, "campopraga")
    r = await client.get(f"/api/v1/pragas/plantas/{praga.id}", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_financeiro_painel_nao_vaza_insumo_outra_empresa(client: AsyncClient, db: AsyncSession):
    """Painel financeiro não inclui estoque de insumos de outra empresa."""
    empresa2 = Empresa(
        razao_social="Empresa 2 Fin",
        nome_fantasia="E2",
        slug="emp2-fin-iso",
        ativo=True,
    )
    db.add(empresa2)
    await db.flush()
    db.add(
        Insumo(
            nome="Insumo Financeiro Secreto",
            tipo="fertilizante",
            id_empresa=empresa2.id,
            valor_estoque=50_000,
            quantidade_estoque=100,
        )
    )

    user = Funcionario(
        nome="Financeiro ISO",
        cpf="333.222.111-00",
        usuario="finiso",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Financeiro",
        perfis=["financeiro"],
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(user)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=user.id, id_viveiro=DEFAULT_VIVEIRO_ID))
    await db.commit()

    headers = await _login(client, "finiso")
    r = await client.get("/api/v1/financeiro/painel", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert float(body["estoque"]["valor_insumos"]) < 50_000


@pytest.mark.asyncio
async def test_planta_bola_outro_viveiro_404(client: AsyncClient, db: AsyncSession):
    from app.models.especies import Especie

    esp = Especie(nome_cientifico="BolaPlanta", nome_popular="Bola")
    db.add(esp)
    await db.flush()

    v2 = Viveiro(
        nome="Viveiro BOLA Planta",
        slug="bola-planta",
        modo_operacao="nativo",
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(v2)
    await db.flush()

    planta = Planta(
        id_especie=esp.id,
        id_viveiro=v2.id,
        codigo_rastreio="BOLA-PL-01",
        status="MUDA",
        estagio_producao="em_crescimento",
    )
    db.add(planta)

    user = Funcionario(
        nome="Campo BOLA",
        cpf="121.212.121-21",
        usuario="campobola",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Campo",
        perfis=["campo"],
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(user)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=user.id, id_viveiro=DEFAULT_VIVEIRO_ID))
    await db.commit()

    headers = await _login(client, "campobola")
    r = await client.get(f"/api/v1/plantas/{planta.id}", headers=headers)
    assert r.status_code in (403, 404)


@pytest.mark.asyncio
async def test_venda_bola_outro_viveiro_404(client: AsyncClient, db: AsyncSession):
    from app.models.compradores import Comprador
    from app.models.vendas import Venda

    v2 = Viveiro(
        nome="Viveiro BOLA Venda",
        slug="bola-venda",
        modo_operacao="nativo",
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(v2)
    await db.flush()

    comprador = Comprador(
        tipo="PF",
        nome="Cliente BOLA",
        cpf_cnpj="99.888.777/0001-99",
        ativo=True,
        id_empresa=DEFAULT_EMPRESA_ID,
    )
    db.add(comprador)
    await db.flush()

    user = Funcionario(
        nome="Vendas BOLA",
        cpf="131.313.131-31",
        usuario="vendasbola",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Vendas",
        perfis=["gestor"],
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(user)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=user.id, id_viveiro=DEFAULT_VIVEIRO_ID))

    venda = Venda(
        id_viveiro=v2.id,
        id_comprador=comprador.id,
        id_funcionario=user.id,
        data_venda=__import__("datetime").datetime.now(),
        valor_total=100,
        status="PENDENTE",
    )
    db.add(venda)
    await db.commit()

    headers = await _login(client, "vendasbola")
    r = await client.get(f"/api/v1/vendas/{venda.id}", headers=headers)
    assert r.status_code in (403, 404)


@pytest.mark.asyncio
async def test_especies_plantas_count_escopado_por_viveiro(client: AsyncClient, db: AsyncSession):
    from app.models.especies import Especie

    esp = Especie(nome_cientifico="CountEsp", nome_popular="Count")
    db.add(esp)
    await db.flush()

    v2 = Viveiro(
        nome="Viveiro Count",
        slug="v-count",
        modo_operacao="nativo",
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(v2)
    await db.flush()

    db.add(
        Planta(
            id_especie=esp.id,
            id_viveiro=v2.id,
            codigo_rastreio="COUNT-ISO",
            status="MUDA",
            estagio_producao="em_crescimento",
        )
    )

    user = Funcionario(
        nome="Viveiro Count User",
        cpf="141.414.141-41",
        usuario="countuser",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Campo",
        perfis=["campo"],
        id_empresa=DEFAULT_EMPRESA_ID,
        ativo=True,
    )
    db.add(user)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=user.id, id_viveiro=DEFAULT_VIVEIRO_ID))
    await db.commit()

    headers = await _login(client, "countuser")
    r = await client.get("/api/v1/especies/with-plantas-count", headers=headers)
    assert r.status_code == 200
    row = next((e for e in r.json() if e.get("id") == esp.id), None)
    assert row is not None
    assert int(row.get("total_plantas", 0)) == 0
