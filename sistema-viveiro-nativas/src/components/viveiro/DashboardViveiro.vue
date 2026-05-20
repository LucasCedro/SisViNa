<template>
    <div class="dashboard-container">
        <div class="dashboard-grid">
            <!-- Painel de Quantidade de Mudas por Espécie -->
            <div class="dashboard-card">
                <h3 class="card-title">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                    </svg>
                    Quantidade de Mudas por Espécie
                </h3>
                <div class="chart-container">
                    <div v-for="item in mudaEspecie" :key="item.especie" class="bar-chart-item">
                        <div class="bar-label">{{ item.especie.split(' ')[0] }}</div>
                        <div class="bar-container">
                            <div class="bar" :style="{ width: `${(item.quantidade / maxMudas) * 100}%` }"></div>
                            <span class="bar-value">{{ item.quantidade }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Painel de Tempo Médio de Permanência -->
            <div class="dashboard-card">
                <h3 class="card-title">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Tempo de Permanência
                </h3>
                <div class="metric-container">
                    <div class="big-metric">{{ mediaPermanencia }}</div>
                    <div class="metric-label">Dias (média)</div>
                </div>
            </div>

            <!-- Painel de Temperatura Média dos Canteiros -->
            <div class="dashboard-card">
                <h3 class="card-title">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Plantas por canteiro (API)
                </h3>
                <div class="temp-chart-container">
                    <div v-for="item in temperaturasMedias" :key="item.nome" class="temp-item">
                        <div class="temp-label">{{ item.nome }}</div>
                        <div class="temp-value">
                            {{ item.temperatura }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Painel de Alertas -->
            <div class="dashboard-card alerts-card">
                <h3 class="card-title">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Alertas de Ambiente
                </h3>
                <div class="alerts-container">
                    <div v-if="alertas.length === 0" class="no-alerts">
                        Nenhum alerta ativo no momento
                    </div>
                    <div v-else v-for="alerta in alertas" :key="alerta.id" class="alert-item"
                        :class="getTipoAlertaClass(alerta.tipo)">
                        <div class="alert-indicator"></div>
                        <div class="alert-content">
                            <div class="alert-message">{{ alerta.mensagem }}</div>
                            <div class="alert-time">{{ formatarDataHora(alerta.data) }}</div>
                        </div>
                        <button type="button" class="btn-dismiss" disabled title="Gerencie em Fitossanidade">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20"
                                fill="currentColor">
                                <path fill-rule="evenodd"
                                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                    clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDashboardResumo } from '@/services/dashboard'
import { listPragasPlantas } from '@/services/pragas'

const resumo = ref({ plantas_por_especie: [], ocupacao_canteiros: [] })
const alertas = ref([])

const mudaEspecie = computed(() =>
  (resumo.value.plantas_por_especie || []).map((p) => ({
    especie: p.especie,
    quantidade: p.quantidade
  }))
)
const mediaPermanencia = computed(() => '—')
const temperaturasMedias = computed(() =>
  (resumo.value.ocupacao_canteiros || []).map((c) => ({
    nome: c.nome,
    temperatura: c.total_plantas ?? 0
  }))
)

onMounted(async () => {
  try {
    resumo.value = await getDashboardResumo()
    const pragas = await listPragasPlantas({ limit: 50 })
    alertas.value = pragas
      .filter((p) => ['ALTO', 'CRITICO'].includes(p.nivel_infestacao))
      .map((p) => ({
        id: p.id,
        tipo: 'praga',
        mensagem: `${p.tipo_praga?.nome || 'Praga'} — ${p.especie_nome} (${p.nivel_infestacao})`,
        data: p.data_identificacao
      }))
  } catch (e) {
    console.error(e)
  }
})

// Máximo de mudas por espécie (para o gráfico de barras)
const maxMudas = computed(() => {
    if (mudaEspecie.value.length === 0) return 10;
    return Math.max(...mudaEspecie.value.map(item => item.quantidade));
});

// Funções utilitárias
const formatarDataHora = (dataString) => {
    const data = new Date(dataString);
    return data.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const getTipoAlertaClass = (tipo) => {
    switch (tipo) {
        case 'temperatura-alta':
        case 'temperatura-baixa':
            return 'alert-temp';
        case 'umidade-baixa':
        case 'umidade-alta':
            return 'alert-umidade';
        default:
            return 'alert-generic';
    }
};

const getTemperatureClass = (temp) => {
    if (typeof temp === 'string' && temp === 'N/A') return 'temp-neutral';
    const tempValue = parseFloat(temp);
    if (tempValue >= 25) return 'temp-high';
    if (tempValue <= 20) return 'temp-low';
    return 'temp-normal';
};

const removerAlerta = (alertaId) => {
    store.removerAlerta(alertaId);
};
</script>

<style scoped>
.dashboard-container {
    width: 100%;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

.dashboard-card {
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1rem;
    display: flex;
    flex-direction: column;
}

.alerts-card {
    grid-column: span 2;
}

.card-title {
    display: flex;
    align-items: center;
    font-size: 1rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 1rem;
}

.icon {
    width: 1.25rem;
    height: 1.25rem;
    margin-right: 0.5rem;
    color: #1976D2;
}

.chart-container {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.bar-chart-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.bar-label {
    width: 100px;
    font-size: 0.875rem;
    color: #555;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.bar-container {
    flex-grow: 1;
    height: 1.5rem;
    background-color: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}

.bar {
    height: 100%;
    background-color: #2196F3;
    border-radius: 4px;
}

.bar-value {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.75rem;
    font-weight: 600;
    color: #333;
}

.metric-container {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.big-metric {
    font-size: 3rem;
    font-weight: 700;
    color: #1976D2;
}

.metric-label {
    font-size: 1rem;
    color: #666;
    margin-top: 0.5rem;
}

.temp-chart-container {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 1rem;
    padding: 0.5rem;
}

.temp-item {
    text-align: center;
}

.temp-label {
    font-size: 0.875rem;
    color: #666;
    margin-bottom: 0.25rem;
}

.temp-value {
    font-size: 1.25rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
}

.temp-high {
    background-color: #ffebee;
    color: #c62828;
}

.temp-normal {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.temp-low {
    background-color: #e3f2fd;
    color: #1565c0;
}

.temp-neutral {
    background-color: #f5f5f5;
    color: #757575;
}

.alerts-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 250px;
    overflow-y: auto;
}

.no-alerts {
    padding: 1rem;
    text-align: center;
    color: #757575;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.alert-item {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    border-radius: 4px;
    position: relative;
}

.alert-temp {
    background-color: #fff8e1;
}

.alert-umidade {
    background-color: #e3f2fd;
}

.alert-generic {
    background-color: #f5f5f5;
}

.alert-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 0.75rem;
}

.alert-temp .alert-indicator {
    background-color: #ff9800;
}

.alert-umidade .alert-indicator {
    background-color: #2196f3;
}

.alert-generic .alert-indicator {
    background-color: #9e9e9e;
}

.alert-content {
    flex-grow: 1;
}

.alert-message {
    font-size: 0.875rem;
    color: #333;
}

.alert-time {
    font-size: 0.75rem;
    color: #757575;
    margin-top: 0.25rem;
}

.btn-dismiss {
    background: transparent;
    border: none;
    color: #757575;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 50%;
}

.btn-dismiss:hover {
    background-color: rgba(0, 0, 0, 0.05);
    color: #333;
}

.btn-dismiss svg {
    width: 16px;
    height: 16px;
}

@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }

    .alerts-card {
        grid-column: span 1;
    }
}
</style>