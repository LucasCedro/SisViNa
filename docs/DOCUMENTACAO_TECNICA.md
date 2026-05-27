# SisViNa — Documentação Técnica

**Sistema de Gestão de Viveiro de Plantas Nativas**

| Repositório | `https://github.com/LucasCedro/SisViNa.git` |
|-------------|---------------------------------------------|
| Monorepo    | `bd_viveiro` · `api_viveiro` · `sistema-viveiro-nativas` |

---

## 1. Visão Geral do Sistema

### O que é

O **SisViNa** é um sistema web para gestão operacional e comercial de viveiros de plantas nativas. Cobre o ciclo completo desde o cadastro de **árvores-matriz** e **coleta de sementes** até **produção de mudas**, **controle fitossanitário**, **vendas** e **indicadores financeiros**.

### Problema que resolve

- Centraliza dados dispersos (planilhas, cadernos de campo) em um único fluxo rastreável.
- Garante **rastreabilidade** semente → muda → venda (código de lote, planta e histórico de transferências).
- Apoia decisões com dashboards, relatórios de coleta (CSV) e resumo financeiro (CAPEX/OPEX + receita de vendas).
- Registra operações de campo (coleta, semeadura, fertilização, pragas) vinculadas a funcionários.

### Arquitetura geral

```text
┌─────────────────────┐     HTTPS/JSON      ┌─────────────────────┐
│  sistema-viveiro-   │  Bearer JWT         │     api_viveiro     │
│  nativas (Vue 3)    │ ──────────────────► │  FastAPI + Uvicorn  │
│  Vite · Pinia       │                     │  SQLAlchemy async   │
└─────────────────────┘                     └──────────┬──────────┘
                                                         │
                                                         │ asyncpg
                                                         ▼
                                              ┌─────────────────────┐
                                              │  PostgreSQL 15      │
                                              │  (bd_viveiro/Docker)│
                                              └─────────────────────┘
```

| Camada | Tecnologia | Responsabilidade |
|--------|------------|------------------|
| Frontend | Vue 3, Vue Router, Pinia, Axios, Tailwind, Leaflet, Chart.js | UI, guards de rota, chamadas REST |
| API | Python 3.9, FastAPI, Pydantic v1, SQLAlchemy 2 | Regras de negócio, validação, JWT |
| Persistência | PostgreSQL 15 | Dados transacionais, views e triggers (via Alembic) |
| Migrações | Alembic (`api_viveiro/alembic`) | **Fonte oficial do schema** |

### Módulos funcionais (frontend)

| Rota | Módulo |
|------|--------|
| `/` | Home / resumo |
| `/coleta` | Matrizes, coletas, lotes, testes, semeaduras |
| `/viveiro` | Layout do viveiro e cadastro de mudas |
| `/producao` | Promoção sementeira → canteiro |
| `/estoques` | Lotes em armazém e insumos |
| `/fitossanidade` | Pragas e combates |
| `/fertilizacao` | Atividades e insumos |
| `/vendas-estoque` | Compradores, vendas, estoque de plantas |
| `/financeiro` | Lançamentos CAPEX/OPEX |
| `/biblioteca` | Catálogo de espécies |
| `/prescricao` | Prescrição técnica (PDF local) |

### Autenticação e autorização

- **Implementado:** login JWT; rotas da API exigem `Authorization: Bearer <token>`; frontend bloqueia rotas sem token.
- **Não implementado (previsto):** RBAC por cargo/perfil — qualquer usuário autenticado acessa todos os módulos.

---

## 2. Requisitos e Dependências

### Software

| Componente | Versão recomendada |
|------------|-------------------|
| Node.js | 18+ (LTS) |
| npm | 9+ |
| Python | 3.9+ |
| PostgreSQL | 15 (via Docker) |
| Docker Desktop | Atual (Windows/macOS/Linux) |

### Dependências por pacote

**API** (`api_viveiro/requirements.txt`): FastAPI 0.95, Uvicorn 0.22, SQLAlchemy 2.0.9, Alembic 1.10.4, asyncpg, python-jose, passlib, bcrypt, pytest, httpx.

