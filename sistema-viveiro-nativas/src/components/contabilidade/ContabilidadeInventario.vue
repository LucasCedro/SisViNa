<template>
  <div class="contab-inv module-sec">
    <p v-if="carregando && !dados" class="status-msg">Carregando inventário…</p>
    <p v-else-if="erro" class="alert-erro">{{ erro }}</p>
    <template v-else-if="dados">
      <p class="contab-lead">
        Inventário em <strong>{{ fmtData(dados.data_referencia) }}</strong> —
        registro obrigatório de estoques (Lei 8.218/91, art. 16).
      </p>

      <div class="inv-cards">
        <article
          v-for="card in cardsResumo"
          :key="card.id"
          class="inv-card inv-card--click"
          :class="{ 'inv-card--total': card.id === 'total' }"
        >
          <button type="button" class="inv-card__btn" @click="abrir(card)">
            <span class="inv-card__label">{{ card.label }}</span>
            <strong class="inv-card__valor">R$ {{ fmt(card.valor) }}</strong>
            <span v-if="card.meta" class="inv-card__meta">{{ card.meta }}</span>
            <span class="inv-card__hint">Ver cálculo</span>
          </button>
        </article>
      </div>

      <section v-if="dados.insumos?.length" class="inv-sec">
        <h3>Insumos</h3>
        <div class="module-table-wrap">
          <table class="module-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Tipo</th>
                <th class="num">Qtd</th>
                <th class="num">Preço méd.</th>
                <th class="num">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="i in dados.insumos" :key="i.id">
                <td>{{ i.nome }}</td>
                <td>{{ i.tipo }}</td>
                <td class="num">{{ i.quantidade_estoque }} {{ i.unidade_medida || '' }}</td>
                <td class="num">R$ {{ fmt(i.preco_unitario) }}</td>
                <td class="num">R$ {{ fmt(i.valor_estoque) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="dados.sementes?.length" class="inv-sec">
        <h3>Sementes (lotes ativos)</h3>
        <div class="module-table-wrap">
          <table class="module-table">
            <thead>
              <tr>
                <th>Lote</th>
                <th>Espécie</th>
                <th class="num">Saldo</th>
                <th class="num">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="l in dados.sementes" :key="l.id">
                <td>{{ l.codigo_lote }}</td>
                <td>{{ l.especie_nome }}</td>
                <td class="num">{{ l.quantidade_disponivel }}</td>
                <td class="num">R$ {{ fmt(l.valor_total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <ContabilidadeDetalheModal
        :aberto="!!modal"
        :titulo="modal?.label || ''"
        :valor="modal?.valor"
        :tipo="modal?.tipo || 'resultado'"
        :bloco="modal?.bloco"
        :estoque="modal?.estoque"
        :estoque-foco="modal?.estoqueFoco"
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

const cardsResumo = computed(() => {
  const r = props.dados?.resumo
  const det = props.dados?.detalhes
  if (!r) return []
  return [
    {
      id: 'vivas',
      label: 'Mudas vivas',
      valor: r.mudas_vivas?.valor,
      meta: `${r.mudas_vivas?.quantidade || 0} un. · média R$ ${fmt(r.mudas_vivas?.custo_medio)}`,
      tipo: 'resultado',
      bloco: det?.mudas_vivas,
    },
    {
      id: 'comercial',
      label: 'Mudas comercial',
      valor: r.mudas_comercial?.valor,
      meta: `${r.mudas_comercial?.quantidade || 0} aptas venda`,
      tipo: 'resultado',
      bloco: det?.mudas_comercial,
    },
    {
      id: 'insumos',
      label: 'Insumos',
      valor: r.insumos?.valor,
      meta: `${r.insumos?.itens || 0} item(ns)`,
      tipo: 'estoque',
      bloco: null,
      estoque: det?.insumos
        ? {
            insumos: det.insumos,
            insumos_itens: det.insumos.itens || props.dados.insumos,
          }
        : null,
      estoqueFoco: 'insumos',
    },
    {
      id: 'sementes',
      label: 'Sementes',
      valor: r.sementes?.valor,
      meta: 'Lotes ativos',
      tipo: 'estoque',
      bloco: null,
      estoque: det?.sementes
        ? {
            sementes: det.sementes,
            sementes_itens: det.sementes.itens || props.dados.sementes,
          }
        : null,
      estoqueFoco: 'sementes',
    },
    {
      id: 'total',
      label: 'Valor total inventariado',
      valor: r.valor_total,
      meta: 'Mudas + insumos + sementes',
      tipo: 'resultado',
      bloco: det?.valor_total,
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
.inv-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}
.inv-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.inv-card--total {
  border-color: var(--color-primary);
  background: var(--color-surface-muted);
}
.inv-card__btn {
  width: 100%;
  padding: var(--spacing-md);
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.inv-card__btn:hover .inv-card__hint {
  color: var(--color-primary);
}
.inv-card__label {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}
.inv-card__valor {
  font-size: 1.2rem;
}
.inv-card__meta {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.inv-card__hint {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  margin-top: 0.15rem;
}
.inv-sec h3 {
  font-size: 0.9375rem;
  margin: 0 0 var(--spacing-sm);
}
.num {
  text-align: right;
}
</style>
