# Brotare Viveiros

Plataforma de gestão de viveiros — **mudas nativas** e **mudas plantadas (florestal)**. Coleta, produção, estoques, vendas, financeiro e NF-e.

| Pasta | Descrição |
|-------|-----------|
| `bd_viveiro` | Init-scripts e patches SQL (Postgres) |
| `api_viveiro` | API REST FastAPI + Alembic |
| `sistema-viveiro-nativas` | App Vue 3 + Vite (Brotare Viveiros) |
| `site` | Site marketing (opcional) |
| `compose/` | Fragmentos Docker |
| `docs/` | **Documentação oficial** |

## Documentação

Índice completo: **[docs/README.md](./docs/README.md)**

| Leitura rápida | Arquivo |
|----------------|---------|
| Subir o projeto | [RODAR.md](./RODAR.md) · [docs/DEV_DOCKER.md](./docs/DEV_DOCKER.md) |
| Arquitetura e API | [docs/DOCUMENTACAO_TECNICA.md](./docs/DOCUMENTACAO_TECNICA.md) |
| Viveiro florestal (discovery) | [docs/VIVEIRO_FLORESTAL.md](./docs/VIVEIRO_FLORESTAL.md) |
| Segurança / RBAC | [docs/SEGURANCA_RBAC.md](./docs/SEGURANCA_RBAC.md) |
| Admin God Mode | [docs/ADMIN_COCKPIT.md](./docs/ADMIN_COCKPIT.md) |
| Referência viveiro nativo | [docs/REFERENCIA_VIVEIRO.md](./docs/REFERENCIA_VIVEIRO.md) |
| Demo consultor | [DEMO_CONSULTOR.md](./DEMO_CONSULTOR.md) |

## Desenvolvimento

```powershell
cd C:\Projetos\SisViNa
.\scripts\dev.ps1 start

cd sistema-viveiro-nativas
npm run dev
```

| Serviço | URL |
|---------|-----|
| App | http://localhost:5173 |
| API | http://localhost:8000/docs |

Login dev: `admin` / `Admin@123`

Migrations: `.\scripts\dev.ps1 migrate` (head: `38_viveiros_florestal`)

Testes RBAC: `.\scripts\test_permissions.ps1`
