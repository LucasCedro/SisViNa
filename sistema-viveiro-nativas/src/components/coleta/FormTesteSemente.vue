<template>
  <AppModalOverlay
    :aberto="aberto"
    :handlers="modalClose"
    panel-class="app-modal-panel--md"
  >
      <header class="modal-header">
        <h2>Teste de germinação</h2>
        <button type="button" class="btn-fechar" @click="fechar">×</button>
      </header>

      <form class="modal-body" @submit.prevent="salvar">
        <p class="info">
          {{ lote?.codigo_lote }} · {{ especieNome }} · {{ lote?.matriz_nome || '—' }}
        </p>

        <dl class="saldos">
          <div>
            <dt>Reserva p/ teste</dt>
            <dd>{{ fmt(reservaTeste) }}</dd>
          </div>
          <div>
            <dt>Lote (estoque)</dt>
            <dd>{{ fmt(loteComercial) }}</dd>
          </div>
        </dl>

        <div class="field-row">
          <label class="field">
            Repetições
            <input v-model.number="form.repeticoes" type="number" min="1" required @input="recalcular" />
          </label>
          <label class="field">
            Por repetição
            <input
              v-model.number="form.sementes_por_repeticao"
              type="number"
              min="1"
              required
              @input="recalcular"
            />
          </label>
        </div>

        <p class="total-linha" :class="{ 'total-linha--erro': excedeReserva }">
          <strong>{{ fmt(sementesUsadas) }}</strong> usadas
          <template v-if="reservaTeste > 0">
            de {{ fmt(reservaTeste) }} reservadas
            <template v-if="sobraReserva > 0">
              · sobra {{ fmt(sobraReserva) }} (voltam ao estoque)
            </template>
          </template>
        </p>

        <div class="field-row">
          <label class="field">
            Data
            <input v-model="form.data_teste" type="date" required />
          </label>
          <label class="field">
            Germinação (%)
            <input
              v-model.number="form.percentual_resultado"
              type="number"
              min="0"
              max="100"
              step="0.1"
              required
            />
          </label>
        </div>

        <label class="field">
          Metodologia
          <input v-model="form.metodologia" type="text" placeholder="Opcional" />
        </label>

        <label class="field">
          Observações
          <textarea v-model="form.observacoes" rows="2" />
        </label>

        <p v-if="erro" class="erro">{{ erro }}</p>

        <footer class="modal-footer">
          <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
          <button type="submit" class="btn-prim" :disabled="salvando || excedeReserva">
            {{ salvando ? 'Salvando…' : 'Salvar' }}
          </button>
        </footer>
      </form>
  </AppModalOverlay>
  <ConfirmSaidaModal
    :aberto="confirmAberto"
    @confirmar="confirmarSaida"
    @cancelar="cancelarSaida"
  />
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { useFormDirty } from '@/utils/formDirty'
import { createTesteSementes } from '@/services/testesSementes'
import { useColetaStore } from '@/store/coleta'

const props = defineProps({
  aberto: Boolean,
  lote: { type: Object, default: null },
})
const emit = defineEmits(['fechar', 'salvo'])

const store = useColetaStore()
const salvando = ref(false)
const erro = ref('')

const form = ref({
  data_teste: new Date().toISOString().split('T')[0],
  tipo_teste: 'germinacao',
  percentual_resultado: null,
  repeticoes: 4,
  sementes_por_repeticao: 25,
  sementes_avaliadas: 100,
  metodologia: '',
  observacoes: '',
})

const coleta = computed(() => {
  const id = props.lote?.id_coleta_sementes
  return id ? store.coletas.find((c) => c.id === id) : null
})

const reservaTeste = computed(() => Number(coleta.value?.sementes_reservadas_teste) || 0)
const loteComercial = computed(() => Number(props.lote?.quantidade_disponivel) || 0)
const sementesUsadas = computed(() => Number(form.value.sementes_avaliadas) || 0)
const sobraReserva = computed(() =>
  reservaTeste.value ? Math.max(0, reservaTeste.value - sementesUsadas.value) : null
)
const excedeReserva = computed(
  () => reservaTeste.value > 0 && sementesUsadas.value > reservaTeste.value
)

const especieNome = computed(() => {
  const l = props.lote
  if (!l) return '—'
  if (l.especie_nome) return l.especie_nome
  return store.arvoresMatriz.find((a) => a.id === l.id_arvore_matriz)?.especie_nome || '—'
})

