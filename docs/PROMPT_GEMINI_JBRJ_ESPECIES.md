# Prompt para Gemini — ingestão JBRJ / Flora do Brasil (Darwin Core)

Copie tudo abaixo da linha `---` e envie ao Gemini.

---

Estou desenvolvendo o **SisViNa** — sistema de gestão de viveiro de mudas nativas (FastAPI + PostgreSQL + Vue). Preciso da sua ajuda para desenhar um **script de ingestão** que consulte a API da **JBRJ / Flora do Brasil / SiBBr** (Darwin Core) e enriqueça nosso banco de espécies de forma **estruturada**, sem duplicar lixo nem quebrar o que já existe operacionalmente.

## Contexto do projeto

- Temos **90 espécies** seedadas a partir do manual Embrapa/RSC 2016 (viveiro cerrado).
- Essas espécies são usadas em **matrizes, coletas, lotes, plantas, estoque, produção** — a tabela `especies.id` é FK em vários módulos. **Não podemos recriar espécies do zero**; precisamos **enriquecer/atualizar** registros existentes ou **inserir novas** com matching taxonômico confiável.
- Parte dos dados vem do **banco**; parte vem de **API externa** (speciesLink/iNaturalist só para **imagens**, em cache JSON).
- Quero usar a **API JBRJ** como fonte autoritativa de **taxonomia, distribuição, forma de vida, nomes vernáculos, status de ameaça**, etc.

---

## O que já temos no PostgreSQL (3 camadas)

### 1. `especies` — cadastro base (operacional + identidade)

| Campo | Tipo | Uso |
|-------|------|-----|
| `id` | PK | FK em matriz, lote, planta |
| `nome_cientifico` | varchar(100), unique | Ex.: `Dipteryx alata Vogel` |
| `nome_popular` | varchar(100) | Um nome só — ex.: `Baru` |
| `familia` | varchar(50) | Ex.: `Fabaceae` |
| `descricao` | text | Texto curto |
| `tempo_germinacao` | int (dias) | Referência manual |
| `tempo_crescimento` | int (dias) | Referência manual |
| `altura_maxima` | numeric | Muitas null |
| `data_cadastro` | timestamp | |

### 2. `especies_biblioteca` — conteúdo da UI Biblioteca

| Campo | Tipo | Uso |
|-------|------|-----|
| `id_especie` | PK/FK | 1:1 com `especies` |
| `resumo_manejo` | text | Texto longo do manual (fitofisionomia, coleta, semeadura…) — **muitas vezes truncado ou redundante** |
| `imagem_arvore`, `imagem_semente`, `imagem_folha` | varchar | Paths locais `/assets/biblioteca/especies/.../{id}.jpg` |
| `imagens_externas` | json | Cache de URLs (iNaturalist) |
| `imagens_externas_atualizado_em`, `cache_imagens_em` | timestamp | |

### 3. `especies_ficha_embrapa` — ficha técnica estruturada (produção / avisos)

| Campo | Tipo | Exemplo Baru |
|-------|------|--------------|
| `nome_cientifico_ref` | varchar | Dipteryx alata Vogel |
| `fitofisionomia` | text | Mata Seca, Cerradão, Cerrado restrito |
| `mes_coleta_inicio`, `mes_coleta_fim` | smallint | **null/null** (texto diz set–nov) |
| `armazenamento_tipo` | varchar | ortodoxa |
| `armazenamento_obs` | text | fruto, sombreado, ventilado |
| `profundidade_semeadura_cm_min/max` | numeric | 0,5 – 1,0 cm |
| `dias_inicio_germinacao` | int | 12 |
| `pct_germinacao_tipico` | numeric | 95% |
| `substrato_tipo` | smallint | 3 (sem legenda no BD) |
| `conduz_pleno_sol` | boolean | true |
| `meses_permanencia_viveiro`, `_max` | int | 6 / 6 |
| `dias_rustificacao_minimo` | int | null → usa regra global |
| `altura_campo_cm_min/max` | numeric | null → usa regra global |
| `adubacao_obs`, `observacoes_gerais` | text | manual viveiro |
| `fonte` | varchar | `SisViNa` / Embrapa |

### 4. `viveiro_regras_globais` (10 regras)

Parâmetros default: rustificação mínima (30 dias), altura campo cerrado (20–30 cm), rega germinação 2×/dia, fração máxima coleta por matriz, etc. A ficha por espécie **sobrescreve** quando preenchida.

### 5. Seed / fonte estática

- `api_viveiro/data/especies_manual_enriched.json` — 90 espécies parseadas do manual, com seções (`fitofisionomia`, `epoca`, `processamento`, `armazenamento`, `semeadura`, `conducao`, `substrato`, `permanencia`, `adubacao`, `observacoes`) que **não estão em tabela separada** — só no JSON e parcialmente em `resumo_manejo` / `ficha_embrapa`.

