# ETL JBRJ → `especies_master`

Script **standalone** que consulta a API pública da Flora do Brasil e grava na tabela **`especies_master`** — referência taxonômica **imutável**, separada da tabela operacional `especies` do ERP.

## Por que duas tabelas?

| Tabela | Papel | Quem edita |
|--------|--------|------------|
| `especies_master` | Taxonomia, distribuição, nomes (JBRJ) | **Só ETL** (script) |
| `especies` | Cadastro usado em matriz, lote, planta, biblioteca Embrapa | Operacional / manual viveiro |

Isso evita **data poisoning**: um usuário de tenant A não altera parâmetros globais que afetam tenant B. O ERP faz **link** por `nome_cientifico` ou `taxon_id_jbrj` quando integrarmos as camadas.

## API real (testada)

```
GET https://servicos.jbrj.gov.br/v2/flora/taxon/{nome científico URL-encoded}
```

Resposta: array JSON com `taxon`, `distribuition` (sic), `specie_profile`, `vernacular_name`, etc.

**Limitações conhecidas da API v2 (jun/2026):**

- `vernacular_name` frequentemente vazio — nomes populares podem precisar de fonte adicional (IPT DwC-A).
- Campo `notes` com fenologia **não vem** no JSON simplificado; o regex de fenologia atua em `notas_origem` quando houver texto (ou extensão futura CNCFlora).
- `status_ameaca` pode vir null até integrarmos CNCFlora.

## Uso

```powershell
cd api_viveiro\scripts\jbrj_flora_etl
pip install -r requirements.txt
copy especies_input.example.txt especies_input.txt
# editar especies_input.txt

$env:DATABASE_URL = "postgresql://viveiro_admin:senha_segura_aqui@localhost:5432/viveiro_db"
python import_species_master.py
```

Migration Alembic (recomendado em dev Docker):

```powershell
.\scripts\dev.ps1 migrate   # 29_especies_master + 30_especies_master_chave_gin
```

## Comportamento

- **1 espécie por vez** + **2 s** após cada sucesso
- **Retry** (tenacity): até 5 tentativas em 429/502/503/504
- Falhas → `failed_species.log`; corrija o `.txt` e **rode de novo** (idempotente)
- **UPSERT** por `nome_cientifico_chave` (case-insensitive — `Dipteryx alata` = `DIPTERYX ALATA`)
- **URL encoding** na API (`St. -Hil.` → `%20`; fallback compacta autor `A. St. -Hil.` → `A.St.-Hil.`)
- Entrada: `sanitize_input_name()` (strip + colapsa espaços); dedupe por chave normalizada

## Schema (`especies_master`)

| Coluna | Tipo | Notas |
|--------|------|-------|
| `nome_cientifico` | TEXT | Nome canônico retornado pela JBRJ |
| `nome_cientifico_chave` | TEXT UNIQUE | `lower(trim + espaços)` — chave do UPSERT |
| `nomes_populares` | TEXT[] | GIN index |
| `meses_floracao` / `meses_frutificacao` | INTEGER[] | Regex em `notas_origem` quando houver |
| `ultima_atualizacao` | TIMESTAMP | Atualizado a cada UPSERT |

## Arquivos

| Arquivo | Função |
|---------|--------|
| `import_species_master.py` | CLI principal |
| `jbrj_client.py` | HTTP + transformação DwC/JBRJ |
| `fenologia.py` | Regex floração/frutificação |
| `normalizacao.py` | strip, `normalize_key`, URL encode |
| `db.py` | PostgreSQL + UPSERT |
| `especies_input.txt` | Entrada (90 espécies, ordem A–Z) |

## Próximo passo (ERP)

- View ou job que cruza `especies.id` ↔ `especies_master.taxon_id_jbrj`
- Nunca sobrescrever `ficha_embrapa` / manejo de viveiro com dados JBRJ
- CNCFlora opcional para `status_ameaca`
