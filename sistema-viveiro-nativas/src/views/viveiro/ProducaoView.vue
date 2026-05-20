<template>
  <div class="producao-view">
    <div class="content-wrapper">
      <h1 class="titulo-pagina">Produção — Sementeira → Canteiro</h1>
      <p class="subtitulo">
        Registre quando as sementes plantadas germinaram e devem sair da sementeira para o canteiro.
        O rastreio por lote e matriz é mantido na transferência.
      </p>

      <div class="painel-filtros">
        <label class="field">
          Sementeira
          <select v-model="filtroCanteiro" @change="carregar">
            <option value="">Todas</option>
            <option v-for="c in sementeiras" :key="c.id" :value="c.id">{{ c.nome }}</option>
          </select>
        </label>
        <label class="field">
          Espécie
          <select v-model="filtroEspecie" @change="carregar">
            <option value="">Todas</option>
            <option v-for="e in especies" :key="e.id" :value="e.id">
              {{ e.nome_popular || e.nome_cientifico }}
            </option>
          </select>
        </label>
        <button type="button" class="btn-sec" @click="carregar">Atualizar</button>
      </div>

      <div class="painel-transferencia">
        <label class="field">
          Canteiro de destino (mudas)
          <select v-model="idDestino" required>
            <option value="">Selecione o canteiro</option>
            <option v-for="c in canteirosDestino" :key="c.id" :value="c.id">{{ c.nome }}</option>
          </select>
        </label>
        <label class="field">
          Data da germinação
          <input v-model="dataGerminacao" type="date" />
        </label>
        <button
          type="button"
          class="btn-prim"
          :disabled="!selecionados.length || !idDestino || transferindo"
          @click="transferir"
        >
          Transferir {{ selecionados.length }} para canteiro
        </button>
      </div>

      <div v-if="erro" class="erro">{{ erro }}</div>
      <div v-if="sucesso" class="sucesso">{{ sucesso }}</div>

      <div class="tabela-wrap">
        <table class="tabela">
          <thead>
            <tr>
              <th><input type="checkbox" :checked="todosSelecionados" @change="toggleTodos" /></th>
              <th>Código</th>
              <th>Espécie</th>
              <th>Lote</th>
              <th>Sementeira</th>
              <th>Plantio</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!pendentes.length">
              <td colspan="6" class="vazio">Nenhuma semente aguardando transferência na sementeira.</td>
            </tr>
            <tr v-for="p in pendentes" :key="p.id">
              <td>
                <input v-model="selecionados" type="checkbox" :value="p.id" />
              </td>
              <td>{{ p.codigo_rastreio }}</td>
              <td>{{ p.especie_nome }}</td>
              <td>{{ p.codigo_lote || '—' }}</td>
              <td>{{ p.nome_canteiro }}</td>
              <td>{{ formatarData(p.data_plantio) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listCanteiros } from '@/services/canteiros'
import { listEspecies } from '@/services/especies'
import { listPendentesTransferencia, promoverMudas } from '@/services/plantas'

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
const erro = ref('')
const sucesso = ref('')

const todosSelecionados = computed(
  () => pendentes.value.length > 0 && selecionados.value.length === pendentes.value.length
)

async function carregar() {
  erro.value = ''
  const params = {}
  if (filtroCanteiro.value) params.id_canteiro = Number(filtroCanteiro.value)
  if (filtroEspecie.value) params.id_especie = Number(filtroEspecie.value)
  pendentes.value = await listPendentesTransferencia(params)
  selecionados.value = []
}

onMounted(async () => {
  const [cant, esp] = await Promise.all([
    listCanteiros({ ativo: true }),
    listEspecies()
  ])
  sementeiras.value = cant.filter((c) => c.tipo_local === 'sementeira')
  canteirosDestino.value = cant.filter((c) => c.tipo_local === 'canteiro')
  especies.value = esp
  await carregar()
})

function toggleTodos(e) {
  selecionados.value = e.target.checked ? pendentes.value.map((p) => p.id) : []
}

async function transferir() {
  erro.value = ''
  sucesso.value = ''
  transferindo.value = true
  try {
    const res = await promoverMudas({
      ids_plantas: selecionados.value.map(Number),
      id_canteiro_destino: Number(idDestino.value),
      data_germinacao: dataGerminacao.value || null
    })
    sucesso.value = `${res.transferidas} planta(s) transferida(s) para o canteiro.`
    await carregar()
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
</script>

<style scoped>
.producao-view {
  width: 100%;
  height: 100%;
}
.content-wrapper {
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}
.titulo-pagina {
  font-size: 1.75rem;
  font-weight: 700;
}
.subtitulo {
  color: var(--color-text-secondary);
  margin-top: -0.5rem;
}
.painel-filtros,
.painel-transferencia {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  background: var(--color-surface);
  padding: 1rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}
.field select,
.field input {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-width: 180px;
}
.btn-prim {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 600;
}
.btn-prim:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-sec {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  background: white;
  border-radius: var(--radius-sm);
  cursor: pointer;
}
.tabela-wrap {
  overflow-x: auto;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}
.tabela {
  width: 100%;
  border-collapse: collapse;
}
.tabela th,
.tabela td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.tabela th {
  background: #f8f9fa;
}
.vazio {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 2rem;
}
.erro {
  color: #c0392b;
}
.sucesso {
  color: #27ae60;
}
</style>
