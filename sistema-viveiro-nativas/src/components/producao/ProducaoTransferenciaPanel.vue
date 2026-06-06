<template>
  <div class="transfer-panel">
    <header class="panel-intro">
      <h2 class="panel-title">Transferir para o canteiro</h2>
      <p class="panel-lead">
        Transfira apenas plântulas já marcadas como <strong>aptas p/ transferência</strong>.
        Plantas em desenvolvimento precisam ser liberadas antes na aba
        <button type="button" class="link-btn" @click="$emit('ir-estagios')">Liberar estágios</button>.
      </p>
    </header>

    <div v-if="!podeTransferir" class="alert alert-error">
      Seu perfil só permite visualização. Transferências exigem permissão de operação de produção.
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
        <select v-model="filtroEspecie" @change="carregar">
          <option value="">Todas</option>
          <option v-for="e in especies" :key="e.id" :value="e.id">
            {{ e.nome_popular || e.nome_cientifico }}
          </option>
        </select>
      </label>
      <button type="button" class="btn btn-outline btn-sm" @click="carregar">Atualizar</button>
    </div>

    <div class="transfer-bar">
      <label class="field field--sm">
        Canteiro de destino
        <select v-model="idDestino" :disabled="!podeTransferir">
          <option value="">Selecione</option>
          <option v-for="c in canteirosDestino" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
      </label>
      <label class="field field--sm">
        Data germinação
        <input v-model="dataGerminacao" type="date" :disabled="!podeTransferir" />
      </label>
      <button
        type="button"
        class="btn btn-primary"
        :disabled="!podeTransferir || !selecionados.length || !idDestino || transferindo"
        @click="confirmarTransferencia"
      >
        Transferir {{ selecionados.length || 0 }} muda(s)
      </button>
    </div>

    <p v-if="carregando" class="status-msg">Carregando…</p>
    <p v-else-if="erro" class="alert alert-error">{{ erro }}</p>
    <p v-else-if="sucesso" class="alert alert-success">{{ sucesso }}</p>

    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-check">
              <input
                type="checkbox"
                :checked="todosSelecionados"
                :disabled="!podeTransferir || !pendentes.length"
                @change="toggleTodos"
              />
            </th>
            <th>Código</th>
            <th>Espécie</th>
            <th>Matriz</th>
            <th>Lote</th>
            <th>Sementeira</th>
            <th>Plantio</th>
            <th>Dias</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!carregando && !pendentes.length">
            <td colspan="8" class="empty-cell">
              Nenhuma planta apta para transferência.
              <button type="button" class="link-btn" @click="$emit('ir-estagios')">
                Liberar estágios
              </button>
              ou
              <button type="button" class="link-btn" @click="$emit('ir-semeadura')">
                registrar semeadura
              </button>
            </td>
          </tr>
          <tr v-for="p in pendentes" :key="p.id">
            <td>
              <input
                v-model="selecionados"
                type="checkbox"
                :value="p.id"
                :disabled="!podeTransferir"
              />
            </td>
            <td><code>{{ p.codigo_rastreio }}</code></td>
            <td>{{ p.especie_nome }}</td>
            <td>{{ p.matriz_nome || '—' }}</td>
            <td>{{ p.codigo_lote || '—' }}</td>
            <td>{{ p.nome_canteiro }}</td>
            <td>{{ formatarData(p.data_plantio) }}</td>
            <td>{{ diasDesde(p.data_plantio) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <dialog ref="dialogConfirm" class="app-dialog">
      <form class="dialog-panel" @submit.prevent="transferir">
        <header class="dialog-panel__header">
          <h3>Confirmar transferência</h3>
        </header>
        <div class="dialog-panel__body">
          <p>
            Mover <strong>{{ selecionados.length }}</strong> planta(s) para o canteiro selecionado?
          </p>
        </div>
        <footer class="dialog-panel__footer">
          <button type="button" class="btn btn-secondary" @click="fecharDialog">Cancelar</button>
          <button type="submit" class="btn btn-primary">Confirmar</button>
        </footer>
      </form>
    </dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listCanteiros } from '@/services/canteiros'
import { listEspecies } from '@/services/especies'
import { listPendentesTransferencia, promoverMudas } from '@/services/plantas'
import { usePermissions } from '@/composables/usePermissions'

const emit = defineEmits(['atualizado', 'ir-semeadura', 'ir-estagios'])
const { can } = usePermissions()
const podeTransferir = computed(() => can('producao.transfer'))

const pendentes = ref([])
const sementeiras = ref([])
const canteirosDestino = ref([])
const especies = ref([])
const filtroCanteiro = ref('')
const filtroEspecie = ref('')
const selecionados = ref([])
const idDestino = ref('')
const dataGerminacao = ref(new Date().toISOString().split('T')[0])
const transferindo = ref(false)
const carregando = ref(false)
const erro = ref('')
const sucesso = ref('')
const dialogConfirm = ref(null)

const todosSelecionados = computed(
  () => pendentes.value.length > 0 && selecionados.value.length === pendentes.value.length
)

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const params = {}
    if (filtroCanteiro.value) params.id_canteiro = Number(filtroCanteiro.value)
    if (filtroEspecie.value) params.id_especie = Number(filtroEspecie.value)
    pendentes.value = await listPendentesTransferencia(params)
    selecionados.value = []
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar pendências.'
    pendentes.value = []
  } finally {
    carregando.value = false
  }
}

