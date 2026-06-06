# Docker — desenvolvimento SisViNa

**Um único projeto Compose** na raiz (`sisvina`). Código separado por pasta; Docker centralizado.

## Comandos

| Comando | O quê sobe |
|---------|------------|
| `.\scripts\dev.ps1 start` | Postgres + API |
| `.\scripts\dev.ps1 start-all` | + front Vue em Docker |
| `.\scripts\dev.ps1 start-demo` | + site + PgAdmin |
| `.\scripts\dev.ps1 stop` | Para tudo (dados preservados) |
| `.\scripts\dev.ps1 restart-api` | Recria API após `.env` |
| `.\scripts\dev.ps1 migrate` | Alembic upgrade head |
| `.\scripts\dev.ps1 ps` | Status |

## Fluxo por papel

### Backend

```powershell
cd C:\Projetos\SisViNa
.\scripts\dev.ps1 start
.\scripts\dev.ps1 migrate   # se necessário
docker compose logs -f api
```

### Frontend (recomendado)

```powershell
# Terminal 1
.\scripts\dev.ps1 start

# Terminal 2
cd sistema-viveiro-nativas
npm run dev
```

### Demo / consultor

```powershell
.\scripts\dev.ps1 start-demo
```

## URLs

| Serviço | URL |
|---------|-----|
| App | http://localhost:5173 |
| API | http://localhost:8000/docs |
| Site | http://localhost:3000 (profile site) |
| PgAdmin | http://localhost:5050 (profile tools) |

## Estrutura

```
docker-compose.yml     ← include compose/*.yml
compose/
  infra.yml
  api.yml
  web.yml
  site.yml
scripts/dev.ps1
```

Pastas `bd_viveiro/`, `api_viveiro/`, etc. têm `DOCKER.md` com atalhos — **sem compose próprio**.

## Reset do banco (apaga dados)

**Atenção:** `down -v` remove volumes **nomeados do projeto**, não o externo `bd_viveiro_postgres_data`. Para wipe total do banco legado:

```powershell
docker compose down
docker volume rm bd_viveiro_postgres_data   # irreversível
.\scripts\dev.ps1 start
.\scripts\dev.ps1 migrate
```

Reset só do stack (preserva `bd_viveiro_postgres_data`):

```powershell
docker compose down
.\scripts\dev.ps1 start
.\scripts\dev.ps1 migrate
```

## Memória (Docker Desktop ~12 GB?)

Os containers **SisViNa** usam ~300 MB no total (Postgres + API + web). O que enche RAM no Docker Desktop:

| O quê | Tamanho típico |
|-------|----------------|
| VM WSL2 (limite configurado) | 4–12 GB reservados |
| Imagens + build cache | 3–5 GB em disco |
| Volumes (Postgres) | ~750 MB |

**Não é normal** o SisViNa sozinho usar 12 GB — é o **Docker Desktop inteiro**.

Reduzir:

1. **Front local** (economiza container Node): `npm run dev` + `.\scripts\dev.ps1 start` (só API+BD)
2. Limpar cache: `docker system prune -a` (cuidado — remove imagens não usadas)
3. Docker Desktop → Settings → Resources → Memory: **4–6 GB** basta para dev
4. Parar o que não usa: `.\scripts\dev.ps1 stop`

## Banco legado (init-scripts sem Alembic)

Se login der `ERR_EMPTY_RESPONSE` ou API cair com `column perfis does not exist`:

```powershell
.\scripts\migrate-legacy.ps1
```

## Volume Postgres (CRÍTICO)

O compose usa o volume **externo** `bd_viveiro_postgres_data` (dados reais de dev).

| Volume | Situação |
|--------|----------|
| `bd_viveiro_postgres_data` | **Oficial** — 349+ plantas, layout, etc. |
| `sisvina_postgres_data` | Volume vazio criado na reorganização — **não usar** |

Sintomas com volume errado/vazio:
- Home e Produção zeradas (0 mudas, 0 canteiros)
- Layout do viveiro vazio `{}`

Se apareceu volume vazio por engano:

```powershell
# compose/infra.yml já aponta para bd_viveiro_postgres_data
.\scripts\dev.ps1 stop
.\scripts\dev.ps1 start
.\scripts\dev.ps1 migrate
```

Opcional (só se tiver certeza que não precisa): `docker volume rm sisvina_postgres_data`

## CORS + 500 nos endpoints

Mensagem tipo *"No Access-Control-Allow-Origin"* em `/estoques/resumo` ou `/viveiro/layout/` **não é config CORS** — é a API retornando **500** antes de montar os headers.

Causas comuns neste projeto:
1. Schema incompleto (migrations 06–20 puladas com `stamp` manual)
2. Colunas faltando: `funcionarios.perfis`, `insumos.valor_estoque`, tabela `viveiro_layout`

Reparo: migration `26_repair_schema_skipped` via `.\scripts\dev.ps1 migrate`.

Verifique: `docker compose logs api --tail 50` e teste `GET http://localhost:8000/health`.

**Nunca** rode `alembic stamp` manual — só `alembic upgrade head`.
