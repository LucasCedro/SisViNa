# Home operacional e perfis de acesso

## Home (`/`)

Painel de trabalho (`home.view`):

- Saudação + nome do viveiro (`VITE_VIVEIRO_NOME` no `.env`)
- Chips de perfis do usuário logado
- Ações rápidas filtradas por `auth.can(permission)`
- Pendências (transferência, pragas, lotes sem teste)
- Resumo clicável, fluxo matriz → venda, onboarding, atividade recente

## Perfis (`funcionarios.perfis` — JSON no Postgres)

| ID | Uso típico |
|----|------------|
| `admin` | Tudo + God Mode |
| `gestor` | Operação, vendas (sem aprovar), estoques |
| `campo` | Coleta, produção, manejo |
| `financeiro` | Financeiro, NF-e, aprovação de vendas |
| `rh` | Ver usuários; sem editar |
| `consulta` | Somente leitura (sem lista de funcionários) |

Exemplo no banco:

```json
["campo", "financeiro"]
```

## Enforcement (importante)

- **Backend:** `app/security/rbac.py` — permissões efetivas por perfil
- **Front:** `GET /auth/me` → `permissions[]`; router usa `meta.permission`
- **Não** inferir acesso por `cargo` — labels em `src/constants/roles.js` são só display

Documentação completa: [docs/SEGURANCA_RBAC.md](../../docs/SEGURANCA_RBAC.md)

## Migração / seed

```powershell
.\scripts\dev.ps1 migrate
```

Migration **27** garante `perfis` não nulos (default `["campo"]`). Admin dev pode ter vários perfis no seed; em produção use só `["admin"]`.
