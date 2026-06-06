# Limpeza e convenções — frontend

## Layout base (Maio/2026)

| Arquivo | Papel |
|---------|--------|
| `components/layout/PageLayout.vue` | Padding/gap padrão da página |
| `components/layout/PageSection.vue` | Card/seção com slots |
| Título da página | Apenas no `Header.vue` (via `App.vue` + rota) |
| `store/viveiro.js` | Planta baixa e mudas via API (`viveiroApiMapper.js`) |
| `AnaliseRecorrencia.vue` | Gráficos/alertas derivados de pragas + atividades (sem mock) |

Views migradas para `PageLayout`: Viveiro, Fertilização, Fitossanidade, Prescrição, Financeiro, Vendas, Estoques, Produção, Planta baixa editor, Biblioteca, Coleta.

Home redesenhada como cockpit operacional; perfis e RBAC — ver [HOME_E_PERFIS.md](./HOME_E_PERFIS.md) e [SEGURANCA_RBAC.md](../../docs/SEGURANCA_RBAC.md).

---

## Estrutura canônica

```
src/views/{modulo}/{Modulo}View.vue   → rota + PageLayout
src/components/{modulo}/              → lógica de tela 
src/services/                         → API
src/store/                            → Pinia
src/constants/                        → domínio + chartColors
src/assets/main.css                   → design tokens
docs/DESIGN_SYSTEM.md                 → paleta e UI
```

**Router:** única fonte de rotas em `src/router/index.js`.


## Checklist antes de novo módulo

- [ ] View em `views/{modulo}/`, não na raiz de `views/`
- [ ] Registrar rota em `router/index.js`
- [ ] Cores via `var(--color-*)` ou `chartColors.js`
- [ ] Sem dependência nova sem uso no código
- [ ] Um único `<h1>` por página (na view wrapper)
