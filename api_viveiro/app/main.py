from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.bootstrap import ensure_default_admin, ensure_demo_especies, ensure_demo_comprador
from app.config import settings
from app.database import get_db
from app.routes import (
    especies,
    plantas,
    funcionarios,
    compradores,
    canteiros,
    atividades,
    pragas,
    insumos,
    vendas,
    arvores_matriz,
    coletas_sementes,
    lotes_sementes,
    testes_sementes,
    semeaduras,
    coleta_relatorios,
    dashboard,
    lancamentos_financeiros,
    estoques,
    producao,
    referencia_viveiro,
)
from app.auth.router import router as auth_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup():
    # Schema criado pelos scripts SQL em bd_viveiro/init-scripts
    await ensure_default_admin()
    await ensure_demo_especies()
    await ensure_demo_comprador()


@app.get("/")
async def root():
    return {"message": "Bem-vindo à API do Sistema de Gestão de Viveiro de Plantas"}


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Tenta executar uma consulta simples
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


# Incluir todos os routers da API
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"],
)

app.include_router(
    especies.router,
    prefix=f"{settings.API_V1_STR}/especies",
    tags=["especies"],
)

app.include_router(
    plantas.router,
    prefix=f"{settings.API_V1_STR}/plantas", 
    tags=["plantas"],
)

app.include_router(
    funcionarios.router,
    prefix=f"{settings.API_V1_STR}/funcionarios",
    tags=["funcionarios"],
)

app.include_router(
    compradores.router, 
    prefix=f"{settings.API_V1_STR}/compradores",
    tags=["compradores"],
)

app.include_router(
    canteiros.router,
    prefix=f"{settings.API_V1_STR}/canteiros",
    tags=["canteiros"],
)

app.include_router(
    atividades.router,
    prefix=f"{settings.API_V1_STR}/atividades",
    tags=["atividades"],
)

app.include_router(
    pragas.router,
    prefix=f"{settings.API_V1_STR}/pragas",
    tags=["pragas"],
)

app.include_router(
    insumos.router,
    prefix=f"{settings.API_V1_STR}/insumos",
    tags=["insumos"],
)

app.include_router(
    vendas.router,
    prefix=f"{settings.API_V1_STR}/vendas",
    tags=["vendas"],
)

app.include_router(
    arvores_matriz.router,
    prefix=f"{settings.API_V1_STR}/arvores-matriz",
    tags=["arvores-matriz"],
)

app.include_router(
    coletas_sementes.router,
    prefix=f"{settings.API_V1_STR}/coletas-sementes",
    tags=["coletas-sementes"],
)

app.include_router(
    lotes_sementes.router,
    prefix=f"{settings.API_V1_STR}/lotes-sementes",
    tags=["lotes-sementes"],
)

app.include_router(
    testes_sementes.router,
    prefix=f"{settings.API_V1_STR}/testes-sementes",
    tags=["testes-sementes"],
)

app.include_router(
    semeaduras.router,
    prefix=f"{settings.API_V1_STR}/semeaduras",
    tags=["semeaduras"],
)

app.include_router(
    coleta_relatorios.router,
    prefix=f"{settings.API_V1_STR}/coleta-relatorios",
    tags=["coleta-relatorios"],
)

app.include_router(
    dashboard.router,
    prefix=f"{settings.API_V1_STR}/dashboard",
    tags=["dashboard"],
)

app.include_router(
    lancamentos_financeiros.router,
    prefix=f"{settings.API_V1_STR}/lancamentos-financeiros",
    tags=["lancamentos-financeiros"],
)

app.include_router(
    estoques.router,
    prefix=f"{settings.API_V1_STR}/estoques",
    tags=["estoques"],
)

app.include_router(
    producao.router,
    prefix=f"{settings.API_V1_STR}/producao",
    tags=["producao"],
)

app.include_router(
    referencia_viveiro.router,
    prefix=f"{settings.API_V1_STR}/referencia-viveiro",
    tags=["referencia-viveiro"],
)