**Estatísticas atuais:** 90 espécies, 90 biblioteca, 90 fichas; **54 fichas** com `mes_coleta_inicio/fim` null apesar do texto existir.

---

## Exemplo real no nosso banco: Baru (`Dipteryx alata Vogel`, id=36)

**`especies`:** Baru, Fabaceae, tempo_germinacao=12, tempo_crescimento=180, altura_maxima=null.

**`especies_ficha_embrapa`:** germinação 12 dias / 95%, substrato tipo 3, pleno sol, permanência 6 meses, armazenamento ortodoxa; meses de coleta **null**; rustificação e altura campo **null**.

**`especies_biblioteca`:** resumo longo do manual (coleta set–nov, rega 2×/dia, semeadura direta…); 12 URLs iNaturalist em cache; paths de imagens locais.

**Problemas conhecidos:**

- Duplicação entre `descricao`, `fitofisionomia`, `resumo_manejo`
- Campos estruturados vazios enquanto o texto tem a info
- `nome_popular` aceita **só 1 nome**; Baru tem vários sinônimos populares
- KPI **real** de germinação vem de `testes_sementes` por lote — `%` da ficha é só referência
- Matching científico: nosso BD usa `Dipteryx alata Vogel` (com autor); API pode exigir grafia exata (`Dipteryx alata` com **y**)

---

## O que a API JBRJ / Flora do Brasil retorna (Darwin Core limpo)

Quando busco **Baru / Dipteryx alata** na Flora do Brasil ou SiBBr, após limpar o JSON, a essência útil é:

```json
{
  "taxonID": "12345",
  "scientificName": "Dipteryx alata Vogel",
  "family": "Fabaceae",
  "taxonomicStatus": "ACCEPTED",
  "vernacularNames": [
    {"name": "Baru", "language": "pt"},
    {"name": "Cumbaru", "language": "pt"},
    {"name": "Cumaru-do-cerrado", "language": "pt"}
  ],
  "lifeForm": ["Árvore"],
  "habitat": ["Terrestre"],
  "distribution": {
    "endemism": "Não endêmica do Brasil",
    "biomes": ["Cerrado"],
    "states": ["DF", "GO", "MG", "MS", "MT", "SP", "TO"]
  },
  "notes": "Floração: outubro a janeiro. Frutificação: setembro a outubro.",
  "threatStatus": "Vulnerável (VU)"
}
```

Isso **não substitui** o manual Embrapa (manejo de viveiro, substrato, profundidade semeadura, % germinação típica), mas **complementa** taxonomia, nomes, distribuição, fenologia e conservação.

---

## O que preciso que você me ajude a definir

1. **Modelo de dados alvo** — quais campos DwC/JBRJ entram em quais tabelas (novas tabelas vs colunas novas)? Ex.: `especies_vernacular_names`, `especies_distribuicao`, `especies_conservacao`, `especies_taxon_ref` (taxonID, status, scientificNameAuthorship)?

2. **Estratégia de merge** — como fazer match `especies` existente ↔ resposta JBRJ:
   - Por `scientificName` normalizado (sem autor? com autor?)
   - Por `taxonID` persistido após primeira sync
   - Tratar homônimos e grafias (`alata` vs typos)

3. **Regras de prioridade de fonte:**
   - JBRJ → taxonomia, distribuição, nomes, ameaça, fenologia em `notes`
   - Manual Embrapa → manejo viveiro (`ficha_embrapa`, `resumo_manejo`) — **não sobrescrever** com API
   - Operacional (`testes_sementes`) → KPI real, separado de referência

4. **Script de ingestão** (Python):
   - Entrada: lista de `nome_cientifico` ou `taxonID` das 90 espécies + novas
   - Chamada API JBRJ (me oriente nos endpoints Flora do Brasil / SiBBr se souber)
   - Parse DwC → upsert estruturado
   - Log de não encontrados / ambíguos
   - Idempotente (rodar de novo sem duplicar)

5. **Gap analysis Baru** — mapeie campo a campo o JSON DwC acima vs nossas 3 tabelas: o que preenche direto, o que exige tabela nova, o que fica em `notes` parseado (ex.: extrair meses frutificação set–out → `mes_coleta_inicio=9`, `mes_coleta_fim=10`).

6. **Proposta de schema SQL** (migration Alembic) mínima para “banco robusto” sem quebrar FKs existentes.

Responda com: diagrama lógico das entidades, tabela de mapeamento DwC → colunas SisViNa, pseudocódigo do pipeline de sync, e lista de riscos (encoding, autor científico, espécies fora da Flora do Brasil, rate limit API).

**Stack:** Python 3.9, SQLAlchemy async, PostgreSQL 15, FastAPI. Repositório monorepo `api_viveiro/`.
