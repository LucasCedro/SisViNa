# Segurança e RBAC — Brotare Viveiros

Autorização **fail-closed**: o backend é a fonte da verdade; o frontend consome `permissions[]` e contexto de empresa/viveiro do `/auth/me`.

## Arquivos centrais

| Camada | Path |
|--------|------|
| Catálogo + mapa de perfis | `api_viveiro/app/security/rbac.py` |
| Contexto empresa (tenant) | `api_viveiro/app/security/tenant_context.py` |
| Contexto viveiro | `api_viveiro/app/security/viveiro_context.py` |
| Escopo combinado | `api_viveiro/app/security/scope_context.py` |
| Escopo financeiro (ContextVar) | `api_viveiro/app/security/financeiro_scope.py` |
| Sessão / `/me` | `app/auth/session.py`, `schemas/auth.py` |
| God Mode (plataforma) | `require_godmode()` + `app/routes/admin_cockpit.py` |
| Gestão usuários empresa | `app/routes/empresa.py` |
| Front | `store/auth.js`, `store/viveiroContext.js`, `AdminEmpresaSelector.vue`, `AdminViveiroSelector.vue` |

## Perfis (`funcionarios.perfis` — JSON array)

| ID | Uso |
|----|-----|
| `platform_admin` | God Mode Brotare + `X-Empresa-Id` + `X-Viveiro-Id` |
| `admin` | Legado — tratado como `platform_admin` |
| `empresa_admin` | Gestão de usuários da própria empresa + seletor viveiro (2+ unidades) |
| `gestor` | Operação, vendas (sem aprovar), estoques, fiscal/contabilidade view, florestal |
| `campo` | Coleta, produção, viveiro, fitossanidade, florestal |
| `financeiro` | Financeiro, fiscal emit, `vendas.approve`, contabilidade |
| `consulta` | Somente `.view` (exceto `users.view`) |
| `rh` | `users.view` + financeiro/biblioteca view |

União **OR** quando há múltiplos perfis. Sem perfis válidos → baseline: `home.view`, `configuracoes.view`, `config.profile.edit`.

## Multi-tenant SaaS

| Regra | Detalhe |
|-------|---------|
| Empresa do usuário | `funcionarios.id_empresa` (fixo para não-platform) |
| Header `X-Empresa-Id` | **Somente `platform_admin`** — demais perfis → **403** + auditoria |
| Header `X-Viveiro-Id` | `platform_admin` e `empresa_admin` (dentro da empresa) |
| Contexto ativo | `resolve_scope_context()` — valida viveiro ∈ empresa |
| Insumos | Escopo **empresa** (`insumos.id_empresa`) |
| Dados operacionais | Escopo **viveiro** (`plantas`, `lotes`, vendas, coleta, etc.) |
| CPF funcionário | Único por empresa (`uq_funcionarios_empresa_cpf`) |
| Códigos | `codigo_rastreio` / `codigo_lote` únicos por viveiro |

### Seletores no header (front)

| Componente | Quem vê | Persistência |
|------------|---------|--------------|
| `AdminEmpresaSelector` | `pode_selecionar_empresa` (`platform_admin`) | `brotare_admin_empresa_id` |
| `AdminViveiroSelector` | `pode_selecionar_viveiro` (admin empresa/plataforma, 2+ viveiros) | `brotare_admin_viveiro_id` |

## Permissões exclusivas da plataforma (God Mode)

| Permissão | Escopo |
|-----------|--------|
| `admin.godmode.view` | Overview multi-empresa + matriz RBAC |
| `admin.godmode.manage` | CRUD usuários cross-tenant + criar viveiro |

`require_godmode()` exige perfil **`platform_admin`** (ou legado `admin`) **e** a permissão.

Router front: `meta.adminOnly` → `auth.user.is_platform_admin` (não checa só `perfis.includes('admin')`).

Ver [ADMIN_COCKPIT.md](./ADMIN_COCKPIT.md).

## Gestão de usuários da empresa

Rota `/api/v1/empresa/usuarios` — perfil `empresa_admin` + `require_empresa_user_manage()`.

- CPF validado **por empresa**
- Não pode promover a `platform_admin`

## Módulos com escopo aplicado

Rotas operacionais usam `Depends(get_scope_context)` e filtram CRUD por `id_viveiro` e/ou `id_empresa`:

`plantas`, `canteiros`, `vendas`, `compradores`, `coletas`, `semeaduras`, `lotes`, `estoques`, `financeiro`, `contabilidade`, `dashboard`, `producao`, `pragas`, `atividades`, `testes_sementes`, `insumos`, `florestal`, `coleta-relatorios` (exports CSV).

## Segregação de funções (SoD) — vendas

| Ação | Permissão |
|------|-----------|
| Criar venda | `vendas.create` → status `PENDENTE` |
| Aprovar | `vendas.approve` → `POST /vendas/{id}/aprovar` |
| Gestor | **Não** tem `vendas.approve` |

## Testes automatizados

```powershell
cd api_viveiro
pytest tests/test_tenant_saas.py tests/test_tenant_isolation.py tests/test_viveiro_context.py -q
```

Cobre: header empresa bloqueado, plantas por viveiro, estoques, insumos por empresa, exports CSV, BOLA (praga cross-viveiro → 404), financeiro com escopo.

## Pendente (P3+)

- Cypress E2E guard + `cy.request` 403
- Rate limiting no login
- Catálogos globais (tipos praga/atividade) — escopo por empresa se necessário
