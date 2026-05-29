<template>
  <div class="graficos-container">
    <div class="card">
      <div class="card-head">
        <h3 class="card-title">{{ tituloGraficoSementes }}</h3>
        <div class="toggle-group">
          <button
            type="button"
            :class="{ ativo: modoSementes === 'especie' }"
            @click="modoSementes = 'especie'"
          >
            Por espécie
          </button>
          <button
            type="button"
            :class="{ ativo: modoSementes === 'matriz' }"
            @click="modoSementes = 'matriz'"
          >
            Por matriz
          </button>
        </div>
      </div>
      <div v-if="semDados" class="sem-dados">Nenhuma matriz no filtro atual.</div>
      <div v-else class="chart-container">
        <Bar :data="sementesChartData" :options="chartOptionsComScroll" />
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <h3 class="card-title">Taxa de germinação</h3>
      </div>
      <div v-if="semDados" class="sem-dados">Nenhuma matriz no filtro atual.</div>
      <div v-else-if="semGerminacao" class="sem-dados">
        Preencha «Taxa de germinação» ao cadastrar/editar a matriz.
      </div>
      <div v-else class="chart-container">
        <Line :data="germinacaoData" :options="chartOptionsComScroll" />
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <h3 class="card-title">Evolução da coleta</h3>
        <div class="head-acoes">
          <div class="toggle-group">
            <button
              type="button"
              :class="{ ativo: modoEvolucao === 'especie' }"
              @click="modoEvolucao = 'especie'"
            >
              Por espécie
            </button>
            <button
              type="button"
              :class="{ ativo: modoEvolucao === 'matriz' }"
              @click="modoEvolucao = 'matriz'"
            >
              Por matriz
            </button>
          </div>
          <button
            v-if="!semEvolucao"
            type="button"
            class="btn-filtro"
            @click="abrirModalFiltro"
          >
            Filtrar
            <span class="badge">{{ selecaoEvolucao.length }}/{{ itensFiltroEvolucao.length }}</span>
          </button>
        </div>
      </div>

      <div v-if="semEvolucao" class="sem-dados">
        Registre coletas em «Cadastrar coleta» para ver a evolução ao longo do tempo.
      </div>
      <div v-else-if="selecaoEvolucao.length === 0" class="sem-dados">
        Selecione ao menos uma {{ modoEvolucao === 'especie' ? 'espécie' : 'matriz' }} em «Filtrar».
      </div>
      <div v-else class="chart-container">
        <Line :data="evolucaoData" :options="chartOptionsBase" />
      </div>
    </div>

    <div v-if="modalFiltroAberto" class="modal-overlay" @click.self="fecharModalFiltro">
      <div class="modal-filtro" role="dialog" aria-labelledby="titulo-filtro-evolucao">
        <header class="modal-filtro-header">
          <h2 id="titulo-filtro-evolucao">
            Filtrar evolução — {{ modoEvolucao === 'especie' ? 'espécies' : 'matrizes' }}
          </h2>
          <button type="button" class="btn-fechar" aria-label="Fechar" @click="fecharModalFiltro">×</button>
        </header>

        <div class="modal-filtro-body">
          <input
            v-model="buscaFiltro"
            type="search"
            class="busca-filtro"
            placeholder="Buscar por nome..."
          />

          <div class="modal-filtro-acoes">
            <button type="button" class="link-btn" @click="selecionarTodasRascunho">Selecionar todas</button>
            <button type="button" class="link-btn" @click="limparRascunho">Limpar</button>
          </div>

          <ul class="lista-filtro">
            <li v-for="item in itensFiltroModal" :key="item.id">
              <label>
                <input v-model="selecaoRascunho" type="checkbox" :value="item.id" />
                <span>{{ item.nome }}</span>
              </label>
            </li>
            <li v-if="itensFiltroModal.length === 0" class="lista-vazia">
              Nenhum resultado para «{{ buscaFiltro }}».
            </li>
          </ul>
        </div>

        <footer class="modal-filtro-footer">
          <button type="button" class="btn-sec" @click="fecharModalFiltro">Cancelar</button>
          <button type="button" class="btn-prim" @click="aplicarFiltro">Aplicar</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { nomePopularExibicao } from '@/utils/especiesDisplay'
import { useColetaStore } from '@/store/coleta'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

import { CHART_PALETTE, CHART_PRIMARY, CHART_PRIMARY_DARK, CHART_INFO, withAlpha } from '../../constants/chartColors'

const CORES = CHART_PALETTE
const store = useColetaStore()
const modoSementes = ref('especie')
const modoEvolucao = ref('especie')
const selecaoEvolucao = ref([])
const modalFiltroAberto = ref(false)
const selecaoRascunho = ref([])
const buscaFiltro = ref('')

