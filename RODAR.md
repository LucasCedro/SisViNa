# SisViNa — rodar tudo com Docker

## Git (monorepo na raiz)

Abra no Cursor a pasta **`C:\Projetos\SisViNa`** (não só uma subpasta).

Repositório: `https://github.com/LucasCedro/SisViNa.git` (branch `main`).

**Nunca** commite `.env` com senhas — só `.env.example` na API. Fluxo usual: `git status` → `git add` → `commit` → `push origin main`.

---

## Pré-requisito

Docker Desktop instalado e em execução.

> **Fluxo oficial e arquitetura dos composes:** [docs/DEV_DOCKER.md](./docs/DEV_DOCKER.md)

## Subir o sistema

```powershell
cd c:\Projetos\SisViNa
.\scripts\dev.ps1 start          # Postgres + API
cd sistema-viveiro-nativas
npm run dev                      # front (recomendado)
```

Tudo em Docker (front + API + BD):

```powershell
.\scripts\dev.ps1 start-all
```

Demo consultor (site + PgAdmin):

```powershell
.\scripts\dev.ps1 start-demo
```

Parar:

```powershell
.\scripts\dev.ps1 stop
```

Após editar `api_viveiro/.env`:

```powershell
.\scripts\dev.ps1 restart-api
```

### Reset limpo (apaga dados do Postgres)

```powershell
docker compose down -v
.\scripts\dev.ps1 start
.\scripts\dev.ps1 migrate
```

## NF-e (Focus) — `api_viveiro/.env`

Se o bloco abaixo **não existir** no seu `.env`, copie de `.env.example`:

```env
FOCUS_NFE_TOKEN=
FOCUS_NFE_URL_HOMOLOGACAO=https://homologacao.focusnfe.com.br
FOCUS_NFE_URL_PRODUCAO=https://api.focusnfe.com.br
FOCUS_NFE_TIMEOUT=60
NFE_ALLOW_PRODUCAO=false
```

| Variável | Se ausente | Efeito |
|----------|------------|--------|
| `FOCUS_NFE_TOKEN` | vazio | Modo **simulação** (não chama Focus) — UI avisa |
| URLs | defaults em `config.py` | Homologação OK |
| `NFE_ALLOW_PRODUCAO` | `false` | Produção **bloqueada** |

Após editar: `.\scripts\dev.ps1 restart-api`. Conferir: `docker compose logs api | Select-String "NF-e"`.

## Acessar

| Serviço | URL |
|---------|-----|
| **Site público (marketing)** | http://localhost:3000 |
| **App (login + sistema)** | http://localhost:5173 |
| **Login direto** | http://localhost:5173/login |
| **API (Swagger)** | http://localhost:8000/docs |
| **API health** | http://localhost:8000/health |
| **PgAdmin** | http://localhost:5050 |

### Fluxo para demonstração (v0.1)

1. Abra o **site** em http://localhost:3000 (página pública, sem login).
2. Clique em **Entrar** (canto superior) → vai para http://localhost:5173/login.
3. Após login, a **Home** (`/`) é o painel do viveiro (não é o site marketing).

O site (`site/`) e o app (`sistema-viveiro-nativas/`) são **dois frontends** em portas diferentes. A integração é por link configurável (`VITE_APP_URL` no build do site).

### Subir o site marketing junto

Na raiz do monorepo (já incluso no `docker compose` principal):

```powershell
cd c:\Projetos\SisViNa
docker compose --profile site --profile docker-web up -d --build site web api postgres
```

Ou: `.\scripts\dev.ps1 start-demo`

Variável opcional antes do build (produção):

```env
# site/.env ou ARG no compose
VITE_APP_URL=https://app.seudominio.com.br
```

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

## Alterou código do front e o browser não atualizou?

No **Docker + Windows**, o Vite precisa de *polling* (já configurado em `vite.config.js`).

1. Salve o arquivo (`Ctrl+S`)
2. Espere ~1 s — a página deve atualizar sozinha
3. Se não: **F5** (não precisa `docker compose up` de novo)

Só reinicie o front se mudou `package.json`:

```powershell
docker compose restart web
```

---

## Ver logs

```powershell
docker compose logs -f api web
```

## Parar

```powershell
.\scripts\dev.ps1 stop
```

## Schema coleta → produção → venda (banco via `bd_viveiro/init-scripts`)

Fluxo persistente no Postgres:

`arvores_matriz` → `coletas_sementes` → `lotes_sementes` → `testes_sementes` → `semeaduras` → `plantas` → `itens_venda` / `vendas`

Views: `vw_rastreabilidade_muda`, `vw_cadeia_semente_muda_venda`.

Se `alembic upgrade head` falhar com «relation species already exists», o Postgres foi criado **sem** Alembic.

Banco **já com** coletas/lotes/semeadura (migração antiga) — só falta a view até venda:

```powershell
Get-Content c:\Projetos\SisViNa\bd_viveiro\patches\cadeia-semente-muda-venda.sql -Raw | docker compose exec -T postgres psql -U viveiro_admin -d viveiro_db
.\scripts\dev.ps1 restart-api
```

Lançamentos financeiros (CAPEX/OPEX + view `vw_resumo_financeiro`):

```powershell
Get-Content c:\Projetos\SisViNa\bd_viveiro\patches\lancamentos-financeiros.sql -Raw | docker compose exec -T postgres psql -U viveiro_admin -d viveiro_db
.\scripts\dev.ps1 restart-api
```

Banco **sem** esse módulo ainda — script único `05-coleta-producao-cadeia.sql` (idempotente):

```powershell
Get-Content c:\Projetos\SisViNa\bd_viveiro\init-scripts\05-coleta-producao-cadeia.sql -Raw | docker compose exec -T postgres psql -U viveiro_admin -d viveiro_db
.\scripts\dev.ps1 restart-api
```

Use `.\scripts\dev.ps1 migrate` em banco **novo** gerido só pelo Alembic.

## Patch: produção, locais e estoques (`07`)

Banco **já existente** sem `tipo_local` / transferências:

```powershell
Get-Content c:\Projetos\SisViNa\bd_viveiro\patches\producao-locais-origem.sql -Raw | docker compose exec -T postgres psql -U viveiro_admin -d viveiro_db
.\scripts\dev.ps1 restart-api
```

Depois, marque cada **canteiro** com `tipo_local`: `sementeira`, `canteiro` ou `armazem` (via API ou PgAdmin). Sem isso, semeadura e transferência não encontram locais corretos.

Fluxo operacional:

1. **Coleta** → gera lote rastreável (matriz + coleta).
2. **Semeadura** → debita lote, cria plantas `SEMENTE` na **sementeira**.
3. **Produção** (`/producao`) → promove para `MUDA` e move para **canteiro** (histórico em `transferencias_plantas`).
4. **Cadastro de mudas** (viveiro) → lote com origem `compra` / inventário inicial.
5. **Estoques** (`/estoques`) → lotes no armazém + insumos; entrada de sementes sem coleta.

## Banco zerado (recriar schema + seeds)

Se você já tinha um volume antigo sem seeds:

```powershell
docker compose down -v
.\scripts\dev.ps1 start-all
.\scripts\dev.ps1 migrate
```

`-v` apaga os volumes (dados do Postgres).

## Referência Docker

Ver [docs/DEV_DOCKER.md](./docs/DEV_DOCKER.md) — único compose na raiz, `scripts/dev.ps1`.
