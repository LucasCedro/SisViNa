# Docker — site

Site institucional (porta 3000). Compose na raiz, profile `site`:

```powershell
cd C:\Projetos\SisViNa
docker compose --profile site up -d --build site
```

Demo completa: `.\scripts\dev.ps1 start-demo`

Ver [docs/DEV_DOCKER.md](../docs/DEV_DOCKER.md).
