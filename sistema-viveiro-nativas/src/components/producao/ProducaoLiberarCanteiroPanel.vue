<template>
  <div class="panel">
    <header class="panel-intro">
      <h2 class="panel-title">Liberar p/ canteiro</h2>
      <p class="panel-lead">
        Marque plântulas que já germinaram e estão prontas para sair da sementeira.
        Depois use <strong>Transferir p/ canteiro</strong>.
      </p>
    </header>

    <div v-if="!podeOperar" class="alert alert-error">
      Seu perfil só permite visualização.
    </div>

    <div class="stage-header">
      <button
        type="button"
        class="btn btn-primary"
        :disabled="!podeOperar || !sel.length || processando"
        @click="liberar"
      >
        Marcar {{ sel.length || 0 }} como apta(s) p/ transferência
      </button>
    </div>

    <div class="toolbar">
      <label class="field field--sm">
        Sementeira
        <select v-model="filtroCanteiro" @change="carregar">
          <option value="">Todas</option>
          <option v-for="c in sementeiras" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
      </label>
      <label class="field field--sm">
        Espécie
        <select v-model="filtroEsp" @change="carregar">
          <option value="">Todas</option>
          <option v-for="e in especies" :key="e.id" :value="e.id">
            {{ e.nome_popular || e.nome_cientifico }}
          </option>
        </select>
      </label>
    </div>

    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-check">
              <input
                type="checkbox"
                :checked="todos"
                :disabled="!podeOperar || !lista.length"
                @change="toggleTodos"
              />
            </th>
            <th>Código</th>
            <th>Espécie</th>
            <th>Sementeira</th>
            <th>Plantio</th>
            <th>Dias</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!carregando && !lista.length">
            <td colspan="6" class="empty-cell">Nenhuma plântula em desenvolvimento.</td>
          </tr>
          <tr v-for="p in lista" :key="p.id">
            <td>
              <input v-model="sel" type="checkbox" :value="p.id" :disabled="!podeOperar" />
            </td>
            <td><code>{{ p.codigo_rastreio }}</code></td>
            <td>{{ p.especie_nome }}</td>
            <td>{{ p.nome_canteiro }}</td>
            <td>{{ formatarData(p.data_plantio) }}</td>
            <td>{{ diasDesde(p.data_plantio) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="erro" class="alert alert-error">{{ erro }}</p>
    <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listCanteiros } from '@/services/canteiros'
import { listEspecies } from '@/services/especies'
import { listEmDesenvolvimentoSementeira, atualizarEstagioProducao } from '@/services/plantas'
import { usePermissions } from '@/composables/usePermissions'

const emit = defineEmits(['atualizado'])
const { can } = usePermissions()
const podeOperar = computed(() => can('producao.transfer'))

const lista = ref([])
const sementeiras = ref([])
const especies = ref([])
const sel = ref([])
const filtroCanteiro = ref('')
const filtroEsp = ref('')
const carregando = ref(false)
const processando = ref(false)
const erro = ref('')
const sucesso = ref('')

const todos = computed(() => lista.value.length > 0 && sel.value.length === lista.value.length)

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const params = {}
    if (filtroCanteiro.value) params.id_canteiro = Number(filtroCanteiro.value)
    if (filtroEsp.value) params.id_especie = Number(filtroEsp.value)
    lista.value = await listEmDesenvolvimentoSementeira(params)
    sel.value = []
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar.'
    lista.value = []
  } finally {
    carregando.value = false
  }
}

onMounted(async () => {
  const [cant, esp] = await Promise.all([listCanteiros({ ativo: true }), listEspecies()])
  sementeiras.value = cant.filter((c) => c.tipo_local === 'sementeira')
  especies.value = esp
  await carregar()
})

defineExpose({ carregar })

function toggleTodos(e) {
  sel.value = e.target.checked ? lista.value.map((p) => p.id) : []
}

async function liberar() {
  processando.value = true
  erro.value = ''
  sucesso.value = ''
  try {
    const res = await atualizarEstagioProducao({
      ids_plantas: sel.value.map(Number),
      estagio_producao: 'apta_transferencia',
    })
    sucesso.value = `${res.atualizadas} planta(s) apta(s) para ir ao canteiro.`
    await carregar()
    emit('atualizado')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao liberar.'
  } finally {
    processando.value = false
  }
}

function formatarData(d) {
  if (!d) return '—'
  return new Date(String(d).includes('T') ? d : `${d}T12:00:00`).toLocaleDateString('pt-BR')
}

function diasDesde(d) {
  if (!d) return '—'
  const dt = new Date(String(d).includes('T') ? d : `${d}T12:00:00`)
  const dias = Math.floor((Date.now() - dt.getTime()) / 86400000)
  return dias >= 0 ? `${dias}d` : '—'
}
</script>

<style scoped>
@import './producao-panel-shared.css';
</style>