**Frontend** (`sistema-viveiro-nativas/package.json`): Vue 3.4, Vue Router 4, Pinia 2, Axios 1.6, Vite 5, Tailwind 3, Leaflet, Chart.js.

### Variáveis de ambiente

#### API — `api_viveiro/.env`

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | Conexão async PostgreSQL | `postgresql+asyncpg://viveiro_admin:senha_segura_aqui@localhost:5432/viveiro_db` |
| `TEST_DATABASE_URL` | Banco de testes | `.../viveiro_test_db` |
| `API_V1_STR` | Prefixo da API | `/api/v1` |
| `PROJECT_NAME` | Título OpenAPI | `Viveiro API` |
| `BACKEND_CORS_ORIGINS` | Origens CORS (JSON array) | `["http://localhost:5173"]` |
| `SECRET_KEY` | Chave JWT | Alterar em produção |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token | `480` |

#### Frontend — `sistema-viveiro-nativas/.env` (opcional)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `VITE_API_URL` | URL base da API | `http://localhost:8000` |

### Seeds e dados de demonstração

Executados no **startup da API** (`app/bootstrap.py`) **somente quando o registro ainda não existe**:

| Seed | Condição | Conteúdo |
|------|----------|----------|
| Admin padrão | Sem usuário `admin` | `admin` / `Admin@123` |
| Espécies demo | Tabela `especies` vazia | Ipê, Jatobá, Araucária |
| Comprador demo | Tabela `compradores` vazia | Comprador PF de exemplo |

> **Produção:** desabilitar ou remover seeds automáticos antes do deploy.

### Rede Docker

A API e o Postgres usam a rede externa `viveiro_network`:

```powershell
docker network create viveiro_network
```

---

## 3. Estrutura de Pastas

### Monorepo (raiz)

```text
SisViNa/
├── bd_viveiro/              # Postgres + PgAdmin (Docker)
├── api_viveiro/             # API REST FastAPI
├── sistema-viveiro-nativas/ # SPA Vue 3
├── docs/                    # Documentação do projeto
├── docker-compose.yml       # Orquestração opcional (tudo em Docker)
├── RODAR.md                 # Guia operacional Docker
└── README.md
```

### `api_viveiro/`

| Pasta / arquivo | Papel |
|-----------------|-------|
| `app/main.py` | App FastAPI, CORS, registro de routers, startup |
| `app/routes/` | Endpoints HTTP por domínio |
| `app/crud/` | Regras de negócio e queries |
| `app/models/` | Entidades SQLAlchemy |
| `app/schemas/` | DTOs Pydantic (entrada/saída) |
| `app/auth/` | JWT, login, `get_current_user` |
| `app/bootstrap.py` | Seeds de desenvolvimento |
| `alembic/versions/` | Migrações oficiais do schema |
| `tests/` | Testes de integração (pytest + httpx) |

**Migrações Alembic (ordem):**

| Revision | Conteúdo |
|----------|----------|
| `001_criar_tabelas_iniciais` | Espécies, funcionários, compradores, canteiros, plantas, atividades, pragas, insumos, vendas, views/triggers base |
| `002_arvores_matriz` | Árvores-matriz |
| `003_coletas_sementes` | Coletas + view BI |
| `004_coleta_integracao` | Lotes, testes, semeaduras, rastreabilidade |
| `005_lancamentos_financeiros` | CAPEX/OPEX + `vw_resumo_financeiro` |

### `sistema-viveiro-nativas/`

| Pasta | Papel |
|-------|-------|
| `src/router/` | Rotas e guard de autenticação |
| `src/store/` | Estado Pinia (`auth`, `coleta`, …) |
| `src/services/` | Cliente Axios por recurso REST |
| `src/views/` | Páginas (uma por rota principal) |
| `src/components/` | UI por módulo (`coleta`, `viveiro`, `financeiro`, …) |
| `src/constants/` | Enums e cores de gráficos |
| `docs/DESIGN_SYSTEM.md` | Tokens visuais e padrões de UI |

### `bd_viveiro/`