onMounted(async () => {
  try {
    const [cant, esp] = await Promise.all([
      listCanteiros({ ativo: true }),
      listEspecies(),
    ])
    sementeiras.value = cant.filter((c) => c.tipo_local === 'sementeira')
    canteirosDestino.value = cant.filter((c) => c.tipo_local === 'canteiro')
    especies.value = esp
  } catch {
    erro.value = 'Erro ao carregar canteiros ou espécies.'
  }
  await carregar()
})

function toggleTodos(e) {
  selecionados.value = e.target.checked ? pendentes.value.map((p) => p.id) : []
}

function confirmarTransferencia() {
  dialogConfirm.value?.showModal()
}

function fecharDialog() {
  dialogConfirm.value?.close()
}

async function transferir() {
  fecharDialog()
  erro.value = ''
  sucesso.value = ''
  transferindo.value = true
  try {
    const res = await promoverMudas({
      ids_plantas: selecionados.value.map(Number),
      id_canteiro_destino: Number(idDestino.value),
      data_germinacao: dataGerminacao.value || null,
    })
    sucesso.value = `${res.transferidas} muda(s) transferida(s) para o canteiro.`
    await carregar()
    emit('atualizado')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro na transferência.'
  } finally {
    transferindo.value = false
  }
}

function formatarData(d) {
  if (!d) return '—'
  return new Date(d + (String(d).includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR')
}

function diasDesde(d) {
  if (!d) return '—'
  const dt = new Date(String(d).includes('T') ? d : `${d}T12:00:00`)
  const dias = Math.floor((Date.now() - dt.getTime()) / 86400000)
  return dias >= 0 ? `${dias}d` : '—'
}

defineExpose({ carregar })
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

.toolbar,
.transfer-bar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  align-items: flex-end;
  padding: var(--spacing-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-md);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.field select,
.field input {
  padding: 0.45rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 0.875rem;
  min-width: 160px;
}

.table-card {
  overflow-x: auto;
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table th,
.data-table td {
  padding: 0.65rem 0.85rem;
  border-bottom: 1px solid var(--color-border-subtle);
  text-align: left;
}

.data-table th {
  background: var(--color-surface-muted);
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text-secondary);
}

.col-check {
  width: 2.5rem;
}

.empty-cell {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-muted);
}

.link-btn {
  border: none;
  background: none;
  color: var(--color-primary);
  font-weight: 600;
  cursor: pointer;
  margin-left: 0.35rem;
  font-family: inherit;
}

code {
  font-size: 0.8125rem;
  color: var(--color-primary-700);
}
</style>
