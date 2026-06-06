# Docker — bd_viveiro

Infra de banco (Postgres, init-scripts, patches SQL). **Não há compose nesta pasta.**

Subir Postgres:

```powershell
cd C:\Projetos\SisViNa
.\scripts\dev.ps1 start
```

Ou manualmente na raiz:

```powershell
docker compose up -d postgres
```

PgAdmin (opcional):

```powershell
docker compose --profile tools up -d pgadmin
```

SQL no banco:

```powershell
Get-Content patches\arquivo.sql -Raw | docker compose exec -T postgres psql -U viveiro_admin -d viveiro_db
```

Ver [docs/DEV_DOCKER.md](../docs/DEV_DOCKER.md).
