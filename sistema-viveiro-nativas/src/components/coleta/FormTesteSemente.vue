<template>
  <div v-if="aberto" class="modal-overlay" @click.self="fechar">
    <div class="modal-card" role="dialog">
      <header class="modal-header">
        <h2>Teste de qualidade</h2>
        <button type="button" class="btn-fechar" @click="fechar">×</button>
      </header>
      <form class="modal-body" @submit.prevent="salvar">
        <p class="info">Lote <strong>{{ lote?.codigo_lote }}</strong></p>
        <div class="field-row">
          <label class="field">
            Data do teste
            <input v-model="form.data_teste" type="date" required />
          </label>
          <label class="field">
            Tipo
            <select v-model="form.tipo_teste" required>
              <option v-for="t in TIPOS_TESTE" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </label>
        </div>
        <label class="field">
          Resultado (%)
          <input v-model.number="form.percentual_resultado" type="number" min="0" max="100" step="0.1" required />
        </label>
        <div class="field-row">
          <label class="field">
            Repetições
            <input v-model.number="form.repeticoes" type="number" min="1" />
          </label>
          <label class="field">
            Sementes avaliadas
            <input v-model.number="form.sementes_avaliadas" type="number" min="1" />
          </label>
        </div>
        <label class="field">
          Metodologia
          <textarea v-model="form.metodologia" rows="2" placeholder="Ex.: Germinador, substrato, temperatura..." />
        </label>
        <label class="field">
          Observações
          <textarea v-model="form.observacoes" rows="2" />
        </label>
        <p v-if="form.tipo_teste === 'germinacao'" class="dica">
          Testes de germinação atualizam o resumo na matriz.
        </p>
        <p v-if="erro" class="erro">{{ erro }}</p>
        <footer class="modal-footer">
          <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
          <button type="submit" class="btn-prim" :disabled="salvando">Registrar teste</button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { TIPOS_TESTE } from '@/constants/coletaDominio'
import { createTesteSementes } from '@/services/testesSementes'
import { useColetaStore } from '@/store/coleta'

const props = defineProps({
  aberto: Boolean,
  lote: { type: Object, default: null }
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
  sementes_avaliadas: null,
  metodologia: '',
  observacoes: ''
})

watch(
  () => props.aberto,
  (v) => {
    if (!v) return
    erro.value = ''
    form.value.data_teste = new Date().toISOString().split('T')[0]
  }
)

function fechar() {
  emit('fechar')
}

async function salvar() {
  if (!props.lote) return
  erro.value = ''
  salvando.value = true
  try {
    const teste = await createTesteSementes({
      id_lote_sementes: props.lote.id,
      ...form.value
    })
    store.upsertTeste(teste)
    await store.recarregarMatriz(props.lote.id_arvore_matriz)
    emit('salvo', teste)
    fechar()
  } catch (e) {
    erro.value = e.response?.data?.detail || e.message || 'Erro'
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
  max-width: 480px;
  max-height: 90vh;
  overflow: auto;
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
  margin: 0 0 1rem;
  font-size: 0.875rem;
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
  border: 1px solid #d1d5db;
  border-radius: 6px;
}
.dica {
  font-size: 0.8125rem;
  color: #6b7280;
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
}
</style>