const lista = computed(() => store.matrizesFiltradas)
const coletas = computed(() => store.coletasFiltradas)

const semDados = computed(() => lista.value.length === 0)

const semGerminacao = computed(
  () => !lista.value.some((a) => a.taxa_germinacao != null && a.taxa_germinacao !== '')
)

const semEvolucao = computed(() => coletas.value.length === 0)

const tituloGraficoSementes = computed(() =>
  modoSementes.value === 'especie' ? 'Total de sementes por espécie' : 'Total de sementes por matriz'
)

const itensFiltroEvolucao = computed(() => {
  if (modoEvolucao.value === 'especie') {
    return store.especiesParaFiltro
  }
  return store.matrizesParaGrafico.map((m) => ({ id: m.id, nome: m.nome }))
})

const itensFiltroModal = computed(() => {
  const q = buscaFiltro.value.trim().toLowerCase()
  if (!q) return itensFiltroEvolucao.value
  return itensFiltroEvolucao.value.filter((i) => i.nome.toLowerCase().includes(q))
})

function sincronizarSelecaoEvolucao() {
  selecaoEvolucao.value = itensFiltroEvolucao.value.map((i) => i.id)
}

watch(modoEvolucao, sincronizarSelecaoEvolucao)
watch(itensFiltroEvolucao, sincronizarSelecaoEvolucao, { immediate: true })

function abrirModalFiltro() {
  selecaoRascunho.value = [...selecaoEvolucao.value]
  buscaFiltro.value = ''
  modalFiltroAberto.value = true
}

function fecharModalFiltro() {
  modalFiltroAberto.value = false
}

function aplicarFiltro() {
  selecaoEvolucao.value = [...selecaoRascunho.value]
  fecharModalFiltro()
}

function selecionarTodasRascunho() {
  const visiveis = new Set(itensFiltroModal.value.map((i) => i.id))
  const mantidas = selecaoRascunho.value.filter((id) => !visiveis.has(id))
  selecaoRascunho.value = [...mantidas, ...visiveis]
}

function limparRascunho() {
  const visiveis = new Set(itensFiltroModal.value.map((i) => i.id))
  selecaoRascunho.value = selecaoRascunho.value.filter((id) => !visiveis.has(id))
}

const chartOptionsBase = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'bottom',
      labels: { boxWidth: 12, font: { size: 10 }, padding: 10 }
    }
  },
  scales: {
    y: { beginAtZero: true },
    x: { grid: { display: false } }
  }
}

function seriesColors(total) {
  return Array.from({ length: total }, (_, i) => CORES[i % CORES.length])
}

const chartOptionsComScroll = computed(() => ({
  ...chartOptionsBase,
  scales: {
    ...chartOptionsBase.scales,
    x: {
      ...chartOptionsBase.scales.x,
      ticks: {
        maxRotation: 45,
        minRotation: 0,
        autoSkip: lista.value.length <= 20
      }
    }
  }
}))

const sementesChartData = computed(() => {
  if (modoSementes.value === 'matriz') {
    const colors = seriesColors(lista.value.length)
    return {
      labels: lista.value.map((a) => a.nome),
      datasets: [
        {
          label: 'Sementes coletadas',
          data: lista.value.map((a) => a.sementes_coletadas || 0),
          backgroundColor: colors.map((c) => withAlpha(c, 0.82)),
          borderColor: colors,
          hoverBackgroundColor: colors.map((c) => withAlpha(c, 0.95)),
          hoverBorderColor: colors,
          borderWidth: 1.2
        }
      ]
    }
  }

  const porEspecie = {}
  lista.value.forEach((a) => {
    const esp = nomePopularExibicao(a.especie_nome) || 'Outras'
    porEspecie[esp] = (porEspecie[esp] || 0) + (a.sementes_coletadas || 0)
  })
  const labels = Object.keys(porEspecie)
  const colors = seriesColors(labels.length)
  return {
    labels,
    datasets: [
      {
        label: 'Sementes coletadas',
        data: labels.map((l) => porEspecie[l]),
        backgroundColor: colors.map((c) => withAlpha(c, 0.82)),
        borderColor: colors,
        hoverBackgroundColor: colors.map((c) => withAlpha(c, 0.95)),
        hoverBorderColor: colors,
        borderWidth: 1.2
      }
    ]
  }
})

