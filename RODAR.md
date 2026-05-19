# SisViNa — rodar tudo com Docker

## Git (monorepo na raiz)

Abra no Cursor a pasta **`C:\Projetos\SisViNa`** (não só uma subpasta).

```powershell
cd c:\Projetos\SisViNa
git status
git add -A
git commit -m "sua mensagem"
git push
```

Primeira vez no GitHub: crie um repositório **vazio** (sem README) e:

```powershell
git remote add origin https://github.com/SEU_USUARIO/SisViNa.git
git push -u origin main
```

`.env` não é versionado (só `.env.example` na API).

---

## Pré-requisito

Docker Desktop instalado e em execução.

## Subir o sistema

### Se você já tinha Postgres/API rodando (seu caso comum)

```powershell
cd c:\Projetos\SisViNa\api_viveiro
docker compose up -d --build

cd c:\Projetos\SisViNa\sistema-viveiro-nativas
docker compose up -d
```

Aguarde ~1–2 min no primeiro `npm ci` do front.

### Tudo do zero (raiz — só se não houver containers `viveiro_*`)

```powershell
cd c:\Projetos\SisViNa
docker network create viveiro_network
docker compose up -d --build
```

Se der conflito de nome de container, pare os antigos (`docker stop viveiro_postgres viveiro_api ...`) ou use o modo acima por pasta.

### Erro da rede `viveiro_network` (label incorrect)

A rede foi criada manualmente (`docker network create`). O `bd_viveiro` usa `external: true` — só precisa existir:

```powershell
docker network create viveiro_network
```

Se ainda falhar, reset limpo (apaga dados do Postgres):

```powershell
docker stop viveiro_postgres viveiro_pgadmin viveiro_api viveiro_web 2>$null
docker rm viveiro_postgres viveiro_pgadmin viveiro_api viveiro_web 2>$null
docker network rm viveiro_network
docker network create viveiro_network
cd c:\Projetos\SisViNa\bd_viveiro
docker compose up -d
```

## Acessar

| Serviço | URL |
|---------|-----|
| **Front (app)** | http://localhost:5173 |
| **API (Swagger)** | http://localhost:8000/docs |
| **API health** | http://localhost:8000/health |
| **PgAdmin** | http://localhost:5050 |

### Login do sistema

- **Usuário:** `admin`
- **Senha:** `Admin@123`

### PgAdmin (opcional)

- E-mail: `admin@viveiro.com`
- Senha: `admin_senha`
- Servidor Postgres: host `postgres`, porta `5432`, user `viveiro_admin`, senha `senha_segura_aqui`, DB `viveiro_db`

## O que foi integrado

- Postgres sobe com schema SQL + usuário admin + 3 espécies de exemplo
- API conecta no banco e cria admin automaticamente se faltar
- Front exige login; **Biblioteca** e contador da **Home** leem dados reais da API

## Ver logs

```powershell
docker compose logs -f api web
```

## Parar

```powershell
docker compose down
```

## Banco zerado (recriar schema + seeds)

Se você já tinha um volume antigo sem seeds:

```powershell
docker compose down -v
docker compose up -d --build
```

`-v` apaga os volumes (dados do Postgres).

## Subir só BD ou só API (repos separados)

Ordem recomendada:

1. `cd bd_viveiro` → `docker compose up -d`
2. `cd api_viveiro` → `docker compose up -d --build`
3. `cd sistema-viveiro-nativas` → `docker compose up -d`

Use o `docker-compose.yml` da **raiz** para evitar essa ordem manual.
