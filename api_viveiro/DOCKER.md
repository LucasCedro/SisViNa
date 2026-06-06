# Docker — api_viveiro

API FastAPI. **Compose fica na raiz do monorepo** (`compose/api.yml`).

```powershell
cd C:\Projetos\SisViNa
.\scripts\dev.ps1 start          # Postgres + API
.\scripts\dev.ps1 restart-api    # após editar .env
.\scripts\dev.ps1 migrate
docker compose logs -f api
docker compose exec api alembic upgrade head
```

Desenvolvimento sem Docker: venv + `uvicorn app.main:app --reload` (Postgres via `dev.ps1 start`).

Ver [docs/DEV_DOCKER.md](../docs/DEV_DOCKER.md).
