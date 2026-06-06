# Segurança e RBAC — SisViNa

Autorização **fail-closed**: o backend é a fonte da verdade; o frontend consome `permissions[]` do `/auth/me`.

## Arquivos centrais

| Camada | Path |
|--------|------|
| Catálogo + mapa de perfis | `api_viveiro/app/security/rbac.py` |
| Sessão / `/me` | `api_viveiro/app/auth/session.py`, `schemas/auth.py` |
| Guard de rotas API | `Depends(require_permission(...))` em `app/routes/*` |
| God Mode (admin) | `require_godmode()` + `app/routes/admin_cockpit.py` |
| Front | `sistema-viveiro-nativas/src/store/auth.js`, `router/index.js` |

## Perfis (`funcionarios.perfis` — JSON array)

| ID | Uso |
|----|-----|
| `admin` | Acesso total + God Mode |
| `gestor` | Operação, vendas (sem aprovar), estoques, fiscal/contabilidade **view** |
| `campo` | Coleta, produção, viveiro, fitossanidade |
| `financeiro` | Financeiro, fiscal emit, **vendas.approve**, contabilidade |
| `consulta` | Somente `.view` (exceto `users.view`) |
| `rh` | `users.view` + financeiro/biblioteca view |

União **OR** quando há múltiplos perfis. Sem perfis válidos → baseline: `home.view`, `configuracoes.view`, `config.profile.edit`.

Migration **27** preenche `perfis` NULL/`[]` com `["campo"]`.

## Permissões exclusivas do Admin (God Mode)

| Permissão | Escopo |
|-----------|--------|
| `admin.godmode.view` | Overview + matriz RBAC |
| `admin.godmode.manage` | CRUD usuários via `/admin/cockpit` |

`require_godmode()` exige **perfil `admin` no BD** e a permissão — esconder botão no front não basta.

Ver [ADMIN_COCKPIT.md](./ADMIN_COCKPIT.md).

## Segregação de funções (SoD) — vendas

| Ação | Permissão | Regra |
|------|-----------|--------|
| Criar venda | `vendas.create` | Status nasce `PENDENTE` |
| Editar venda aberta | `vendas.edit` | Só status `PENDENTE`; sem `PAGO` no PUT |
| Aprovar (PENDENTE → PAGO) | `vendas.approve` | `POST /vendas/{id}/aprovar` |
| Gestor | — | **Não** tem `vendas.approve` |

Implementação: `app/services/vendas_sod.py`.

## Decisões de segurança

- **PATCH /auth/me** — schema sem `perfis`, `extra = "ignore"` (anti mass assignment)
- **Consulta** — sem `users.view` (LGPD)
- **GET /funcionarios/simples** — auth básica; retorna só `{id, nome}` para dropdowns
- **fiscal.view** ≠ **contabilidade.view** — rotas e guards separados
- **403** logado com `usuario`, `id`, `permissao`, `perfis`

## Matriz rota ↔ permissão (GET principais)

| Módulo | GET | Mutações típicas |
|--------|-----|------------------|
| funcionarios (lista) | `users.view` | `users.*` |
| coleta / lotes / testes / matrizes | `coleta.view` | `coleta.*` |
| vendas / compradores | `vendas.view` | `create` / `edit` / `approve` |
| plantas / produção / dashboard/resumo | `producao.view` / `viveiro.view` | `producao.*` |
| pragas | `fitossanidade.view` | `create` / `edit` |
| insumos / estoques | `estoques.view` | `estoques.edit` |
| espécies / biblioteca | `viveiro.view` / `biblioteca.view` | `biblioteca.edit` |
| financeiro / lançamentos | `financeiro.view` | `financeiro.*` |
| dashboard/financeiro | `financeiro.view` | — |
| fiscal / nfe | `fiscal.view` / `contabilidade.view` | `fiscal.*` |

Lista completa: `ALL_PERMISSIONS` em `rbac.py` (~44 permissões).

## Testes

```powershell
# Unitários (host, com viveiro_test_db)
cd api_viveiro
pytest tests/test_rbac.py tests/test_vendas_sod.py -q

# Smoke API real
.\scripts\test_permissions.ps1
```

Casos críticos: escalação PUT funcionários, PATCH `/me` com `perfis`, consulta 403 em POST, gestor 403 em `/admin/cockpit`.

## Pendente (P2)

- Esconder botões UI com `auth.can('modulo.create')`
- Cypress E2E guard + `cy.request` 403
- Log de auditoria (vendas, financeiro, funcionários)
- Rate limiting no login (gateway ou `slowapi`)
