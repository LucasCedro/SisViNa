<template>
  <div
    v-if="bloco || (tipo === 'estoque' && estoque)"
    class="fin-detalhe"
    :class="{ 'fin-detalhe--modal': !embedded }"
  >
    <p v-if="bloco?.formula" class="fin-detalhe__formula">
      <span class="fin-detalhe__tag">Cálculo</span>
      {{ bloco.formula }}
    </p>
    <p v-if="bloco?.explicacao" class="fin-detalhe__explicacao">{{ bloco.explicacao }}</p>

    <div v-if="bloco?.passos?.length" class="fin-detalhe__passos">
      <div v-for="(p, i) in bloco.passos" :key="i" class="fin-detalhe__passo">
        <span v-if="p.operador && i > 0" class="fin-detalhe__op">{{ p.operador }}</span>
        <span class="fin-detalhe__passo-label">{{ p.label }}</span>
        <strong class="fin-detalhe__passo-valor">{{ fmtMoeda(p.valor) }}</strong>
      </div>
    </div>

    <div v-if="tipo === 'faturamento' && receitas?.length" class="fin-detalhe__tabela-wrap">
      <table class="fin-detalhe__tabela">
        <thead>
          <tr>
            <th>Data</th>
            <th>Comprador</th>
            <th class="num">Itens</th>
            <th class="num">Valor</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in receitas" :key="r.id">
            <td>{{ fmtData(r.data_venda) }}</td>
            <td>{{ r.comprador_nome || '—' }}</td>
            <td class="num">{{ r.total_itens }}</td>
            <td class="num">{{ fmtMoeda(r.valor_total) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" class="num"><strong>Total faturamento</strong></td>
            <td class="num"><strong>{{ fmtMoeda(bloco?.total) }}</strong></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- Recebimentos (DFC / caixa) -->
    <div v-if="tipo === 'recebimentos' && bloco.itens?.length" class="fin-detalhe__tabela-wrap">
      <table class="fin-detalhe__tabela">
        <thead>
          <tr>
            <th>Data pag.</th>
            <th>Descrição</th>
            <th>Forma</th>
            <th class="num">Valor</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in bloco.itens" :key="item.id">
            <td>{{ fmtData(item.data) }}</td>
            <td>{{ item.descricao }}</td>
            <td>{{ item.forma_pagamento || '—' }}</td>
            <td class="num">{{ fmtMoeda(item.valor) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" class="num"><strong>Total recebimentos</strong></td>
            <td class="num"><strong>{{ fmtMoeda(bloco?.total) }}</strong></td>
          </tr>
        </tfoot>
      </table>
    </div>
    <p v-else-if="tipo === 'recebimentos'" class="fin-detalhe__vazio">Nenhum recebimento neste período.</p>

    <!-- CMV: itens vendidos -->
    <div v-if="tipo === 'cmv' && bloco.itens?.length" class="fin-detalhe__tabela-wrap">
      <p v-if="bloco.truncado" class="fin-detalhe__aviso">
        Mostrando {{ bloco.itens.length }} de {{ bloco.total_itens }} itens.
      </p>
      <table class="fin-detalhe__tabela">
        <thead>
          <tr>
            <th>Data</th>
            <th>Muda</th>
            <th>Espécie</th>
            <th class="num">Qtd</th>
            <th class="num">Receita</th>
            <th class="num">Custo un.</th>
            <th class="num">CMV</th>
            <th>Origem</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in bloco.itens" :key="item.id_item">
            <td>{{ fmtData(item.data_venda) }}</td>
            <td><code>{{ item.codigo_rastreio || '—' }}</code></td>
            <td>{{ item.especie_nome }}</td>
            <td class="num">{{ item.quantidade }}</td>
            <td class="num">{{ fmtMoeda(item.receita_linha) }}</td>
            <td class="num">{{ fmtMoeda(item.custo_unitario) }}</td>
            <td class="num">{{ fmtMoeda(item.cmv_linha) }}</td>
            <td>
              <span class="fin-detalhe__badge" :class="'fin-detalhe__badge--' + item.origem_custo">
                {{ item.origem_custo === 'congelado' ? 'Na venda' : 'Planta atual' }}
              </span>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="6" class="num"><strong>Total CMV</strong></td>
            <td class="num"><strong>{{ fmtMoeda(bloco?.total) }}</strong></td>
            <td />
          </tr>
        </tfoot>
      </table>
    </div>
    <p v-else-if="tipo === 'cmv'" class="fin-detalhe__vazio">Nenhuma venda paga no período.</p>

    <!-- Compras de insumos -->
    <div v-if="tipo === 'compras_insumos' && bloco.itens?.length" class="fin-detalhe__tabela-wrap">
      <table class="fin-detalhe__tabela">
        <thead>
          <tr>
            <th>Data NF</th>
            <th>Insumo</th>
            <th>Pagamento</th>
            <th class="num">Qtd</th>
            <th class="num">Valor</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in bloco.itens" :key="item.id">
            <td>{{ fmtData(item.data_movimento || item.data) }}</td>
            <td>{{ item.insumo_nome }}</td>
            <td>{{ item.status_pagamento === 'PENDENTE' ? 'A prazo' : fmtData(item.data_pagamento || item.data_movimento) }}</td>
            <td class="num">{{ item.quantidade }}</td>
            <td class="num">{{ fmtMoeda(item.valor_total) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="4" class="num"><strong>Total compras</strong></td>
            <td class="num"><strong>{{ fmtMoeda(bloco?.total) }}</strong></td>
          </tr>
        </tfoot>
      </table>
    </div>
    <p v-else-if="tipo === 'compras_insumos'" class="fin-detalhe__vazio">Nenhuma compra de insumo no período.</p>

    <!-- A receber (vendas pendentes) -->
    <div v-if="tipo === 'a_receber' && bloco.itens?.length" class="fin-detalhe__tabela-wrap">
      <table class="fin-detalhe__tabela">
        <thead>
          <tr>
            <th>Data venda</th>
            <th>Comprador</th>
            <th>Forma</th>
            <th class="num">Valor</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in bloco.itens" :key="item.id">
            <td>{{ fmtData(item.data_venda) }}</td>
            <td>{{ item.comprador_nome || '—' }}</td>
            <td>{{ item.forma_pagamento || '—' }}</td>
            <td class="num">{{ fmtMoeda(item.valor_total) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" class="num"><strong>Total a receber</strong></td>
            <td class="num"><strong>{{ fmtMoeda(bloco?.total) }}</strong></td>
          </tr>
        </tfoot>
      </table>
    </div>
    <p v-else-if="tipo === 'a_receber'" class="fin-detalhe__vazio">Nenhuma venda pendente.</p>

    <!-- OPEX -->
    <div v-if="tipo === 'opex'" class="fin-detalhe__tabela-wrap">
      <p class="fin-detalhe__base">
        Base comissão: faturamento do período = <strong>{{ fmtMoeda(bloco.faturamento_base) }}</strong>
      </p>
      <table v-if="bloco.itens?.length" class="fin-detalhe__tabela">
        <thead>
          <tr>
            <th>Premissa</th>
            <th>Tipo</th>
            <th>Fórmula</th>
            <th class="num">Valor</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in bloco.itens" :key="item.chave">
            <td>{{ item.nome }}</td>
            <td>{{ item.tipo === 'comissao' ? 'Comissão' : 'Fixa/mês' }}</td>
            <td class="fin-detalhe__formula-cell">{{ item.formula || '—' }}</td>
            <td class="num">{{ fmtMoeda(item.valor) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" class="num"><strong>Total OPEX</strong></td>
            <td class="num"><strong>{{ fmtMoeda(bloco?.total) }}</strong></td>
          </tr>
        </tfoot>
      </table>
      <p v-else class="fin-detalhe__vazio">Configure premissas DESPESA em Financeiro → Premissas.</p>
    </div>

    <!-- Estoque -->
    <template v-if="tipo === 'estoque' && estoque">
      <div v-for="sec in estoqueSecoes" :key="sec.id" class="fin-detalhe__estoque-sec">
        <h4 class="fin-detalhe__subtitulo">{{ sec.bloco.titulo }}</h4>
        <p class="fin-detalhe__formula fin-detalhe__formula--sm">
          <span class="fin-detalhe__tag">Cálculo</span>
          {{ sec.bloco.formula }}
        </p>
        <p v-if="sec.bloco.explicacao" class="fin-detalhe__explicacao">{{ sec.bloco.explicacao }}</p>
        <strong class="fin-detalhe__total-linha">{{ fmtMoeda(sec.bloco.total) }}</strong>

        <div v-if="sec.itens?.length" class="fin-detalhe__tabela-wrap">
          <table class="fin-detalhe__tabela">
            <thead>
              <tr>
                <th v-for="col in sec.colunas" :key="col.key">{{ col.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in sec.itens" :key="idx">
                <td v-for="col in sec.colunas" :key="col.key" :class="col.num ? 'num' : ''">
                  <code v-if="col.mono">{{ row[col.key] }}</code>
                  <template v-else-if="col.moeda">{{ fmtMoeda(row[col.key]) }}</template>
                  <template v-else>{{ row[col.key] ?? '—' }}</template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- CAPEX -->
    <div v-if="tipo === 'capex'" class="fin-detalhe__tabela-wrap">
      <table v-if="bloco.itens?.length" class="fin-detalhe__tabela">
        <thead>
          <tr>
            <th>Data</th>
            <th>Descrição</th>
            <th>Categoria</th>
            <th class="num">Valor</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in bloco.itens" :key="item.id">
            <td>{{ fmtData(item.data_lancamento || item.data) }}</td>
            <td>{{ item.descricao }}</td>
            <td>{{ item.categoria }}</td>
            <td class="num">{{ fmtMoeda(item.valor) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" class="num"><strong>Total CAPEX</strong></td>
            <td class="num"><strong>{{ fmtMoeda(bloco?.total) }}</strong></td>
          </tr>
        </tfoot>
      </table>
      <p v-else class="fin-detalhe__vazio">Nenhum lançamento CAPEX neste período.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tipo: { type: String, required: true },
  bloco: { type: Object, default: null },
  receitas: { type: Array, default: () => [] },
  estoque: { type: Object, default: null },
  estoqueFoco: { type: String, default: null },
  embedded: { type: Boolean, default: true },
})

const estoqueSecoes = computed(() => {
  const e = props.estoque
  if (!e) return []
  const secoes = [
    { id: 'parque', bloco: e.parque, itens: null, colunas: [] },
    { id: 'comercial', bloco: e.comercial, itens: null, colunas: [] },
    {
      id: 'insumos',
      bloco: e.insumos,
      itens: e.insumos_itens,
      colunas: [
        { key: 'nome', label: 'Insumo' },
        { key: 'tipo', label: 'Tipo' },
        { key: 'quantidade_estoque', label: 'Qtd', num: true },
        { key: 'unidade_medida', label: 'Un.' },
        { key: 'preco_unitario', label: 'Preço méd.', num: true, moeda: true },
        { key: 'valor_estoque', label: 'Valor', num: true, moeda: true },
      ],
    },
    {
      id: 'sementes',
      bloco: e.sementes,
      itens: e.sementes_itens,
      colunas: [
        { key: 'codigo_lote', label: 'Lote', mono: true },
        { key: 'especie_nome', label: 'Espécie' },
        { key: 'quantidade_disponivel', label: 'Saldo', num: true },
        { key: 'custo_unitario', label: 'Custo/un.', num: true, moeda: true },
        { key: 'valor_total', label: 'Valor', num: true, moeda: true },
      ],
    },
  ]
  const lista = secoes.filter((s) => s.bloco)
  if (props.estoqueFoco) {
    return lista.filter((s) => s.id === props.estoqueFoco)
  }
  return lista
})

function fmtMoeda(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function fmtData(iso) {
  if (!iso) return '—'
  const d = iso.includes('T') ? iso.slice(0, 10) : iso
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y}`
}
</script>

<style scoped>
.fin-detalhe {
  padding: 0.75rem 1rem 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-primary-100);
  border-radius: var(--radius-md);
  margin-top: 0.35rem;
}

.fin-detalhe--modal {
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0;
  margin-top: 0;
}

.fin-detalhe__formula {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-text-secondary);
}

.fin-detalhe__formula--sm {
  margin-bottom: 0.35rem;
}

.fin-detalhe__tag {
  display: inline-block;
  margin-right: 0.35rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: var(--color-primary-50);
  color: var(--color-primary-700);
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.fin-detalhe__explicacao {
  margin: 0 0 0.65rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.fin-detalhe__passos {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
  padding: 0.65rem 0.75rem;
  background: var(--color-primary-50);
  border-radius: var(--radius-md);
}

.fin-detalhe__passo {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem 0.5rem;
  font-size: 0.8125rem;
}

.fin-detalhe__op {
  font-weight: 700;
  color: var(--color-text-muted);
  min-width: 1rem;
}

.fin-detalhe__passo-label {
  flex: 1;
  color: var(--color-text-secondary);
}

.fin-detalhe__passo-valor {
  font-variant-numeric: tabular-nums;
}

.fin-detalhe__base {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.fin-detalhe__tabela-wrap {
  overflow-x: auto;
  margin-top: 0.5rem;
}

.fin-detalhe__tabela {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.fin-detalhe__tabela th {
  text-align: left;
  padding: 0.4rem 0.5rem;
  background: var(--color-primary-50);
  border-bottom: 1px solid var(--color-primary-100);
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text-secondary);
}

.fin-detalhe__tabela td {
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid var(--color-primary-50);
  vertical-align: top;
}

.fin-detalhe__tabela .num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.fin-detalhe__tabela code {
  font-size: 0.75rem;
}

.fin-detalhe__formula-cell {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  max-width: 14rem;
}

.fin-detalhe__badge {
  display: inline-block;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 600;
}

.fin-detalhe__badge--congelado {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.fin-detalhe__badge--planta_atual {
  background: var(--color-attention-bg);
  color: var(--color-text-secondary);
}

.fin-detalhe__aviso,
.fin-detalhe__vazio {
  margin: 0.35rem 0;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.fin-detalhe__estoque-sec {
  padding-top: 0.75rem;
  margin-top: 0.75rem;
  border-top: 1px dashed var(--color-primary-100);
}

.fin-detalhe__estoque-sec:first-child {
  padding-top: 0;
  margin-top: 0;
  border-top: none;
}

.fin-detalhe__subtitulo {
  margin: 0 0 0.35rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.fin-detalhe__total-linha {
  display: block;
  margin: 0.35rem 0 0.5rem;
  font-size: 1rem;
}
</style>
