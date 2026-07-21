<template>
  <AppModalOverlay
    :aberto="aberto"
    :handlers="modalClose"
    panel-class="app-modal-panel--md"
    aria-labelledby="editar-coleta-title"
  >
      <header class="modal-header">
        <div>
          <p class="modal-eyebrow">Campo · Coleta</p>
          <h2 id="editar-coleta-title">Editar coleta</h2>
        </div>
        <button type="button" class="btn-fechar" @click="fechar">×</button>
      </header>

      <form class="modal-body" @submit.prevent="salvar">
        <section class="form-secao">
          <h3 class="form-secao__title">Origem</h3>
          <div class="matriz-resumo">
            <div class="matriz-resumo__item">
              <span>Matriz</span>
              <strong>{{ coleta?.matriz_nome || '—' }}</strong>
            </div>
            <div class="matriz-resumo__item">
              <span>Data original</span>
              <strong>{{ formatarData(coleta?.data_coleta) }}</strong>
            </div>
            <div v-if="lotesColeta.length" class="matriz-resumo__item">
              <span>Lote(s)</span>
              <strong class="mono">{{ lotesColeta.map((l) => l.codigo_lote).join(', ') }}</strong>
            </div>
          </div>
        </section>

        <section class="form-secao">
          <h3 class="form-secao__title">Dados da coleta</h3>
          <div class="field-row">
            <label class="field">
              Data da coleta
              <input v-model="form.data_coleta" type="date" required />
            </label>
            <label class="field">
              Quantidade coletada (total)
              <input v-model.number="form.quantidade_sementes" type="number" min="1" step="1" required />
            </label>
          </div>

          <label class="field">
            Sementes reservadas para teste de germinação
            <input v-model.number="form.sementes_reservadas_teste" type="number" min="0" step="1" />
            <small v-if="qtdLote > 0" class="field-hint">
              Entram no lote (armazém): <strong>{{ qtdLote.toLocaleString('pt-BR') }}</strong> sementes
            </small>
          </label>

          <label class="field">
            Horas em campo
            <input
              v-model.number="form.horas_campo"
              type="number"
              min="0"
              step="0.25"
              placeholder="Ex.: 4"
            />
            <small class="field-hint">Tempo total da equipe: deslocamento, coleta, beneficiamento e retorno.</small>
          </label>

          <label class="field">
            Observações de campo
            <textarea v-model="form.observacoes" rows="3" placeholder="Clima, acesso, maturidade dos frutos..." />
          </label>
        </section>

        <p v-if="erro" class="erro">{{ erro }}</p>

        <footer class="modal-footer">
          <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
          <button type="submit" class="btn-prim" :disabled="salvando">
            {{ salvando ? 'Salvando…' : 'Salvar alterações' }}
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
import { useColetaStore } from '@/store/coleta'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { useFormDirty } from '@/utils/formDirty'

const props = defineProps({
  aberto: Boolean,
  coleta: { type: Object, default: null }
})
const emit = defineEmits(['fechar', 'salvo'])

const store = useColetaStore()
const salvando = ref(false)
const erro = ref('')
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

const lotesColeta = computed(() => props.coleta?.lotes || [])

const { isDirty, rebase } = useFormDirty(form, () => props.aberto)

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
    await nextTick()
    rebase()
  }
)

function formatarData(d) {
  if (!d) return '—'
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR')
}

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
  erro.value = ''
  const reserva = Number(form.value.sementes_reservadas_teste) || 0
  if (reserva >= form.value.quantidade_sementes) {
    erro.value = 'A reserva para teste deve ser menor que a quantidade coletada.'
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
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.modal-eyebrow {
  margin: 0 0 0.2rem;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.btn-fechar {
  border: none;
  background: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-muted);
  line-height: 1;
}

.modal-body {
  padding: 1.25rem 1.5rem 1.5rem;
}

.form-secao {
  margin-bottom: 1.25rem;
}

.form-secao__title {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-secondary);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.875rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.field input,
.field textarea {
  font-weight: 400;
  padding: 0.6rem 0.75rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

.field-hint {
  font-size: 0.8125rem;
  font-weight: 400;
  color: var(--color-text-muted);
  margin-top: 0.15rem;
}

.field-hint strong {
  color: var(--color-primary-700);
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.matriz-resumo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.65rem;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary-100);
}

.matriz-resumo__item span {
  display: block;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  margin-bottom: 0.15rem;
}

.matriz-resumo__item strong {
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.matriz-resumo__item .mono {
  font-family: var(--font-mono, monospace);
  font-size: 0.8125rem;
}

.erro {
  color: var(--color-error-dark);
  font-size: 0.875rem;
  background: var(--color-error-bg);
  padding: 0.6rem 0.75rem;
  border-radius: var(--radius-md);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.btn-sec,
.btn-prim {
  padding: 0.65rem 1.1rem;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
}

.btn-sec {
  background: var(--color-surface-muted);
  color: var(--color-text-secondary);
}

.btn-prim {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-prim:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 520px) {
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
