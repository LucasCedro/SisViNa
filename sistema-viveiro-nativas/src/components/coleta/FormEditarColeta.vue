<template>
  <div v-if="aberto" class="modal-overlay" @click.self="fechar">
    <div class="modal-card" role="dialog">
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
        <label class="field">
          Quantidade de sementes
          <input v-model.number="form.quantidade_sementes" type="number" min="1" required />
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
import { ref, watch } from 'vue'
import { useColetaStore } from '@/store/coleta'

const props = defineProps({
  aberto: Boolean,
  coleta: { type: Object, default: null }
})
const emit = defineEmits(['fechar', 'salvo'])

const store = useColetaStore()
const salvando = ref(false)
const erro = ref('')
const form = ref({ data_coleta: '', quantidade_sementes: null, observacoes: '' })

watch(
  () => [props.aberto, props.coleta],
  ([aberto]) => {
    if (!aberto || !props.coleta) return
    erro.value = ''
    form.value = {
      data_coleta: String(props.coleta.data_coleta).split('T')[0],
      quantidade_sementes: props.coleta.quantidade_sementes,
      observacoes: props.coleta.observacoes || ''
    }
  }
)

function formatarData(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString('pt-BR')
}

function fechar() {
  emit('fechar')
}

async function salvar() {
  erro.value = ''
  salvando.value = true
  try {
    await store.atualizarColeta(props.coleta.id, {
      data_coleta: form.value.data_coleta,
      quantidade_sementes: form.value.quantidade_sementes,
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
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
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
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 1rem;
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
.field textarea {
  font-weight: 400;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
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
  background: #f3f4f6;
}
.btn-prim {
  background: #6ca234;
  color: #fff;
  font-weight: 600;
}
.erro {
  color: #b91c1c;
  font-size: 0.875rem;
}
</style>