| Pasta | Papel |
|-------|-------|
| `docker-compose.yml` | Postgres 15 + PgAdmin |
| `init-scripts/` | Scripts SQL legados (não usar como fonte oficial de schema) |

> O schema evolutivo deve ser mantido via **Alembic** em `api_viveiro`.

---

## 4. Fluxo de Dados e Principais Funcionalidades

### 4.1 Autenticação

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant A as API
    participant DB as PostgreSQL

    U->>F: login + senha
    F->>A: POST /api/v1/auth/login (form-urlencoded)
    A->>DB: valida funcionario.usuario + senha (bcrypt)
    A-->>F: access_token + token_type
    F->>F: localStorage.token
    F->>A: GET /api/v1/auth/me (Bearer)
    A-->>F: FuncionarioOut
    Note over F: router.beforeEach bloqueia rotas sem token
```

**Regras:**

- Login usa `OAuth2PasswordRequestForm` (`username`, `password`).
- Usuário inativo → `403`.
- Credenciais inválidas → `401`.
- Frontend: interceptor Axios redireciona para `/login` em `401`.

### 4.2 Cadeia coleta → produção → venda

Fluxo central do negócio:

```text
arvores_matriz → coletas_sementes → lotes_sementes → testes_sementes
       → semeaduras → plantas (SEMENTE) → promover-mudas → plantas (MUDA)
       → vendas / itens_venda → plantas (VENDIDA)
