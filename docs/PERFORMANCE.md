# scripts/smoke.ps1 (conceito)
# 1. Wait-Health http://localhost:8000/health → status ok + database connected
# 2. Wait-Http  http://localhost:5173 (200)
# 3. Login admin → Bearer
# 4. Assert 200: GET /api/v1/dashboard/resumo
# 5. Assert 200: GET /api/v1/coletas-sementes?limit=5
# 6. Assert 200: GET /api/v1/vendas/?limit=5
# exit 0 / throw




# Performance — SisViNa

Referência consolidada da auditoria read-only (front + API). **Nada aqui foi alterado no código** — serve para priorizar otimizações no futuro.

## Veredito geral

Para **viveiro pequeno/médio** (centenas a poucos milhares de mudas, dezenas de matrizes, 1–5 usuários simultâneos): **utilizável no dia a dia**.

O risco não é “lento por acidente grosseiro”, e sim **crescimento mal** em telas e endpoints específicos quando o volume de dados aumenta.

| Volume (ordem de grandeza) | Experiência esperada |
|----------------------------|----------------------|
| &lt; 2k mudas, &lt; 500 coletas | OK; picos em Produção, Financeiro, Estoques |
| 2k–10k mudas | Estoques resumo e Financeiro começam a pesar |
| 10k+ mudas | Estoques + painel financeiro + CIF na semeadura viram gargalo sério |

---

## O que está bem

### Frontend (`sistema-viveiro-nativas`)

| Item | Detalhe |
|------|---------|
| Lazy routes | Quase todas as views com `import()` dinâmico; exceção: **Home** (eager no bundle inicial) |
| Stack leve | Vue 3 + Pinia + Axios + Tailwind — sem UI kit pesado |
| Paralelismo | `Promise.all` / `allSettled` em home, store coleta |
| Cache Pinia | `useViveiroStore` usa flag `hidratado` — reabrir `/viveiro` não refaz 7 APIs |
| Lazy pontual | `html2pdf` dinâmico na exportação de coleta; imagens lazy na biblioteca |
| Tabs corretas em alguns lugares | `FitossanidadeView`, abas cadastro/locais do Viveiro usam `v-if` |

Arquivos de referência: `src/router/index.js`, `src/store/viveiro.js`, `src/store/viveiroContext.js`, `src/services/home.js`.

### Backend (`api_viveiro`)

| Item | Detalhe |
|------|---------|
| Async I/O | `create_async_engine` + `asyncpg` + `AsyncSession` |
| Eager loading | `joinedload` / `selectinload` em coletas, lotes, semeaduras, vendas |
| Agregação SQL | Resumos de produção/estoque com `COUNT` / `SUM` / `GROUP BY` |
| Batch parcial | `_mapa_ultimos_testes_germinacao` em lotes (`lotes_sementes.py`) — window `row_number()` |
| Views PG | `vw_ocupacao_canteiros`, `vw_resumo_financeiro` |
| Paginação | Maioria dos CRUDs com `skip` / `limit` |

---

## Gargalos — Frontend

### HIGH

| Problema | Onde | Impacto |
|----------|------|---------|
| Storm de APIs na primeira visita | `ProducaoView.vue` + painéis com **`v-show`** | Todos os painéis montam e rodam `onMounted(carregar)` mesmo ocultos; inclui `limit: 2000` em rustificação. **3–8s+** em rede lenta |
| N+1 readiness NF-e (até 100 req) | `ClientesCadastroPanel.vue` → `carregarNfeStatus` | `getCompradorNfeReadiness` por cliente; monta com `v-show` em Vendas |
| N+1 notas por venda (até 50 req) | `VendasPanel.vue` → `carregarNotasVendas` | Após `listVendas({ limit: 200 })`, uma API por venda |
| Coleta sem cache | `store/coleta.js` + `ColetaView.vue` | `carregar()` refetch completo em toda visita; sem `hidratado` |
| Chunk pesado da Coleta | `ColetaView.vue` | 15+ componentes + Leaflet no mesmo chunk da rota |

### MEDIUM

| Problema | Onde | Impacto |
|----------|------|---------|
| Sem `manualChunks` no Vite | `vite.config.js` | Chart.js, Leaflet embutidos nos chunks das rotas |
| Home eager + 8 APIs | `router/index.js`, `HomeView.vue` | Bundle inicial maior; refetch em cada visita |
| `v-show` em tabs = fetch oculto | `Vendas.vue`, `Financeiro.vue`, `ContabilidadePanel.vue`, tabelas Coleta | Ex.: `FinanceiroPremissas` carrega na aba errada |
| Listas sem virtualização | `TabelaColeta`, `BibliotecaView`, `EstoquesView` | DOM grande com centenas de linhas |
| `listLancamentos()` sem limit | `Financeiro.vue` | Payload cresce com histórico |
| Leaflet + watch deep | `MapaColeta.vue` | Recria markers a cada filtro |
| Timer 2s no editor | `ViveiroLayoutEditor` / designer | CPU em background na rota do editor |

### LOW

- `vue-chartjs` no `package.json` mas não usado (código usa `chart.js/auto` direto)
- APIs duplicadas entre Home, Viveiro, Fitossanidade (só viveiro cacheia)
- Sem `<KeepAlive>` nas rotas — troca de página destrói view e refaz `onMounted`
- Biblioteca: `limit: 1000` + grid completo (imagens lazy ajudam)

---

## Gargalos — Backend

### HIGH

