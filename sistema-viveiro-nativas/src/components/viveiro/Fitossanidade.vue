<template>
  <div class="fitossanidade-container">
    <h1 class="page-title">Monitoramento Fitossanitário</h1>
    
    <!-- Seção de filtros -->
    <div class="filters-section">
      <div class="filter-group">
        <label for="filter-especie">Espécie:</label>
        <select id="filter-especie" v-model="filtros.especie">
          <option value="">Todas</option>
          <option v-for="especie in especiesUnicas" :key="especie" :value="especie">{{ especie }}</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="filter-severidade">Severidade:</label>
        <select id="filter-severidade" v-model="filtros.severidade">
          <option value="">Todas</option>
          <option value="leve">Leve</option>
          <option value="moderada">Moderada</option>
          <option value="grave">Grave</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="filter-data-inicio">Data início:</label>
        <input type="date" id="filter-data-inicio" v-model="filtros.dataInicio">
      </div>
      
      <div class="filter-group">
        <label for="filter-data-fim">Data fim:</label>
        <input type="date" id="filter-data-fim" v-model="filtros.dataFim">
      </div>
      
      <button class="btn-aplicar-filtro" @click="aplicarFiltros">Aplicar filtros</button>
      <button class="btn-limpar-filtro" @click="limparFiltros">Limpar</button>
    </div>
    
    <!-- Seção para resumo e gráficos -->
    <div class="dashboard-section">
      <div class="dashboard-grid">
        <!-- Ocorrências por mês -->
        <div class="dashboard-card">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Ocorrências por Mês
          </h3>
          <div class="chart-container">
            <canvas ref="ocorrenciasPorMesChart"></canvas>
          </div>
        </div>
        
        <!-- Pragas mais comuns -->
        <div class="dashboard-card">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            Pragas mais Comuns
          </h3>
          <div class="chart-container">
            <canvas ref="pragasMaisComunsChart"></canvas>
          </div>
        </div>
        
        <!-- Custo mensal com controle -->
        <div class="dashboard-card">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Custo Mensal com Controle
          </h3>
          <div class="chart-container">
            <canvas ref="custoMensalChart"></canvas>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Botão para nova ocorrência -->
    <div class="action-buttons">
      <button class="btn-nova-ocorrencia" @click="abrirFormulario">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nova Ocorrência
      </button>
    </div>
    
    <!-- Tabela de ocorrências -->
    <div class="table-section">
      <h2 class="section-title">Ocorrências Registradas</h2>
      <div class="table-container">
        <table class="ocorrencias-table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Canteiro</th>
              <th>Espécie</th>
              <th>Praga/Doença</th>
              <th>Severidade</th>
              <th>Produto Aplicado</th>
              <th>Responsável</th>
              <th>Custo (R$)</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ocorrencia in ocorrenciasFiltradas" :key="ocorrencia.id">
              <td>{{ formatarData(ocorrencia.data) }}</td>
              <td>{{ ocorrencia.canteiro }}</td>
              <td>{{ ocorrencia.especie }}</td>
              <td>{{ ocorrencia.pragaDoenca }}</td>
              <td>
                <span class="tag" :class="'severidade-' + ocorrencia.severidade">
                  {{ ocorrencia.severidade }}
                </span>
              </td>
              <td>{{ ocorrencia.produto || 'Nenhum' }}</td>
              <td>{{ ocorrencia.responsavel }}</td>
              <td>R$ {{ ocorrencia.custo.toFixed(2) }}</td>
              <td class="acoes">
                <button class="btn-acao" @click="verDetalhes(ocorrencia)" title="Ver detalhes">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon-small" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button class="btn-acao" @click="editarOcorrencia(ocorrencia)" title="Editar">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon-small" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button class="btn-acao btn-deletar" @click="excluirOcorrencia(ocorrencia.id)" title="Excluir">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon-small" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Modal de formulário -->
    <div class="modal-overlay" v-if="formularioAberto" @click.self="fecharFormulario">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">{{ modoEdicao ? 'Editar Ocorrência' : 'Nova Ocorrência' }}</h2>
          <button class="btn-fechar" @click="fecharFormulario">×</button>
        </div>
        <form @submit.prevent="salvarOcorrencia" class="formulario-ocorrencia">
          <div class="form-row">
            <div class="form-group">
              <label for="canteiro">Canteiro:</label>
              <select id="canteiro" v-model="ocorrenciaForm.canteiro" required>
                <option value="">Selecione um canteiro</option>
                <option v-for="canteiro in canteiros" :key="canteiro.id" :value="canteiro.nome">
                  {{ canteiro.nome }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="especie">Espécie:</label>
              <input type="text" id="especie" v-model="ocorrenciaForm.especie" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="data">Data:</label>
              <input type="date" id="data" v-model="ocorrenciaForm.data" required>
            </div>
            
            <div class="form-group">
              <label for="praga-doenca">Praga/Doença:</label>
              <input type="text" id="praga-doenca" v-model="ocorrenciaForm.pragaDoenca" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="severidade">Severidade:</label>
              <select id="severidade" v-model="ocorrenciaForm.severidade" required>
                <option value="leve">Leve</option>
                <option value="moderada">Moderada</option>
                <option value="grave">Grave</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="responsavel">Responsável:</label>
              <input type="text" id="responsavel" v-model="ocorrenciaForm.responsavel" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="produto">Produto Aplicado:</label>
              <input type="text" id="produto" v-model="ocorrenciaForm.produto">
            </div>
            
            <div class="form-group">
              <label for="custo">Custo (R$):</label>
              <input type="number" id="custo" v-model="ocorrenciaForm.custo" step="0.01" min="0">
            </div>
          </div>
          
          <div class="form-group full-width">
            <label for="observacoes">Observações:</label>
            <textarea id="observacoes" v-model="ocorrenciaForm.observacoes" rows="4"></textarea>
          </div>
          
          <div class="form-group full-width">
            <label for="imagem">Imagem:</label>
            <div class="upload-area">
              <input type="file" id="imagem" @change="previewImagem" accept="image/*" class="file-input">
              <label for="imagem" class="file-label">
                <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Selecionar Imagem
              </label>
            </div>
            <div v-if="imagemPreview" class="imagem-preview">
              <img :src="imagemPreview" alt="Preview">
            </div>
          </div>
          
          <div class="form-buttons">
            <button type="button" class="btn-cancelar" @click="fecharFormulario">Cancelar</button>
            <button type="submit" class="btn-salvar">Salvar</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Modal de detalhes -->
    <div class="modal-overlay" v-if="detalhesAbertos" @click.self="fecharDetalhes">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">Detalhes da Ocorrência</h2>
          <button class="btn-fechar" @click="fecharDetalhes">×</button>
        </div>
        <div class="detalhes-ocorrencia" v-if="ocorrenciaSelecionada">
          <div class="detalhes-header">
            <div class="detalhes-info">
              <h3>{{ ocorrenciaSelecionada.pragaDoenca }}</h3>
              <p>
                <span class="tag" :class="'severidade-' + ocorrenciaSelecionada.severidade">
                  {{ ocorrenciaSelecionada.severidade }}
                </span>
              </p>
              <p><strong>Data:</strong> {{ formatarData(ocorrenciaSelecionada.data) }}</p>
              <p><strong>Canteiro:</strong> {{ ocorrenciaSelecionada.canteiro }}</p>
              <p><strong>Espécie:</strong> {{ ocorrenciaSelecionada.especie }}</p>
            </div>
            <div class="detalhes-imagem" v-if="ocorrenciaSelecionada.imagem">
              <img :src="ocorrenciaSelecionada.imagem" alt="Imagem da ocorrência">
            </div>
          </div>
          
          <div class="detalhes-body">
            <div class="detalhes-section">
              <h4>Tratamento</h4>
              <p><strong>Produto:</strong> {{ ocorrenciaSelecionada.produto || 'Nenhum' }}</p>
              <p><strong>Responsável:</strong> {{ ocorrenciaSelecionada.responsavel }}</p>
              <p><strong>Custo:</strong> R$ {{ ocorrenciaSelecionada.custo.toFixed(2) }}</p>
            </div>
            
            <div class="detalhes-section">
              <h4>Observações</h4>
              <p>{{ ocorrenciaSelecionada.observacoes || 'Nenhuma observação' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import Chart from 'chart.js/auto'
import { listCanteiros } from '@/services/canteiros'
import { listPragasPlantas, listTiposPragas, createPragaPlanta } from '@/services/pragas'
import { listPlantasComRelacoes } from '@/services/plantas'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const canteiros = ref([])
const plantas = ref([])
const tiposPraga = ref([])

const SEV_MAP = { leve: 'BAIXO', moderada: 'MEDIO', grave: 'ALTO' }
const SEV_REV = { BAIXO: 'leve', MEDIO: 'moderada', ALTO: 'grave', CRITICO: 'grave' }

const ocorrencias = ref([])

function mapPraga(p) {
  const pl = plantas.value.find((x) => x.id === p.id_planta)
  return {
    id: p.id,
    data: p.data_identificacao,
    canteiro: pl?.nome_canteiro || '—',
    especie: p.especie_nome || '—',
    pragaDoenca: p.tipo_praga?.nome || '—',
    severidade: SEV_REV[p.nivel_infestacao] || 'leve',
    produto: '—',
    responsavel: '—',
    custo: 0,
    observacoes: p.observacoes || '',
    imagem: null,
    id_planta: p.id_planta,
    id_tipo_praga: p.id_tipo_praga
  }
}

async function carregarFitossanidade() {
  const [cant, pl, tp, pr] = await Promise.all([
    listCanteiros({ ativo: true }),
    listPlantasComRelacoes({ limit: 300 }),
    listTiposPragas(),
    listPragasPlantas({ limit: 200 })
  ])
  canteiros.value = cant
  plantas.value = pl
  tiposPraga.value = tp
  ocorrencias.value = pr.map(mapPraga)
  atualizarGraficos()
}

onMounted(carregarFitossanidade)

// Formulário para nova ocorrência
const ocorrenciaForm = reactive({
  id: null,
  data: '',
  canteiro: '',
  especie: '',
  pragaDoenca: '',
  severidade: 'leve',
  produto: '',
  responsavel: '',
  custo: 0,
  observacoes: '',
  imagem: null
});

// Estados de UI
const formularioAberto = ref(false);
const modoEdicao = ref(false);
const detalhesAbertos = ref(false);
const ocorrenciaSelecionada = ref(null);
const imagemPreview = ref(null);

// Filtros
const filtros = reactive({
  especie: '',
  severidade: '',
  dataInicio: '',
  dataFim: ''
});

// Computadas
const especiesUnicas = computed(() => {
  const especies = new Set();
  ocorrencias.value.forEach(ocorrencia => especies.add(ocorrencia.especie));
  return [...especies];
});

const ocorrenciasFiltradas = computed(() => {
  let resultado = [...ocorrencias.value];
  
  if (filtros.especie) {
    resultado = resultado.filter(item => item.especie === filtros.especie);
  }
  
  if (filtros.severidade) {
    resultado = resultado.filter(item => item.severidade === filtros.severidade);
  }
  
  if (filtros.dataInicio) {
    resultado = resultado.filter(item => new Date(item.data) >= new Date(filtros.dataInicio));
  }
  
  if (filtros.dataFim) {
    resultado = resultado.filter(item => new Date(item.data) <= new Date(filtros.dataFim));
  }
  
  return resultado.sort((a, b) => new Date(b.data) - new Date(a.data));
});

// Elementos de gráficos
const ocorrenciasPorMesChart = ref(null);
const pragasMaisComunsChart = ref(null);
const custoMensalChart = ref(null);
let chartInstances = {
  ocorrenciasPorMes: null,
  pragasMaisComuns: null,
  custoMensal: null
};

// Funções
const formatarData = (data) => {
  return new Date(data).toLocaleDateString('pt-BR');
};

const abrirFormulario = () => {
  modoEdicao.value = false;
  resetarFormulario();
  formularioAberto.value = true;
};

const fecharFormulario = () => {
  formularioAberto.value = false;
  resetarFormulario();
};

const resetarFormulario = () => {
  Object.keys(ocorrenciaForm).forEach(key => {
    if (key === 'severidade') {
      ocorrenciaForm[key] = 'leve';
    } else if (key === 'custo') {
      ocorrenciaForm[key] = 0;
    } else {
      ocorrenciaForm[key] = '';
    }
  });
  ocorrenciaForm.id = null;
  imagemPreview.value = null;
};

const previewImagem = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = e => {
      imagemPreview.value = e.target.result;
      ocorrenciaForm.imagem = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const salvarOcorrencia = async () => {
  if (modoEdicao.value) {
    alert('Edição via API em breve. Exclua e recadastre se necessário.')
    return
  }
  const planta = plantas.value.find((p) =>
    ocorrenciaForm.especie && String(p.especie_nome).includes(ocorrenciaForm.especie.split('(')[0].trim())
  ) || plantas.value[0]
  const tipo = tiposPraga.value.find((t) => t.nome === ocorrenciaForm.pragaDoenca) || tiposPraga.value[0]
  if (!planta || !tipo) {
    alert('Cadastre plantas e tipos de praga no banco.')
    return
  }
  try {
    await createPragaPlanta({
      id_planta: planta.id,
      id_tipo_praga: tipo.id,
      data_identificacao: ocorrenciaForm.data,
      nivel_infestacao: SEV_MAP[ocorrenciaForm.severidade] || 'MEDIO',
      observacoes: ocorrenciaForm.observacoes
    })
    fecharFormulario()
    await carregarFitossanidade()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar ocorrência.')
  }
}

const editarOcorrencia = (ocorrencia) => {
  modoEdicao.value = true;
  Object.keys(ocorrenciaForm).forEach(key => {
    ocorrenciaForm[key] = ocorrencia[key];
  });
  imagemPreview.value = ocorrencia.imagem;
  formularioAberto.value = true;
};

const excluirOcorrencia = (id) => {
  if (confirm('Tem certeza que deseja excluir esta ocorrência?')) {
    ocorrencias.value = ocorrencias.value.filter(item => item.id !== id);
    atualizarGraficos();
  }
};

const verDetalhes = (ocorrencia) => {
  ocorrenciaSelecionada.value = ocorrencia;
  detalhesAbertos.value = true;
};

const fecharDetalhes = () => {
  detalhesAbertos.value = false;
  ocorrenciaSelecionada.value = null;
};

const aplicarFiltros = () => {
  // Os filtros são aplicados automaticamente através do computed
};

const limparFiltros = () => {
  Object.keys(filtros).forEach(key => {
    filtros[key] = '';
  });
};

// Funções para gráficos
const criarGraficos = () => {
  criarGraficoOcorrenciasPorMes();
  criarGraficoPragasMaisComuns();
  criarGraficoCustoMensal();
};

const criarGraficoOcorrenciasPorMes = () => {
  const ctx = ocorrenciasPorMesChart.value.getContext('2d');
  
  // Processar dados para ocorrências por mês
  const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  const dadosPorMes = Array(12).fill(0);
  
  ocorrencias.value.forEach(ocorrencia => {
    const data = new Date(ocorrencia.data);
    const mes = data.getMonth();
    dadosPorMes[mes]++;
  });
  
  // Criar gráfico
  if (chartInstances.ocorrenciasPorMes) {
    chartInstances.ocorrenciasPorMes.destroy();
  }
  
  chartInstances.ocorrenciasPorMes = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: meses,
      datasets: [{
        label: 'Ocorrências',
        data: dadosPorMes,
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  });
};

const criarGraficoPragasMaisComuns = () => {
  const ctx = pragasMaisComunsChart.value.getContext('2d');
  
  // Processar dados para pragas mais comuns
  const pragasContagem = {};
  ocorrencias.value.forEach(ocorrencia => {
    if (pragasContagem[ocorrencia.pragaDoenca]) {
      pragasContagem[ocorrencia.pragaDoenca]++;
    } else {
      pragasContagem[ocorrencia.pragaDoenca] = 1;
    }
  });
  
  // Ordenar por frequência
  const pragasOrdenadas = Object.entries(pragasContagem)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  
  const labels = pragasOrdenadas.map(item => item[0]);
  const dados = pragasOrdenadas.map(item => item[1]);
  
  // Criar gráfico
  if (chartInstances.pragasMaisComuns) {
    chartInstances.pragasMaisComuns.destroy();
  }
  
  chartInstances.pragasMaisComuns = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Ocorrências',
        data: dados,
        backgroundColor: [
          'rgba(255, 99, 132, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 206, 86, 0.7)',
          'rgba(75, 192, 192, 0.7)',
          'rgba(153, 102, 255, 0.7)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  });
};

const criarGraficoCustoMensal = () => {
  const ctx = custoMensalChart.value.getContext('2d');
  
  // Processar dados para custo mensal
  const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  const custoPorMes = Array(12).fill(0);
  
  ocorrencias.value.forEach(ocorrencia => {
    const data = new Date(ocorrencia.data);
    const mes = data.getMonth();
    custoPorMes[mes] += ocorrencia.custo;
  });
  
  // Criar gráfico
  if (chartInstances.custoMensal) {
    chartInstances.custoMensal.destroy();
  }
  
  chartInstances.custoMensal = new Chart(ctx, {
    type: 'line',
    data: {
      labels: meses,
      datasets: [{
        label: 'Custo (R$)',
        data: custoPorMes,
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
};

const atualizarGraficos = () => {
  criarGraficos();
};

// Montar componente
onMounted(() => {
  criarGraficos();
});
</script>

<style scoped>
.fitossanidade-container {
  width: 100%;
  height: auto;
  padding-bottom: 2rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #333;
}

/* Seção de filtros */
.filters-section {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  min-width: 200px;
}

.btn-aplicar-filtro,
.btn-limpar-filtro {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
  align-self: flex-end;
  margin-top: 1.25rem;
}

.btn-aplicar-filtro {
  background-color: #4CAF50;
  color: white;
}

.btn-limpar-filtro {
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
  margin-left: 0.5rem;
}

/* Seção de dashboard */
.dashboard-section {
  margin-bottom: 2rem;
  width: 100%;
  overflow: visible;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
  min-height: 300px;
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
  position: relative;
  height: 250px;
  width: 100%;
}

/* Botões de ação */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1.5rem;
}

.btn-nova-ocorrencia {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: #1976D2;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-nova-ocorrencia:hover {
  background-color: #1565C0;
}

/* Seção de tabela */
.table-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
}

.table-container {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 2rem;
}

.ocorrencias-table {
  width: 100%;
  min-width: 900px; /* Garante que a tabela tenha um tamanho mínimo */
  border-collapse: collapse;
}

.ocorrencias-table th,
.ocorrencias-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.ocorrencias-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #444;
}

.ocorrencias-table tbody tr:hover {
  background-color: #f8f9fa;
}

.tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.severidade-leve {
  background-color: #e3f2fd;
  color: #1976D2;
}

.severidade-moderada {
  background-color: #fff8e1;
  color: #FFA000;
}

.severidade-grave {
  background-color: #ffebee;
  color: #D32F2F;
}

.acoes {
  display: flex;
  gap: 0.5rem;
}

.btn-acao {
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
}

.btn-acao:hover {
  background-color: #f0f0f0;
}

.btn-deletar:hover {
  background-color: #ffebee;
  color: #D32F2F;
}

.icon-small {
  width: 1rem;
  height: 1rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.btn-fechar {
  background-color: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #777;
}

/* Formulário */
.formulario-ocorrencia {
  padding: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.full-width {
  width: 100%;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.625rem;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.upload-area {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100px;
  border: 2px dashed #ddd;
  border-radius: 0.25rem;
  margin-bottom: 1rem;
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #777;
}

.imagem-preview {
  width: 100%;
  margin-bottom: 1rem;
  border-radius: 0.25rem;
  overflow: hidden;
}

.imagem-preview img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.form-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-cancelar {
  padding: 0.625rem 1.25rem;
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-salvar {
  padding: 0.625rem 1.25rem;
  background-color: #1976D2;
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-salvar:hover {
  background-color: #1565C0;
}

/* Detalhes ocorrência */
.detalhes-ocorrencia {
  padding: 1.5rem;
}

.detalhes-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.detalhes-info {
  flex: 1;
}

.detalhes-info h3 {
  font-size: 1.25rem;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.detalhes-imagem {
  flex: 1;
  display: flex;
  justify-content: center;
}

.detalhes-imagem img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 0.25rem;
  object-fit: contain;
}

.detalhes-body {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detalhes-section h4 {
  font-size: 1rem;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 0.75rem;
  padding-bottom: 0.375rem;
  border-bottom: 1px solid #eee;
}

/* Responsividade */
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    width: 100%;
    margin-bottom: 0.75rem;
  }
}
</style>