# Testes — API Viveiro

## Estrutura

| Arquivo | Conteúdo |
|---------|----------|
| `conftest.py` | Fixtures `db`, `client`, `empresa`, `viveiro`, `auth_headers`, `test_user` |
| `tenant_fixtures.py` | Seed empresa/viveiro padrão (`DEFAULT_EMPRESA_ID`, `DEFAULT_VIVEIRO_ID`) |
| `test_tenant_saas.py` | Header `X-Empresa-Id`, isolamento empresa |
| `test_tenant_isolation.py` | Isolamento viveiro/empresa, BOLA, financeiro, catálogos |
| `test_auth.py` | Login, `/me` |
| `test_rbac.py` | Matriz RBAC, escalação, consulta 403, God Mode |
| `test_viveiro_context.py` | Multi-unidade, anti-escalação `X-Viveiro-Id` |
| Demais `test_*.py` | Módulos funcionais (plantas, vendas, estoques, etc.) |

## Executar

Variável de ambiente (opcional — há default no `conftest.py`):

```powershell
$env:TEST_DATABASE_URL = "postgresql+asyncpg://viveiro_admin:senha_segura_aqui@localhost:5432/viveiro_test_db"
```

### Host

```powershell
cd api_viveiro
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
pytest tests/test_tenant_isolation.py tests/test_tenant_saas.py -v
```

### Docker (API container — pasta `tests/` montada em `compose/api.yml`)

```powershell
docker exec sisvina-postgres-1 psql -U viveiro_admin -d postgres -c "CREATE DATABASE viveiro_test_db;" 2>$null
docker exec -e TEST_DATABASE_URL=postgresql+asyncpg://viveiro_admin:senha_segura_aqui@viveiro_postgres:5432/viveiro_test_db sisvina-api-1 python -m pytest /app/tests/test_tenant_isolation.py /app/tests/test_tenant_saas.py -q
```

O init script `bd_viveiro/init-scripts/13-viveiro-test-db.sql` cria o banco em novos volumes Postgres.

## Smoke (API real)

Na raiz do monorepo:

```powershell
.\scripts\test_permissions.ps1
.\scripts\smoke.ps1
```
