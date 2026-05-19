<template>
  <div class="vendas-estoque-container">
    <h1 class="page-title">Vendas e Estoque de Mudas</h1>
    
    <!-- Seção de registro de vendas -->
    <div class="secao">
      <div class="secao-header">
        <h2 class="secao-titulo">Histórico de Vendas</h2>
        <button class="btn-principal" @click="abrirFormularioNovaVenda">
          <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Registrar Nova Venda
        </button>
      </div>
      
      <div class="tabela-container">
        <table class="tabela-vendas">
          <thead>
            <tr>
              <th>Data</th>
              <th>Espécie</th>
              <th>Quantidade</th>
              <th>Valor Total (R$)</th>
              <th>Comprador</th>
              <th>Pagamento</th>
              <th>Observações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="venda in historicoVendas" :key="venda.id">
              <td>{{ formatarData(venda.data) }}</td>
              <td>
                <div class="especie-info">
                  <div class="nome-popular">{{ venda.especie.nomePopular }}</div>
                  <div class="nome-cientifico">{{ venda.especie.nomeCientifico }}</div>
                </div>
              </td>
              <td>{{ venda.quantidade }}</td>
              <td>R$ {{ venda.valorTotal.toFixed(2) }}</td>
              <td>{{ venda.comprador }}</td>
              <td>
                <span class="tag pagamento-tag">{{ venda.formaPagamento }}</span>
              </td>
              <td>{{ venda.observacoes || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Seção de controle de estoque -->
    <div class="secao">
      <div class="secao-header">
        <h2 class="secao-titulo">Controle de Estoque</h2>
      </div>
      
      <div class="tabela-container">
        <table class="tabela-estoque">
          <thead>
            <tr>
              <th>Espécie</th>
              <th>Tamanho</th>
              <th>Quantidade</th>
              <th>Valor Unitário (R$)</th>
              <th>Localização</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in estoqueItems" :key="item.id" :class="{ 'estoque-baixo': item.quantidade < 20 }">
              <td>
                <div class="especie-info">
                  <div class="nome-popular">{{ item.nomePopular }}</div>
                  <div class="nome-cientifico">{{ item.nomeCientifico }}</div>
                </div>
              </td>
              <td>{{ item.tamanho }}</td>
              <td>
                <span :class="{ 'qtd-alerta': item.quantidade < 20 }">
                  {{ item.quantidade }}
                </span>
              </td>
              <td>R$ {{ item.valorUnitario.toFixed(2) }}</td>
              <td>{{ item.localizacao }}</td>
              <td>
                <button class="btn-acao" @click="editarEstoque(item)">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon-small" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Modal de edição de estoque -->
    <div class="modal-overlay" v-if="modalEstoqueAberto" @click.self="fecharModalEstoque">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">Editar Estoque</h2>
          <button class="btn-fechar" @click="fecharModalEstoque">×</button>
        </div>
        <form @submit.prevent="salvarEstoque" class="formulario-estoque">
          <div class="form-row">
            <div class="form-group">
              <label for="nome-popular">Nome Popular:</label>
              <input type="text" id="nome-popular" v-model="formEstoque.nomePopular" required disabled>
            </div>
            
            <div class="form-group">
              <label for="nome-cientifico">Nome Científico:</label>
              <input type="text" id="nome-cientifico" v-model="formEstoque.nomeCientifico" required disabled>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="tamanho">Tamanho:</label>
              <select id="tamanho" v-model="formEstoque.tamanho" required disabled>
                <option value="Pequena">Pequena</option>
                <option value="Média">Média</option>
                <option value="Grande">Grande</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="quantidade">Quantidade:</label>
              <input type="number" id="quantidade" v-model.number="formEstoque.quantidade" min="0" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="valor-unitario">Valor Unitário (R$):</label>
              <input type="number" id="valor-unitario" v-model.number="formEstoque.valorUnitario" step="0.01" min="0" required>
            </div>
            
            <div class="form-group">
              <label for="localizacao">Localização:</label>
              <input type="text" id="localizacao" v-model="formEstoque.localizacao" required>
            </div>
          </div>
          
          <div class="form-buttons">
            <button type="button" class="btn-cancelar" @click="fecharModalEstoque">Cancelar</button>
            <button type="submit" class="btn-salvar">Salvar</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Modal de Nova Venda -->
    <div class="modal-overlay" v-if="modalVendaAberto" @click.self="fecharModalVenda">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">Registrar Nova Venda</h2>
          <button class="btn-fechar" @click="fecharModalVenda">×</button>
        </div>
        <form @submit.prevent="salvarVenda" class="formulario-venda">
          <div class="form-row">
            <div class="form-group">
              <label for="especie-venda">Espécie:</label>
              <select id="especie-venda" v-model="formVenda.especieId" required @change="atualizarDadosEspecie">
                <option value="">Selecione uma espécie</option>
                <option v-for="item in estoqueDisponivel" :key="item.id" :value="item.id">
                  {{ item.nomePopular }} ({{ item.quantidade }} disponíveis)
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="quantidade-venda">Quantidade:</label>
              <input 
                type="number" 
                id="quantidade-venda" 
                v-model.number="formVenda.quantidade" 
                min="1" 
                :max="especieSelecionada ? especieSelecionada.quantidade : 0" 
                required
                @input="calcularValorTotal"
              >
              <small v-if="especieSelecionada" class="info-texto">
                Máximo disponível: {{ especieSelecionada.quantidade }}
              </small>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="comprador">Nome do Comprador:</label>
              <input type="text" id="comprador" v-model="formVenda.comprador" required>
            </div>
            
            <div class="form-group">
              <label for="valor-total">Valor Total (R$):</label>
              <input type="number" id="valor-total" v-model.number="formVenda.valorTotal" step="0.01" min="0" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="forma-pagamento">Forma de Pagamento:</label>
              <select id="forma-pagamento" v-model="formVenda.formaPagamento" required>
                <option value="PIX">PIX</option>
                <option value="Transferência">Transferência</option>
                <option value="Boleto">Boleto</option>
                <option value="Dinheiro">Dinheiro</option>
                <option value="Cartão">Cartão</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="data-venda">Data da Venda:</label>
              <input type="date" id="data-venda" v-model="formVenda.data" required>
            </div>
          </div>
          
          <div class="form-group full-width">
            <label for="observacoes">Observações:</label>
            <textarea id="observacoes" v-model="formVenda.observacoes" rows="2"></textarea>
          </div>
          
          <div class="form-buttons">
            <button type="button" class="btn-cancelar" @click="fecharModalVenda">Cancelar</button>
            <button type="submit" class="btn-salvar">Registrar Venda</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

// Mock de dados para o estoque
const estoqueItems = ref([
  {
    id: 1,
    nomePopular: 'Ipê Amarelo',
    nomeCientifico: 'Handroanthus albus',
    tamanho: 'Média',
    quantidade: 45,
    valorUnitario: 25.00,
    localizacao: 'Canteiro B3'
  },
  {
    id: 2,
    nomePopular: 'Jatobá',
    nomeCientifico: 'Hymenaea courbaril',
    tamanho: 'Grande',
    quantidade: 12,
    valorUnitario: 35.50,
    localizacao: 'Canteiro A2'
  },
  {
    id: 3,
    nomePopular: 'Pau-Brasil',
    nomeCientifico: 'Paubrasilia echinata',
    tamanho: 'Pequena',
    quantidade: 30,
    valorUnitario: 20.00,
    localizacao: 'Canteiro C1'
  },
  {
    id: 4,
    nomePopular: 'Aroeira',
    nomeCientifico: 'Schinus terebinthifolia',
    tamanho: 'Média',
    quantidade: 18,
    valorUnitario: 22.00,
    localizacao: 'Canteiro D2'
  },
  {
    id: 5,
    nomePopular: 'Cedro',
    nomeCientifico: 'Cedrela fissilis',
    tamanho: 'Grande',
    quantidade: 28,
    valorUnitario: 40.00,
    localizacao: 'Canteiro B1'
  }
]);

// Mock de dados para o histórico de vendas
const historicoVendas = ref([
  {
    id: 1,
    data: '2023-10-15',
    especie: {
      nomePopular: 'Ipê Amarelo',
      nomeCientifico: 'Handroanthus albus'
    },
    quantidade: 5,
    valorTotal: 125.00,
    comprador: 'Prefeitura de São Carlos',
    formaPagamento: 'Transferência',
    observacoes: 'Projeto de arborização urbana'
  },
  {
    id: 2,
    data: '2023-11-03',
    especie: {
      nomePopular: 'Pau-Brasil',
      nomeCientifico: 'Paubrasilia echinata'
    },
    quantidade: 10,
    valorTotal: 200.00,
    comprador: 'João Silva',
    formaPagamento: 'PIX',
    observacoes: 'Reflorestamento em área particular'
  },
  {
    id: 3,
    data: '2023-11-20',
    especie: {
      nomePopular: 'Jatobá',
      nomeCientifico: 'Hymenaea courbaril'
    },
    quantidade: 3,
    valorTotal: 106.50,
    comprador: 'Maria Oliveira',
    formaPagamento: 'Dinheiro',
    observacoes: ''
  }
]);

// Estado para modais
const modalVendaAberto = ref(false);

// Formulários
const formVenda = ref({
  data: new Date().toISOString().substr(0, 10),
  especieId: '',
  quantidade: 1,
  valorTotal: 0,
  comprador: '',
  formaPagamento: 'PIX',
  observacoes: ''
});

// Computed properties
const estoqueDisponivel = computed(() => {
  return estoqueItems.value.filter(item => item.quantidade > 0);
});

const especieSelecionada = computed(() => {
  if (!formVenda.value.especieId) return null;
  return estoqueItems.value.find(item => item.id === formVenda.value.especieId);
});

// Métodos para o registro de vendas
function abrirFormularioNovaVenda() {
  formVenda.value = {
    data: new Date().toISOString().substr(0, 10),
    especieId: '',
    quantidade: 1,
    valorTotal: 0,
    comprador: '',
    formaPagamento: 'PIX',
    observacoes: ''
  };
  modalVendaAberto.value = true;
}

function fecharModalVenda() {
  modalVendaAberto.value = false;
}

function atualizarDadosEspecie() {
  if (especieSelecionada.value) {
    formVenda.value.quantidade = 1;
    calcularValorTotal();
  }
}

function calcularValorTotal() {
  if (especieSelecionada.value && formVenda.value.quantidade) {
    formVenda.value.valorTotal = especieSelecionada.value.valorUnitario * formVenda.value.quantidade;
  }
}

function salvarVenda() {
  // Verificar se a quantidade solicitada está disponível
  if (!especieSelecionada.value || formVenda.value.quantidade > especieSelecionada.value.quantidade) {
    alert('Quantidade indisponível no estoque!');
    return;
  }
  
  // Criar nova venda
  const novoId = historicoVendas.value.length > 0 
    ? Math.max(...historicoVendas.value.map(venda => venda.id)) + 1 
    : 1;
  
  const novaVenda = {
    id: novoId,
    data: formVenda.value.data,
    especie: {
      nomePopular: especieSelecionada.value.nomePopular,
      nomeCientifico: especieSelecionada.value.nomeCientifico
    },
    quantidade: formVenda.value.quantidade,
    valorTotal: formVenda.value.valorTotal,
    comprador: formVenda.value.comprador,
    formaPagamento: formVenda.value.formaPagamento,
    observacoes: formVenda.value.observacoes
  };
  
  // Adicionar ao histórico
  historicoVendas.value.push(novaVenda);
  
  // Atualizar o estoque
  const index = estoqueItems.value.findIndex(item => item.id === formVenda.value.especieId);
  if (index !== -1) {
    estoqueItems.value[index].quantidade -= formVenda.value.quantidade;
  }
  
  fecharModalVenda();
}

// Função para formatar data
function formatarData(dataString) {
  const data = new Date(dataString);
  return data.toLocaleDateString('pt-BR');
}
</script>

<style>
.vendas-estoque-container {
  width: 100%;
  padding: 1.5rem;
}

.page-title {
  font-size: 1.75rem;
  margin-bottom: 1.5rem;
  color: var(--color-text-primary);
  font-weight: 700;
}

.secao {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.secao-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eeeeee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.secao-titulo {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.tabela-container {
  padding: 1rem;
  overflow-x: auto;
}

.tabela-estoque,
.tabela-vendas {
  width: 100%;
  border-collapse: collapse;
}

.tabela-estoque th,
.tabela-estoque td,
.tabela-vendas th,
.tabela-vendas td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #eeeeee;
}

.tabela-estoque th,
.tabela-vendas th {
  font-weight: 600;
  color: var(--color-text-primary);
  background-color: #f8f9fa;
}

.tabela-estoque tbody tr:hover,
.tabela-vendas tbody tr:hover {
  background-color: #f8f9fa;
}

.especie-info {
  display: flex;
  flex-direction: column;
}

.nome-popular {
  font-weight: 500;
  color: var(--color-text-primary);
}

.nome-cientifico {
  font-style: italic;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.estoque-baixo {
  background-color: rgba(255, 193, 7, 0.1);
}

.qtd-alerta {
  color: #e53935;
  font-weight: 600;
}

.btn-acao {
  padding: 0.25rem;
  border: none;
  background: none;
  color: var(--color-primary);
  cursor: pointer;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.btn-acao:hover {
  background-color: rgba(0, 123, 255, 0.1);
}

.icon-small {
  width: 1.25rem;
  height: 1.25rem;
}

.btn-principal {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-principal:hover {
  background-color: var(--color-primary-dark);
}

.btn-principal .icon {
  width: 1.25rem;
  height: 1.25rem;
}

.tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.pagamento-tag {
  background-color: #e3f2fd;
  color: #1976d2;
}

/* Estilos para o modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eeeeee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.btn-fechar {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #666;
  cursor: pointer;
}

/* Estilos para formulários */
.formulario-venda {
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
}

.full-width {
  width: 100%;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  font-size: 1rem;
}

.form-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cancelar {
  padding: 0.5rem 1rem;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-salvar {
  padding: 0.5rem 1rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
}

.info-texto {
  font-size: 0.75rem;
  color: #666;
  margin-top: 0.25rem;
}

/* Responsividade */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .tabela-container {
    overflow-x: auto;
  }
  
  .tabela-estoque,
  .tabela-vendas {
    min-width: 650px;
  }
}
</style> 