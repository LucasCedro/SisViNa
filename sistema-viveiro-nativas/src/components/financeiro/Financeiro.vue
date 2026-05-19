<template>
  <div class="financeiro-container">
    <!-- Cabeçalho e Tipo de Viveiro -->
    <div class="cabecalho">
      <h1 class="titulo">Financeiro do Viveiro</h1>
      <div class="tipo-viveiro">
        <label for="tipoViveiro" class="label">Tipo de Viveiro:</label>
        <select id="tipoViveiro" v-model="tipoViveiro" class="select-tipo">
          <option value="mecanizado">Viveiro com Mecanização</option>
          <option value="manual">Viveiro Manual</option>
          <option value="urbano">Viveiro Urbano</option>
          <option value="outro">Outro</option>
        </select>
      </div>
    </div>

    <!-- Resumo Financeiro -->
    <div class="secao">
      <h2 class="subtitulo">Resumo Financeiro</h2>
      <div class="grid-cards">
        <div class="card-resumo">
          <div class="card-icone capex">
            <svg xmlns="http://www.w3.org/2000/svg" class="icone" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
            </svg>
          </div>
          <div class="card-conteudo">
            <h3 class="card-titulo">Total CAPEX</h3>
            <p class="card-valor">{{ formatarMoeda(resumoFinanceiro.totalCapex) }}</p>
          </div>
        </div>

        <div class="card-resumo">
          <div class="card-icone opex">
            <svg xmlns="http://www.w3.org/2000/svg" class="icone" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-14a3 3 0 00-3 3v2H7a1 1 0 000 2h1v1a1 1 0 01-1 1 1 1 0 100 2h6a1 1 0 100-2H9.83c.11-.313.17-.65.17-1v-1h1a1 1 0 100-2h-1V7a1 1 0 112 0 1 1 0 102 0 3 3 0 00-3-3z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="card-conteudo">
            <h3 class="card-titulo">Total OPEX</h3>
            <p class="card-valor">{{ formatarMoeda(resumoFinanceiro.totalOpex) }}</p>
          </div>
        </div>

        <div class="card-resumo">
          <div class="card-icone mensal">
            <svg xmlns="http://www.w3.org/2000/svg" class="icone" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="card-conteudo">
            <h3 class="card-titulo">Total Mês Atual</h3>
            <p class="card-valor">{{ formatarMoeda(resumoFinanceiro.totalMesAtual) }}</p>
          </div>
        </div>

        <div class="card-resumo">
          <div class="card-icone anual">
            <svg xmlns="http://www.w3.org/2000/svg" class="icone" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="card-conteudo">
            <h3 class="card-titulo">Total Ano</h3>
            <p class="card-valor">{{ formatarMoeda(resumoFinanceiro.totalAno) }}</p>
          </div>
        </div>

        <div class="card-resumo">
          <div class="card-icone muda">
            <svg xmlns="http://www.w3.org/2000/svg" class="icone" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm-7-8a7 7 0 1114 0 7 7 0 01-14 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="card-conteudo">
            <h3 class="card-titulo">Custo por Muda</h3>
            <p class="card-valor">{{ formatarMoeda(resumoFinanceiro.custoPorMuda) }}</p>
          </div>
        </div>

        <div class="card-resumo">
          <div class="card-icone previsao">
            <svg xmlns="http://www.w3.org/2000/svg" class="icone" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 0l-2 2a1 1 0 101.414 1.414L8 10.414l1.293 1.293a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="card-conteudo">
            <h3 class="card-titulo">Previsão até Dez</h3>
            <p class="card-valor">{{ formatarMoeda(resumoFinanceiro.previsaoFimAno) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Gráficos -->
    <div class="secao">
      <h2 class="subtitulo">Dashboards</h2>
      <div class="grid-graficos">
        <div class="grafico-container">
          <h3 class="grafico-titulo">Distribuição OPEX por Categoria</h3>
          <div class="grafico-barras-horizontais">
            <div v-for="(item, index) in distribuicaoOpex" :key="`barra-h-${index}`" class="barra-horizontal-container">
              <div class="barra-horizontal-info">
                <span class="barra-horizontal-label">{{ item.categoria }}</span>
                <span class="barra-horizontal-valor">{{ formatarMoeda(item.valor) }} ({{ item.porcentagem }}%)</span>
              </div>
              <div class="barra-horizontal-wrapper">
                <div class="barra-horizontal-valor" 
                     :style="{ width: `${item.porcentagem}%`, backgroundColor: item.cor }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="grafico-container">
          <h3 class="grafico-titulo">Comparação CAPEX por Tipo</h3>
          <div class="grafico-barras-verticais">
            <div v-for="(item, index) in comparacaoCapex" :key="`barra-v-${index}`" class="barra-vertical-container">
              <div class="barra-vertical-wrapper">
                <div class="barra-vertical-valor group" :style="{ height: `${item.altura}%`, backgroundColor: item.cor }">
                  <div class="barra-vertical-tooltip">{{ formatarMoeda(item.valor) }}</div>
                </div>
              </div>
              <div class="barra-vertical-label">{{ item.categoria.split(' ')[0] }}</div>
            </div>
          </div>
          <div class="grafico-legenda">
            <div v-for="(item, index) in comparacaoCapex" :key="`legenda-v-${index}`" class="legenda-item-vertical">
              <span class="legenda-cor" :style="{ backgroundColor: item.cor }"></span>
              <span class="legenda-texto">{{ item.categoria }} ({{ item.porcentagem }}%)</span>
            </div>
          </div>
        </div>

        <div class="grafico-container grafico-largo">
          <h3 class="grafico-titulo">Evolução de Gastos Mensais</h3>
          <div class="grafico-linha">
            <div class="grafico-linha-eixoy">
              <div v-for="n in 5" :key="`eixoy-${n}`" class="linha-eixoy-valor">
                {{ formatarMoeda((5-n+1) * 10000) }}
              </div>
            </div>
            <div class="grafico-linha-conteudo">
              <div class="grafico-linha-grid">
                <div v-for="n in 12" :key="`grid-${n}`" class="linha-grid"></div>
              </div>
              <div class="grafico-linha-dados">
                <svg width="100%" height="200" viewBox="0 0 1200 200" preserveAspectRatio="none">
                  <!-- Área sombreada sob a linha -->
                  <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#2c5282" stop-opacity="0.3" />
                    <stop offset="100%" stop-color="#2c5282" stop-opacity="0.05" />
                  </linearGradient>
                  <path :d="`M0,${200 - (evolucaoGastos[0].valor / 50000 * 200)} ${pontosGraficoLinha} 1200,200 0,200`" 
                        fill="url(#areaGradient)" />
                  
                  <!-- Linha principal -->
                  <polyline 
                    :points="pontosGraficoLinha" 
                    fill="none" 
                    stroke="#2c5282" 
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round" 
                  />
                </svg>
                <div v-for="(ponto, index) in evolucaoGastos" :key="`ponto-${index}`" 
                    class="ponto-dados" 
                    :style="{ left: `${(index / (evolucaoGastos.length-1)) * 100}%`, bottom: `${(ponto.valor / 50000) * 100}%` }">
                  <div class="tooltip-ponto">{{ formatarMoeda(ponto.valor) }}</div>
                </div>
              </div>
              <div class="grafico-linha-eixox">
                <div v-for="(mes, index) in mesesAbreviados" :key="`eixox-${index}`" class="linha-eixox-valor">
                  {{ mes }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Separação por Tipo de Custo (Abas) -->
    <div class="secao">
      <h2 class="subtitulo">Controle de Custos</h2>
      
      <div class="abas-container">
        <div class="abas-navegacao">
          <button 
            @click="abaAtiva = 'capex'" 
            :class="['aba-btn', { ativo: abaAtiva === 'capex' }]"
          >
            CAPEX (Investimentos)
          </button>
          <button 
            @click="abaAtiva = 'opex'" 
            :class="['aba-btn', { ativo: abaAtiva === 'opex' }]"
          >
            OPEX (Operacionais)
          </button>
        </div>
        
        <div class="abas-conteudo">
          <!-- Conteúdo CAPEX -->
          <div v-if="abaAtiva === 'capex'" class="aba-painel">
            <div class="painel-cabecalho">
              <div class="filtros">
                <div class="filtro-grupo">
                  <label class="filtro-label">Data Inicial:</label>
                  <input type="date" v-model="filtros.dataInicial" class="filtro-input" />
                </div>
                <div class="filtro-grupo">
                  <label class="filtro-label">Data Final:</label>
                  <input type="date" v-model="filtros.dataFinal" class="filtro-input" />
                </div>
                <div class="filtro-grupo">
                  <label class="filtro-label">Categoria:</label>
                  <select v-model="filtros.categoriaCapex" class="filtro-input">
                    <option value="">Todas</option>
                    <option v-for="cat in categoriasCapex" :key="cat" :value="cat">{{ cat }}</option>
                  </select>
                </div>
                <button @click="aplicarFiltros" class="btn-aplicar">Aplicar</button>
                <button @click="limparFiltros" class="btn-limpar">Limpar</button>
              </div>
              <button @click="abrirModalNovoCusto('CAPEX')" class="btn-adicionar">
                <svg xmlns="http://www.w3.org/2000/svg" class="btn-icone" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                Novo CAPEX
              </button>
            </div>
            
            <div class="tabela-container">
              <table class="tabela">
                <thead>
                  <tr>
                    <th>Descrição</th>
                    <th>Categoria</th>
                    <th>Data</th>
                    <th>Valor</th>
                    <th>Forma de Pagamento</th>
                    <th>Observações</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in custosCapexFiltrados" :key="item.id">
                    <td>{{ item.descricao }}</td>
                    <td>{{ item.categoria }}</td>
                    <td>{{ formatarData(item.data) }}</td>
                    <td class="coluna-valor">{{ formatarMoeda(item.valor) }}</td>
                    <td>{{ item.formaPagamento }}</td>
                    <td>{{ item.observacoes }}</td>
                    <td class="coluna-acoes">
                      <button @click="editarCusto(item)" class="btn-acao editar">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icone-acao" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                        </svg>
                      </button>
                      <button @click="excluirCusto(item.id)" class="btn-acao excluir">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icone-acao" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="custosCapexFiltrados.length === 0">
                    <td colspan="7" class="mensagem-vazia">Nenhum registro encontrado.</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="3" class="total-label">Total:</td>
                    <td class="total-valor">{{ formatarMoeda(totalCapexFiltrado) }}</td>
                    <td colspan="3"></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
          
          <!-- Conteúdo OPEX -->
          <div v-if="abaAtiva === 'opex'" class="aba-painel">
            <div class="painel-cabecalho">
              <div class="filtros">
                <div class="filtro-grupo">
                  <label class="filtro-label">Data Inicial:</label>
                  <input type="date" v-model="filtros.dataInicial" class="filtro-input" />
                </div>
                <div class="filtro-grupo">
                  <label class="filtro-label">Data Final:</label>
                  <input type="date" v-model="filtros.dataFinal" class="filtro-input" />
                </div>
                <div class="filtro-grupo">
                  <label class="filtro-label">Categoria:</label>
                  <select v-model="filtros.categoriaOpex" class="filtro-input">
                    <option value="">Todas</option>
                    <option v-for="cat in categoriasOpex" :key="cat" :value="cat">{{ cat }}</option>
                  </select>
                </div>
                <button @click="aplicarFiltros" class="btn-aplicar">Aplicar</button>
                <button @click="limparFiltros" class="btn-limpar">Limpar</button>
              </div>
              <button @click="abrirModalNovoCusto('OPEX')" class="btn-adicionar">
                <svg xmlns="http://www.w3.org/2000/svg" class="btn-icone" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                Novo OPEX
              </button>
            </div>
            
            <div class="tabela-container">
              <table class="tabela">
                <thead>
                  <tr>
                    <th>Descrição</th>
                    <th>Categoria</th>
                    <th>Data</th>
                    <th>Valor</th>
                    <th>Forma de Pagamento</th>
                    <th>Observações</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in custosOpexFiltrados" :key="item.id">
                    <td>{{ item.descricao }}</td>
                    <td>{{ item.categoria }}</td>
                    <td>{{ formatarData(item.data) }}</td>
                    <td class="coluna-valor">{{ formatarMoeda(item.valor) }}</td>
                    <td>{{ item.formaPagamento }}</td>
                    <td>{{ item.observacoes }}</td>
                    <td class="coluna-acoes">
                      <button @click="editarCusto(item)" class="btn-acao editar">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icone-acao" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                        </svg>
                      </button>
                      <button @click="excluirCusto(item.id)" class="btn-acao excluir">
                        <svg xmlns="http://www.w3.org/2000/svg" class="icone-acao" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="custosOpexFiltrados.length === 0">
                    <td colspan="7" class="mensagem-vazia">Nenhum registro encontrado.</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="3" class="total-label">Total:</td>
                    <td class="total-valor">{{ formatarMoeda(totalOpexFiltrado) }}</td>
                    <td colspan="3"></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Adição/Edição de Custo -->
    <div v-if="modalAberto" class="modal-overlay" @click="fecharModal">
      <div class="modal-conteudo" @click.stop>
        <div class="modal-cabecalho">
          <h2 class="modal-titulo">{{ custoEmEdicao.id ? 'Editar' : 'Adicionar' }} {{ custoEmEdicao.tipo }}</h2>
          <button class="btn-fechar" @click="fecharModal">
            <svg xmlns="http://www.w3.org/2000/svg" class="icone-fechar" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <div class="modal-corpo">
          <form @submit.prevent="salvarCusto" class="formulario">
            <div class="form-grupo">
              <label class="form-label">Descrição:</label>
              <input type="text" v-model="custoEmEdicao.descricao" required class="form-input" />
            </div>
            
            <div class="form-grupo">
              <label class="form-label">Categoria:</label>
              <select v-model="custoEmEdicao.categoria" required class="form-input">
                <option v-for="cat in custoEmEdicao.tipo === 'CAPEX' ? categoriasCapex : categoriasOpex" 
                       :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>
            
            <div class="form-grupo">
              <label class="form-label">Data:</label>
              <input type="date" v-model="custoEmEdicao.data" required class="form-input" />
            </div>
            
            <div class="form-grupo">
              <label class="form-label">Valor (R$):</label>
              <input type="number" v-model="custoEmEdicao.valor" step="0.01" min="0" required class="form-input" />
            </div>
            
            <div class="form-grupo">
              <label class="form-label">Forma de Pagamento:</label>
              <select v-model="custoEmEdicao.formaPagamento" required class="form-input">
                <option value="Dinheiro">Dinheiro</option>
                <option value="Cartão de Crédito">Cartão de Crédito</option>
                <option value="Cartão de Débito">Cartão de Débito</option>
                <option value="Transferência Bancária">Transferência Bancária</option>
                <option value="Pix">Pix</option>
                <option value="Boleto Bancário">Boleto Bancário</option>
              </select>
            </div>
            
            <div class="form-grupo">
              <label class="form-label">Observações:</label>
              <textarea v-model="custoEmEdicao.observacoes" class="form-textarea"></textarea>
            </div>
            
            <div class="form-acoes">
              <button type="button" @click="fecharModal" class="btn-cancelar">Cancelar</button>
              <button type="submit" class="btn-salvar">Salvar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

// Configuração inicial
const tipoViveiro = ref('mecanizado');
const abaAtiva = ref('capex');
const modalAberto = ref(false);

// Dados para filtros
const filtros = ref({
  dataInicial: '',
  dataFinal: '',
  categoriaCapex: '',
  categoriaOpex: ''
});

// Listas de categorias
const categoriasCapex = [
  'Construção e Infraestrutura',
  'Máquinas e Equipamentos',
  'Sistemas de Irrigação',
  'Veículos',
  'Terrenos',
  'Ferramentas Permanentes',
  'Estufas e Estruturas',
  'Tecnologia e Software'
];

const categoriasOpex = [
  'Insumos',
  'Mão de Obra',
  'Manutenção',
  'Energia e Água',
  'Combustível',
  'Embalagens',
  'EPIs',
  'Transporte',
  'Aluguel',
  'Seguros',
  'Impostos e Taxas',
  'Administrativo'
];

// Mock de dados para custos
const custos = ref([
  {
    id: 1,
    tipo: "CAPEX",
    descricao: "Construção de estufa principal",
    categoria: "Estufas e Estruturas",
    data: "2025-01-15",
    valor: 85000.00,
    formaPagamento: "Transferência Bancária",
    observacoes: "Estrutura metálica com cobertura em arco, área de 500m²"
  },
  {
    id: 2,
    tipo: "CAPEX",
    descricao: "Aquisição de trator compacto",
    categoria: "Máquinas e Equipamentos",
    data: "2025-02-10",
    valor: 45000.00,
    formaPagamento: "Financiamento",
    observacoes: "Modelo TX-450 com implementos básicos"
  },
  {
    id: 3,
    tipo: "CAPEX",
    descricao: "Sistema de irrigação automatizado",
    categoria: "Sistemas de Irrigação",
    data: "2025-02-25",
    valor: 32000.00,
    formaPagamento: "Cartão de Crédito",
    observacoes: "Sistema por gotejamento com controlador digital"
  },
  {
    id: 4,
    tipo: "CAPEX",
    descricao: "Bancadas para mudas",
    categoria: "Estufas e Estruturas",
    data: "2025-03-05",
    valor: 12500.00,
    formaPagamento: "Transferência Bancária",
    observacoes: "15 bancadas de concreto com 2,5m x 1,2m cada"
  },
  {
    id: 5,
    tipo: "CAPEX",
    descricao: "Software de gestão de viveiro",
    categoria: "Tecnologia e Software",
    data: "2025-03-20",
    valor: 8500.00,
    formaPagamento: "Boleto Bancário",
    observacoes: "Licença permanente com 2 anos de suporte"
  },
  {
    id: 6,
    tipo: "OPEX",
    descricao: "Folha de pagamento - Janeiro",
    categoria: "Mão de Obra",
    data: "2025-01-05",
    valor: 15000.00,
    formaPagamento: "Transferência Bancária",
    observacoes: "5 funcionários fixos"
  },
  {
    id: 7,
    tipo: "OPEX",
    descricao: "Compra de substrato orgânico",
    categoria: "Insumos",
    data: "2025-01-10",
    valor: 5800.00,
    formaPagamento: "Boleto Bancário",
    observacoes: "5 toneladas"
  },
  {
    id: 8,
    tipo: "OPEX",
    descricao: "Sementes de espécies nativas",
    categoria: "Insumos",
    data: "2025-01-15",
    valor: 4200.00,
    formaPagamento: "Pix",
    observacoes: "20 variedades"
  },
  {
    id: 9,
    tipo: "OPEX",
    descricao: "Conta de energia - Janeiro",
    categoria: "Energia e Água",
    data: "2025-01-20",
    valor: 2300.00,
    formaPagamento: "Débito Automático",
    observacoes: "Aumento de 15% em relação ao mês anterior"
  },
  {
    id: 10,
    tipo: "OPEX",
    descricao: "Manutenção do sistema de irrigação",
    categoria: "Manutenção",
    data: "2025-01-25",
    valor: 1200.00,
    formaPagamento: "Dinheiro",
    observacoes: "Substituição de válvulas e limpeza geral"
  },
  {
    id: 11,
    tipo: "OPEX",
    descricao: "Folha de pagamento - Fevereiro",
    categoria: "Mão de Obra",
    data: "2025-02-05",
    valor: 15000.00,
    formaPagamento: "Transferência Bancária",
    observacoes: "5 funcionários fixos"
  },
  {
    id: 12,
    tipo: "OPEX",
    descricao: "Conta de água - Fevereiro",
    categoria: "Energia e Água",
    data: "2025-02-15",
    valor: 1800.00,
    formaPagamento: "Débito Automático",
    observacoes: ""
  },
  {
    id: 13,
    tipo: "OPEX",
    descricao: "Compra de bandejas plásticas",
    categoria: "Embalagens",
    data: "2025-02-20",
    valor: 3500.00,
    formaPagamento: "Boleto Bancário",
    observacoes: "1000 unidades"
  },
  {
    id: 14,
    tipo: "OPEX",
    descricao: "Combustível - Fevereiro",
    categoria: "Combustível",
    data: "2025-02-28",
    valor: 800.00,
    formaPagamento: "Cartão de Débito",
    observacoes: ""
  },
  {
    id: 15,
    tipo: "OPEX",
    descricao: "Compra de EPIs",
    categoria: "EPIs",
    data: "2025-03-02",
    valor: 1500.00,
    formaPagamento: "Cartão de Crédito",
    observacoes: "Botas, luvas, óculos e protetores auriculares"
  },
  {
    id: 16,
    tipo: "OPEX",
    descricao: "Folha de pagamento - Março",
    categoria: "Mão de Obra",
    data: "2025-03-05",
    valor: 16000.00,
    formaPagamento: "Transferência Bancária",
    observacoes: "Contratação de 1 funcionário temporário"
  },
  {
    id: 17,
    tipo: "OPEX",
    descricao: "Manutenção do trator",
    categoria: "Manutenção",
    data: "2025-03-10",
    valor: 2200.00,
    formaPagamento: "Pix",
    observacoes: "Troca de óleo e revisão completa"
  },
  {
    id: 18,
    tipo: "OPEX",
    descricao: "Conta de energia - Março",
    categoria: "Energia e Água",
    data: "2025-03-20",
    valor: 2500.00,
    formaPagamento: "Débito Automático",
    observacoes: ""
  }
]);

// Estado para o item em edição
const custoEmEdicao = ref({
  id: null,
  tipo: '',
  descricao: '',
  categoria: '',
  data: '',
  valor: 0,
  formaPagamento: '',
  observacoes: ''
});

// Filtros de custos
const custosCapexFiltrados = computed(() => {
  let resultado = custos.value.filter(item => item.tipo === 'CAPEX');
  
  if (filtros.value.dataInicial) {
    resultado = resultado.filter(item => item.data >= filtros.value.dataInicial);
  }
  
  if (filtros.value.dataFinal) {
    resultado = resultado.filter(item => item.data <= filtros.value.dataFinal);
  }
  
  if (filtros.value.categoriaCapex) {
    resultado = resultado.filter(item => item.categoria === filtros.value.categoriaCapex);
  }
  
  return resultado;
});

const custosOpexFiltrados = computed(() => {
  let resultado = custos.value.filter(item => item.tipo === 'OPEX');
  
  if (filtros.value.dataInicial) {
    resultado = resultado.filter(item => item.data >= filtros.value.dataInicial);
  }
  
  if (filtros.value.dataFinal) {
    resultado = resultado.filter(item => item.data <= filtros.value.dataFinal);
  }
  
  if (filtros.value.categoriaOpex) {
    resultado = resultado.filter(item => item.categoria === filtros.value.categoriaOpex);
  }
  
  return resultado;
});

const totalCapexFiltrado = computed(() => {
  return custosCapexFiltrados.value.reduce((total, item) => total + item.valor, 0);
});

const totalOpexFiltrado = computed(() => {
  return custosOpexFiltrados.value.reduce((total, item) => total + item.valor, 0);
});

// Dados para resumo financeiro
const resumoFinanceiro = computed(() => {
  const totalCapex = custos.value
    .filter(item => item.tipo === 'CAPEX')
    .reduce((total, item) => total + item.valor, 0);
  
  const totalOpex = custos.value
    .filter(item => item.tipo === 'OPEX')
    .reduce((total, item) => total + item.valor, 0);
  
  // Data atual para filtrar mês e ano
  const dataAtual = new Date();
  const mesAtual = dataAtual.getMonth() + 1;
  const anoAtual = dataAtual.getFullYear();
  
  // Total do mês atual
  const totalMesAtual = custos.value
    .filter(item => {
      const data = new Date(item.data);
      return data.getMonth() + 1 === mesAtual && data.getFullYear() === anoAtual;
    })
    .reduce((total, item) => total + item.valor, 0);
  
  // Total do ano atual
  const totalAno = custos.value
    .filter(item => {
      const data = new Date(item.data);
      return data.getFullYear() === anoAtual;
    })
    .reduce((total, item) => total + item.valor, 0);
  
  // Custo por muda (estimado com base em uma produção de 50.000 mudas)
  const custoPorMuda = (totalOpex / 50000).toFixed(2);
  
  // Previsão até o final do ano (considerando média mensal * meses restantes + valores atuais)
  const mesesPassados = mesAtual;
  const mesesRestantes = 12 - mesesPassados;
  const mediaGastosMensal = totalAno / mesesPassados;
  const previsaoFimAno = totalAno + (mediaGastosMensal * mesesRestantes);
  
  return {
    totalCapex,
    totalOpex,
    totalMesAtual,
    totalAno,
    custoPorMuda,
    previsaoFimAno
  };
});

// Dados para os gráficos
const mesesAbreviados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

// Evolução de gastos mensais
const evolucaoGastos = computed(() => {
  const resultado = [];
  const anoAtual = new Date().getFullYear();
  
  // Para cada mês do ano
  for (let mes = 1; mes <= 12; mes++) {
    // Filtra os gastos do mês
    const gastosMes = custos.value.filter(item => {
      const data = new Date(item.data);
      return data.getMonth() + 1 === mes && data.getFullYear() === anoAtual;
    });
    
    // Soma os valores
    const valorMes = gastosMes.reduce((total, item) => total + item.valor, 0);
    
    resultado.push({
      mes,
      valor: valorMes
    });
  }
  
  return resultado;
});

// Pontos para o gráfico de linha
const pontosGraficoLinha = computed(() => {
  const pontos = evolucaoGastos.value.map((ponto, index) => {
    const x = (index / (evolucaoGastos.value.length - 1)) * 1200;
    // Escala o valor para a altura do gráfico (200px)
    // Assume valor máximo de 50.000 para escala
    const y = 200 - (ponto.valor / 50000 * 200);
    return `${x},${y}`;
  });
  
  return pontos.join(' ');
});

// Distribuição do OPEX por categoria
const distribuicaoOpex = computed(() => {
  const totalOpex = custosOpexFiltrados.value.reduce((total, item) => total + item.valor, 0);
  const categorias = {};
  
  // Agrupa os valores por categoria
  custosOpexFiltrados.value.forEach(item => {
    if (!categorias[item.categoria]) {
      categorias[item.categoria] = 0;
    }
    categorias[item.categoria] += item.valor;
  });
  
  // Paleta de cores profissional
  const cores = [
    '#1f4e79', '#2c5282', '#3d6a97', '#4a7aab', '#587ba0',
    '#6a6f6c', '#505f66', '#384c54', '#2e3e48', '#253746'
  ];
  
  const resultado = Object.keys(categorias).map((categoria, index) => {
    const valor = categorias[categoria];
    const porcentagem = ((valor / totalOpex) * 100).toFixed(1);
    
    return {
      categoria,
      valor,
      porcentagem,
      cor: cores[index % cores.length]
    };
  });
  
  // Ordena por valor (maior para menor)
  resultado.sort((a, b) => b.valor - a.valor);
  
  return resultado;
});

// Comparação do CAPEX por tipo
const comparacaoCapex = computed(() => {
  const totalCapex = custosCapexFiltrados.value.reduce((total, item) => total + item.valor, 0);
  const categorias = {};
  
  // Agrupa os valores por categoria
  custosCapexFiltrados.value.forEach(item => {
    if (!categorias[item.categoria]) {
      categorias[item.categoria] = 0;
    }
    categorias[item.categoria] += item.valor;
  });
  
  // Paleta de cores profissional
  const cores = [
    '#1f4e79', '#2c5282', '#3d6a97', '#4a7aab', '#587ba0',
    '#6a6f6c', '#505f66', '#384c54', '#2e3e48', '#253746'
  ];
  
  const resultado = Object.keys(categorias).map((categoria, index) => {
    const valor = categorias[categoria];
    const porcentagem = ((valor / totalCapex) * 100).toFixed(1);
    
    return {
      categoria,
      valor,
      porcentagem,
      cor: cores[index % cores.length],
      altura: Math.max(10, (valor / totalCapex) * 100) // Mínimo de 10% para visualização
    };
  });
  
  // Ordena por valor (maior para menor)
  resultado.sort((a, b) => b.valor - a.valor);
  
  return resultado;
});

// Funções para gestão de custos
const abrirModalNovoCusto = (tipo) => {
  custoEmEdicao.value = {
    id: null,
    tipo,
    descricao: '',
    categoria: tipo === 'CAPEX' ? categoriasCapex[0] : categoriasOpex[0],
    data: new Date().toISOString().split('T')[0],
    valor: 0,
    formaPagamento: 'Transferência Bancária',
    observacoes: ''
  };
  modalAberto.value = true;
};

const editarCusto = (custo) => {
  custoEmEdicao.value = { ...custo };
  modalAberto.value = true;
};

const fecharModal = () => {
  modalAberto.value = false;
};

const salvarCusto = () => {
  if (custoEmEdicao.value.id) {
    // Atualizar um custo existente
    const index = custos.value.findIndex(item => item.id === custoEmEdicao.value.id);
    if (index !== -1) {
      custos.value[index] = { ...custoEmEdicao.value };
    }
  } else {
    // Adicionar um novo custo
    const novoId = Math.max(0, ...custos.value.map(item => item.id)) + 1;
    custos.value.push({
      ...custoEmEdicao.value,
      id: novoId
    });
  }
  
  fecharModal();
};

const excluirCusto = (id) => {
  if (confirm('Tem certeza que deseja excluir este registro?')) {
    custos.value = custos.value.filter(item => item.id !== id);
  }
};

const aplicarFiltros = () => {
  // Os filtros já estão sendo aplicados via computed properties
};

const limparFiltros = () => {
  filtros.value = {
    dataInicial: '',
    dataFinal: '',
    categoriaCapex: '',
    categoriaOpex: ''
  };
};

// Funções de formatação
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

const formatarData = (dataStr) => {
  const data = new Date(dataStr);
  return data.toLocaleDateString('pt-BR');
};

// Inicialização
onMounted(() => {
  // Poderia ter lógica de inicialização, como carregar dados de uma API
});
</script>

<style scoped>
.financeiro-container {
  @apply w-full max-w-7xl mx-auto p-6 bg-white min-h-[calc(100vh-64px)];
}

.cabecalho {
  @apply flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8;
}

.titulo {
  @apply text-2xl font-bold text-gray-800;
}

.tipo-viveiro {
  @apply flex items-center gap-2;
}

.label {
  @apply text-sm font-medium text-gray-700;
}

.select-tipo {
  @apply py-1 px-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.secao {
  @apply mb-10;
}

.subtitulo {
  @apply text-xl font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200;
}

/* Cards do resumo financeiro */
.grid-cards {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4;
}

.card-resumo {
  @apply bg-white border border-gray-200 rounded-lg shadow-sm p-4 flex items-center gap-4 hover:shadow-md transition-shadow;
}

.card-icone {
  @apply w-12 h-12 rounded-full flex items-center justify-center;
}

.capex {
  @apply bg-blue-50 text-blue-800;
}

.opex {
  @apply bg-slate-50 text-slate-800;
}

.mensal {
  @apply bg-gray-50 text-gray-800;
}

.anual {
  @apply bg-indigo-50 text-indigo-800;
}

.muda {
  @apply bg-slate-50 text-slate-800;
}

.previsao {
  @apply bg-blue-50 text-blue-800;
}

.icone {
  @apply w-6 h-6;
}

.card-conteudo {
  @apply flex-1;
}

.card-titulo {
  @apply text-sm font-medium text-gray-600;
}

.card-valor {
  @apply text-lg font-bold text-gray-900;
}

/* Estilos dos gráficos */
.grid-graficos {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-6;
}

.grafico-container {
  @apply bg-white border border-gray-200 rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow;
}

.grafico-largo {
  @apply lg:col-span-2;
}

.grafico-titulo {
  @apply text-base font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-100;
}

/* Gráfico de barras horizontais (substituindo pizza) */
.grafico-barras-horizontais {
  @apply flex flex-col gap-3 mt-4;
}

.barra-horizontal-container {
  @apply w-full;
}

.barra-horizontal-info {
  @apply flex justify-between text-sm mb-1;
}

.barra-horizontal-label {
  @apply font-medium text-gray-700 truncate max-w-[70%];
}

.barra-horizontal-info .barra-horizontal-valor {
  @apply text-gray-600 text-right;
}

.barra-horizontal-wrapper {
  @apply w-full h-6 bg-gray-100 rounded-full overflow-hidden;
}

.barra-horizontal-wrapper .barra-horizontal-valor {
  @apply h-full rounded-full transition-all duration-500;
}

/* Gráfico de barras verticais */
.grafico-barras-verticais {
  @apply flex items-end justify-around h-48 mt-6 mb-4;
}

.barra-vertical-container {
  @apply flex flex-col items-center w-full;
}

.barra-vertical-wrapper {
  @apply w-full max-w-[40px] h-[180px] flex items-end justify-center mx-auto;
}

.barra-vertical-valor {
  @apply w-full rounded-t-md relative transition-all duration-500;
}

.barra-vertical-tooltip {
  @apply absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs py-1 px-2 rounded opacity-0 transition-opacity whitespace-nowrap;
}

.group:hover .barra-vertical-tooltip {
  @apply opacity-100;
}

.barra-vertical-label {
  @apply text-xs text-gray-600 mt-2 text-center w-full truncate;
}

.grafico-legenda {
  @apply mt-4 flex flex-wrap gap-3 justify-center;
}

.legenda-item-vertical {
  @apply flex items-center gap-1.5;
}

.legenda-cor {
  @apply w-3 h-3 rounded-sm;
}

.legenda-texto {
  @apply text-xs text-gray-700;
}

/* Gráfico de linha melhorado */
.grafico-linha {
  @apply flex mt-4 h-64;
}

.grafico-linha-eixoy {
  @apply flex flex-col justify-between h-[200px] pr-2 text-right;
}

.linha-eixoy-valor {
  @apply text-xs text-gray-500;
}

.grafico-linha-conteudo {
  @apply flex-1 relative;
}

.grafico-linha-grid {
  @apply absolute inset-0 flex;
}

.linha-grid {
  @apply flex-1 border-l border-gray-100;
}

.grafico-linha-dados {
  @apply absolute inset-0 h-[200px];
}

.ponto-dados {
  @apply absolute w-3 h-3 bg-blue-700 rounded-full transform -translate-x-1/2 -translate-y-1/2 hover:w-4 hover:h-4 transition-all duration-200 cursor-pointer z-10;
}

.tooltip-ponto {
  @apply absolute bottom-full left-1/2 transform -translate-x-1/2 text-xs bg-gray-800 text-white px-2 py-1 rounded opacity-0 pointer-events-none mb-1 whitespace-nowrap;
}

.ponto-dados:hover .tooltip-ponto {
  @apply opacity-100;
}

.grafico-linha-eixox {
  @apply flex pt-2;
}

.linha-eixox-valor {
  @apply flex-1 text-center text-xs text-gray-500;
}

/* Estilos das abas */
.abas-container {
  @apply mt-4;
}

.abas-navegacao {
  @apply flex gap-1 border-b border-gray-200;
}

.aba-btn {
  @apply px-4 py-2 text-sm font-medium rounded-t-lg focus:outline-none;
}

.aba-btn.ativo {
  @apply bg-white text-blue-800 border-l border-t border-r border-gray-200 border-b-0;
}

.aba-btn:not(.ativo) {
  @apply text-gray-600 hover:text-gray-900 hover:bg-gray-50;
}

.abas-conteudo {
  @apply bg-white rounded-b-lg;
}

.aba-painel {
  @apply p-4;
}

.painel-cabecalho {
  @apply flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4;
}

.filtros {
  @apply flex flex-wrap items-end gap-4;
}

.filtro-grupo {
  @apply flex flex-col gap-1;
}

.filtro-label {
  @apply text-xs font-medium text-gray-700;
}

.filtro-input {
  @apply py-1 px-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.btn-aplicar {
  @apply py-1 px-4 bg-blue-700 text-white rounded-md text-sm hover:bg-blue-800 transition-colors;
}

.btn-limpar {
  @apply py-1 px-4 border border-gray-300 bg-white text-gray-700 rounded-md text-sm hover:bg-gray-50 transition-colors;
}

.btn-adicionar {
  @apply flex items-center gap-2 py-2 px-4 bg-blue-700 text-white rounded-md text-sm hover:bg-blue-800 transition-colors;
}

.btn-icone {
  @apply w-4 h-4;
}

.tabela-container {
  @apply overflow-x-auto;
}

.tabela {
  @apply w-full border-collapse;
}

.tabela th {
  @apply bg-gray-50 text-left text-xs uppercase font-medium text-gray-600 p-3 border-b border-gray-200;
}

.tabela td {
  @apply text-sm p-3 border-b border-gray-200;
}

.coluna-valor {
  @apply font-medium text-right;
}

.coluna-acoes {
  @apply flex gap-2 justify-end;
}

.btn-acao {
  @apply p-1 rounded-full;
}

.editar {
  @apply text-blue-700 hover:bg-blue-50;
}

.excluir {
  @apply text-gray-700 hover:bg-gray-50;
}

.icone-acao {
  @apply w-4 h-4;
}

.mensagem-vazia {
  @apply text-center py-8 text-gray-500;
}

.total-label {
  @apply text-right font-medium text-gray-700;
}

.total-valor {
  @apply font-bold text-right;
}

/* Estilos do modal */
.modal-overlay {
  @apply fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm;
}

.modal-conteudo {
  @apply bg-white rounded-xl shadow-xl w-full max-w-lg;
}

.modal-cabecalho {
  @apply p-6 border-b border-gray-200 flex justify-between items-center;
}

.modal-titulo {
  @apply text-xl font-bold text-gray-800;
}

.btn-fechar {
  @apply p-2 rounded-full hover:bg-gray-100 transition-colors;
}

.icone-fechar {
  @apply w-5 h-5 text-gray-500;
}

.modal-corpo {
  @apply p-6;
}

.formulario {
  @apply space-y-4;
}

.form-grupo {
  @apply flex flex-col gap-1;
}

.form-label {
  @apply text-sm font-medium text-gray-700;
}

.form-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.form-textarea {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[100px] resize-none;
}

.form-acoes {
  @apply flex justify-end gap-3 pt-4;
}

.btn-cancelar {
  @apply px-4 py-2 border border-gray-300 bg-white text-gray-700 rounded-md text-sm hover:bg-gray-50 transition-colors;
}

.btn-salvar {
  @apply px-4 py-2 bg-blue-700 text-white rounded-md text-sm hover:bg-blue-800 transition-colors;
}
</style> 