"""Testes de isolamento SaaS — tenant empresa."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import gerar_senha_hash
from app.models.empresas import Empresa
from app.models.funcionarios import Funcionario
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.models.viveiros import Viveiro


@pytest.mark.asyncio
async def test_empresa_header_blocked_for_gestor(client: AsyncClient, db: AsyncSession):
    empresa = Empresa(
        id=99,
        razao_social="Outra Empresa",
        nome_fantasia="Outra",
        slug="outra",
        ativo=True,
    )
    db.add(empresa)
    gestor = Funcionario(
        nome="Gestor Tenant",
        cpf="123.456.789-09",
        usuario="gestortenant",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Gestor",
        perfis=["gestor"],
        id_empresa=1,
        ativo=True,
    )
    db.add(gestor)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=gestor.id, id_viveiro=1))
    await db.commit()

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "gestortenant", "password": "Senha@123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Empresa-Id": "99"}

    r = await client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_plantas_scoped_by_viveiro(client: AsyncClient, db: AsyncSession):
    """Plantas de outro viveiro não aparecem na listagem."""
    from app.models.plantas import Planta
    from app.models.especies import Especie

    esp = (await db.execute(__import__("sqlalchemy").select(Especie).limit(1))).scalars().first()
    if esp is None:
        esp = Especie(nome_cientifico="Teste", nome_popular="Teste")
        db.add(esp)
        await db.flush()

    v2 = Viveiro(
        nome="Viveiro Isolado",
        slug="isolado-test",
        modo_operacao="nativo",
        id_empresa=1,
        ativo=True,
    )
    db.add(v2)
    await db.flush()
    db.add(
        Planta(
            id_especie=esp.id,
            id_viveiro=v2.id,
            codigo_rastreio="ISO-TEST-001",
            status="ATIVA",
            estagio_producao="em_crescimento",
        )
    )
    campo = Funcionario(
        nome="Campo V1",
        cpf="987.654.321-00",
        usuario="campov1only",
        senha=gerar_senha_hash("Senha@123"),
        cargo="Campo",
        perfis=["campo"],
        id_empresa=1,
        ativo=True,
    )
    db.add(campo)
    await db.flush()
    db.add(FuncionarioViveiro(id_funcionario=campo.id, id_viveiro=1))
    await db.commit()

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "campov1only", "password": "Senha@123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.get("/api/v1/plantas/", headers=headers)
    assert r.status_code == 200
    codigos = [p.get("codigo_rastreio") for p in r.json()]
    assert "ISO-TEST-001" not in codigos