| Problema | Onde | Impacto |
|----------|------|---------|
| **`GET /estoques/resumo` monolítico** | `crud/estoques.py`, `estoques_analytics.py`, `estoques_timeline.py` | Full-scan de plantas vivas **3–4×** na mesma request (analítico, timeline, integridade CMV) |
| **`GET /financeiro/painel`** | `crud/financeiro.py` (~1326+) | Estimativa **80–150+ queries** (evolução 12 meses × DRE/livro caixa); `sanear_custos_coleta_campo_pendentes` com **write** dentro do GET |
| **N+1 em coletas** | `crud/coletas_sementes.py` | `_ultimo_teste_germinacao` por lote no loop; default `limit=2000` |
| **N+1 em semeaduras** | `crud/semeaduras.py` | `_count_plantas` por linha; default `limit=2000` |
| **`redistribuir_cif_parque`** | `services/custeio.py` | O(plantas) queries SUM; dispara em toda semeadura |
| **`echo=True` no engine** | `database.py` | Log de cada SQL — overhead em prod |
| **Limits altos** | várias rotas | Defaults 2000–5000 (coletas, lotes, semeaduras, relatórios) |

### MEDIUM

| Problema | Onde | Impacto |
|----------|------|---------|
| Produção resumo ~25+ queries | `crud/producao.py` | Latência linear; consolidável com `FILTER`/`CASE` |
| Índices faltando | migrations / init-scripts | `vendas(data_venda)`, `vendas(status)`, `vendas(data_pagamento)`, `plantas(id_semeadura)`, `transferencias_plantas(id_planta)` |
| `_armazem_por_especie` em Python | `estoques_timeline.py` | Loop artificial até 500 itens por lote |
| Pool sem tuning | `database.py` | Sem `pool_size`, `max_overflow`, `pool_pre_ping` |
| Docker sem limits | `compose/api.yml`, `compose/infra.yml` | API + Postgres competem por RAM |
| 1 worker uvicorn | `Dockerfile` | Sem workers múltiplos em prod |

### LOW

- `main.py`: só CORS; sem GZip, rate limit, timing
- `get_db()` faz `commit()` no finally mesmo em GETs
- Dashboard fallback N+1 se view `vw_ocupacao_canteiros` falhar (`crud/dashboard.py`)

---

## Matriz “o que quebra primeiro”

```
                    volume de plantas / histórico
                    baixo      médio       alto
dashboard/resumo    OK         OK          ⚠️
producao/resumo     OK         OK          ⚠️
coletas (lista)     OK         ⚠️ N+1      🔴
semeaduras (lista)  OK         ⚠️ N+1      🔴
estoques/resumo     OK         🔴          🔴
financeiro/painel   OK         🔴          🔴
semeadura (write)   OK         ⚠️          🔴
```

---

## Como medir (checklist manual)

DevTools → **Network** (com API local):

1. **Produção** (primeira visita) — contar requests e tempo total
2. **Estoques** — tempo de `GET /api/v1/estoques/resumo`
3. **Financeiro** — tempo de `GET /api/v1/financeiro/painel`
4. **Vendas** — quantas chamadas NF-e / readiness por cliente
5. **Coleta** — sair e voltar: confirma refetch completo (sem cache)

Referência subjetiva em LAN:

- **&lt; 1s** — saudável
- **2–4s** — aceitável com dados
- **&gt; 5s** numa tela só — gargalo real naquela rota

---

## Prioridade de otimização (quando for a hora)

Ordem sugerida por **retorno / risco**:

| # | Ação | Camada | Esforço |
|---|------|--------|---------|
| 1 | Produção: `v-if` na aba ativa em vez de `v-show` em todos os painéis | Front | Baixo |
| 2 | Batch NF-e readiness + notas por venda (endpoint único no backend) | Back + Front | Médio |
| 3 | Cache `hidratado` no store de coleta (como viveiro) | Front | Baixo |
| 4 | Fatiar ou cachear `GET /estoques/resumo` | Back | Alto |
| 5 | Painel financeiro: cache mensal, remover write no GET, reduzir queries | Back | Alto |
| 6 | Usar batch de testes de germinação na listagem de coletas | Back | Médio |
| 7 | CIF incremental em vez de redistribuir todas as plantas | Back | Alto |
| 8 | Índices em vendas, plantas, semeadura, transferências | DB | Baixo |
| 9 | `echo=False` em prod, pool tuning, limits Docker | Ops | Baixo |
| 10 | Virtualização de tabelas grandes (coleta, biblioteca) | Front | Médio |

---

## Arquivos centrais para revisitar

| Área | Path |
|------|------|
| Router / lazy | `sistema-viveiro-nativas/src/router/index.js` |
| Vite | `sistema-viveiro-nativas/vite.config.js` |
| Store viveiro (cache) | `sistema-viveiro-nativas/src/store/viveiro.js` |
| Store coleta (sem cache) | `sistema-viveiro-nativas/src/store/coleta.js` |
| Produção (v-show) | `sistema-viveiro-nativas/src/views/viveiro/ProducaoView.vue` |
| Vendas N+1 | `sistema-viveiro-nativas/src/components/vendas/VendasPanel.vue`, `ClientesCadastroPanel.vue` |
| Estoques resumo | `api_viveiro/app/crud/estoques.py`, `estoques_analytics.py`, `estoques_timeline.py` |
| Financeiro painel | `api_viveiro/app/crud/financeiro.py` |
| Coletas N+1 | `api_viveiro/app/crud/coletas_sementes.py` |
| CIF | `api_viveiro/app/services/custeio.py` |
| Engine / pool | `api_viveiro/app/database.py` |
| Docker | `compose/api.yml`, `compose/infra.yml` |

---

## Notas

- Auditoria feita em modo **read-only** — nenhuma alteração de performance foi aplicada no código por causa deste documento.
- Complementa `docs/SEGURANCA_RBAC.md` (segurança ≠ performance).
- Atualizar este arquivo quando otimizações forem feitas (marcar item como resolvido com data).
