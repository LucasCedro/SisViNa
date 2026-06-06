# Testes — API Viveiro

## Estrutura

| Arquivo | Conteúdo |
|---------|----------|
| `conftest.py` | Fixtures `db`, `client`, `auth_headers`, `test_user` |
| `test_auth.py` | Login, `/me` |
| `test_especies.py` | CRUD espécies |
| `test_rbac.py` | Matriz RBAC, escalação, consulta 403, God Mode |
| `test_vendas_sod.py` | SoD vendas (edit vs approve) |

## Executar

Requer Postgres com banco **`viveiro_test_db`** e `TEST_DATABASE_URL` em `conftest.py` (ou env).

```powershell
cd api_viveiro
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
pytest tests/test_rbac.py tests/test_vendas_sod.py -v
```

No container Docker a pasta `tests/` **não** está montada por padrão — rode no host ou inclua no Dockerfile de CI.

## Smoke RBAC (API real)

Na raiz do monorepo:

```powershell
.\scripts\test_permissions.ps1
```

Usuário `consulta` (ou variáveis `CONSULTA_USER` / `CONSULTA_PASS`) — espera **403** em mutações.

## Fixture `auth_headers`

Usuário admin criado no teste. Para RBAC negativo, crie usuários com perfis específicos no teste (ver `test_rbac.py`).
