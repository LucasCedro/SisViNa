<template>
  <AppModalOverlay
    :aberto="aberto"
    :handlers="modalClose"
    panel-class="app-modal-panel--wide"
    aria-labelledby="cmv-detalhe-titulo"
  >
      <header class="estoque-modal__header estoque-modal__header--split">
        <div>
          <h3 id="cmv-detalhe-titulo">Composição do estoque</h3>
          <p class="cmv-subtitulo">
            {{ tituloEspecie }}
            <span v-if="detalhe" class="cmv-subtitulo__escopo">{{ detalhe.escopo_label }}</span>
          </p>
        </div>
        <button type="button" class="btn-fechar" aria-label="Fechar" @click="fechar">×</button>
      </header>

      <div class="cmv-toolbar" role="group" aria-label="Escopo do estoque">
        <button
          type="button"
          class="cmv-toolbar__btn"
          :class="{ 'cmv-toolbar__btn--ativa': escopo === 'comercial' }"
          :disabled="carregando"
          @click="trocarEscopo('comercial')"
        >
          Comercial
        </button>
        <button
          type="button"
          class="cmv-toolbar__btn"
          :class="{ 'cmv-toolbar__btn--ativa': escopo === 'vivas' }"
          :disabled="carregando"
          @click="trocarEscopo('vivas')"
        >
          Todas vivas
        </button>
      </div>

      <div class="estoque-modal__body cmv-body">
        <p v-if="carregando" class="alert alert-info">Carregando composição…</p>
        <p v-else-if="erro" class="alert alert-error">{{ erro }}</p>

        <template v-else-if="detalhe">
          <p v-if="detalhe.parque_total" class="cmv-parque-info">
            Parque total: <strong>{{ detalhe.parque_total }} mudas vivas</strong>
            · CIF: <strong>R$ {{ fmt4(detalhe.cif_unitario_parque) }}/muda</strong>
          </p>

          <div class="cmv-kpis">
            <article class="cmv-kpi">
              <span class="cmv-kpi__label">Valor estoque</span>
              <strong class="cmv-kpi__valor">R$ {{ fmt(detalhe.valor_total) }}</strong>
            </article>
            <article class="cmv-kpi">
              <span class="cmv-kpi__label">Quantidade</span>
              <strong class="cmv-kpi__valor">{{ detalhe.quantidade }}</strong>
              <span class="cmv-kpi__meta">muda(s)</span>
            </article>
            <article class="cmv-kpi">
              <span class="cmv-kpi__label">Custo médio</span>
              <strong class="cmv-kpi__valor">R$ {{ fmt(detalhe.custo_medio) }}</strong>
            </article>
          </div>

          <p class="cmv-formula">
            <span class="cmv-formula__tag">Cálculo</span>
            {{ detalhe.formula }}
          </p>

          <section v-if="detalhe.resumo_calculo" class="cmv-bloco">
            <h4 class="cmv-bloco__titulo">Decomposição do total</h4>
            <div class="cmv-table-wrap">
              <table class="cmv-table">
                <tbody>
                  <tr>
                    <td>Custo base na semeadura</td>
                    <td class="cmv-table__num">R$ {{ fmt(detalhe.resumo_calculo.custo_base_semeadura) }}</td>
                  </tr>
                  <tr>
                    <td>Ajustes pós-semeadura</td>
                    <td class="cmv-table__num">R$ {{ fmt(detalhe.resumo_calculo.ajustes_pos_semeadura) }}</td>
                  </tr>
                  <tr class="cmv-table__total">
                    <td><strong>Total</strong></td>
                    <td class="cmv-table__num"><strong>R$ {{ fmt(detalhe.resumo_calculo.valor_total) }}</strong></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section v-if="detalhe.composicao_agregada?.length" class="cmv-bloco">
            <h4 class="cmv-bloco__titulo">Itens de custeio</h4>
            <div class="cmv-table-wrap">
              <table class="cmv-table">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th class="cmv-table__num">R$/muda</th>
                    <th class="cmv-table__num">Total escopo</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in detalhe.composicao_agregada" :key="item.chave">
                    <td class="cmv-table__item">
                      <span class="cmv-table__badge">{{ item.origem }}</span>
                      <span class="cmv-table__desc" :title="item.descricao">{{ item.descricao }}</span>
                    </td>
                    <td class="cmv-table__num">R$ {{ fmt4(item.valor_unitario_medio) }}</td>
                    <td class="cmv-table__num">R$ {{ fmt(item.valor_total) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section v-if="detalhe.por_semeadura?.length" class="cmv-bloco">
            <h4 class="cmv-bloco__titulo">Por semeadura / lote</h4>
            <article v-for="s in detalhe.por_semeadura" :key="s.id_semeadura" class="cmv-lote">
              <div class="cmv-lote__topo">
                <div class="cmv-lote__info">
                  <strong class="cmv-lote__codigo">{{ s.codigo_lote || 'Sem lote' }}</strong>
                  <span class="cmv-lote__meta">
                    Semeadura #{{ s.id_semeadura }}
                    <template v-if="s.data_semeadura"> · {{ s.data_semeadura }}</template>
                  </span>
                </div>
                <div class="cmv-lote__total">
                  <strong>R$ {{ fmt(s.valor_total) }}</strong>
                  <span>{{ s.quantidade_no_escopo }} un.</span>
                </div>
              </div>
              <p v-if="s.mudas_base_rateio" class="cmv-lote__rateio">
                CIF ÷ <strong>{{ s.mudas_base_rateio }}</strong> mudas no parque
                · unit. <strong>R$ {{ fmt4(s.composicao_unitario.indireto) }}</strong>/muda
              </p>
            </article>
          </section>

          <section v-if="detalhe.observacoes?.length" class="cmv-bloco cmv-bloco--notas">
            <h4 class="cmv-bloco__titulo">Como interpretar</h4>
            <ul class="cmv-notas">
              <li v-for="(obs, i) in detalhe.observacoes" :key="i">{{ obs }}</li>
            </ul>
          </section>
        </template>
      </div>

      <footer class="estoque-modal__footer">
        <button type="button" class="btn btn-secondary" @click="fechar">Fechar</button>
      </footer>
  </AppModalOverlay>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import { getCmvDetalheEspecie } from '@/services/estoques'
import { useSimpleModalClose } from '@/composables/useSimpleModalClose'
import './estoques-shared.css'

const props = defineProps({
  item: { type: Object, default: null },
})

const aberto = ref(false)
const detalhe = ref(null)
const carregando = ref(false)
const erro = ref('')
const escopo = ref('comercial')

function fecharInterno() {
  aberto.value = false
  detalhe.value = null
  erro.value = ''
}

const modalClose = useSimpleModalClose(fecharInterno, () => aberto.value)

const tituloEspecie = computed(() => {
  const i = props.item
  if (!i) return ''
  return i.nomePopular || i.nomeCientifico || `Espécie #${i.id_especie}`
})

function fmt(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function fmt4(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 4 })
}

async function carregar() {
  if (!props.item?.id_especie) return
  carregando.value = true
  erro.value = ''
  try {
    detalhe.value = await getCmvDetalheEspecie(props.item.id_especie, escopo.value)
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Não foi possível carregar a composição.'
    detalhe.value = null
  } finally {
    carregando.value = false
  }
}

async function trocarEscopo(novo) {
  if (escopo.value === novo) return
  escopo.value = novo
  await carregar()
}

function abrir() {
  escopo.value = 'comercial'
  detalhe.value = null
  erro.value = ''
  aberto.value = true
  carregar()
}

function fechar() {
  modalClose.resetOverlayPress()
  fecharInterno()
}

watch(
  () => props.item?.id_especie,
  () => {
    if (aberto.value) carregar()
  }
)

defineExpose({ abrir, fechar })
</script>

<style scoped>
.estoque-modal--cmv {
  width: 100%;
  max-width: min(720px, calc(100vw - 1.5rem));
}

.estoque-modal__header--split {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.estoque-modal__header--split > div {
  min-width: 0;
  flex: 1;
}

.btn-fechar {
  flex-shrink: 0;
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: var(--color-text-muted);
  padding: 0.15rem 0.35rem;
  border-radius: var(--radius-sm);
}

.btn-fechar:hover {
  color: var(--color-text-primary);
  background: var(--color-surface-muted);
}

.cmv-subtitulo {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
  word-break: break-word;
}

.cmv-subtitulo__escopo {
  display: block;
  margin-top: 0.15rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.cmv-toolbar {
  display: flex;
  gap: 0.5rem;
  padding: 0.65rem var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-subtle);
  background: var(--color-surface-muted);
  flex-shrink: 0;
}

.cmv-toolbar__btn {
  flex: 1;
  border: 1px solid var(--color-border-subtle);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 0.45rem 0.65rem;
  font-size: 0.8125rem;
  font-family: inherit;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.cmv-toolbar__btn--ativa {
  border-color: var(--color-primary-400);
  background: var(--color-primary-subtle);
  color: var(--color-primary-800);
  font-weight: 600;
}

.cmv-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

.cmv-parque-info {
  margin: 0;
  padding: 0.55rem 0.75rem;
  font-size: 0.8125rem;
  background: var(--color-info-bg);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
}

.cmv-kpis {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
}

.cmv-kpi {
  min-width: 0;
  padding: 0.75rem;
  border-radius: var(--radius-lg);
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary-100);
}

.cmv-kpi__label {
  display: block;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-secondary);
}

.cmv-kpi__valor {
  display: block;
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  color: var(--color-primary-800);
  line-height: 1.2;
}

.cmv-kpi__meta {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
}

.cmv-formula {
  margin: 0;
  padding: 0.65rem 0.75rem;
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
  line-height: 1.45;
  word-break: break-word;
}

.cmv-formula__tag {
  display: inline-block;
  margin-right: 0.35rem;
  padding: 0.1rem 0.4rem;
  border-radius: var(--radius-sm);
  background: var(--color-primary-subtle);
  color: var(--color-primary-800);
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
}

.cmv-bloco__titulo {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.cmv-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
}

.cmv-table {
  width: 100%;
  min-width: 16rem;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.cmv-table th,
.cmv-table td {
  padding: 0.5rem 0.65rem;
  border-bottom: 1px solid var(--color-border-subtle);
  text-align: left;
  vertical-align: top;
}

.cmv-table th {
  background: var(--color-surface-muted);
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-secondary);
}

.cmv-table__num {
  text-align: right;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  width: 30%;
}

.cmv-table__item {
  word-break: break-word;
}

.cmv-table__badge {
  display: inline-block;
  margin-right: 0.25rem;
  font-size: 0.5625rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.cmv-table__total td {
  border-top: 2px solid var(--color-border);
}

.cmv-lote {
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: 0.75rem;
  margin-bottom: 0.5rem;
}

.cmv-lote__topo {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.cmv-lote__info {
  min-width: 0;
  flex: 1 1 10rem;
}

.cmv-lote__codigo {
  word-break: break-all;
}

.cmv-lote__meta {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.cmv-lote__total {
  text-align: right;
}

.cmv-lote__total span {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.cmv-lote__rateio {
  margin: 0.4rem 0 0;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.cmv-bloco--notas {
  padding: 0.75rem;
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
}

.cmv-notas {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  line-height: 1.45;
}

@media (max-width: 560px) {
  .cmv-kpis {
    grid-template-columns: 1fr;
  }
}
</style>
