# Brotare Viveiros — Frontend

Vue 3 + Vite + Pinia. Pasta do repositório: `sistema-viveiro-nativas`.

## Design System

Paleta de cores, tokens CSS e regras de UI/UX: **[docs/DESIGN_SYSTEM.md](./docs/DESIGN_SYSTEM.md)**

Tokens implementados em `src/assets/main.css`.

## Stores Pinia (domínio)

| Store | Papel |
|-------|--------|
| `auth.js` | JWT, permissões, `/auth/me` |
| `viveiroContext.js` | Unidade ativa (nativo/florestal), nav por pipeline |
| `viveiro.js` | Planta baixa e mapa operacional (`/viveiro`) |
| `coleta.js` | Módulo coleta |

## Limpeza / legado

Convenções Vue: **[docs/CLEANUP.md](./docs/CLEANUP.md)**

## Segurança e perfis

RBAC e God Mode: **[../../docs/SEGURANCA_RBAC.md](../../docs/SEGURANCA_RBAC.md)** · **[../../docs/ADMIN_COCKPIT.md](../../docs/ADMIN_COCKPIT.md)**

- Nativo (Embrapa): **[../../docs/REFERENCIA_VIVEIRO.md](../../docs/REFERENCIA_VIVEIRO.md)**
- Florestal: **[../../docs/VIVEIRO_FLORESTAL.md](../../docs/VIVEIRO_FLORESTAL.md)**

Copie `.env.example` para `.env` e ajuste `VITE_VIVEIRO_NOME`.