function fmt(n) {
  if (n == null || Number.isNaN(n)) return '—'
  return Number(n).toLocaleString('pt-BR')
}

function recalcular() {
  const rep = Number(form.value.repeticoes) || 0
  const por = Number(form.value.sementes_por_repeticao) || 0
  if (rep > 0 && por > 0) form.value.sementes_avaliadas = rep * por
}

function resetForm() {
  erro.value = ''
  const rep = 4
  const reserva = reservaTeste.value
  let por = 25
  if (reserva > 0) {
    por = Math.max(1, Math.floor(reserva / rep))
    if (por * rep > reserva) por = Math.max(1, Math.ceil(reserva / rep))
  }
  form.value = {
    data_teste: new Date().toISOString().split('T')[0],
    tipo_teste: 'germinacao',
    percentual_resultado: null,
    repeticoes: rep,
    sementes_por_repeticao: por,
    sementes_avaliadas: rep * por,
    metodologia: '',
    observacoes: '',
  }
  if (reserva > 0 && form.value.sementes_avaliadas > reserva) {
    form.value.sementes_avaliadas = reserva
    form.value.sementes_por_repeticao = Math.max(1, Math.floor(reserva / rep))
  }
}

const { isDirty, rebase } = useFormDirty(form, () => props.aberto)

watch(
  () => [props.aberto, props.lote?.id],
  async ([aberto]) => {
    if (!aberto) return
    resetForm()
    await nextTick()
    rebase()
  }
)

function fecharInterno() {
  emit('fechar')
}

const modalClose = useModalFormClose(fecharInterno, () => isDirty.value, () => props.aberto)
const {
  resetOverlayPress,
  confirmAberto,
  confirmarSaida,
  cancelarSaida,
  requestClose,
  sairSemConfirmar,
} = modalClose

function fechar() {
  resetOverlayPress()
  requestClose()
}

async function salvar() {
  if (!props.lote) return
  if (form.value.percentual_resultado == null || form.value.percentual_resultado < 0) {
    erro.value = 'Informe a germinação (%).'
    return
  }
  if (!sementesUsadas.value) {
    erro.value = 'Informe repetições e sementes por repetição.'
    return
  }
  if (excedeReserva.value) {
    erro.value = 'Total usado maior que a reserva da coleta.'
    return
  }
  erro.value = ''
  salvando.value = true
  try {
    const { sementes_por_repeticao: _, ...payload } = form.value
    const teste = await createTesteSementes({
      id_lote_sementes: props.lote.id,
      ...payload,
    })
    store.upsertTeste(teste)
    const idx = store.lotes.findIndex((l) => l.id === props.lote.id)
    if (idx !== -1) {
      store.lotes[idx] = {
        ...store.lotes[idx],
        ultimo_teste_germinacao: form.value.percentual_resultado,
      }
    }
    await store.recarregarMatriz(props.lote.id_arvore_matriz)
    emit('salvo', teste)
    sairSemConfirmar()
  } catch (e) {
    erro.value = e.response?.data?.detail || e.message || 'Erro ao salvar'
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.125rem;
}

.btn-fechar {
  border: none;
  background: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-muted);
}

.modal-body {
  padding: 1.25rem;
  box-sizing: border-box;
}

.info {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  line-height: 1.4;
  color: var(--color-text-muted);
}

.saldos {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin: 0 0 1rem;
  padding: 0.75rem;
  background: var(--color-surface-muted);
  border-radius: 8px;
}

.saldos > div {
  min-width: 0;
}

.saldos dt {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: 0.15rem;
}

.saldos dd {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.field-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.field-row .field {
  margin-bottom: 0;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1rem;
  min-width: 0;
  font-size: 0.875rem;
  font-weight: 500;
}

.field input,
.field textarea {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  font-weight: 400;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

.field input[type='date'],
.field input[type='number'] {
  min-width: 0;
}

.total-linha {
  margin: 0 0 1rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.total-linha strong {
  color: var(--color-text-primary);
}

.total-linha--erro {
  color: var(--color-error);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-sec,
.btn-prim {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-sec {
  background: var(--color-surface-muted);
}

.btn-prim {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-weight: 600;
}

.btn-prim:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.erro {
  color: var(--color-error);
  font-size: 0.875rem;
  margin: 0 0 0.75rem;
}

@media (max-width: 480px) {
  .field-row,
  .saldos {
    grid-template-columns: 1fr;
  }
}
</style>
