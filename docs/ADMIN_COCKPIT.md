# Admin Cockpit (God Mode)

Área **exclusiva do administrador** do sistema — visão overseer, unidades viveiro e gestão de usuários.

## Acesso

1. Login com usuário que tenha perfil **`admin`** no banco
2. **Configurações** → aba **Configurações** → botão **Abrir God Mode**
3. Rota direta: `/admin/god-mode` (bloqueada pelo router se não autorizado)

### Blindagem

| Camada | Verificação |
|--------|-------------|
| Front | `auth.can('admin.godmode.view')` **e** `perfis.includes('admin')` |
| API | `require_godmode('admin.godmode.view' \| 'admin.godmode.manage')` |

Usuário gestor/financeiro/consulta → **403** mesmo conhecendo a URL.

## API — `/api/v1/admin/cockpit`

| Método | Rota | Permissão |
|--------|------|-----------|
| GET | `/overview` | `admin.godmode.view` |
| GET | `/rbac` | `admin.godmode.view` |
| POST | `/viveiros` | `admin.godmode.manage` |
| GET | `/funcionarios` | `admin.godmode.manage` |
| POST | `/funcionarios` | `admin.godmode.manage` |
| PUT | `/funcionarios/{id}` | `admin.godmode.manage` |
| DELETE | `/funcionarios/{id}` | `admin.godmode.manage` (soft: `ativo=false`) |

Proteções: não desativa a própria conta; não remove próprio perfil `admin`.

## UI — abas

1. **Visão geral** — totais (usuários, unidades viveiro, plantas, vendas), usuários por perfil, revision Alembic, **tabela cross-unidade viveiro**
2. **Usuários** — listagem, criar, editar perfis/senha, desativar
3. **Matriz RBAC** — mapa estático perfil → permissões (SSOT do backend)

## Seletor de unidade (header)

- Componente: `AdminViveiroSelector.vue`
- Visível **somente** para admin com 2+ unidades (`pode_selecionar_viveiro` no `/auth/me`)
- Envia `X-Viveiro-Id` nas requisições — validado no backend (`viveiro_context.py`)
- Operadores de campo **não** veem o seletor

## Front

- View: `sistema-viveiro-nativas/src/views/admin/GodModeView.vue`
- Service: `src/services/adminCockpit.js`
- Contexto unidade: `src/store/viveiroContext.js`

## Produção

- Conta admin deve ter **apenas** `["admin"]` — evitar seed com todos os perfis
- God Mode não substitui backup/restore do Postgres; use para operação do dia a dia
