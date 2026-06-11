<template>
  <div
    v-if="aberto"
    class="modal-overlay"
    @pointerdown.self="onOverlayPointerDown"
    @pointerup.self="onOverlayPointerUp"
    @pointercancel.self="cancelarFechamentoOverlay"
  >
    <div class="modal-card" role="dialog" @pointerdown="onModalPointerDown">
      <header class="modal-header">
        <h2>Editar coleta</h2>
        <button type="button" class="btn-fechar" @click="fechar">×</button>
      </header>
      <form class="modal-body" @submit.prevent="salvar">
        <p class="info">{{ coleta?.matriz_nome }} — {{ formatarData(coleta?.data_coleta) }}</p>
        <label class="field">
          Data da coleta
          <input v-model="form.data_coleta" type="date" required />
        </label>
        <div class="field-row">
          <label class="field">
            Quantidade coletada
            <input v-model.number="form.quantidade_sementes" type="number" min="1" required />
          </label>
          <label class="field">
            Reserva p/ teste
            <input v-model.number="form.sementes_reservadas_teste" type="number" min="0" />
          </label>
        </div>
        <label class="field">
          Horas de campo
          <input v-model.number="form.horas_campo" type="number" min="0" step="0.25" placeholder="Opcional" />
          <small v-if="refCusto.premissa_ativa" class="hint">
            {{ fmtHoras(form.horas_campo) }} h × {{ fmtMoeda(refCusto.valor_hora) }}/h =
            {{ fmtMoeda(custoPreview) }}
            <template v-if="custoPreview > 0 && qtdLote > 0">
              · {{ fmtMoeda(custoPreview / qtdLote) }}/semente
            </template>
          </small>
        </label>
        <label class="field">
          Observações
          <textarea v-model="form.observacoes" rows="3" />
        </label>
        <p v-if="erro" class="erro">{{ erro }}</p>
        <footer class="modal-footer">
          <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
          <button type="submit" class="btn-prim" :disabled="salvando">Salvar</button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useColetaStore } from '@/store/coleta'
import { useModalOverlayClose } from '@/composables/useModalOverlayClose'
import { getCustoCampoReferencia } from '@/services/coletasSementes'

const props = defineProps({
  aberto: Boolean,
  coleta: { type: Object, default: null }
})
const emit = defineEmits(['fechar', 'salvo'])

const store = useColetaStore()
const salvando = ref(false)
const erro = ref('')
const refCusto = ref({ valor_hora: 0, premissa_ativa: false })
const form = ref({
  data_coleta: '',
  quantidade_sementes: null,
  sementes_reservadas_teste: 0,
  horas_campo: null,
  observacoes: ''
})

const qtdLote = computed(() => {
  const total = Number(form.value.quantidade_sementes) || 0
  const reserva = Number(form.value.sementes_reservadas_teste) || 0
  return Math.max(0, total - reserva)
})

const custoPreview = computed(() => {
  const h = Number(form.value.horas_campo) || 0
  const vh = Number(refCusto.value.valor_hora) || 0
  return h > 0 && vh > 0 ? Math.round(h * vh * 100) / 100 : 0
})

function fmtMoeda(v) {
  return Number(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function fmtHoras(h) {
  return (Number(h) || 0).toLocaleString('pt-BR', { maximumFractionDigits: 2 })
}

watch(
  () => [props.aberto, props.coleta],
  async ([aberto]) => {
    if (!aberto || !props.coleta) return
    erro.value = ''
    form.value = {
      data_coleta: String(props.coleta.data_coleta).split('T')[0],
      quantidade_sementes: props.coleta.quantidade_sementes,
      sementes_reservadas_teste: props.coleta.sementes_reservadas_teste || 0,
      horas_campo: props.coleta.horas_campo ?? null,
      observacoes: props.coleta.observacoes || ''
    }
    try {
      refCusto.value = await getCustoCampoReferencia()
    } catch {
      refCusto.value = { valor_hora: 0, premissa_ativa: false }
    }
  }
)

function formatarData(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR')
}

function fecharInterno() {
  emit('fechar')
}

const {
  onModalPointerDown,
  onOverlayPointerDown,
  onOverlayPointerUp,
  cancelarFechamentoOverlay,
  resetOverlayPress,
} = useModalOverlayClose(fecharInterno)

function fechar() {
  resetOverlayPress()
  fecharInterno()
}

async function salvar() {
  erro.value = ''
  const reserva = Number(form.value.sementes_reservadas_teste) || 0
  if (reserva >= form.value.quantidade_sementes) {
    erro.value = 'Reserva deve ser menor que a quantidade coletada.'
    return
  }
  salvando.value = true
  try {
    await store.atualizarColeta(props.coleta.id, {
      data_coleta: form.value.data_coleta,
      quantidade_sementes: form.value.quantidade_sementes,
      sementes_reservadas_teste: reserva,
      horas_campo: form.value.horas_campo > 0 ? form.value.horas_campo : null,
      observacoes: form.value.observacoes || null
    })
    emit('salvo')
    fechar()
  } catch (e) {
    erro.value = e.response?.data?.detail || e.message || 'Erro ao salvar'
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1500;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.modal-card {
  background: var(--color-surface);
  border-radius: 12px;
  width: 100%;
  max-width: 440px;
  max-height: 90vh;
  overflow: auto;
}
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
}
.modal-body {
  padding: 1.25rem;
}
.info {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.875rem;
  font-size: 0.875rem;
  font-weight: 600;
}
.field input,
.field textarea {
  font-weight: 400;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}
.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.hint {
  font-weight: 400;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.erro {
  color: var(--color-error);
  font-size: 0.875rem;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}
.btn-sec,
.btn-prim {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}
.btn-sec {
  background: var(--color-surface-muted);
}
.btn-prim {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-weight: 600;
}
</style>
