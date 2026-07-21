<template>
  <AppModalOverlay
    :aberto="aberto"
    :handlers="modalClose"
    panel-class="app-modal-panel--wide"
  >
      <header class="modal-header">
        <h2>Registrar semeadura (produção)</h2>
        <button type="button" class="btn-fechar" @click="fechar">×</button>
      </header>
      <form class="modal-body" @submit.prevent="salvar">
        <p class="info">
          Lote <strong>{{ lote?.codigo_lote }}</strong> —
          {{ lote?.quantidade_disponivel }} sementes disponíveis
        </p>
        <p class="rastreio">
          Origem: matriz {{ lote?.matriz_nome }} · coleta {{ formatarData(lote?.data_coleta) }}
        </p>
        <div class="field-row">
          <label class="field">
            Data da semeadura
            <input v-model="form.data_semeadura" type="date" required />
          </label>
          <label class="field">
            Sementes usadas
            <input
              v-model.number="form.quantidade_sementes_usadas"
              type="number"
              min="1"
              :max="lote?.quantidade_disponivel"
              required
            />
          </label>
        </div>
        <label class="field">
          Sementeira
          <select v-model="form.id_canteiro" required>
            <option value="">Selecione a sementeira</option>
            <option v-for="c in canteiros" :key="c.id" :value="c.id">{{ c.nome }}</option>
          </select>
        </label>
        <label class="field">
          Mudas obtidas (opcional)
          <input v-model.number="form.quantidade_mudas_obtidas" type="number" min="0" />
        </label>
        <label class="check">
          <input v-model="form.registrar_plantas" type="checkbox" />
          Criar registros de plantas no viveiro (rastreio automático)
        </label>
        <p v-if="form.registrar_plantas && form.quantidade_sementes_usadas" class="plantas-hint">
          Serão criadas <strong>{{ form.quantidade_sementes_usadas }}</strong> plantas SEMENTE
          (1 por semente usada).
        </p>
        <label class="field">
          Observações
          <textarea v-model="form.observacoes" rows="2" />
        </label>
        <p v-if="erro" class="erro">{{ erro }}</p>
        <footer class="modal-footer">
          <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
          <button type="submit" class="btn-prim" :disabled="salvando">Registrar</button>
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
import { ref, watch, onMounted, nextTick } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { useFormDirty } from '@/utils/formDirty'
import { listCanteiros } from '@/services/canteiros'
import { createSemeadura } from '@/services/semeaduras'
import { useColetaStore } from '@/store/coleta'
import { useGlobalLoading } from '@/composables/useGlobalLoading'

const props = defineProps({
  aberto: Boolean,
  lote: { type: Object, default: null }
})
const emit = defineEmits(['fechar', 'salvo'])

const store = useColetaStore()
const { runWithLoading } = useGlobalLoading()
const canteiros = ref([])
const salvando = ref(false)
const erro = ref('')
const form = ref({
  data_semeadura: new Date().toISOString().split('T')[0],
  quantidade_sementes_usadas: null,
  id_canteiro: '',
  quantidade_mudas_obtidas: null,
  registrar_plantas: true,
  observacoes: ''
})

const { isDirty, rebase } = useFormDirty(form, () => props.aberto)

onMounted(async () => {
  try {
    canteiros.value = await listCanteiros({ ativo: true, tipo_local: 'sementeira' })
  } catch {
    canteiros.value = []
  }
})

watch(
  () => props.aberto,
  async (v) => {
    if (!v) return
    erro.value = ''
    form.value.quantidade_sementes_usadas = props.lote?.quantidade_disponivel || null
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
  if (!props.lote) return
  erro.value = ''
  salvando.value = true
  try {
    await runWithLoading(async () => {
      const payload = {
        id_lote_sementes: props.lote.id,
        data_semeadura: form.value.data_semeadura,
        quantidade_sementes_usadas: form.value.quantidade_sementes_usadas,
        id_canteiro: form.value.id_canteiro || null,
        quantidade_mudas_obtidas: form.value.quantidade_mudas_obtidas ?? null,
        observacoes: form.value.observacoes || null,
        registrar_plantas: form.value.registrar_plantas,
        quantidade_plantas_registrar: form.value.registrar_plantas
          ? form.value.quantidade_sementes_usadas
          : null
      }
      const sem = await createSemeadura(payload)
      store.upsertSemeadura(sem)
      await store.recarregarMatriz(props.lote.id_arvore_matriz)
      emit('salvo', sem)
      sairSemConfirmar()
    }, 'Registrando semeadura…')
  } catch (e) {
    erro.value = e.response?.data?.detail || e.message || 'Erro'
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.modal-header {
  display: flex;
  justify-content: space-between;
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
.info,
.rastreio {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
}
.rastreio {
  color: var(--color-text-muted);
  margin-bottom: 1rem;
}
.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}
.field input,
.field select,
.field textarea {
  font-weight: 400;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}
.check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}
.plantas-hint {
  margin: -0.5rem 0 1rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
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
}
.btn-sec {
  background: var(--color-surface-muted);
}
.btn-prim {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-weight: 600;
}
.erro {
  color: var(--color-error);
}
</style>
