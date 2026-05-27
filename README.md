# SisViNa

Sistema de gestão de viveiro de plantas nativas.

| Pasta | Descrição |
|-------|-----------|
| `bd_viveiro` | PostgreSQL + PgAdmin (Docker) |
| `api_viveiro` | API REST FastAPI |
| `sistema-viveiro-nativas` | Front Vue 3 + Vite |

## Documentação

- **[Documentação técnica completa](./docs/DOCUMENTACAO_TECNICA.md)** — arquitetura, fluxos, API e setup de desenvolvimento
- **[Rodar com Docker](./RODAR.md)** — guia operacional (containers, patches, troubleshooting)
- **[Design system](./sistema-viveiro-nativas/docs/DESIGN_SYSTEM.md)** — UI do frontend

## Desenvolvimento rápido

1. Postgres: `cd bd_viveiro && docker compose up -d`
2. API: `cd api_viveiro` → venv → `alembic upgrade head` → `uvicorn app.main:app --reload`
3. Front: `cd sistema-viveiro-nativas` → `npm install` → `npm run dev`

Detalhes em [docs/DOCUMENTACAO_TECNICA.md](./docs/DOCUMENTACAO_TECNICA.md).

## Login (dev)

- Usuário: `admin`
- Senha: `Admin@123`
