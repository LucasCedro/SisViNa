# SisViNa — rodar tudo com Docker

## Git (monorepo na raiz)

Abra no Cursor a pasta **`C:\Projetos\SisViNa`** (não só uma subpasta).

Repositório remoto deste projeto:

`https://github.com/LucasCedro/SisViNa.git` (branch `main`)

### Enviar código para o GitHub (push)

Tudo que mudou precisa de **commit** antes do **push**:

```powershell
cd c:\Projetos\SisViNa

git status

git add -A

git commit -m "feat: descreva o que mudou"

git push origin main
```

Exemplo de mensagem de commit:

```powershell
git commit -m "feat: coleta, produção sementeira→canteiro, estoques e integração API"
```

Antes do `git add -A`, confira se **não** aparece `.env` com senha — só `.env.example` deve ir pro Git.

### Login no GitHub (HTTPS)

Se o `git push` pedir usuário/senha:

- **Usuário:** seu login do GitHub
- **Senha:** um [Personal Access Token](https://github.com/settings/tokens) (não use a senha da conta)

Alternativa com SSH (depois de cadastrar chave no GitHub):

```powershell
git remote set-url origin git@github.com:LucasCedro/SisViNa.git
git push origin main
```

### Se o push for rejeitado

Alguém pode ter subido commits antes. Atualize e envie de novo:

```powershell
git pull origin main
git push origin main
```

### Primeira vez (repositório ainda sem remote)

Crie no GitHub um repositório **vazio** (sem README) e:

```powershell
cd c:\Projetos\SisViNa
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

## Alterou código do front e o browser não atualizou?

No **Docker + Windows**, o Vite precisa de *polling* (já configurado em `vite.config.js`).

1. Salve o arquivo (`Ctrl+S`)
2. Espere ~1 s — a página deve atualizar sozinha
3. Se não: **F5** (não precisa `docker compose up` de novo)

Só reinicie o front se mudou `package.json`:

```powershell
docker restart viveiro_web
```

---

## Ver logs

```powershell
docker compose logs -f api web
```

## Parar

```powershell
docker compose down
```

## Schema coleta → produção → venda (banco via `bd_viveiro/init-scripts`)

Fluxo persistente no Postgres:

`arvores_matriz` → `coletas_sementes` → `lotes_sementes` → `testes_sementes` → `semeaduras` → `plantas` → `itens_venda` / `vendas`

Views: `vw_rastreabilidade_muda`, `vw_cadeia_semente_muda_venda`.

Se `alembic upgrade head` falhar com «relation species already exists», o Postgres foi criado **sem** Alembic.

Banco **já com** coletas/lotes/semeadura (migração antiga) — só falta a view até venda:

```powershell
Get-Content c:\Projetos\SisViNa\bd_viveiro\patches\cadeia-semente-muda-venda.sql -Raw | docker exec -i viveiro_postgres psql -U viveiro_admin -d viveiro_db
docker restart viveiro_api
```

Lançamentos financeiros (CAPEX/OPEX + view `vw_resumo_financeiro`):

```powershell
Get-Content c:\Projetos\SisViNa\bd_viveiro\patches\lancamentos-financeiros.sql -Raw | docker exec -i viveiro_postgres psql -U viveiro_admin -d viveiro_db
docker restart viveiro_api
```

Banco **sem** esse módulo ainda — script único `05-coleta-producao-cadeia.sql` (idempotente):

```powershell
Get-Content c:\Projetos\SisViNa\bd_viveiro\init-scripts\05-coleta-producao-cadeia.sql -Raw | docker exec -i viveiro_postgres psql -U viveiro_admin -d viveiro_db
docker restart viveiro_api
```

Só use `docker exec viveiro_api alembic upgrade head` em banco **novo** gerido só pelo Alembic.

## Patch: produção, locais e estoques (`07`)

Banco **já existente** sem `tipo_local` / transferências:

```powershell
Get-Content c:\Projetos\SisViNa\bd_viveiro\patches\producao-locais-origem.sql -Raw | docker exec -i viveiro_postgres psql -U viveiro_admin -d viveiro_db
docker restart viveiro_api
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
docker compose up -d --build
```

`-v` apaga os volumes (dados do Postgres).

## Subir só BD ou só API (repos separados)

Ordem recomendada:

1. `cd bd_viveiro` → `docker compose up -d`
2. `cd api_viveiro` → `docker compose up -d --build`
3. `cd sistema-viveiro-nativas` → `docker compose up -d`

Use o `docker-compose.yml` da **raiz** para evitar essa ordem manual.
