<template>
  <div class="fertilizacao-container">
    <!-- Seção de filtros -->
    <div class="filters-section">
      <div class="filter-group">
        <label for="filter-canteiro">Canteiro:</label>
        <select id="filter-canteiro" v-model="filtros.canteiro">
          <option value="">Todos</option>
          <option v-for="canteiro in canteiros" :key="canteiro.id" :value="canteiro.nome">
            {{ canteiro.nome }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label for="filter-especie">Espécie:</label>
        <select id="filter-especie" v-model="filtros.especie">
          <option value="">Todas</option>
          <option v-for="especie in especiesUnicas" :key="especie" :value="especie">{{ especie }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="filter-tipo">Tipo de Fertilizante:</label>
        <select id="filter-tipo" v-model="filtros.tipoFertilizante">
          <option value="">Todos</option>
          <option value="orgânico">Orgânico</option>
          <option value="químico">Químico</option>
          <option value="foliar">Foliar</option>
          <option value="biofertilizante">Biofertilizante</option>
        </select>
      </div>

      <button class="btn-aplicar-filtro" @click="aplicarFiltros">Aplicar filtros</button>
      <button class="btn-limpar-filtro" @click="limparFiltros">Limpar</button>
    </div>

    <!-- Seção de Dashboard/Gráficos -->
    <div class="dashboard-section">
      <div class="dashboard-grid">
        <!-- Custo mensal com fertilização -->
        <div class="dashboard-card">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Custo Mensal com Fertilização
          </h3>
          <div class="chart-container">
            <canvas ref="custoMensalChart"></canvas>
          </div>
        </div>

        <!-- Quantidade total por tipo -->
        <div class="dashboard-card">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Quantidade por Tipo de Fertilizante
          </h3>
          <div class="chart-container">
            <canvas ref="quantidadePorTipoChart"></canvas>
          </div>
        </div>

        <!-- Frequência por espécie -->
        <div class="dashboard-card">
          <h3 class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Frequência de Aplicação por Espécie
          </h3>
          <div class="chart-container">
            <canvas ref="frequenciaPorEspecieChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Botão para nova aplicação -->
    <div v-if="podeCriar" class="action-buttons">
      <button class="btn-nova-aplicacao" @click="abrirFormulario">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nova Aplicação
      </button>
    </div>

    <!-- Tabela de aplicações -->
    <div class="table-section">
      <h2 class="section-title">Aplicações Registradas</h2>
      <div class="table-container">
        <table class="aplicacoes-table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Canteiro</th>
              <th>Espécie</th>
              <th>Tipo</th>
              <th>Nutrientes</th>
              <th>Quantidade</th>
              <th>Forma Aplicação</th>
              <th>Responsável</th>
              <th>Custo (R$)</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="aplicacao in aplicacoesFiltradas" :key="aplicacao.id">
              <td>{{ formatarData(aplicacao.data) }}</td>
              <td>{{ aplicacao.canteiro }}</td>
              <td>{{ aplicacao.especie }}</td>
              <td>{{ aplicacao.tipoFertilizante }}</td>
              <td>{{ aplicacao.nutrientes }}</td>
              <td>{{ aplicacao.quantidade }} {{ aplicacao.unidade }}</td>
              <td>{{ aplicacao.formaAplicacao }}</td>
              <td>{{ aplicacao.responsavel }}</td>
              <td>R$ {{ aplicacao.custo.toFixed(2) }}</td>
              <td class="acoes">
                <button class="btn-acao" @click="verDetalhes(aplicacao)" title="Ver detalhes">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon-small" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button v-if="podeEditar" class="btn-acao" @click="editarAplicacao(aplicacao)" title="Editar">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon-small" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button v-if="podeEditar" class="btn-acao btn-deletar" @click="excluirAplicacao(aplicacao.id)" title="Excluir">
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
    <AppModalOverlay
      :aberto="formularioAberto"
      :handlers="modalCloseFormulario"
      panel-class="app-modal-panel--xl"
    >
      <div class="modal-header">
          <h2 class="modal-title">{{ modoEdicao ? 'Editar Aplicação' : 'Nova Aplicação' }}</h2>
          <button class="btn-fechar" @click="fecharFormulario">×</button>
        </div>
        <form @submit.prevent="salvarAplicacao" class="formulario-aplicacao">
          <div class="form-row">
            <div class="form-group">
              <label for="canteiro">Canteiro:</label>
              <select id="canteiro" v-model="aplicacaoForm.canteiro" required>
                <option value="">Selecione um canteiro</option>
                <option v-for="canteiro in canteiros" :key="canteiro.id" :value="canteiro.nome">
                  {{ canteiro.nome }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="especie">Espécie:</label>
              <input type="text" id="especie" v-model="aplicacaoForm.especie" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="data">Data:</label>
              <input type="date" id="data" v-model="aplicacaoForm.data" required>
            </div>
            
            <div class="form-group">
              <label for="tipo-fertilizante">Tipo de Fertilizante:</label>
              <select id="tipo-fertilizante" v-model="aplicacaoForm.tipoFertilizante" required>
                <option value="orgânico">Orgânico</option>
                <option value="químico">Químico</option>
                <option value="foliar">Foliar</option>
                <option value="biofertilizante">Biofertilizante</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="nutrientes">Nutrientes Principais:</label>
              <input type="text" id="nutrientes" v-model="aplicacaoForm.nutrientes" placeholder="ex: NPK 10-10-10">
            </div>
            
            <div class="form-group">
              <label for="responsavel">Responsável:</label>
              <input type="text" id="responsavel" v-model="aplicacaoForm.responsavel" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="quantidade">Quantidade:</label>
              <div class="quantidade-input">
                <input type="number" id="quantidade" v-model="aplicacaoForm.quantidade" step="0.01" min="0" required>
                <select v-model="aplicacaoForm.unidade">
                  <option value="kg">kg</option>
                  <option value="L">L</option>
                  <option value="g">g</option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="custo">Custo (R$):</label>
              <input type="number" id="custo" v-model="aplicacaoForm.custo" step="0.01" min="0">
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="forma-aplicacao">Forma de Aplicação:</label>
              <select id="forma-aplicacao" v-model="aplicacaoForm.formaAplicacao" required>
                <option value="aspersão">Aspersão</option>
                <option value="gotejo">Gotejo</option>
                <option value="manual">Manual</option>
                <option value="fertirrigação">Fertirrigação</option>
              </select>
            </div>
          </div>
          
          <div class="form-group full-width">
            <label for="observacoes">Observações:</label>
            <textarea id="observacoes" v-model="aplicacaoForm.observacoes" rows="4"></textarea>
          </div>
          
          <div class="form-buttons">
            <button type="button" class="btn-cancelar" @click="fecharFormulario">Cancelar</button>
            <button type="submit" class="btn-salvar">Salvar</button>
          </div>
        </form>
    </AppModalOverlay>
    <ConfirmSaidaModal
      :aberto="confirmAbertoFormulario"
      @confirmar="confirmarSaidaFormulario"
      @cancelar="cancelarSaidaFormulario"
    />

    <!-- Modal de detalhes -->
    <AppModalOverlay
      :aberto="detalhesAbertos"
      :handlers="modalCloseDetalhes"
      panel-class="app-modal-panel--xl"
    >
      <div class="modal-header">
          <h2 class="modal-title">Detalhes da Aplicação</h2>
          <button class="btn-fechar" @click="fecharDetalhes">×</button>
        </div>
        <div class="detalhes-aplicacao" v-if="aplicacaoSelecionada">
          <div class="detalhes-header">
            <div class="detalhes-info">
              <h3>{{ aplicacaoSelecionada.tipoFertilizante }}</h3>
              <p><strong>Data:</strong> {{ formatarData(aplicacaoSelecionada.data) }}</p>
              <p><strong>Canteiro:</strong> {{ aplicacaoSelecionada.canteiro }}</p>
              <p><strong>Espécie:</strong> {{ aplicacaoSelecionada.especie }}</p>
            </div>
          </div>
          
          <div class="detalhes-body">
            <div class="detalhes-section">
              <h4>Informações do Fertilizante</h4>
              <p><strong>Nutrientes:</strong> {{ aplicacaoSelecionada.nutrientes || 'Não especificado' }}</p>
              <p><strong>Quantidade:</strong> {{ aplicacaoSelecionada.quantidade }} {{ aplicacaoSelecionada.unidade }}</p>
              <p><strong>Forma de Aplicação:</strong> {{ aplicacaoSelecionada.formaAplicacao }}</p>
            </div>
            
            <div class="detalhes-section">
              <h4>Informações Adicionais</h4>
              <p><strong>Responsável:</strong> {{ aplicacaoSelecionada.responsavel }}</p>
              <p><strong>Custo:</strong> R$ {{ aplicacaoSelecionada.custo.toFixed(2) }}</p>
              <p><strong>Observações:</strong> {{ aplicacaoSelecionada.observacoes || 'Nenhuma observação' }}</p>
            </div>
          </div>
        </div>
    </AppModalOverlay>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { useSimpleModalClose } from '@/composables/useSimpleModalClose'
import { useFormDirty } from '@/utils/formDirty'
import { usePermissions } from '@/composables/usePermissions'
import { listCanteiros } from '@/services/canteiros'
import { listPlantasComRelacoes } from '@/services/plantas'
import { listAtividades, listTiposAtividades, createAtividade } from '@/services/atividades'
import { useAuthStore } from '@/store/auth'
import {
  CHART_PRIMARY,
  CHART_PRIMARY_DARK,
  CHART_SUCCESS,
  CHART_WARNING,
  CHART_INFO,
  withAlpha,
} from '@/constants/chartColors'

const auth = useAuthStore()
const { can } = usePermissions()
const podeCriar = computed(() => can('fertilizacao.create'))
const podeEditar = computed(() => can('fertilizacao.edit'))
const canteiros = ref([])
const plantas = ref([])
const tipoFertilizacaoId = ref(null)
const aplicacoes = ref([])

function mapAtividade(a) {
  return {
    id: a.id,
    data: String(a.data_atividade).slice(0, 10),
    canteiro: '—',
    especie: a.especie_nome,
    tipoFertilizante: 'atividade',
    nutrientes: a.descricao || a.tipo_atividade_nome,
    quantidade: 1,
    unidade: '—',
    formaAplicacao: 'manual',
    responsavel: a.funcionario_nome,
    custo: Number(a.custo_atividade) || 0,
    observacoes: a.observacoes || ''
  }
}

async function carregarFertilizacao() {
  const [cant, pl, tipos, ativ] = await Promise.all([
    listCanteiros({ ativo: true }),
    listPlantasComRelacoes({ limit: 300 }),
    listTiposAtividades(),
    listAtividades({ limit: 200 })
  ])
  canteiros.value = cant
  plantas.value = pl
  const fert = tipos.find((t) => t.nome === 'FERTILIZACAO')
  tipoFertilizacaoId.value = fert?.id
  aplicacoes.value = ativ
    .filter((a) => !tipoFertilizacaoId.value || a.id_tipo_atividade === tipoFertilizacaoId.value)
    .map(mapAtividade)
  atualizarGraficos()
}

onMounted(carregarFertilizacao)

// Formulário para nova aplicação
const aplicacaoForm = reactive({
  id: null,
  data: '',
  canteiro: '',
  especie: '',
  tipoFertilizante: 'orgânico',
  nutrientes: '',
  quantidade: 0,
  unidade: 'kg',
  formaAplicacao: 'manual',
  responsavel: '',
  custo: 0,
  observacoes: ''
});

// Estados de UI
const formularioAberto = ref(false);
const modoEdicao = ref(false);
const detalhesAbertos = ref(false);
const aplicacaoSelecionada = ref(null);

const { isDirty: isDirtyFormulario, rebase: rebaseFormulario } = useFormDirty(
  aplicacaoForm,
  () => formularioAberto.value
);

// Filtros
const filtros = reactive({
  canteiro: '',
  especie: '',
  tipoFertilizante: ''
});

// Computadas
const especiesUnicas = computed(() => {
  const especies = new Set();
  aplicacoes.value.forEach(aplicacao => especies.add(aplicacao.especie));
  return [...especies];
});

const aplicacoesFiltradas = computed(() => {
  let resultado = [...aplicacoes.value];
  
  if (filtros.canteiro) {
    resultado = resultado.filter(item => item.canteiro === filtros.canteiro);
  }
  
  if (filtros.especie) {
    resultado = resultado.filter(item => item.especie === filtros.especie);
  }
  
  if (filtros.tipoFertilizante) {
    resultado = resultado.filter(item => item.tipoFertilizante === filtros.tipoFertilizante);
  }
  
  return resultado.sort((a, b) => new Date(b.data) - new Date(a.data));
});

// Elementos de gráficos
const custoMensalChart = ref(null);
const quantidadePorTipoChart = ref(null);
const frequenciaPorEspecieChart = ref(null);
let chartInstances = {
  custoMensal: null,
  quantidadePorTipo: null,
  frequenciaPorEspecie: null
};

// Funções
const formatarData = (data) => {
  return new Date(data).toLocaleDateString('pt-BR');
};

const abrirFormulario = async () => {
  if (!podeCriar.value) return
  modoEdicao.value = false;
  resetarFormulario();
  formularioAberto.value = true;
  await nextTick();
  rebaseFormulario();
};

const fecharFormularioInterno = () => {
  formularioAberto.value = false;
  resetarFormulario();
};

const modalCloseFormulario = useModalFormClose(
  fecharFormularioInterno,
  () => isDirtyFormulario.value,
  () => formularioAberto.value,
)
const {
  resetOverlayPress: resetOverlayPressFormulario,
  confirmAberto: confirmAbertoFormulario,
  confirmarSaida: confirmarSaidaFormulario,
  cancelarSaida: cancelarSaidaFormulario,
  requestClose: requestCloseFormulario,
  sairSemConfirmar: sairSemConfirmarFormulario,
} = modalCloseFormulario

const fecharFormulario = () => {
  resetOverlayPressFormulario()
  requestCloseFormulario()
}

const resetarFormulario = () => {
  Object.keys(aplicacaoForm).forEach(key => {
    if (key === 'tipoFertilizante') {
      aplicacaoForm[key] = 'orgânico';
    } else if (key === 'formaAplicacao') {
      aplicacaoForm[key] = 'manual';
    } else if (key === 'quantidade' || key === 'custo') {
      aplicacaoForm[key] = 0;
    } else if (key === 'unidade') {
      aplicacaoForm[key] = 'kg';
    } else {
      aplicacaoForm[key] = '';
    }
  });
  aplicacaoForm.id = null;
};

const salvarAplicacao = async () => {
  if (!tipoFertilizacaoId.value || !auth.user?.id) {
    alert('Tipo FERTILIZACAO ou usuário não disponível.')
    return
  }
  const planta = plantas.value[0]
  if (!planta) {
    alert('Cadastre plantas no viveiro primeiro.')
    return
  }
  try {
    await createAtividade({
      id_tipo_atividade: tipoFertilizacaoId.value,
      id_planta: planta.id,
      id_funcionario: auth.user.id,
      data_atividade: new Date(aplicacaoForm.data + 'T12:00:00').toISOString(),
      descricao: `${aplicacaoForm.nutrientes} (${aplicacaoForm.tipoFertilizante})`,
      custo_atividade: aplicacaoForm.custo || 0,
      observacoes: aplicacaoForm.observacoes
    })
    sairSemConfirmarFormulario()
    await carregarFertilizacao()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao registrar fertilização.')
  }
}

const editarAplicacao = async (aplicacao) => {
  if (!podeEditar.value) return
  modoEdicao.value = true;
  Object.keys(aplicacaoForm).forEach(key => {
    aplicacaoForm[key] = aplicacao[key];
  });
  formularioAberto.value = true;
  await nextTick();
  rebaseFormulario();
};

const excluirAplicacao = (id) => {
  if (!podeEditar.value) return
  if (confirm('Tem certeza que deseja excluir esta aplicação?')) {
    aplicacoes.value = aplicacoes.value.filter(item => item.id !== id);
    atualizarGraficos();
  }
};

const verDetalhes = (aplicacao) => {
  aplicacaoSelecionada.value = aplicacao;
  detalhesAbertos.value = true;
};

const fecharDetalhesInterno = () => {
  detalhesAbertos.value = false;
  aplicacaoSelecionada.value = null;
};

const modalCloseDetalhes = useSimpleModalClose(fecharDetalhesInterno, () => detalhesAbertos.value)

const fecharDetalhes = () => {
  modalCloseDetalhes.resetOverlayPress()
  fecharDetalhesInterno()
}

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
  criarGraficoCustoMensal();
  criarGraficoQuantidadePorTipo();
  criarGraficoFrequenciaPorEspecie();
};

const criarGraficoCustoMensal = () => {
  const ctx = custoMensalChart.value.getContext('2d');
  
  // Processar dados para custo mensal
  const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  const custoPorMes = Array(12).fill(0);
  
  aplicacoes.value.forEach(aplicacao => {
    const data = new Date(aplicacao.data);
    const mes = data.getMonth();
    custoPorMes[mes] += aplicacao.custo;
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
        backgroundColor: withAlpha(CHART_INFO, 0.18),
        borderColor: CHART_INFO,
        borderWidth: 2,
        tension: 0.15,
        fill: true,
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

const criarGraficoQuantidadePorTipo = () => {
  const ctx = quantidadePorTipoChart.value.getContext('2d');
  
  // Processar dados para quantidade por tipo
  const tiposFertilizantes = ['orgânico', 'químico', 'foliar', 'biofertilizante'];
  const quantidadePorTipo = {
    'orgânico': { kg: 0, L: 0, g: 0 },
    'químico': { kg: 0, L: 0, g: 0 },
    'foliar': { kg: 0, L: 0, g: 0 },
    'biofertilizante': { kg: 0, L: 0, g: 0 }
  };
  
  aplicacoes.value.forEach(aplicacao => {
    const tipo = aplicacao.tipoFertilizante;
    const unidade = aplicacao.unidade;
    quantidadePorTipo[tipo][unidade] += aplicacao.quantidade;
  });
  
  // Convertendo para formato adequado para o gráfico
  const datasets = [
    {
      label: 'kg',
      data: tiposFertilizantes.map(tipo => quantidadePorTipo[tipo].kg),
      backgroundColor: withAlpha(CHART_PRIMARY, 0.8),
      borderColor: CHART_PRIMARY_DARK,
      borderWidth: 1,
    },
    {
      label: 'L',
      data: tiposFertilizantes.map(tipo => quantidadePorTipo[tipo].L),
      backgroundColor: withAlpha(CHART_SUCCESS, 0.85),
      borderColor: CHART_SUCCESS,
      borderWidth: 1,
    },
    {
      label: 'g',
      data: tiposFertilizantes.map(tipo => quantidadePorTipo[tipo].g),
      backgroundColor: withAlpha(CHART_WARNING, 0.85),
      borderColor: CHART_WARNING,
      borderWidth: 1,
    }
  ];
  
  // Criar gráfico
  if (chartInstances.quantidadePorTipo) {
    chartInstances.quantidadePorTipo.destroy();
  }
  
  chartInstances.quantidadePorTipo = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: tiposFertilizantes.map(tipo => tipo.charAt(0).toUpperCase() + tipo.slice(1)),
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Quantidade'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Tipo de Fertilizante'
          }
        }
      }
    }
  });
};

