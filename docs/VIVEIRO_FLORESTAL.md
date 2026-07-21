# Viveiro florestal — discovery e referência

**Produto:** Brotare Viveiros · **Modo:** `florestal` (mudas plantadas, foco **clonal**)  
**Status:** Fase 0 — validação com AGEF e clientes florestais antes de expandir o MVP.

Documento canônico do domínio florestal. Espelho de [REFERENCIA_VIVEIRO.md](./REFERENCIA_VIVEIRO.md) (modo nativo).

---

## Decisões tomadas (não reabrir sem motivo)

| Tema | Decisão |
|------|---------|
| Propagação | **Clonal** (miniestaca / material de viveiro clonal). Semente melhorada fica fora do escopo inicial. |
| Unidade operacional | **Livre:** bandeja, tubete, estufa, pleno sol; lote diário, semanal ou mensal — código de lote definido pelo operador. |
| Unidade de venda/rastreio | **Quantidade em mudas** por lote lógico (não planta individual). |
| Clientes | Suzano, Klabin, Bracell, etc. — **rastreabilidade exigida por todos**; viveiro pode atender vários simultaneamente. |
| Ferramenta atual no mercado | Planilha Excel ou sistema concorrente — barra de UX e confiabilidade altas. |
| Arquitetura no código | Uma plataforma, `viveiro.modo_operacao = florestal`, pipeline em `app/domain/pipelines/florestal.py`. Ver [DOCUMENTACAO_TECNICA.md](./DOCUMENTACAO_TECNICA.md#multi-unidade-e-modo-florestal). |

---

## Pipeline de produção (rascunho — clonal)

```text
entrada_material → casa_vegetacao → endurecimento → expedicao
        ↓                ↓               ↓
    descarte         descarte        descarte / perda
```

| Estágio | Descrição |
|---------|-----------|
| `entrada_material` | Chegada de miniestacas / material clonal ao viveiro |
| `casa_vegetacao` | Estufa / ambiente controlado |
| `endurecimento` | Pleno sol / aclimatização |
| `expedicao` | Saída para cliente (contrato / ordem de carregamento) |
| `descartado` | Lote encerrado por perda total ou descarte de qualidade |

**Hierarquia física vs lógica:**

```text
Viveiro (unidade)
 └── Área (estufa, casa de vegetação, pleno sol)     ← canteiros / layout
      └── Lote lógico (código livre + período ref.)
           └── Quantidade (mudas)
```

Bandeja/tubete: conversão operacional (ex. 1 bandeja = N tubetes), não entidade rígida no MVP.

---

## KPIs do diretor (4 camadas)

### 1. Caixa e faturamento
- Receita do mês vs meta
- Pedidos em carteira (contratos com data de entrega)
- % entregue no prazo
- Ticket médio (R$/mil mudas)
- Recebíveis em aberto
- CMV do lote vs preço de venda

### 2. Produtividade
- Mudas expedidas / semana
- **% aproveitamento** (expedidas ÷ plantadas)
- Custo por mil mudas
- Ocupação por estufa/área
- Giro (dias bandeja → expedição)
- Perdas por estágio

### 3. Qualidade
- IQM / % dentro do spec contratual
- Altura e colo (média + % fora da faixa)
- Rejeição em vistoria do cliente
- Conformidade MAPA / laudos

### 4. Comercial
- Mix de clientes (concentração de risco)
- Backlog por cliente
- Margem por contrato
- Renovação de contrato

---

## Rastreabilidade multi-cliente

| Exigência | Registro no sistema |
|-----------|---------------------|
| Clone / genótipo | `genotipos` |
| Lote + datas | `lotes_producao`, `movimentacoes_lote` |
| Área física | `id_canteiro` + layout viveiro |
| Cliente destino | Pedido/expedição (futuro: contrato → lote) |
| Auditoria | Histórico de movimentações + usuário (`id_funcionario`) |

---

## API e UI (MVP implementado)

| Camada | Path |
|--------|------|
| API | `/api/v1/florestal/*` (genótipos, lotes, transferir, perda) |
| Permissões | `florestal.view`, `florestal.create`, `florestal.edit`, `florestal.transfer` |
| Front | Rota `/florestal` — visível só em unidade `modo_operacao=florestal` |
| Isolamento | `id_viveiro` + header `X-Viveiro-Id` (somente admin) |

---

## Perguntas abertas (AGEF / clientes)

- [ ] Fluxo clonal validado passo a passo com operador de campo
- [ ] Onde registram perda (diário na ronda vs só na transferência)?
- [ ] Spec de qualidade por cliente (Suzano vs Klabin) ou padrão único?
- [ ] Pedido: contrato anual com tranches ou ordem semanal?
- [ ] Pacote de rastreio na expedição (PDF/CSV/planilha do cliente)?
- [ ] Sistema concorrente usado hoje e o que odeiam nele
- [ ] Faturamento na expedição ou no pedido?

---

## Próximas iterações (pós Fase 0)

1. Filtrar todas as queries nativas por `id_viveiro`
2. Vendas florestal por quantidade (lote, não planta individual)
3. Dashboard executivo (4 camadas de KPI)
4. Contratos / pedidos com data de entrega
5. Tipos de área no layout (`casa_vegetacao`, `endurecimento`)

---

## Referências cruzadas

- Nativo (Embrapa, coleta, matriz): [REFERENCIA_VIVEIRO.md](./REFERENCIA_VIVEIRO.md)
- Segurança multi-unidade: [SEGURANCA_RBAC.md](./SEGURANCA_RBAC.md)
- God Mode (visão cross-viveiro): [ADMIN_COCKPIT.md](./ADMIN_COCKPIT.md)
