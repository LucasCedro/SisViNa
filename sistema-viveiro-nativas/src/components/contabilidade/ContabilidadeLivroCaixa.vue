<template>
  <div class="contab-lc module-sec">
    <p v-if="carregando && !dados" class="status-msg">Carregando livro caixa…</p>
    <p v-else-if="erro" class="alert-erro">{{ erro }}</p>
    <template v-else-if="dados">
      <p class="contab-lead">
        Movimentação em <strong>regime de caixa</strong> — entradas na data de pagamento,
        saídas operacionais (compras pagas) e CAPEX na data do lançamento.
      </p>

      <div class="kpi-grid kpi-grid--dfc">
        <article
          v-for="card in cards"
          :key="card.id"
          class="kpi-card"
          :class="card.classe"
        >
          <button type="button" class="kpi-card__btn" @click="abrir(card)">
            <span class="kpi-card__label">{{ card.label }}</span>
            <strong class="kpi-card__valor">R$ {{ fmt(card.valor) }}</strong>
            <span v-if="card.meta" class="kpi-card__meta">{{ card.meta }}</span>
            <span class="kpi-card__hint">Ver cálculo</span>
          </button>
        </article>
      </div>

      <div class="lc-tabelas">
        <section>
          <h3>Entradas — recebimentos</h3>
          <div v-if="dados.entradas?.length" class="module-table-wrap">
            <table class="module-table">
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Descrição</th>
                  <th>Pagamento</th>
                  <th class="num">Valor</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in dados.entradas" :key="'e-' + e.id">
                  <td>{{ fmtData(e.data) }}</td>
                  <td>{{ e.descricao }}</td>
                  <td>{{ e.forma_pagamento || '—' }}</td>
                  <td class="num">R$ {{ fmt(e.valor) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty">Nenhuma entrada no período.</p>
        </section>

        <section>
          <h3>Saídas operacionais — compras de insumo</h3>
          <div v-if="dados.saidas_operacionais?.length" class="module-table-wrap">
            <table class="module-table">
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Descrição</th>
                  <th class="num">Valor</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in dados.saidas_operacionais" :key="'so-' + s.id">
                  <td>{{ fmtData(s.data) }}</td>
                  <td>{{ s.descricao }}</td>
                  <td class="num">R$ {{ fmt(s.valor) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty">Nenhuma saída operacional no período.</p>
        </section>

        <section>
          <h3>Saídas — CAPEX</h3>
          <div v-if="dados.saidas?.length" class="module-table-wrap">
            <table class="module-table">
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Descrição</th>
                  <th>Categoria</th>
                  <th class="num">Valor</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in dados.saidas" :key="'s-' + s.id">
                  <td>{{ fmtData(s.data) }}</td>
                  <td>{{ s.descricao }}</td>
                  <td>{{ s.categoria || '—' }}</td>
                  <td class="num">R$ {{ fmt(s.valor) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty">Nenhuma saída CAPEX no período.</p>
        </section>
      </div>

      <aside v-if="dados.observacoes?.length" class="module-banner module-banner--info">
        <ul>
          <li v-for="(o, i) in dados.observacoes" :key="i">{{ o }}</li>
        </ul>
      </aside>

      <ContabilidadeDetalheModal
        :aberto="!!modal"
        :titulo="modal?.label || ''"
        :valor="modal?.valor"
        :tipo="modal?.tipo || 'resultado'"
        :bloco="modal?.bloco"
        @fechar="modal = null"
      />
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import ContabilidadeDetalheModal from './ContabilidadeDetalheModal.vue'

const props = defineProps({
  dados: { type: Object, default: null },
  carregando: { type: Boolean, default: false },
  erro: { type: String, default: null },
})

const modal = ref(null)

const cards = computed(() => {
  const d = props.dados
  const det = d?.detalhes
  if (!d) return []
  return [
    {
      id: 'entradas',
      label: 'Entradas',
      valor: d.total_entradas,
      meta: `${d.entradas?.length || 0} recebimento(s)`,
      classe: 'kpi-card--dfc-entrada',
      tipo: 'recebimentos',
      bloco: det?.entradas,
    },
    {
      id: 'saidas-op',
      label: 'Saídas operacionais',
      valor: d.total_saidas_operacionais,
      meta: `${d.saidas_operacionais?.length || 0} compra(s) pagas`,
      classe: 'kpi-card--dfc-saida',
      tipo: 'compras_insumos',
      bloco: det?.saidas_operacionais,
    },
    {
      id: 'capex',
      label: 'Saídas CAPEX',
      valor: d.total_saidas_investimento,
      meta: `${d.saidas?.length || 0} lançamento(s)`,
      classe: 'kpi-card--dfc-saida',
      tipo: 'capex',
      bloco: det?.saidas_investimento,
    },
    {
      id: 'saldo',
      label: 'Saldo do período',
      valor: d.saldo_periodo,
      meta: 'Entradas − saídas',
      classe: d.saldo_periodo >= 0 ? 'kpi-card--dfc-saldo-pos' : 'kpi-card--dfc-saldo-neg',
      tipo: 'resultado',
      bloco: det?.saldo,
    },
  ]
})

function abrir(card) {
  modal.value = card
}

function fmt(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function fmtData(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR')
}
</script>

<style scoped>
@import '@/components/financeiro/financeiro-shared.css';

.contab-lead {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin: 0 0 var(--spacing-md);
}
.lc-tabelas {
  display: grid;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-lg);
}
.lc-tabelas h3 {
  font-size: 0.9375rem;
  margin: 0 0 var(--spacing-sm);
}
.num {
  text-align: right;
}
.empty {
  color: var(--color-text-muted);
  font-size: 0.875rem;
}
.module-banner ul {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.8125rem;
}
</style>
