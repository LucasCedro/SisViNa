# Docker — front (opcional)

**Recomendado:** Vite local (hot reload mais rápido):

```powershell
cd C:\Projetos\SisViNa\sistema-viveiro-nativas
npm ci
npm run dev
```

API deve estar em http://localhost:8000 (`.\scripts\dev.ps1 start` na raiz).

Front em Docker (profile `docker-web`):

```powershell
cd C:\Projetos\SisViNa
.\scripts\dev.ps1 start-all
```

Ver [docs/DEV_DOCKER.md](../docs/DEV_DOCKER.md).
