from sqlalchemy import select

from app.auth.utils import gerar_senha_hash
from app.database import AsyncSessionLocal
from app.models.especies import Especie
from app.models.funcionarios import Funcionario
from app.models.compradores import Comprador
from app.models.compradores import Comprador

DEFAULT_ADMIN = {
    "nome": "Administrador",
    "cpf": "000.000.000-00",
    "usuario": "admin",
    "senha_plana": "Admin@123",
    "cargo": "Administrador",
    "email": "admin@viveiro.com",
}


async def ensure_default_admin() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Funcionario).where(Funcionario.usuario == DEFAULT_ADMIN["usuario"])
        )
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
                ativo=True,
            )
        )
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
                ativo=True,
            )
        )
        await db.commit()
