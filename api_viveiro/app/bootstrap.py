from sqlalchemy import select

from app.auth.utils import gerar_senha_hash
from app.database import AsyncSessionLocal
from app.models.especies import Especie
from app.models.funcionarios import Funcionario
from app.models.compradores import Comprador
from app.models.viveiros import Viveiro
from app.models.funcionario_viveiro import FuncionarioViveiro
from app.constants.viveiro_modo import MODO_FLORESTAL, MODO_NATIVO

ALL_PERFIS = ["admin", "gestor", "campo", "financeiro", "rh", "consulta"]

DEFAULT_ADMIN = {
    "nome": "Administrador",
    "cpf": "000.000.000-00",
    "usuario": "admin",
    "senha_plana": "Admin@123",
    "cargo": "Administrador",
    "email": "admin@viveiro.com",
    "perfis": ALL_PERFIS,
}

# Usuários de demonstração RBAC — senha comum para testes de perfil
RBAC_DEMO_PASSWORD = "Senha!@#"

RBAC_DEMO_USERS = [
    {
        "usuario": "demo.admin",
        "nome": "Demo Administrador",
        "cpf": "529.982.247-25",
        "cargo": "Administrador",
        "email": "demo.admin@viveiro.local",
        "perfis": ["admin"],
    },
    {
        "usuario": "demo.gestor",
        "nome": "Demo Gestor",
        "cpf": "390.533.447-05",
        "cargo": "Gestor do Viveiro",
        "email": "demo.gestor@viveiro.local",
        "perfis": ["gestor"],
    },
    {
        "usuario": "demo.campo",
        "nome": "Demo Campo",
        "cpf": "153.509.460-56",
        "cargo": "Operação de Campo",
        "email": "demo.campo@viveiro.local",
        "perfis": ["campo"],
    },
    {
        "usuario": "demo.financeiro",
        "nome": "Demo Financeiro",
        "cpf": "231.002.999-00",
        "cargo": "Financeiro",
        "email": "demo.financeiro@viveiro.local",
        "perfis": ["financeiro"],
    },
    {
        "usuario": "demo.consulta",
        "nome": "Demo Consulta",
        "cpf": "111.444.777-35",
        "cargo": "Consulta",
        "email": "demo.consulta@viveiro.local",
        "perfis": ["consulta"],
    },
    {
        "usuario": "demo.rh",
        "nome": "Demo RH",
        "cpf": "886.415.779-47",
        "cargo": "Recursos Humanos",
        "email": "demo.rh@viveiro.local",
        "perfis": ["rh"],
    },
]


async def ensure_default_admin() -> None:
    """Seed somente em banco vazio (1º deploy). Renomear/trocar senha não recria admin."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Funcionario).limit(1))
        if result.scalars().first():
            return

        db.add(
            Funcionario(
                nome=DEFAULT_ADMIN["nome"],
                cpf=DEFAULT_ADMIN["cpf"],
                usuario=DEFAULT_ADMIN["usuario"],
                senha=gerar_senha_hash(DEFAULT_ADMIN["senha_plana"]),
                cargo=DEFAULT_ADMIN["cargo"],
                email=DEFAULT_ADMIN["email"],
                perfis=list(ALL_PERFIS),
                ativo=True,
            )
        )
        await db.commit()


async def ensure_rbac_demo_users() -> None:
    """Garante um usuário de cada perfil RBAC para testes (upsert por login)."""
    senha_hash = gerar_senha_hash(RBAC_DEMO_PASSWORD)
    async with AsyncSessionLocal() as db:
        for spec in RBAC_DEMO_USERS:
            result = await db.execute(
                select(Funcionario).where(Funcionario.usuario == spec["usuario"])
            )
            row = result.scalars().first()
            if row:
                row.nome = spec["nome"]
                row.cpf = spec["cpf"]
                row.cargo = spec["cargo"]
                row.email = spec["email"]
                row.perfis = list(spec["perfis"])
                row.senha = senha_hash
                row.ativo = True
            else:
                db.add(
                    Funcionario(
                        nome=spec["nome"],
                        cpf=spec["cpf"],
                        usuario=spec["usuario"],
                        senha=senha_hash,
                        cargo=spec["cargo"],
                        email=spec["email"],
                        perfis=list(spec["perfis"]),
                        ativo=True,
                    )
                )
        await db.commit()


async def ensure_default_viveiros() -> None:
    """Garante unidades padrão e vínculo de funcionários (pós-migration 38)."""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Viveiro).limit(1))
        except Exception:
            # Migration 38 ainda não aplicada — não derrubar a API no startup
            await db.rollback()
            return

        if not result.scalars().first():
            db.add_all(
                [
                    Viveiro(id=1, nome="Viveiro Principal", slug="principal", modo_operacao=MODO_NATIVO, ativo=True),
                    Viveiro(
                        id=2,
                        nome="Demo Florestal",
                        slug="demo-florestal",
                        modo_operacao=MODO_FLORESTAL,
                        ativo=True,
                    ),
                ]
            )
            await db.flush()

        funcionarios = (await db.execute(select(Funcionario))).scalars().all()
        for f in funcionarios:
            await db.merge(FuncionarioViveiro(id_funcionario=f.id, id_viveiro=1))
            if f.usuario in ("admin", "demo.admin"):
                await db.merge(FuncionarioViveiro(id_funcionario=f.id, id_viveiro=2))
        await db.commit()


async def ensure_demo_especies() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Especie).limit(1))
        if result.scalars().first():
            return

        db.add_all(
            [
                Especie(
                    nome_cientifico="Handroanthus albus",
                    nome_popular="Ipê-amarelo",
                    familia="Bignoniaceae",
                    descricao="Árvore nativa ornamental de flores amarelas.",
                    tempo_germinacao=30,
                    tempo_crescimento=365,
                ),
                Especie(
                    nome_cientifico="Hymenaea courbaril",
                    nome_popular="Jatobá",
                    familia="Fabaceae",
                    descricao="Árvore de grande porte, frutos comestíveis.",
                    tempo_germinacao=45,
                    tempo_crescimento=730,
                ),
                Especie(
                    nome_cientifico="Araucaria angustifolia",
                    nome_popular="Araucária",
                    familia="Araucariaceae",
                    descricao="Conífera nativa, pinhão comestível.",
                    tempo_germinacao=60,
                    tempo_crescimento=1095,
                ),
            ]
        )
        await db.commit()


async def ensure_demo_comprador() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Comprador).limit(1))
        if result.scalars().first():
            return
        db.add(
            Comprador(
                tipo="PF",
                nome="Comprador demonstração",
                cpf_cnpj="111.444.777-35",
                email="comprador@demo.local",
                endereco="Rua Demonstração",
                numero="100",
                bairro="Centro",
                cidade="São Paulo",
                estado="SP",
                cep="01001-000",
                codigo_municipio_ibge="3550308",
                indicador_ie="9",
                ativo=True,
            )
        )
        await db.commit()
