# Referência técnica do viveiro (Embrapa / manual)

Parâmetros operacionais usados em **avisos suaves** na produção — não bloqueiam fluxos por padrão.

## Fonte de dados

| Camada | Path |
|--------|------|
| Constantes default | `api_viveiro/app/constants/referencia_embrapa_viveiro.py` |
| Tabelas | `viveiro_regras_globais`, `especie_ficha_embrapa` (migration **09**) |
| CRUD | `app/crud/referencia_viveiro.py` |
| Avisos na UI | `app/services/validacao_producao.py` (rustificação, altura, liberação venda) |

Migration **10** inclui seed de **90 espécies** do manual na biblioteca (`especies_biblioteca`).

## API — `/api/v1/referencia-viveiro`

Permissão: `viveiro.view`.

| Método | Rota | Resposta |
|--------|------|----------|
| GET | `/regras` | Lista `RegraGlobalOut` (chave, valor, descrição, fonte) |
| GET | `/resumo` | Fonte + regras globais |
| GET | `/especies/{id}/ficha` | Ficha técnica da espécie ou `404` |

## Regras globais (exemplos)

| Chave | Uso |
|-------|-----|
| `rustificacao_dias_minimo` | Mínimo de dias em rustificação antes de liberar venda |
| `altura_campo_cerrado_cm_min/max` | Faixa típica de altura para campo (cerrado) |
| `permanencia_viveiro_meses_tipico` | Referência de permanência no viveiro |
| `coleta_fracao_maxima_arvore` | Fração máxima de coleta por matriz |

Ficha por espécie pode **sobrescrever** valores globais (ex.: `dias_rustificacao_minimo`, altura de campo).

## Biblioteca de espécies

- **UI:** `/biblioteca` (`biblioteca.view` / `biblioteca.edit`)
- **API:** `GET /especies/biblioteca`, imagens externas em `GET /especies/{id}/imagens-externas`
- **Assets locais:** `sistema-viveiro-nativas/public/assets/biblioteca/` — ver README na pasta
- **Sync speciesLink:** `docker compose exec api python scripts/sync_specieslink_imagens.py` (requer `SPECIESLINK_API_KEY`)

## Onde os avisos aparecem

Painéis de produção (rustificação, liberar venda) consomem avisos da API quando a operação diverge dos parâmetros — operador pode prosseguir; mensagem é orientativa.
