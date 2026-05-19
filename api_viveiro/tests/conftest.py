import asyncio
import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.main import app
from app.config import settings
from app.auth.jwt import create_access_token
from app.models.funcionarios import Funcionario
from app.auth.utils import gerar_senha_hash

# Banco de dados de teste
TEST_DATABASE_URL = "postgresql+asyncpg://viveiro_admin:senha_segura_aqui@localhost:5432/viveiro_test_db"

# Engine de teste
engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
async_session_test = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function")
async def db() -> AsyncGenerator:
    """
    Cria um banco de dados de teste limpo para cada teste.
    Todas as tabelas são criadas e depois removidas após o teste.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Conecta-se ao banco de dados e cria uma transação
    async with async_session_test() as session:
        yield session
        await session.rollback()
        await session.close()

@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator:
    """
    Cria um cliente de teste para a aplicação FastAPI.
    """
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
async def test_user(db: AsyncSession) -> dict:
    """
    Cria um usuário de teste no banco de dados.
    """
    user_data = {
        "nome": "Teste Usuário",
        "cpf": "123.456.789-00",
        "email": "teste@exemplo.com",
        "usuario": "testuser",
        "senha": gerar_senha_hash("Senha@123"),
        "cargo": "Administrador",
        "ativo": True
    }
    
    db_user = Funcionario(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Criar token de acesso
    access_token = create_access_token(data={"sub": user_data["usuario"]})
    
    return {
        "user": db_user,
        "token": access_token
    }

@pytest.fixture(scope="function")
async def auth_headers(test_user: dict) -> dict:
    """
    Retorna os cabeçalhos de autenticação para um usuário de teste.
    """
    return {"Authorization": f"Bearer {test_user['token']}"}