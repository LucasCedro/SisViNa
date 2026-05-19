<template>
  <div class="graficos-container">
    <!-- Card de Total de Sementes por Espécie -->
    <div class="card">
      <h3 class="card-title">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Total de Sementes por Espécie
      </h3>
      <div class="chart-container">
        <Bar :data="sementesPorEspecieData" :options="chartOptions" />
      </div>
    </div>

    <!-- Card de Taxa de Germinação -->
    <div class="card">
      <h3 class="card-title">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Taxa de Germinação por Espécie
      </h3>
      <div class="chart-container">
        <Line :data="germinacaoData" :options="chartOptions" />
      </div>
    </div>

    <!-- Card de Evolução Temporal -->
    <div class="card">
      <h3 class="card-title">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
        Evolução da Coleta
      </h3>
      <div class="chart-container">
        <Line :data="evolucaoData" :options="chartOptions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { useColetaStore } from '../../store/coleta'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend)

const store = useColetaStore()

// Opções comuns para todos os gráficos
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      titleColor: 'var(--color-text-primary)',
      bodyColor: 'var(--color-text-secondary)',
      borderColor: 'var(--color-border)',
      borderWidth: 1,
      padding: 10,
      displayColors: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}

// Dados para o gráfico de sementes por espécie
const sementesPorEspecieData = computed(() => ({
  labels: store.arvoresMatriz.map(a => a.especie),
  datasets: [{
    data: store.arvoresMatriz.map(a => a.sementes_coletadas),
    backgroundColor: 'var(--color-primary)',
    borderColor: 'var(--color-primary-dark)',
    borderWidth: 1
  }]
}))

// Dados para o gráfico de taxa de germinação
const germinacaoData = computed(() => ({
  labels: store.arvoresMatriz.map(a => a.especie),
  datasets: [{
    data: store.arvoresMatriz.map(a => a.taxa_germinacao),
    borderColor: 'var(--color-secondary)',
    backgroundColor: 'rgba(33, 150, 243, 0.1)',
    tension: 0.1,
    fill: true
  }]
}))

// Dados para o gráfico de evolução temporal
const evolucaoData = computed(() => ({
  labels: store.arvoresMatriz.map(a => new Date(a.data_coleta).toLocaleDateString()),
  datasets: [{
    data: store.arvoresMatriz.map(a => a.sementes_coletadas),
    borderColor: 'var(--color-accent)',
    backgroundColor: 'rgba(255, 152, 0, 0.1)',
    tension: 0.1,
    fill: true
  }]
}))
</script>

<style>
.graficos-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  width: 100%;
}

.card {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  height: 350px;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.icon {
  width: 1rem;
  height: 1rem;
  margin-right: var(--spacing-sm);
  color: var(--color-primary);
}

.chart-container {
  flex-grow: 1;
  position: relative;
  min-height: 280px;
}

@media (max-width: 1200px) {
  .graficos-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .graficos-container {
    grid-template-columns: 1fr;
  }

  .card {
    height: 300px;
  }

  .chart-container {
    min-height: 230px;
  }
}
</style>