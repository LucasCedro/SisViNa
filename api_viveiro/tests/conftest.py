import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.main import app
from app.auth.jwt import create_access_token
from app.models.funcionarios import Funcionario
from app.auth.utils import gerar_senha_hash

from tests.tenant_fixtures import (
    DEFAULT_EMPRESA_ID,
    DEFAULT_VIVEIRO_ID,
    ensure_tenant_base,
    link_funcionario_viveiro,
)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://viveiro_admin:senha_segura_aqui@localhost:5432/viveiro_test_db",
)

engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
async_session_test = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_test() as session:
        await ensure_tenant_base(session)
        await session.commit()
        yield session
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def empresa(db: AsyncSession):
    emp, _ = await ensure_tenant_base(db)
    return emp


@pytest_asyncio.fixture(scope="function")
async def viveiro(db: AsyncSession):
    _, viv = await ensure_tenant_base(db)
    return viv


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def test_user(db: AsyncSession) -> dict:
    user_data = {
        "nome": "Teste Usuário",
        "cpf": "123.456.789-00",
        "email": "teste@exemplo.com",
        "usuario": "testuser",
        "senha": gerar_senha_hash("Senha@123"),
        "cargo": "Administrador",
        "ativo": True,
    }

    db_user = Funcionario(**user_data, perfis=["admin"], id_empresa=DEFAULT_EMPRESA_ID)
    db.add(db_user)
    await db.flush()
    await link_funcionario_viveiro(db, db_user.id, DEFAULT_VIVEIRO_ID)
    await db.commit()
    await db.refresh(db_user)

    access_token = create_access_token(data={"sub": user_data["usuario"]})

    return {"user": db_user, "token": access_token}


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user: dict) -> dict:
    return {"Authorization": f"Bearer {test_user['token']}"}
