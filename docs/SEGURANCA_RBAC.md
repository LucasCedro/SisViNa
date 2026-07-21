# Segurança e RBAC — Brotare Viveiros

Autorização **fail-closed**: o backend é a fonte da verdade; o frontend consome `permissions[]` e contexto de unidade do `/auth/me`.

## Arquivos centrais

| Camada | Path |
|--------|------|
| Catálogo + mapa de perfis | `api_viveiro/app/security/rbac.py` |
| Contexto multi-unidade | `api_viveiro/app/security/viveiro_context.py` |
| Sessão / `/me` | `app/auth/session.py`, `schemas/auth.py` |
| Guard de rotas API | `Depends(require_permission(...))` em `app/routes/*` |
| God Mode (admin) | `require_godmode()` + `app/routes/admin_cockpit.py` |
| Front | `store/auth.js`, `store/viveiroContext.js`, `router/index.js`, `composables/usePermissions.js`, `components/shared/CanAccess.vue` |

## Perfis (`funcionarios.perfis` — JSON array)

| ID | Uso |
|----|-----|
| `admin` | Acesso total + God Mode + seletor de unidade viveiro (2+ unidades) |
| `gestor` | Operação, vendas (sem aprovar), estoques, fiscal/contabilidade **view**, florestal |
| `campo` | Coleta, produção, viveiro, fitossanidade, florestal (view/create/transfer) |
| `financeiro` | Financeiro, fiscal emit, **vendas.approve**, contabilidade |
| `consulta` | Somente `.view` (exceto `users.view`) |
| `rh` | `users.view` + financeiro/biblioteca view |

União **OR** quando há múltiplos perfis. Sem perfis válidos → baseline: `home.view`, `configuracoes.view`, `config.profile.edit`.

Migration **27** preenche `perfis` NULL/`[]` com `["campo"]`.

## Multi-unidade viveiro

| Regra | Detalhe |
|-------|---------|
| Vínculo usuário ↔ unidade | Tabela `funcionario_viveiros` |
| Contexto ativo | Resolvido no backend por `resolve_viveiro_context()` |
| Header `X-Viveiro-Id` | **Somente admin** — não-admin que envia → **403** |
| Modo de operação | Lido de `viveiros.modo_operacao` no BD — cliente não escolhe pipeline |
| Módulos na UI | `modulos_nav_desabilitados` no `/auth/me` (ex.: coleta oculta no florestal) |
| Seletor no front | Visível **apenas** para admin com 2+ unidades (`AdminViveiroSelector.vue`) |

## Permissões exclusivas do Admin (God Mode)

| Permissão | Escopo |
|-----------|--------|
| `admin.godmode.view` | Overview + matriz RBAC + unidades viveiro |
| `admin.godmode.manage` | CRUD usuários + criar unidade viveiro |

`require_godmode()` exige **perfil `admin` no BD** e a permissão — esconder botão no front não basta.

Ver [ADMIN_COCKPIT.md](./ADMIN_COCKPIT.md).

## Módulo florestal

| Permissão | Escopo |
|-----------|---------|
| `florestal.view` | Resumo, genótipos, lotes |
| `florestal.create` | Criar genótipo / lote |
| `florestal.edit` | Editar genótipo, registrar perda |
| `florestal.transfer` | Transferir estágio do lote |

Rotas em `/api/v1/florestal/*` — bloqueadas com **403** se `viveiro.modo_operacao != florestal`.

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
- **Cross-tenant** — `assert_record_belongs_to_viveiro()` em mutações florestais
- **403** logado com `usuario`, `id`, `permissao`, `perfis`

## Matriz rota ↔ permissão (GET principais)

| Módulo | GET | Mutações típicas |
|--------|-----|------------------|
| funcionarios (lista) | `users.view` | `users.*` |
| coleta / lotes / testes / matrizes | `coleta.view` | `coleta.*` |
| florestal | `florestal.view` | `create` / `edit` / `transfer` |
| vendas / compradores | `vendas.view` | `create` / `edit` / `approve` |
| plantas / produção / dashboard/resumo | `producao.view` / `viveiro.view` | `producao.*` |
| viveiros contexto | `home.view` | — |
| pragas | `fitossanidade.view` | `create` / `edit` |
| insumos / estoques | `estoques.view` | `estoques.edit` |
| espécies / biblioteca | `viveiro.view` / `biblioteca.view` | `biblioteca.edit` |
| financeiro / lançamentos | `financeiro.view` | `financeiro.*` |
| dashboard/financeiro | `financeiro.view` | — |
| fiscal / nfe | `fiscal.view` / `contabilidade.view` | `fiscal.*` |

Lista completa: `ALL_PERMISSIONS` em `rbac.py` (**48** permissões).

## Testes

```powershell
# Unitários (host, com viveiro_test_db)
cd api_viveiro
pytest tests/test_rbac.py tests/test_vendas_sod.py tests/test_viveiro_context.py -q

# Smoke API real
.\scripts\test_permissions.ps1
.\scripts\smoke.ps1
```

Casos críticos: escalação PUT funcionários, PATCH `/me` com `perfis`, consulta 403 em POST, gestor 403 em `/admin/cockpit`, não-admin com `X-Viveiro-Id` → 403.

## Pendente (P2)

- Cypress E2E guard + `cy.request` 403
- Log de auditoria (vendas, financeiro, funcionários, movimentações lote)
- Rate limiting no login (gateway ou `slowapi`)
- Filtrar **todas** as queries nativas por `id_viveiro` (isolamento completo)
