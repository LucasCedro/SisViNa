<template>
  <div v-if="aberto" class="modal-overlay" @click.self="fechar">
    <div class="modal-card" role="dialog">
      <header class="modal-header">
        <h2>Cadastrar coleta</h2>
        <button type="button" class="btn-fechar" @click="fechar">×</button>
      </header>

      <form class="modal-body" @submit.prevent="salvar">
        <label class="field">
          Árvore matriz
          <select v-model="form.id_arvore_matriz" required :disabled="Boolean(matriz?.id)">
            <option value="">Selecione...</option>
            <option v-for="m in matrizesOpcoes" :key="m.id" :value="m.id">
              {{ m.nome }} — {{ m.especie_nome || 'Espécie' }}
            </option>
          </select>
        </label>

        <div class="field-row">
          <label class="field">
            Data da coleta
            <input v-model="form.data_coleta" type="date" required />
          </label>
          <label class="field">
            Quantidade de sementes
            <input v-model.number="form.quantidade_sementes" type="number" min="1" required />
          </label>
        </div>

        <p v-if="auth.user" class="funcionario-info">
          Registrado por: <strong>{{ auth.user.nome }}</strong>
        </p>

        <label class="check">
          <input v-model="form.gerar_lote" type="checkbox" />
          Gerar lote de sementes automaticamente (código rastreável)
        </label>

        <label class="field">
          Observações
          <textarea v-model="form.observacoes" rows="3" placeholder="Condições, clima, acesso..." />
        </label>

        <p v-if="erro" class="erro">{{ erro }}</p>

        <footer class="modal-footer">
          <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
          <button type="submit" class="btn-prim" :disabled="salvando">
            {{ salvando ? 'Salvando...' : 'Registrar coleta' }}
          </button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useColetaStore } from '@/store/coleta'
import { useAuthStore } from '@/store/auth'

const props = defineProps({
  aberto: { type: Boolean, default: false },
  matriz: { type: Object, default: null }
})

const emit = defineEmits(['fechar', 'salvo'])

const store = useColetaStore()
const auth = useAuthStore()
const salvando = ref(false)
const erro = ref('')

const matrizesOpcoes = computed(() =>
  [...store.arvoresMatriz].sort((a, b) => (a.nome || '').localeCompare(b.nome || ''))
)

const formPadrao = () => ({
  id_arvore_matriz: '',
  data_coleta: new Date().toISOString().split('T')[0],
  quantidade_sementes: null,
  observacoes: '',
  gerar_lote: true
})

const form = ref(formPadrao())

watch(
  () => [props.aberto, props.matriz],
  ([aberto]) => {
    if (!aberto) return
    erro.value = ''
    form.value = formPadrao()
    if (props.matriz?.id) {
      form.value.id_arvore_matriz = props.matriz.id
    }
  }
)

function fechar() {
  emit('fechar')
}

async function salvar() {
  erro.value = ''
  if (!form.value.id_arvore_matriz) {
    erro.value = 'Selecione a matriz.'
    return
  }
  if (!form.value.quantidade_sementes || form.value.quantidade_sementes < 1) {
    erro.value = 'Informe a quantidade de sementes (mínimo 1).'
    return
  }
  salvando.value = true
  try {
    const resultado = await store.registrarColeta({
      id_arvore_matriz: Number(form.value.id_arvore_matriz),
      data_coleta: form.value.data_coleta,
      quantidade_sementes: form.value.quantidade_sementes,
      observacoes: form.value.observacoes || null,
      gerar_lote: form.value.gerar_lote
    })
    emit('salvo', resultado)
    fechar()
  } catch (e) {
    const detail = e.response?.data?.detail
    erro.value = Array.isArray(detail)
      ? detail.map((d) => d.msg || d).join(', ')
      : detail || e.message || 'Erro ao registrar coleta'
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
  max-height: 92vh;
  overflow: auto;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  color: #6b7280;
}

.modal-body {
  padding: 1.25rem;
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
  padding: 0.5rem 0.65rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.funcionario-info {
  font-size: 0.8125rem;
  color: #6b7280;
  margin: 0 0 1rem;
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
  background: #f3f4f6;
}

.btn-prim {
  background: #6ca234;
  color: #fff;
  font-weight: 600;
}

.btn-prim:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.erro {
  color: #b91c1c;
  font-size: 0.875rem;
}
</style>
