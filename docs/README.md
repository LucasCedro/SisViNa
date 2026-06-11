# Documentação SisViNa

Índice oficial do monorepo. Preferir estes arquivos em vez de notas soltas ou handoffs temporários.

## Operacional

| Documento | Conteúdo |
|-----------|----------|
| [DEV_DOCKER.md](./DEV_DOCKER.md) | Compose, `dev.ps1`, volumes, troubleshooting |
| [../RODAR.md](../RODAR.md) | Subir stack, URLs, patches SQL legados, NF-e `.env` |
| [../DEMO_CONSULTOR.md](../DEMO_CONSULTOR.md) | Roteiro de apresentação site + app |

## Técnica

| Documento | Conteúdo |
|-----------|----------|
| [DOCUMENTACAO_TECNICA.md](./DOCUMENTACAO_TECNICA.md) | Arquitetura, fluxos, API, schema |
| [SEGURANCA_RBAC.md](./SEGURANCA_RBAC.md) | Perfis, permissões, SoD, testes de segurança |
| [ADMIN_COCKPIT.md](./ADMIN_COCKPIT.md) | God Mode — cockpit exclusivo do admin |
| [FISCAL_CONTADOR.md](./FISCAL_CONTADOR.md) | NF-e, regras fiscais, papéis contador vs operador |
| [REFERENCIA_VIVEIRO.md](./REFERENCIA_VIVEIRO.md) | Parâmetros Embrapa/manual, biblioteca 90 espécies, avisos produção |
| [PROMPT_GEMINI_JBRJ_ESPECIES.md](./PROMPT_GEMINI_JBRJ_ESPECIES.md) | Prompt (Gemini): schema atual + ingestão JBRJ/Flora do Brasil |
| [../api_viveiro/scripts/jbrj_flora_etl/README.md](../api_viveiro/scripts/jbrj_flora_etl/README.md) | ETL CLI → `especies_master` (referência JBRJ) |

## Frontend

| Documento | Conteúdo |
|-----------|----------|
| [../sistema-viveiro-nativas/docs/DESIGN_SYSTEM.md](../sistema-viveiro-nativas/docs/DESIGN_SYSTEM.md) | Tokens, paleta, UI |
| [../sistema-viveiro-nativas/docs/HOME_E_PERFIS.md](../sistema-viveiro-nativas/docs/HOME_E_PERFIS.md) | Home operacional + perfis na UI |
| [../sistema-viveiro-nativas/docs/CLEANUP.md](../sistema-viveiro-nativas/docs/CLEANUP.md) | Convenções de layout e estrutura Vue |
| [../sistema-viveiro-nativas/public/assets/biblioteca/README.md](../sistema-viveiro-nativas/public/assets/biblioteca/README.md) | Imagens locais + sync speciesLink |

## Infra / compose

| Documento | Conteúdo |
|-----------|----------|
| [../compose/README.md](../compose/README.md) | Fragmentos `compose/*.yml` |
| [../api_viveiro/DOCKER.md](../api_viveiro/DOCKER.md) | Atalhos API (compose na raiz) |
| [../bd_viveiro/DOCKER.md](../bd_viveiro/DOCKER.md) | Postgres, patches SQL |

## Testes

| Documento | Conteúdo |
|-----------|----------|
| [../api_viveiro/tests/README.md](../api_viveiro/tests/README.md) | pytest, banco de teste |
| [../scripts/test_permissions.ps1](../scripts/test_permissions.ps1) | Smoke RBAC contra API (PowerShell) |
| [../scripts/test_permissions.sh](../scripts/test_permissions.sh) | Idem (bash) |

## Migrações

Fonte oficial do schema: `api_viveiro/alembic/versions/` — aplicar com `.\scripts\dev.ps1 migrate`.

Head atual (dev): **`27_backfill_perfis_campo`**.
