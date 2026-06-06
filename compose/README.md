# Docker — SisViNa

Definições compartilhadas. **Único entrypoint:** `docker-compose.yml` na raiz (projeto `sisvina`).

| Arquivo | Serviço |
|---------|---------|
| `infra.yml` | `postgres`, `pgadmin` (profile `tools`) |
| `api.yml` | `api` |
| `web.yml` | `web` (profile `docker-web`) |
| `site.yml` | `site` (profile `site`) |

Não rode compose nas subpastas — use `.\scripts\dev.ps1` na raiz.