const criarGraficoFrequenciaPorEspecie = () => {
  const ctx = frequenciaPorEspecieChart.value.getContext('2d');
  
  // Processar dados para frequência por espécie
  const frequenciaPorEspecie = {};
  aplicacoes.value.forEach(aplicacao => {
    if (frequenciaPorEspecie[aplicacao.especie]) {
      frequenciaPorEspecie[aplicacao.especie]++;
    } else {
      frequenciaPorEspecie[aplicacao.especie] = 1;
    }
  });
  
  // Ordenar por frequência
  const especiesOrdenadas = Object.entries(frequenciaPorEspecie)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  
  const labels = especiesOrdenadas.map(item => {
    // Extrair nome principal, sem o nome científico entre parênteses
    const nome = item[0].split('(')[0].trim();
    return nome;
  });
  const dados = especiesOrdenadas.map(item => item[1]);
  
  // Criar gráfico
  if (chartInstances.frequenciaPorEspecie) {
    chartInstances.frequenciaPorEspecie.destroy();
  }
  
  chartInstances.frequenciaPorEspecie = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Número de Aplicações',
        data: dados,
        backgroundColor: withAlpha(CHART_PRIMARY, 0.8),
        borderColor: CHART_PRIMARY_DARK,
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
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

const atualizarGraficos = () => {
  criarGraficos();
};
</script>

<style scoped>
.fertilizacao-container {
  width: 100%;
  padding: 1.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--color-text-primary);
}

