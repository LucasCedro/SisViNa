# Admin Cockpit (God Mode)

Área **exclusiva do administrador da plataforma Brotare** — visão multi-empresa, unidades viveiro e gestão cross-tenant.

## Acesso

1. Login com usuário **`platform_admin`** (demo: `demo.platform` / `Senha!@#`)
2. **Configurações** → aba **Configurações** → **Abrir God Mode**
3. Rota direta: `/admin/god-mode`

### Blindagem

| Camada | Verificação |
|--------|-------------|
| Front | `auth.can('admin.godmode.view')` **e** `auth.user.is_platform_admin` |
| Router | `meta.adminOnly` → `is_platform_admin` |
| API | `require_godmode()` → perfil `platform_admin`/`admin` + permissão |

`empresa_admin` e demais perfis → **403** mesmo conhecendo a URL.

> **Nota:** `demo.admin` é `empresa_admin` — gerencia usuários em **Configurações → Usuários da empresa**, não no God Mode.

## API — `/api/v1/admin/cockpit`

| Método | Rota | Permissão |
|--------|------|-----------|
| GET | `/overview` | `admin.godmode.view` |
| GET | `/rbac` | `admin.godmode.view` |
| GET | `/auditoria` | `admin.godmode.view` |
| POST | `/viveiros` | `admin.godmode.manage` |
| GET | `/funcionarios` | `admin.godmode.manage` |
| POST | `/funcionarios` | `admin.godmode.manage` |
| PUT | `/funcionarios/{id}` | `admin.godmode.manage` |
| DELETE | `/funcionarios/{id}` | `admin.godmode.manage` (soft: `ativo=false`) |

Proteções: não desativa a própria conta; CPF único **por empresa** na criação.

## API — `/api/v1/empresa` (empresa_admin)

| Método | Rota | Permissão |
|--------|------|-----------|
| GET/POST/PUT/DELETE | `/usuarios` | `users.*` + `require_empresa_user_manage()` |

Escopo: `get_scope_context` — só usuários da empresa ativa.

## UI — God Mode abas

1. **Visão geral** — totais, usuários por perfil, **tabela empresas + viveiros**
2. **Usuários** — listagem cross-tenant, criar, editar, desativar
3. **Matriz RBAC** — mapa estático perfil → permissões

## Seletores no header

| Componente | Visível para | Header enviado |
|------------|--------------|----------------|
| `AdminEmpresaSelector` | `platform_admin` (`pode_selecionar_empresa`) | `X-Empresa-Id` |
| `AdminViveiroSelector` | admin com 2+ viveiros | `X-Viveiro-Id` |

Ao trocar empresa, o seletor de viveiro é resetado e a página recarrega.

Chip read-only: `empresa_ativa.nome_fantasia` + `viveiro_ativo.nome`.

## Front

- View: `sistema-viveiro-nativas/src/views/admin/GodModeView.vue`
- Service: `src/services/adminCockpit.js`
- Empresa: `src/components/layout/AdminEmpresaSelector.vue`
- Viveiro: `src/components/layout/AdminViveiroSelector.vue`
- Contexto: `src/store/viveiroContext.js`, `src/services/api.js` (headers)

## Produção

- Conta `platform_admin` separada de `empresa_admin` operacional
- God Mode não substitui backup/restore do Postgres
- Toda troca de empresa gera evento em `auditoria_cross_tenant`
