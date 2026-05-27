<template>
  <div class="analise-recorrencia-container">
    <h2 class="section-title">Análise de Recorrência</h2>
    <p v-if="carregando" class="status-msg">Carregando dados da API...</p>
    <p v-else-if="erro" class="alert alert-error">{{ erro }}</p>

    <div class="dashboard-section">
      <div class="dashboard-grid">
        <!-- Gráfico de recorrência de pragas -->
        <div class="dashboard-card">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Recorrência de Problemas Fitossanitários
          </h3>
          <div class="chart-container">
            <p v-if="!carregando && !dadosPragas.labels.length" class="empty-hint">Sem ocorrências fitossanitárias registradas.</p>
            <canvas v-show="dadosPragas.labels.length" ref="recorrenciaPragasChart"></canvas>
          </div>
        </div>
        
        <!-- Gráfico de frequência de adubação -->
        <div class="dashboard-card">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Frequência de Adubação por Espécie
          </h3>
          <div class="chart-container">
            <p v-if="!carregando && !dadosAdubacao.labels.length" class="empty-hint">Sem atividades de fertilização registradas.</p>
            <canvas v-show="dadosAdubacao.labels.length" ref="frequenciaAdubacaoChart"></canvas>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Alertas e sugestões -->
    <div class="alertas-section">
      <h3 class="section-subtitle">
        <svg xmlns="http://www.w3.org/2000/svg" class="subtitle-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        Alertas e Sugestões Automatizadas
      </h3>
      
      <div class="filter-controls">
        <div class="filter-group">
          <label for="alerta-nivel">Filtrar por nível:</label>
          <select id="alerta-nivel" v-model="filtroAlerta">
            <option value="todos">Todos</option>
            <option value="baixo">Baixo (Verde)</option>
            <option value="medio">Médio (Amarelo)</option>
            <option value="alto">Alto (Vermelho)</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="alerta-tipo">Filtrar por tipo:</label>
          <select id="alerta-tipo" v-model="filtroTipo">
            <option value="todos">Todos</option>
            <option value="praga">Problema Fitossanitário</option>
            <option value="adubacao">Adubação</option>
          </select>
        </div>
      </div>
      
      <div class="alertas-table-container">
        <table class="alertas-table">
          <thead>
            <tr>
              <th>Nível</th>
              <th>Tipo</th>
              <th>Canteiro</th>
              <th>Descrição</th>
              <th>Sugestão</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!alertasFiltrados.length">
              <td colspan="5" class="empty-hint">Nenhum alerta — registre pragas e fertilizações para gerar análise.</td>
            </tr>
            <tr v-for="alerta in alertasFiltrados" :key="alerta.id" :class="'nivel-' + alerta.nivel">
              <td class="alerta-nivel">
                <span class="nivel-indicador" :class="'nivel-' + alerta.nivel"></span>
                {{ getNivelTexto(alerta.nivel) }}
              </td>
              <td>{{ alerta.tipo === 'praga' ? 'Fitossanitário' : 'Adubação' }}</td>
              <td>{{ alerta.canteiro }}</td>
              <td>{{ alerta.descricao }}</td>
              <td>{{ alerta.sugestao }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Sugestões de Melhoria -->
    <div class="sugestoes-section">
      <h3 class="section-subtitle">
        <svg xmlns="http://www.w3.org/2000/svg" class="subtitle-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Sugestões de Melhoria
      </h3>
      
      <p v-if="!sugestoes.length" class="empty-hint">Sugestões aparecem automaticamente a partir dos alertas de alto risco.</p>
      <div v-else class="sugestoes-grid">
        <div v-for="(sugestao, index) in sugestoes" :key="index" class="sugestao-card">
          <div class="sugestao-header">
            <div class="sugestao-icon" :class="'tipo-' + sugestao.tipo">
              <svg v-if="sugestao.tipo === 'adubacao'" xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <svg v-else-if="sugestao.tipo === 'pratica'" xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h4 class="sugestao-titulo">{{ sugestao.titulo }}</h4>
          </div>
          <p class="sugestao-descricao">{{ sugestao.descricao }}</p>
          <div class="sugestao-especies" v-if="sugestao.especies && sugestao.especies.length">
            <span class="especies-label">Espécies afetadas:</span>
            <div class="especies-tags">
              <span v-for="(especie, i) in sugestao.especies" :key="i" class="especie-tag">{{ especie }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { listPragasPlantas } from '@/services/pragas'
import { listAtividades, listTiposAtividades } from '@/services/atividades'
import { listPlantasComRelacoes } from '@/services/plantas'
import {
  CHART_PRIMARY,
  CHART_PRIMARY_DARK,
  CHART_WARNING,
  CHART_DANGER,
  withAlpha,
} from '@/constants/chartColors'

const filtroAlerta = ref('todos')
const filtroTipo = ref('todos')
const carregando = ref(true)
const erro = ref('')

const recorrenciaPragasChart = ref(null)
const frequenciaAdubacaoChart = ref(null)
let chartInstances = { recorrenciaPragas: null, frequenciaAdubacao: null }

const alertas = ref([])
const sugestoes = ref([])
const dadosPragas = ref({ labels: [], unicas: [], r30: [], r60: [] })
const dadosAdubacao = ref({ labels: [], intervals: [] })

function parseDate(d) {
  if (!d) return null
  const s = String(d)
  return new Date(s.includes('T') ? s : `${s}T12:00:00`)
}

function diasEntre(a, b) {
  const da = parseDate(a)
  const db = parseDate(b)
  if (!da || !db) return Infinity
  return Math.abs(db - da) / 86400000
}

function nivelUiFromInfestacao(nivel) {
  const n = String(nivel || '').toUpperCase()
  if (n === 'CRITICO' || n === 'ALTO') return 'alto'
  if (n === 'MEDIO') return 'medio'
  return 'baixo'
}

function buildDadosPragas(pragas) {
  const byTipo = new Map()
  const rein30 = new Map()
  const rein60 = new Map()
  const groups = new Map()

  for (const p of pragas) {
    const nome = p.tipo_praga_nome || 'Outro'
    byTipo.set(nome, (byTipo.get(nome) || 0) + 1)
    const key = `${p.id_planta}-${p.id_tipo_praga}`
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(p)
  }

  for (const items of groups.values()) {
    items.sort((a, b) => parseDate(a.data_identificacao) - parseDate(b.data_identificacao))
    for (let i = 1; i < items.length; i++) {
      const gap = diasEntre(items[i - 1].data_identificacao, items[i].data_identificacao)
      const nome = items[i].tipo_praga_nome || 'Outro'
      if (gap <= 30) rein30.set(nome, (rein30.get(nome) || 0) + 1)
      if (gap <= 60) rein60.set(nome, (rein60.get(nome) || 0) + 1)
    }
  }

  const labels = [...byTipo.keys()].sort()
  return {
    labels,
    unicas: labels.map((l) => byTipo.get(l) || 0),
    r30: labels.map((l) => rein30.get(l) || 0),
    r60: labels.map((l) => rein60.get(l) || 0),
  }
}

function buildDadosAdubacao(atividades) {
  const byEsp = new Map()
  for (const a of atividades) {
    const esp = a.especie_nome || 'Sem espécie'
    if (!byEsp.has(esp)) byEsp.set(esp, [])
    byEsp.get(esp).push(parseDate(a.data_atividade))
  }
  const labels = []
  const intervals = []
  for (const [esp, dates] of byEsp) {
    const valid = dates.filter(Boolean).sort((a, b) => a - b)
    if (valid.length < 2) continue
    let sum = 0
    for (let i = 1; i < valid.length; i++) sum += (valid[i] - valid[i - 1]) / 86400000
    labels.push(esp)
    intervals.push(Math.round(sum / (valid.length - 1)))
  }
  return { labels, intervals }
}

function buildAlertas(pragas, atividadesFert, plantas) {
  const plById = new Map(plantas.map((p) => [p.id, p]))
  const out = []
  let id = 1

  const pragaGroups = new Map()
  for (const p of pragas) {
    const key = `${p.id_planta}-${p.id_tipo_praga}`
    if (!pragaGroups.has(key)) pragaGroups.set(key, [])
    pragaGroups.get(key).push(p)
  }

  for (const items of pragaGroups.values()) {
    items.sort((a, b) => parseDate(a.data_identificacao) - parseDate(b.data_identificacao))
    const recent = items.filter((p) => diasEntre(p.data_identificacao, new Date()) <= 60)
    if (recent.length < 2) continue
    const last = recent[recent.length - 1]
    const pl = plById.get(last.id_planta)
    const tipoNome = last.tipo_praga_nome || 'problema'
    const nivel = recent.some((p) => ['ALTO', 'CRITICO'].includes(String(p.nivel_infestacao).toUpperCase()))
      ? 'alto'
      : recent.length >= 3
        ? 'medio'
        : 'baixo'
    out.push({
      id: id++,
      nivel,
      tipo: 'praga',
      canteiro: pl?.nome_canteiro || '—',
      especie: last.especie_nome || pl?.especie_nome || '—',
      descricao: `${tipoNome}: ${recent.length} ocorrência(s) em 60 dias (${last.especie_nome || 'espécie não informada'})`,
      sugestao: last.observacoes || 'Revise manejo preventivo e monitoramento no canteiro.',
    })
  }

  const ativPorPlanta = new Map()
  for (const a of atividadesFert) {
    if (!ativPorPlanta.has(a.id_planta)) ativPorPlanta.set(a.id_planta, [])
    ativPorPlanta.get(a.id_planta).push(a)
  }

  for (const [idPlanta, items] of ativPorPlanta) {
    const recent = items.filter((a) => diasEntre(a.data_atividade, new Date()) <= 30)
    if (recent.length < 4) continue
    const pl = plById.get(idPlanta)
    out.push({
      id: id++,
      nivel: 'alto',
      tipo: 'adubacao',
      canteiro: pl?.nome_canteiro || '—',
      especie: pl?.especie_nome || recent[0].especie_nome || '—',
      descricao: `${recent.length} fertilizações em 30 dias na mesma planta`,
      sugestao: 'Reduza a frequência de adubação e alinhe ao protocolo da espécie.',
    })
  }

  const porEspecie = new Map()
  for (const a of atividadesFert) {
    const esp = a.especie_nome || '—'
    if (!porEspecie.has(esp)) porEspecie.set(esp, [])
    porEspecie.get(esp).push(a)
  }
  for (const [esp, items] of porEspecie) {
    const recent = items.filter((a) => diasEntre(a.data_atividade, new Date()) <= 60)
    if (recent.length >= 2) continue
    if (!items.length) continue
    const last = [...items].sort((a, b) => parseDate(b.data_atividade) - parseDate(a.data_atividade))[0]
    if (diasEntre(last.data_atividade, new Date()) <= 45) continue
    out.push({
      id: id++,
      nivel: 'medio',
      tipo: 'adubacao',
      canteiro: '—',
      especie: esp,
      descricao: `Pouca adubação registrada para ${esp} nos últimos 60 dias`,
      sugestao: 'Verifique calendário de fertilização desta espécie.',
    })
  }

  return out
}

function buildSugestoes(listaAlertas) {
  return listaAlertas
    .filter((a) => a.nivel === 'alto')
    .slice(0, 6)
    .map((a) => ({
      tipo: a.tipo === 'praga' ? 'controle' : 'adubacao',
      titulo: a.tipo === 'praga' ? 'Atenção fitossanitária' : 'Revisar adubação',
      descricao: a.descricao,
      especies: a.especie && a.especie !== '—' ? [a.especie] : [],
    }))
}

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const [pragas, tipos, ativ, plantas] = await Promise.all([
      listPragasPlantas({ limit: 500 }),
      listTiposAtividades(),
      listAtividades({ limit: 500 }),
      listPlantasComRelacoes({ limit: 500 }),
    ])
    const tipoFert = tipos.find((t) => t.nome === 'FERTILIZACAO')
    const ativFert = tipoFert
      ? ativ.filter((a) => a.id_tipo_atividade === tipoFert.id)
      : ativ

    dadosPragas.value = buildDadosPragas(pragas)
    dadosAdubacao.value = buildDadosAdubacao(ativFert)
    alertas.value = buildAlertas(pragas, ativFert, plantas)
    sugestoes.value = buildSugestoes(alertas.value)

    await nextTick()
    criarGraficos()
  } catch (e) {
    console.error(e)
    erro.value = 'Não foi possível carregar dados para análise. Verifique a API.'
  } finally {
    carregando.value = false
  }
}