const germinacaoData = computed(() => {
  const comTaxa = lista.value.filter((a) => a.taxa_germinacao != null)
  return {
    labels: comTaxa.map((a) => a.nome),
    datasets: [
      {
        label: 'Taxa de germinação (%)',
        data: comTaxa.map((a) => a.taxa_germinacao),
        borderColor: CHART_INFO,
        backgroundColor: '#47607B22',
        tension: 0.2,
        fill: true
      }
    ]
  }
})

function formatarDataLabel(dataStr) {
  return new Date(dataStr + 'T12:00:00').toLocaleDateString('pt-BR')
}

const evolucaoData = computed(() => {
  const ativos = new Set(selecaoEvolucao.value)
  const filtradas = coletas.value.filter((c) => {
    if (modoEvolucao.value === 'especie') {
      return ativos.has(c.id_especie)
    }
    return ativos.has(c.id_arvore_matriz)
  })

  const labels = [...new Set(filtradas.map((c) => c.data_coleta))].sort()

  if (modoEvolucao.value === 'especie') {
    const especies = store.especiesParaFiltro.filter((e) => ativos.has(e.id))
    return {
      labels: labels.map(formatarDataLabel),
      datasets: especies.map((esp, i) => ({
        label: nomePopularExibicao(esp.nome),
        data: labels.map((data) =>
          filtradas
            .filter((c) => c.data_coleta === data && c.id_especie === esp.id)
            .reduce((s, c) => s + c.quantidade_sementes, 0)
        ),
        borderColor: CORES[i % CORES.length],
        backgroundColor: `${CORES[i % CORES.length]}22`,
        tension: 0.2,
        fill: false
      }))
    }
  }

  const matrizes = store.matrizesParaGrafico.filter((m) => ativos.has(m.id))
  return {
    labels: labels.map(formatarDataLabel),
    datasets: matrizes.map((m, i) => ({
      label: m.nome,
      data: labels.map((data) =>
        filtradas
          .filter((c) => c.data_coleta === data && c.id_arvore_matriz === m.id)
          .reduce((s, c) => s + c.quantidade_sementes, 0)
      ),
      borderColor: CORES[i % CORES.length],
      backgroundColor: `${CORES[i % CORES.length]}22`,
      tension: 0.2,
      fill: false
    }))
  }
})
</script>

<style scoped>
.graficos-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: var(--spacing-md);
  height: 400px;
  display: flex;
  flex-direction: column;
}

.card-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: var(--spacing-sm);
  flex-shrink: 0;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
}

.head-acoes {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
}

.toggle-group {
  display: flex;
  gap: 0.25rem;
  background: var(--color-background);
  padding: 0.2rem;
  border-radius: 6px;
}

.toggle-group button {
  border: none;
  background: transparent;
  padding: 0.3rem 0.55rem;
  font-size: 0.7rem;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.toggle-group button.ativo {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-weight: 600;
}

.btn-filtro {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  padding: 0.3rem 0.6rem;
  font-size: 0.7rem;
  border-radius: 6px;
  cursor: pointer;
  color: var(--color-text-primary);
}

.btn-filtro:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.badge {
  background: var(--color-success-bg);
  color: var(--color-success);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}

.chart-container {
  flex: 1;
  min-height: 0;
  position: relative;
}

.sem-dados {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  text-align: center;
  padding: 1rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1600;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-filtro {
  background: var(--color-surface);
  border-radius: 12px;
  width: 100%;
  max-width: 480px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.modal-filtro-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-filtro-header h2 {
  margin: 0;
  font-size: 1rem;
}

.btn-fechar {
  border: none;
  background: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-muted);
}

.modal-filtro-body {
  padding: 1rem 1.25rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 0;
}

.busca-filtro {
  width: 100%;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 0.875rem;
}

.modal-filtro-acoes {
  display: flex;
  gap: 1rem;
}

.link-btn {
  border: none;
  background: none;
  padding: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-primary);
  cursor: pointer;
}

.link-btn:hover {
  text-decoration: underline;
}

.lista-filtro {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
  max-height: 50vh;
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.lista-filtro li {
  border-bottom: 1px solid var(--color-surface-muted);
}

.lista-filtro li:last-child {
  border-bottom: none;
}

.lista-filtro label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.75rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.lista-filtro label:hover {
  background: var(--color-surface-muted);
}

.lista-vazia {
  padding: 1.5rem;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.modal-filtro-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
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
  background: var(--color-surface-muted);
}

.btn-prim {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-weight: 600;
}

@media (max-width: 1200px) {
  .graficos-container {
    grid-template-columns: repeat(2, 1fr);
  }

  .graficos-container .card:last-child {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .graficos-container {
    grid-template-columns: 1fr;
  }

  .graficos-container .card:last-child {
    grid-column: auto;
  }
}
</style>