/* Seção de filtros */
.filters-section {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: var(--color-surface-muted);
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
  color: var(--color-text-secondary);
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
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
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-limpar-filtro {
  background-color: var(--color-surface-muted);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  margin-left: 0.5rem;
}

/* Seção de dashboard */
.dashboard-section {
  margin-bottom: 2rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.dashboard-card {
  background-color: var(--color-text-inverse);
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 1rem;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
  color: var(--color-info);
}

.chart-container {
  height: 250px;
  width: 100%;
  position: relative;
}

/* Botões de ação */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1.5rem;
}

.btn-nova-aplicacao {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: var(--color-info);
  color: var(--color-text-inverse);
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-nova-aplicacao:hover {
  background-color: var(--color-info-dark);
}

/* Seção de tabela */
.table-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.table-container {
  background-color: var(--color-text-inverse);
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.aplicacoes-table {
  width: 100%;
  border-collapse: collapse;
}

.aplicacoes-table th,
.aplicacoes-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border-subtle);
}

.aplicacoes-table th {
  background-color: var(--color-surface-muted);
  font-weight: 600;
  color: var(--color-text-primary);
}

.aplicacoes-table tbody tr:hover {
  background-color: var(--color-surface-muted);
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
  background-color: var(--color-surface-muted);
}

.btn-deletar:hover {
  background-color: var(--color-error-bg);
  color: var(--color-error);
}

.icon-small {
  width: 1rem;
  height: 1rem;
}

/* Modal */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.btn-fechar {
  background-color: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-muted);
}

/* Formulário */
.formulario-aplicacao {
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
  color: var(--color-text-secondary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.625rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.quantidade-input {
  display: flex;
}

.quantidade-input input {
  flex: 1;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.quantidade-input select {
  width: 60px;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  border-left: none;
}

.form-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-cancelar {
  padding: 0.625rem 1.25rem;
  background-color: var(--color-surface-muted);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-salvar {
  padding: 0.625rem 1.25rem;
  background-color: var(--color-info);
  color: var(--color-text-inverse);
  border: none;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-salvar:hover {
  background-color: var(--color-info-dark);
}

/* Detalhes aplicação */
.detalhes-aplicacao {
  padding: 1.5rem;
}

.detalhes-header {
  margin-bottom: 1.5rem;
}

.detalhes-info h3 {
  font-size: 1.25rem;
  margin-top: 0;
  margin-bottom: 0.5rem;
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
  border-bottom: 1px solid var(--color-border-subtle);
}

/* Responsividade */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    flex-direction: column;
  }
}
</style> 