// Filtragem de alertas
const alertasFiltrados = computed(() => {
  let resultado = [...alertas.value];
  
  if (filtroAlerta.value !== 'todos') {
    resultado = resultado.filter(alerta => alerta.nivel === filtroAlerta.value);
  }
  
  if (filtroTipo.value !== 'todos') {
    resultado = resultado.filter(alerta => alerta.tipo === filtroTipo.value);
  }
  
  return resultado;
});

// Funções auxiliares
const getNivelTexto = (nivel) => {
  switch (nivel) {
    case 'alto': return 'Alto';
    case 'medio': return 'Médio';
    case 'baixo': return 'Baixo';
    default: return 'Desconhecido';
  }
};

// Funções para gráficos
const criarGraficos = () => {
  criarGraficoRecorrenciaPragas();
  criarGraficoFrequenciaAdubacao();
};

const criarGraficoRecorrenciaPragas = () => {
  if (!recorrenciaPragasChart.value || !dadosPragas.value.labels.length) return
  const ctx = recorrenciaPragasChart.value.getContext('2d')
  const d = dadosPragas.value
  const dados = {
    labels: d.labels,
    datasets: [
      {
        label: 'Ocorrências',
        data: d.unicas,
        backgroundColor: withAlpha(CHART_PRIMARY, 0.85),
        borderColor: CHART_PRIMARY_DARK,
        borderWidth: 1,
      },
      {
        label: 'Reincidências (30 dias)',
        data: d.r30,
        backgroundColor: withAlpha(CHART_WARNING, 0.9),
        borderColor: CHART_WARNING,
        borderWidth: 1,
      },
      {
        label: 'Reincidências (60 dias)',
        data: d.r60,
        backgroundColor: withAlpha(CHART_DANGER, 0.9),
        borderColor: CHART_DANGER,
        borderWidth: 1,
      },
    ],
  }
  
  // Criar gráfico
  if (chartInstances.recorrenciaPragas) {
    chartInstances.recorrenciaPragas.destroy();
  }
  
  chartInstances.recorrenciaPragas = new Chart(ctx, {
    type: 'bar',
    data: dados,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: false,
          title: {
            display: true,
            text: 'Problema Fitossanitário'
          }
        },
        y: {
          stacked: false,
          beginAtZero: true,
          title: {
            display: true,
            text: 'Número de Ocorrências'
          },
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  });
};