```

| Etapa | Ação | Efeito principal |
|-------|------|------------------|
| 1. Matriz | Cadastro de árvore-matriz com coordenadas (geo ou UTM) e dados legais/fenológicos | Origem rastreável da semente |
| 2. Coleta | Registro de coleta vinculada à matriz; opcional `gerar_lote: true` | Cria lote com código rastreável |
| 3. Teste | Germinação, viabilidade, tetrazólio no lote | Qualidade do lote |
| 4. Semeadura | Debita `quantidade_disponivel` do lote; local tipo `sementeira` | Plantas `SEMENTE` se `registrar_plantas` |
| 5. Produção | `POST /plantas/promover-mudas` | Status `MUDA`, move para canteiro tipo `canteiro`, grava `transferencias_plantas` |
| 6. Venda | `POST /vendas` com itens | `valor_total` calculado; plantas → `VENDIDA` |

**Tipos de local (`canteiros.tipo_local`):**

| Valor | Uso |
|-------|-----|
| `sementeira` | Semeadura e mudas em fase inicial |
| `canteiro` | Mudas em produção |
| `armazem` | Estoque de sementes (entrada sem coleta) |

### 4.3 Semeadura (regras de negócio)

Endpoint: `POST /api/v1/semeaduras/`

Validações em `app/crud/semeaduras.py`:

- Lote deve existir e não estar `descartado`.
- `quantidade_sementes_usadas` ≤ `lote.quantidade_disponivel`.
- Canteiro informado deve ter `tipo_local = sementeira`.
- Debita estoque do lote; se zerar, `lote.status = esgotado`.
- Com `registrar_plantas: true`, cria N plantas `SEMENTE` com `codigo_rastreio` derivado do lote.

**Exemplo de corpo:**

```json
{
  "id_lote_sementes": 1,
  "id_canteiro": 2,
  "data_semeadura": "2026-05-20",
  "quantidade_sementes_usadas": 50,
  "quantidade_mudas_obtidas": 40,
  "registrar_plantas": true,
  "quantidade_plantas_registrar": 40,
  "observacoes": "Bandeja A1"
}
```

### 4.4 Promoção de mudas (sementeira → canteiro)

Endpoint: `POST /api/v1/plantas/promover-mudas`

- Plantas devem estar em status `SEMENTE`.
- Origem validada como `sementeira`; destino como `canteiro`.
- Atualiza `status` → `MUDA`, `data_germinacao`, `id_canteiro`.
- Registra histórico em `transferencias_plantas`.

### 4.5 Cadastro em lote (compra / inventário)

Endpoint: `POST /api/v1/plantas/cadastro-lote`

- Cria até 500 plantas por requisição.
- `origem`: `semeadura` | `compra` | `doacao` | `ajuste`.
- Canteiro validado conforme `status` (`SEMENTE` → sementeira; demais → canteiro).

### 4.6 Vendas

Endpoint: `POST /api/v1/vendas`

- Exige ao menos um item.
- `valor_total` = soma de `(valor_unitario × quantidade) - desconto` por item.
- Cada planta do item passa a `VENDIDA`.
- Cancelamento (`status: CANCELADO`) reverte plantas para `ADULTA` (comportamento atual).

### 4.7 Financeiro

- `lancamentos_financeiros`: tipo `CAPEX` ou `OPEX`.
- `GET /api/v1/dashboard/financeiro`: agrega receitas (vendas pagas), custos operacionais e lançamentos via view `vw_resumo_financeiro`.

### 4.8 Rastreabilidade

- `GET /api/v1/semeaduras/rastreabilidade/planta/{id}` — cadeia matriz → coleta → lote → semeadura → venda.
- Exportações CSV em `/api/v1/coleta-relatorios/export/*.csv`.

### Modelo de dados (resumo)

```text
especies ─┬─ arvores_matriz ── coletas_sementes ── lotes_sementes ─┬─ testes_sementes
          │                                                        └─ semeaduras ── plantas
          └─ plantas ──┬─ atividades (N:N insumos)
                       ├─ pragas_plantas ── combates_realizados
                       └─ itens_venda ── vendas ── compradores

funcionarios ── (coletas, semeaduras, atividades, vendas, combates)
canteiros ── plantas, semeaduras
lancamentos_financeiros
transferencias_plantas
```

**Status de planta:** `SEMENTE` | `MUDA` | `JOVEM` | `ADULTA` | `VENDIDA` | `MORTA`

---

## 5. Documentação da API (fluxos principais)

**Base URL:** `http://localhost:8000`  
**Prefixo:** `/api/v1`  
**Documentação interativa:** `/docs` (Swagger)  
**Autenticação:** `Authorization: Bearer <token>` em todas as rotas abaixo, exceto login.

**Formato de erro padrão (FastAPI):**

```json
{
  "detail": "Mensagem de erro ou lista de validação"
}
```

| HTTP | Significado usual |
|------|-------------------|
| 400 | Regra de negócio / validação |
| 401 | Token ausente ou inválido |
| 403 | Usuário inativo |
| 404 | Recurso não encontrado |
| 422 | Body/query inválido (Pydantic) |

---

### 5.1 Autenticação

| Método | Rota | Auth | Corpo | Sucesso | Erros |
|--------|------|------|-------|---------|-------|
| POST | `/auth/login` | Não | `application/x-www-form-urlencoded`: `username`, `password` | `200` `{ "access_token", "token_type": "bearer" }` | `401`, `403` |
| GET | `/auth/me` | Sim | — | `200` `FuncionarioOut` | `401` |
| POST | `/auth/reset-password` | Sim | `{ "old_password", "new_password" }` | `200` `FuncionarioOut` | `400`, `404` |

---

### 5.2 Coleta e sementes

#### Árvores-matriz

| Método | Rota | Corpo (JSON) | Sucesso |
|--------|------|--------------|---------|
| GET | `/arvores-matriz/` | Query: filtros opcionais | `200` lista `ArvoreMatrizOut` |
| POST | `/arvores-matriz/` | `ArvoreMatrizCreate` (nome, id_especie, coordenadas geo/UTM, tipo_origem, fenologia…) | `201` |
| PUT | `/arvores-matriz/{id}` | `ArvoreMatrizUpdate` | `200` |
| DELETE | `/arvores-matriz/{id}` | — | `200` |

#### Coletas de sementes

| Método | Rota | Corpo | Sucesso |
|--------|------|-------|---------|
| GET | `/coletas-sementes/` | Query: `id_arvore_matriz`, datas… | `200` |
| POST | `/coletas-sementes/` | `{ id_arvore_matriz, data_coleta, quantidade_sementes, gerar_lote?, observacoes? }` | `201` |
| PUT | `/coletas-sementes/{id}` | `ColetaSementesUpdate` | `200` |

#### Lotes de sementes

| Método | Rota | Corpo | Sucesso |
|--------|------|-------|---------|
| GET | `/lotes-sementes/` | — | `200` |
| POST | `/lotes-sementes/` | Criação manual de lote | `201` |
| POST | `/lotes-sementes/entrada-armazem` | Entrada em armazém | `201` |
| PUT | `/lotes-sementes/{id}` | Atualização de lote | `200` |

#### Testes de sementes

| Método | Rota | Corpo | Sucesso |
|--------|------|-------|---------|
| GET | `/testes-sementes/` | — | `200` |
| POST | `/testes-sementes/` | `{ id_lote_sementes, tipo_teste, percentual_resultado, … }` | `201` |
| PUT | `/testes-sementes/{id}` | — | `200` |

#### Semeaduras

| Método | Rota | Corpo | Sucesso |
|--------|------|-------|---------|
| GET | `/semeaduras/` | — | `200` |
| POST | `/semeaduras/` | `SemeaduraCreate` (ver §4.3) | `201` `SemeaduraOut` |
| GET | `/semeaduras/rastreabilidade/planta/{planta_id}` | — | `200` `RastreabilidadePlantaOut` |

**Erros típicos:** `400` com `detail` em texto (ex.: *"Quantidade usada excede o disponível no lote"*).

---

### 5.3 Produção e plantas

| Método | Rota | Corpo | Sucesso |
|--------|------|-------|---------|
| GET | `/plantas/` | Query: `id_especie`, `id_canteiro`, `status` | `200` |
| GET | `/plantas/pendentes-transferencia` | — | `200` mudas em `SEMENTE` na sementeira |
| POST | `/plantas/promover-mudas` | `{ ids_plantas[], id_canteiro_destino, data_germinacao?, observacoes? }` | `200` `{ transferidas, ids_plantas }` |
| POST | `/plantas/cadastro-lote` | `CadastroLotePlantasRequest` | `201` `{ criadas, ids_plantas }` |
| GET | `/plantas/estoque-resumo` | — | `200` agregado por espécie |
| PATCH | `/plantas/preco-especie/{id_especie}` | `{ preco_venda }` | `200` |

---

### 5.4 Viveiro operacional

#### Canteiros

| Método | Rota | Notas |
|--------|------|-------|
| GET/POST/PUT/DELETE | `/canteiros/` | Incluir `tipo_local` ao cadastrar |

#### Atividades (fertilização)

| Método | Rota |
|--------|------|
| GET/POST | `/atividades/` |
| GET/POST | `/atividades/tipos` |

#### Pragas (fitossanidade)

| Método | Rota |
|--------|------|
| CRUD | `/pragas/tipos`, `/pragas/metodos`, `/pragas/plantas`, `/pragas/combates` |

#### Insumos e estoque

| Método | Rota |
|--------|------|
| CRUD | `/insumos/` |
| POST | `/insumos/{id}/estoque` — entrada de estoque |
| GET | `/estoques/resumo` |
| POST | `/estoques/entrada-sementes` — lote sem coleta |

---

### 5.5 Comercial e financeiro

#### Vendas

| Método | Rota | Corpo |
|--------|------|-------|
| GET | `/vendas/` | — |
| POST | `/vendas/` | `{ id_comprador, id_funcionario, data_venda, status, itens: [{ id_planta, quantidade, valor_unitario, desconto? }] }` |
| PUT | `/vendas/{id}` | Atualização / cancelamento |
| DELETE | `/vendas/{id}` | Remove venda e restaura plantas |

#### Lançamentos financeiros

| Método | Rota | Corpo |
|--------|------|-------|
| GET/POST | `/lancamentos-financeiros/` | `{ tipo: "CAPEX"\|"OPEX", valor, descricao, data, … }` |
| PUT/DELETE | `/lancamentos-financeiros/{id}` | — |

#### Dashboard

| Método | Rota | Resposta |
|--------|------|----------|
| GET | `/dashboard/resumo` | Indicadores gerais do viveiro |
| GET | `/dashboard/financeiro` | `ResumoFinanceiroOut` |

---

### 5.6 Cadastros de apoio

| Recurso | Prefixo |
|---------|---------|
| Espécies | `/especies/` |
| Funcionários | `/funcionarios/` |
| Compradores | `/compradores/` |

---

### 5.7 Relatórios (CSV)

| Método | Rota | Resposta |
|--------|------|----------|
| GET | `/coleta-relatorios/export/matrizes.csv` | `text/csv` |
| GET | `/coleta-relatorios/export/coletas.csv` | `text/csv` |
| GET | `/coleta-relatorios/export/lotes.csv` | `text/csv` |
| GET | `/coleta-relatorios/export/rastreabilidade-matriz.csv` | `text/csv` |

---

### Exemplo: login + chamada autenticada

```bash
# Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin@123"

# Listar matrizes
curl http://localhost:8000/api/v1/arvores-matriz/ \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## 6. Instruções de Configuração (desenvolvimento)

Fluxo recomendado: **Postgres no Docker**; **API e frontend no terminal**.

### 6.1 Clonar o repositório

```powershell
git clone https://github.com/LucasCedro/SisViNa.git
cd SisViNa
```

### 6.2 Subir o banco (Docker)

```powershell
docker network create viveiro_network
cd bd_viveiro
docker compose up -d
```

| Serviço | URL / porta |
|---------|-------------|
| PostgreSQL | `localhost:5432` |
| PgAdmin | http://localhost:5050 |

Credenciais padrão do Postgres (compose):

- **User:** `viveiro_admin`
- **Senha:** `senha_segura_aqui`
- **Database:** `viveiro_db`

### 6.3 Aplicar schema (Alembic)

```powershell
cd ..\api_viveiro
copy .env.example .env
# Ajuste DATABASE_URL se necessário (host localhost:5432)

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
```

> Em banco **novo**, o schema deve vir **somente** do Alembic. Se um volume antigo já tiver tabelas de outra origem, recrie: `docker compose down -v` em `bd_viveiro` e suba de novo antes do `alembic upgrade head`.

### 6.4 Subir a API (terminal)

```powershell
# Com venv ativo em api_viveiro
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| Verificação | URL |
|-------------|-----|
| Health | http://localhost:8000/health |
| Swagger | http://localhost:8000/docs |

No primeiro startup em **dev**, a API cria admin e dados demo se o banco estiver vazio (ver §2).

**Login dev:** `admin` / `Admin@123`

### 6.5 Subir o frontend (terminal)

```powershell
cd ..\sistema-viveiro-nativas
npm install

# Opcional: .env
# VITE_API_URL=http://localhost:8000

npm run dev
```

| App | URL |
|-----|-----|
| Frontend | http://localhost:5173 |

### 6.6 Checklist rápido

- [ ] Docker Desktop em execução
- [ ] Rede `viveiro_network` criada
- [ ] Postgres respondendo na porta 5432
- [ ] `alembic upgrade head` sem erro
- [ ] API em `/health` com `"database": "connected"`
- [ ] Login no front com `admin`
- [ ] Canteiros cadastrados com `tipo_local` (`sementeira`, `canteiro`, `armazem`)

### 6.7 Testes da API

```powershell
cd api_viveiro
pytest
```

Requer `TEST_DATABASE_URL` apontando para um banco de testes separado (`viveiro_test_db`).

### 6.8 Alternativa: tudo em Docker

Para subir API e front também em containers, consulte [RODAR.md](../RODAR.md) na raiz do monorepo.

---

## Referências rápidas

| Documento | Conteúdo |
|-----------|----------|
| [RODAR.md](../RODAR.md) | Docker completo, patches, troubleshooting |
| [DESIGN_SYSTEM.md](../sistema-viveiro-nativas/docs/DESIGN_SYSTEM.md) | UI e tokens visuais |
| `/docs` (API) | OpenAPI gerado pelo FastAPI |

---

*Documentação gerada para o monorepo SisViNa. Schema oficial: Alembic em `api_viveiro`. RBAC: planejado, não implementado.*
