<template>
  <div class="analise-recorrencia-container">
    <h2 class="section-title">Análise de Recorrência</h2>
    
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
            <canvas ref="recorrenciaPragasChart"></canvas>
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
            <canvas ref="frequenciaAdubacaoChart"></canvas>
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
      
      <div class="sugestoes-grid">
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
import { ref, computed, onMounted } from 'vue';
import Chart from 'chart.js/auto';

// Estados
const filtroAlerta = ref('todos');
const filtroTipo = ref('todos');

// Referências para os gráficos
const recorrenciaPragasChart = ref(null);
const frequenciaAdubacaoChart = ref(null);
let chartInstances = {
  recorrenciaPragas: null,
  frequenciaAdubacao: null
};

// Dados mockados - Alertas
const alertas = ref([
  {
    id: 1,
    nivel: 'alto',
    tipo: 'praga',
    canteiro: 'Canteiro A1',
    descricao: 'Reincidência de Ferrugem detectada 3 vezes em 60 dias no Ipê Amarelo',
    sugestao: 'Revise o controle de umidade e aumentar ventilação entre mudas. Considere fungicida sistêmico preventivo.'
  },
  {
    id: 2,
    nivel: 'medio',
    tipo: 'praga',
    canteiro: 'Canteiro B2',
    descricao: 'Cochonilhas detectadas 2 vezes em 45 dias na Aroeira',
    sugestao: 'Aumente a frequência de monitoramento e aplique óleo de neem preventivamente a cada 15 dias.'
  },
  {
    id: 3,
    nivel: 'baixo',
    tipo: 'praga',
    canteiro: 'Canteiro C1',
    descricao: 'Lagartas observadas em pequena quantidade no Jatobá',
    sugestao: 'Monitorar. Considere aplicação de Bacillus thuringiensis caso a infestação aumente.'
  },
  {
    id: 4,
    nivel: 'alto',
    tipo: 'adubacao',
    canteiro: 'Canteiro A2',
    descricao: 'Sobredosagem de NPK em mudas de Peroba Rosa (4 aplicações em 30 dias)',
    sugestao: 'Reduza frequência para 1 vez a cada 30 dias. Espécie sensível a excesso de fertilizantes.'
  },
  {
    id: 5,
    nivel: 'medio',
    tipo: 'adubacao',
    canteiro: 'Canteiro B1',
    descricao: 'Baixa frequência de adubação no Pau-Brasil (apenas 1 aplicação nos últimos 60 dias)',
    sugestao: 'Aumente a frequência para a cada 20 dias com composto orgânico durante fase de desenvolvimento.'
  },
  {
    id: 6,
    nivel: 'baixo',
    tipo: 'adubacao',
    canteiro: 'Canteiro C2',
    descricao: 'Deficiência de fósforo observada em análise de solo',
    sugestao: 'Considere adubação de correção com superfosfato simples (100g/m²).'
  }
]);