const criarGraficoFrequenciaAdubacao = () => {
  if (!frequenciaAdubacaoChart.value || !dadosAdubacao.value.labels.length) return
  const ctx = frequenciaAdubacaoChart.value.getContext('2d')
  const d = dadosAdubacao.value
  const dados = {
    labels: d.labels,
    datasets: [
      {
        label: 'Intervalo médio entre adubações (dias)',
        data: d.intervals,
        backgroundColor: withAlpha(CHART_PRIMARY, 0.85),
        borderColor: CHART_PRIMARY_DARK,
        borderWidth: 1,
      },
    ],
  }
  
  // Criar gráfico
  if (chartInstances.frequenciaAdubacao) {
    chartInstances.frequenciaAdubacao.destroy();
  }
  
  chartInstances.frequenciaAdubacao = new Chart(ctx, {
    type: 'bar',
    data: dados,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Intervalo entre adubações (dias)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Espécie'
          }
        }
      }
    }
  });
};

onMounted(carregar)
</script>

<style>
.analise-recorrencia-container {
  width: 100%;
  height: auto;
  padding-bottom: 2rem;
}

.section-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--color-text-primary);
}

.section-subtitle {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 2rem 0 1rem 0;
  color: var(--color-text-primary);
}

.subtitle-icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
  color: var(--color-info);
}

