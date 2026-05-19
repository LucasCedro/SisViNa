<template>
  <div class="cadastro-mudas-container">
    <h1 class="page-title">Cadastro de Mudas</h1>
    
    <div class="secao">
      <div class="secao-header">
        <h2 class="secao-titulo">Mudas Cadastradas</h2>
        <button class="btn-principal" @click="abrirModalCadastro">
          <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Nova Muda
        </button>
      </div>
      
      <div class="tabela-container">
        <table class="tabela-mudas">
          <thead>
            <tr>
              <th>Espécie</th>
              <th>Data Semeadura</th>
              <th>Canteiro</th>
              <th>Quantidade</th>
              <th>Tamanho</th>
              <th>Estágio</th>
              <th>Germinação</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="muda in mudas" :key="muda.id">
              <td>
                <div class="especie-info">
                  <div class="nome-popular">{{ muda.nomePopular }}</div>
                  <div class="nome-cientifico">{{ muda.nomeCientifico }}</div>
                </div>
              </td>
              <td>{{ formatarData(muda.dataSemeadura) }}</td>
              <td>{{ muda.canteiro }}</td>
              <td>{{ muda.quantidade }}</td>
              <td>{{ muda.tamanho }}</td>
              <td>
                <span :class="'tag estagio-' + muda.estagio.toLowerCase()">
                  {{ muda.estagio }}
                </span>
              </td>
              <td>{{ muda.taxaGerminacao }}%</td>
              <td>
                <button class="btn-acao" @click="editarMuda(muda)">
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
    
    <!-- Modal de Cadastro/Edição de Mudas -->
    <div class="modal-overlay" v-if="modalAberto" @click.self="fecharModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">{{ modoEdicao ? 'Editar Muda' : 'Cadastrar Nova Muda' }}</h2>
          <button class="btn-fechar" @click="fecharModal">×</button>
        </div>
        <form @submit.prevent="salvarMuda" class="formulario-muda">
          <div class="form-row">
            <div class="form-group">
              <label for="nome-popular">Nome Popular:</label>
              <input type="text" id="nome-popular" v-model="formMuda.nomePopular" required>
            </div>
            
            <div class="form-group">
              <label for="nome-cientifico">Nome Científico:</label>
              <input type="text" id="nome-cientifico" v-model="formMuda.nomeCientifico" required>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="data-semeadura">Data da Semeadura:</label>
              <input type="date" id="data-semeadura" v-model="formMuda.dataSemeadura" required>
            </div>
            
            <div class="form-group">
              <label for="canteiro">Canteiro:</label>
              <select id="canteiro" v-model="formMuda.canteiro" required>
                <option value="">Selecione um canteiro</option>
                <option v-for="canteiro in canteiros" :key="canteiro.id" :value="canteiro.nome">
                  {{ canteiro.nome }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="quantidade">Quantidade:</label>
              <input type="number" id="quantidade" v-model.number="formMuda.quantidade" min="1" required>
            </div>
            
            <div class="form-group">
              <label for="tamanho">Tamanho Atual:</label>
              <select id="tamanho" v-model="formMuda.tamanho" required>
                <option value="Pequena">Pequena</option>
                <option value="Média">Média</option>
                <option value="Grande">Grande</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="substrato">Tipo de Substrato:</label>
              <input type="text" id="substrato" v-model="formMuda.substrato" required>
            </div>
            
            <div class="form-group">
              <label for="procedencia">Procedência das Sementes:</label>
              <select id="procedencia" v-model="formMuda.procedencia" required>
                <option value="Árvore Matriz">Árvore Matriz</option>
                <option value="Lote">Lote</option>
                <option value="Fornecedor">Fornecedor</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="taxa-germinacao">Taxa de Germinação Estimada (%):</label>
              <input type="number" id="taxa-germinacao" v-model.number="formMuda.taxaGerminacao" min="0" max="100" required>
            </div>
            
            <div class="form-group">
              <label for="estagio">Estágio Atual:</label>
              <select id="estagio" v-model="formMuda.estagio" required>
                <option value="Emergência">Emergência</option>
                <option value="Crescimento">Crescimento</option>
                <option value="Rustificação">Rustificação</option>
              </select>
            </div>
          </div>
          
          <div class="form-group full-width">
            <label for="observacoes">Observações:</label>
            <textarea id="observacoes" v-model="formMuda.observacoes" rows="3"></textarea>
          </div>
          
          <div class="form-group full-width">
            <label for="imagem">Imagem da Muda:</label>
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
              <img :src="imagemPreview" alt="Preview da muda">
            </div>
          </div>
          
          <div class="form-buttons">
            <button type="button" class="btn-cancelar" @click="fecharModal">Cancelar</button>
            <button type="submit" class="btn-salvar">{{ modoEdicao ? 'Atualizar' : 'Cadastrar' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Lista de canteiros (mock)
const canteiros = ref([
  { id: 1, nome: 'Canteiro A1' },
  { id: 2, nome: 'Canteiro A2' },
  { id: 3, nome: 'Canteiro B1' },
  { id: 4, nome: 'Canteiro B2' },
  { id: 5, nome: 'Canteiro C1' },
  { id: 6, nome: 'Canteiro C2' }
]);

// Dados de mudas (mock)
const mudas = ref([
  {
    id: 1,
    nomePopular: 'Ipê Amarelo',
    nomeCientifico: 'Handroanthus albus',
    dataSemeadura: '2023-08-15',
    canteiro: 'Canteiro A1',
    quantidade: 50,
    tamanho: 'Pequena',
    substrato: 'Terra vegetal com vermiculita',
    procedencia: 'Árvore Matriz',
    taxaGerminacao: 75,
    estagio: 'Emergência',
    observacoes: 'Primeiras folhas começando a aparecer',
    imagem: 'https://via.placeholder.com/200x150?text=Ipe+Amarelo'
  },
  {
    id: 2,
    nomePopular: 'Jatobá',
    nomeCientifico: 'Hymenaea courbaril',
    dataSemeadura: '2023-07-10',
    canteiro: 'Canteiro B2',
    quantidade: 30,
    tamanho: 'Média',
    substrato: 'Substrato florestal',
    procedencia: 'Lote',
    taxaGerminacao: 60,
    estagio: 'Crescimento',
    observacoes: 'Desenvolvimento rápido após quebra de dormência',
    imagem: 'https://via.placeholder.com/200x150?text=Jatoba'
  },
  {
    id: 3,
    nomePopular: 'Peroba Rosa',
    nomeCientifico: 'Aspidosperma polyneuron',
    dataSemeadura: '2023-06-05',
    canteiro: 'Canteiro C1',
    quantidade: 40,
    tamanho: 'Grande',
    substrato: 'Terra vegetal com casca de pinus',
    procedencia: 'Fornecedor',
    taxaGerminacao: 80,
    estagio: 'Rustificação',
    observacoes: 'Pronta para transplante em breve',
    imagem: 'https://via.placeholder.com/200x150?text=Peroba+Rosa'
  }
]);

// Estado do modal
const modalAberto = ref(false);
const modoEdicao = ref(false);
const imagemPreview = ref(null);

// Formulário
const formMuda = ref({
  id: null,
  nomePopular: '',
  nomeCientifico: '',
  dataSemeadura: '',
  canteiro: '',
  quantidade: 0,
  tamanho: 'Pequena',
  substrato: '',
  procedencia: 'Árvore Matriz',
  taxaGerminacao: 70,
  estagio: 'Emergência',
  observacoes: '',
  imagem: ''
});

// Funções
function abrirModalCadastro() {
  modoEdicao.value = false;
  resetarFormulario();
  modalAberto.value = true;
}

function editarMuda(muda) {
  modoEdicao.value = true;
  formMuda.value = { ...muda };
  if (muda.imagem) {
    imagemPreview.value = muda.imagem;
  } else {
    imagemPreview.value = null;
  }
  modalAberto.value = true;
}

function fecharModal() {
  modalAberto.value = false;
}

function resetarFormulario() {
  formMuda.value = {
    id: null,
    nomePopular: '',
    nomeCientifico: '',
    dataSemeadura: formatarDataAtual(),
    canteiro: '',
    quantidade: 0,
    tamanho: 'Pequena',
    substrato: '',
    procedencia: 'Árvore Matriz',
    taxaGerminacao: 70,
    estagio: 'Emergência',
    observacoes: '',
    imagem: ''
  };
  imagemPreview.value = null;
}

function salvarMuda() {
  if (modoEdicao.value) {
    // Atualizar muda existente
    const index = mudas.value.findIndex(m => m.id === formMuda.value.id);
    if (index !== -1) {
      mudas.value[index] = {
        ...formMuda.value,
        imagem: imagemPreview.value || formMuda.value.imagem
      };
    }
  } else {
    // Adicionar nova muda
    const novoId = mudas.value.length > 0
      ? Math.max(...mudas.value.map(m => m.id)) + 1
      : 1;
    
    mudas.value.push({
      ...formMuda.value,
      id: novoId,
      imagem: imagemPreview.value || 'https://via.placeholder.com/200x150?text=Sem+Imagem'
    });
  }
  
  fecharModal();
}

function previewImagem(event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = e => {
      imagemPreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
}

function formatarData(dataString) {
  const data = new Date(dataString);
  return data.toLocaleDateString('pt-BR');
}

function formatarDataAtual() {
  const hoje = new Date();
  return hoje.toISOString().substr(0, 10); // Formato YYYY-MM-DD
}
</script>

<style scoped>
.cadastro-mudas-container {
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

.tabela-mudas {
  width: 100%;
  border-collapse: collapse;
}

.tabela-mudas th,
.tabela-mudas td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #eeeeee;
}

.tabela-mudas th {
  font-weight: 600;
  color: var(--color-text-primary);
  background-color: #f8f9fa;
}

.tabela-mudas tbody tr:hover {
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

.tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.estagio-emergência {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.estagio-crescimento {
  background-color: #e3f2fd;
  color: #1565c0;
}

.estagio-rustificação {
  background-color: #fff8e1;
  color: #ff8f00;
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
  max-width: 700px;
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
.formulario-muda {
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

/* Estilos para upload de imagem */
.upload-area {
  margin-top: 0.5rem;
}

.file-input {
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  position: absolute;
  z-index: -1;
}

.file-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f5f5f5;
  border: 1px dashed #ddd;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  transition: all 0.2s;
}

.file-label:hover {
  background-color: #e9ecef;
  border-color: #ced4da;
}

.file-label .icon {
  width: 1.25rem;
  height: 1.25rem;
}

.imagem-preview {
  margin-top: 1rem;
  max-width: 100%;
  max-height: 200px;
  overflow: hidden;
  border-radius: 0.25rem;
  border: 1px solid #ddd;
}

.imagem-preview img {
  width: 100%;
  height: auto;
  object-fit: contain;
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
  
  .tabela-mudas {
    min-width: 650px;
  }
}
</style> 