// Dados mockados - Sugestões de melhoria
const sugestoes = ref([
  {
    tipo: 'pratica',
    titulo: 'Ajuste de Sombreamento',
    descricao: 'Reduza o sombreamento para 30% nos canteiros de Ipê Amarelo e Aroeira para evitar umidade excessiva que favorece doenças fúngicas.',
    especies: ['Ipê Amarelo', 'Aroeira']
  },
  {
    tipo: 'adubacao',
    titulo: 'Revisão do Calendário de Adubação',
    descricao: 'Crie um calendário escalonado de adubação para cada espécie conforme fase de desenvolvimento, priorizando o Pau-Brasil que está com déficit nutricional.',
    especies: ['Pau-Brasil', 'Jatobá', 'Peroba Rosa']
  },
  {
    tipo: 'controle',
    titulo: 'Substituição de Produto Fitossanitário',
    descricao: 'O fungicida atual tem mostrado baixa eficácia contra ferrugem. Considere substituir por produto à base de tebuconazol ou utilizar calda bordalesa na concentração de 1% cada 15 dias como preventivo.',
    especies: ['Ipê Amarelo']
  },
  {
    tipo: 'pratica',
    titulo: 'Revisão do Espaçamento entre Mudas',
    descricao: 'Aumente o espaçamento entre as mudas nos canteiros A1 e B2 para melhorar a ventilação e reduzir a umidade entre as plantas.',
    especies: []
  }
]);

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
  const ctx = recorrenciaPragasChart.value.getContext('2d');
  
  // Dados mockados para o gráfico
  const dados = {
    labels: ['Ferrugem', 'Cochonilha', 'Oídio', 'Pulgões', 'Antracnose', 'Lagartas'],
    datasets: [
      {
        label: 'Ocorrências Únicas',
        data: [5, 7, 3, 4, 2, 6],
        backgroundColor: 'rgba(75, 192, 192, 0.7)'
      },
      {
        label: 'Reincidências (30 dias)',
        data: [3, 2, 1, 2, 0, 1],
        backgroundColor: 'rgba(255, 206, 86, 0.7)'
      },
      {
        label: 'Reincidências (60 dias)',
        data: [2, 1, 0, 1, 0, 0],
        backgroundColor: 'rgba(255, 99, 132, 0.7)'
      }
    ]
  };
  
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
  const ctx = frequenciaAdubacaoChart.value.getContext('2d');
  
  // Dados mockados para o gráfico
  const dados = {
    labels: ['Ipê Amarelo', 'Jatobá', 'Pau-Brasil', 'Peroba Rosa', 'Aroeira'],
    datasets: [
      {
        label: 'Frequência Recomendada (dias)',
        data: [15, 20, 20, 30, 20],
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
        type: 'line',
        fill: false,
        order: 0
      },
      {
        label: 'Frequência Real (dias)',
        data: [12, 18, 38, 7, 22],
        backgroundColor: [
          'rgba(54, 162, 235, 0.7)', // Normal
          'rgba(54, 162, 235, 0.7)', // Normal
          'rgba(255, 99, 132, 0.7)', // Déficit (muito alto - vermelho)
          'rgba(255, 206, 86, 0.7)', // Excesso (muito baixo - amarelo)
          'rgba(54, 162, 235, 0.7)'  // Normal
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(54, 162, 235, 1)'
        ],
        borderWidth: 1,
        order: 1
      }
    ]
  };
  
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

// Montar componente
onMounted(() => {
  criarGraficos();
});
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
  color: #333;
}

.section-subtitle {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 2rem 0 1rem 0;
  color: #333;
}

.subtitle-icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
  color: #2196F3;
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
  background-color: #fff;
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
  color: #333;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
  color: #2196F3;
}

.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
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
  color: #555;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #ddd;
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
  border-bottom: 1px solid #eee;
}

.alertas-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #444;
}

.alertas-table tbody tr:hover {
  background-color: #f8f9fa;
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
  background-color: #4CAF50;
}

.nivel-medio .nivel-indicador {
  background-color: #FFC107;
}

.nivel-alto .nivel-indicador {
  background-color: #F44336;
}

/* Sugestões */
.sugestoes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.sugestao-card {
  background-color: white;
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
  background-color: #E3F2FD;
}

.sugestao-icon.tipo-adubacao {
  background-color: #E8F5E9;
}

.sugestao-icon.tipo-pratica {
  background-color: #FFF8E1;
}

.sugestao-icon.tipo-controle {
  background-color: #FFEBEE;
}

.sugestao-icon .icon {
  width: 24px;
  height: 24px;
  margin-right: 0;
}

.tipo-adubacao .icon {
  color: #4CAF50;
}

.tipo-pratica .icon {
  color: #FFC107;
}

.tipo-controle .icon {
  color: #F44336;
}

.sugestao-titulo {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.sugestao-descricao {
  margin: 0 0 1rem 0;
  color: #555;
  line-height: 1.5;
}

.sugestao-especies {
  margin-top: 1rem;
}

.especies-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #555;
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
  background-color: #E3F2FD;
  color: #1976D2;
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