/* Dashboard */
.dashboard-section {
  margin-bottom: 2rem;
  width: 100%;
  overflow: visible;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.dashboard-card {
  background-color: var(--color-surface);
  border-radius: 0.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1.25rem;
  overflow: hidden;
  height: auto;
  min-height: 350px;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
  color: var(--color-info);
}

.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}

.empty-hint {
  margin: 0;
  padding: 1rem 0;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  text-align: center;
}

.status-msg {
  margin: 0 0 1rem;
  color: var(--color-text-secondary);
}

/* Alertas */
.alertas-section, 
.sugestoes-section {
  margin-bottom: 2rem;
  width: 100%;
}

.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.875rem;
  min-width: 200px;
}

.alertas-table-container {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.alertas-table {
  width: 100%;
  min-width: 800px;
  border-collapse: collapse;
}

.alertas-table th,
.alertas-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border-subtle);
}

.alertas-table th {
  background-color: var(--color-surface-muted);
  font-weight: 600;
  color: var(--color-text-primary);
}

.alertas-table tbody tr:hover {
  background-color: var(--color-surface-muted);
}

.alerta-nivel {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nivel-indicador {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.nivel-baixo .nivel-indicador {
  background-color: var(--color-primary);
}

.nivel-medio .nivel-indicador {
  background-color: var(--color-attention);
}

.nivel-alto .nivel-indicador {
  background-color: var(--color-error);
}

/* Sugestões */
.sugestoes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.sugestao-card {
  background-color: var(--color-text-inverse);
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.25rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.sugestao-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.sugestao-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.sugestao-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-info-bg);
}

.sugestao-icon.tipo-adubacao {
  background-color: var(--color-success-bg);
}

.sugestao-icon.tipo-pratica {
  background-color: var(--color-attention-bg);
}

.sugestao-icon.tipo-controle {
  background-color: var(--color-error-bg);
}

.sugestao-icon .icon {
  width: 24px;
  height: 24px;
  margin-right: 0;
}

.tipo-adubacao .icon {
  color: var(--color-primary);
}

.tipo-pratica .icon {
  color: var(--color-attention);
}

.tipo-controle .icon {
  color: var(--color-error);
}

.sugestao-titulo {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-primary);
}

.sugestao-descricao {
  margin: 0 0 1rem 0;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.sugestao-especies {
  margin-top: 1rem;
}

.especies-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-right: 0.5rem;
}

.especies-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.especie-tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: var(--color-info-bg);
  color: var(--color-info);
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Responsividade */
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .sugestoes-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-group {
    width: 100%;
    margin-bottom: 0.75rem;
  }
}
</style> 