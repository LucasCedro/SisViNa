<template>
  <div class="semeadura-panel">
    <header class="panel-intro">
      <h2 class="panel-title">Transferir p/ sementeira</h2>
      <p class="panel-lead">
        Indique que sementes de um lote foram para a sementeira. Marque
        <strong>criar plantas</strong> para gerar registros rastreáveis (status SEMENTE).
      </p>
    </header>

    <form class="form-card" @submit.prevent="salvar">
      <label class="field">
        Lote de sementes
        <select v-model.number="form.id_lote_sementes" required @change="aoTrocarLote">
          <option :value="null" disabled>Selecione o lote</option>
          <option v-for="l in lotesDisponiveis" :key="l.id" :value="l.id">
            {{ l.codigo_lote }} — {{ l.especie_nome }} ({{ l.quantidade_disponivel }} disp.)
          </option>
        </select>
      </label>

      <p v-if="loteSelecionado" class="lote-info">
        Matriz: {{ loteSelecionado.matriz_nome || '—' }} ·
        Disponível: {{ loteSelecionado.quantidade_disponivel }}
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
            :max="loteSelecionado?.quantidade_disponivel"
            required
          />
        </label>
      </div>

      <label class="field">
        Sementeira (local)
        <select v-model.number="form.id_canteiro" required>
          <option :value="null" disabled>Selecione</option>
          <option v-for="c in sementeiras" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
      </label>

      <label class="check">
        <input v-model="form.registrar_plantas" type="checkbox" />
        Criar registros de plantas (recomendado — habilita transferência para canteiro)
      </label>

      <label v-if="form.registrar_plantas" class="field">
        Quantidade de plantas a registrar
        <input
          v-model.number="form.quantidade_plantas_registrar"
          type="number"
          min="1"
          :max="form.quantidade_sementes_usadas || 500"
          required
        />
      </label>

      <label class="field">
        Observações
        <textarea v-model="form.observacoes" rows="2" placeholder="Bandeja, recipiente, etc." />
      </label>

      <p v-if="erro" class="alert alert-error">{{ erro }}</p>
      <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="salvando || !podeSemear">
          Registrar semeadura
        </button>
      </div>
    </form>

    <p v-if="!lotesDisponiveis.length && !carregandoLotes" class="empty-hint">
      Nenhum lote com sementes disponíveis.
      <router-link to="/coleta">Cadastre coleta e lote</router-link>
      ou
      <router-link to="/estoques">entrada no armazém</router-link>.
    </p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listLotesSementes } from '@/services/lotesSementes'
import { listCanteiros } from '@/services/canteiros'
import { createSemeadura } from '@/services/semeaduras'
import { usePermissions } from '@/composables/usePermissions'

const emit = defineEmits(['atualizado'])
const { can } = usePermissions()

const lotes = ref([])
const sementeiras = ref([])
const carregandoLotes = ref(true)
const salvando = ref(false)
const erro = ref('')
const sucesso = ref('')

const form = ref({
  id_lote_sementes: null,
  data_semeadura: new Date().toISOString().split('T')[0],
  quantidade_sementes_usadas: null,
  id_canteiro: null,
  registrar_plantas: true,
  quantidade_plantas_registrar: null,
  observacoes: '',
})

const podeSemear = computed(() => can('producao.transfer'))

const lotesDisponiveis = computed(() =>
  lotes.value.filter((l) => l.status === 'ativo' && (l.quantidade_disponivel || 0) > 0)
)

const loteSelecionado = computed(() =>
  lotesDisponiveis.value.find((l) => l.id === form.value.id_lote_sementes)
)

function aoTrocarLote() {
  const l = loteSelecionado.value
  if (!l) return
  form.value.quantidade_sementes_usadas = l.quantidade_disponivel
  form.value.quantidade_plantas_registrar = l.quantidade_disponivel
}

onMounted(async () => {
  try {
    const [lot, cant] = await Promise.all([
      listLotesSementes({ limit: 200 }),
      listCanteiros({ ativo: true, tipo_local: 'sementeira' }),
    ])
    lotes.value = lot
    sementeiras.value = cant.length ? cant : (await listCanteiros({ ativo: true })).filter((c) => c.tipo_local === 'sementeira')
  } finally {
    carregandoLotes.value = false
  }
})

async function salvar() {
  if (!podeSemear.value) return
  erro.value = ''
  sucesso.value = ''
  salvando.value = true
  try {
    await createSemeadura({
      id_lote_sementes: form.value.id_lote_sementes,
      data_semeadura: form.value.data_semeadura,
      quantidade_sementes_usadas: form.value.quantidade_sementes_usadas,
      id_canteiro: form.value.id_canteiro,
      registrar_plantas: form.value.registrar_plantas,
      quantidade_plantas_registrar: form.value.registrar_plantas
        ? form.value.quantidade_plantas_registrar
        : null,
      observacoes: form.value.observacoes || null,
    })
    sucesso.value = 'Semeadura registrada. Plantas SEMENTE criadas na sementeira.'
    lotes.value = await listLotesSementes({ limit: 200 })
    form.value.id_lote_sementes = null
    emit('atualizado')
  } catch (e) {
    const detail = e.response?.data?.detail
    erro.value =
      (typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map((d) => d.msg || d).join(' · ') : null) ||
      (e.message?.includes('Network Error') ? 'Falha de conexão com a API. Verifique se o backend está no ar.' : null) ||
      'Erro ao registrar semeadura.'
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.panel-intro {
  margin-bottom: var(--spacing-md);
}

.panel-title {
  margin: 0 0 0.35rem;
  font-size: 1.125rem;
  font-weight: 600;
}

.panel-lead {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.45;
}

.form-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  max-width: 560px;
}

.field-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8125rem;
  font-weight: 500;
  flex: 1;
  min-width: 140px;
}

.field select,
.field input,
.field textarea {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 0.875rem;
}

.check {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.lote-info {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.form-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-hint {
  margin-top: var(--spacing-md);
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.empty-hint a {
  color: var(--color-primary);
  font-weight: 600;
}
</style>
