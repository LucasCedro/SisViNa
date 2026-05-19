import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Importar a configuração e modelos para o Alembic
from app.config import settings
from app.database import Base
# Importe aqui todos os seus modelos
from app.models import especies, plantas, funcionarios, compradores, canteiros, atividades, insumos, pragas, vendas

# Configuração do Alembic
config = context.config

# Configurar o acesso ao banco de dados
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpretador de configuração de logging do 'alembic.ini'
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Adicionar modelos ao contexto do Alembic
target_metadata = Base.metadata

# Outras variáveis
target_schemas = None
include_schemas = False
include_name = None
include_object = None
compare_type = True
compare_server_default = True

def run_migrations_offline():
    """Executar migrações em modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=include_schemas,
        include_name=include_name,
        include_object=include_object,
        compare_type=compare_type,
        compare_server_default=compare_server_default,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=include_schemas,
        include_name=include_name,
        include_object=include_object,
        compare_type=compare_type,
        compare_server_default=compare_server_default,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Executar migrações em modo 'online'."""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())