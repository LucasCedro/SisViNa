# Home operacional e perfis de acesso

## Home (`/`)

Painel de trabalho com:

- Saudação + nome do viveiro (`VITE_VIVEIRO_NOME` no `.env`)
- Chips de perfis do usuário logado
- Ações rápidas (filtradas por permissão)
- Pendências (transferência, pragas, lotes sem teste)
- Resumo clicável
- Fluxo matriz → venda
- Onboarding quando `matrizes === 0`
- Atividade recente (coletas, pragas, atividades, vendas)

## Perfis (múltiplos por pessoa)

| ID | Uso típico |
|----|------------|
| `admin` | Tudo |
| `gestor` | Operação + vendas + estoques |
| `campo` | Coleta, produção, manejo |
| `financeiro` | Módulo financeiro e vendas |
| `rh` | Sem tela própria; costuma ir com `financeiro` e/ou `consulta` |
| `consulta` | Somente leitura |

Definição de permissões: `src/constants/roles.js`.

No banco (coluna `funcionarios.perfis`, JSON):

```json
["campo", "financeiro"]
```

Admin padrão recebe todos os perfis no bootstrap. Sem `perfis` na API, o front infere pelo `cargo` ou usa `campo`.

## Migração API

```bash
cd api_viveiro
alembic upgrade head
```

Reinicie a API para o bootstrap atualizar `perfis` do usuário `admin`.
