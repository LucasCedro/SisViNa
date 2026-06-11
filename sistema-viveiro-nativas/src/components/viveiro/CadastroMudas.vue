<template>
  <div class="cadastro-mudas-container">
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
    <div
      v-if="modalAberto"
      class="modal-overlay"
      @pointerdown.self="onOverlayPointerDown"
      @pointerup.self="onOverlayPointerUp"
      @pointercancel.self="cancelarFechamentoOverlay"
    >
      <div class="modal-content" @pointerdown="onModalPointerDown">
        <div class="modal-header">
          <h2 class="modal-title">{{ modoEdicao ? 'Editar Muda' : 'Cadastrar Nova Muda' }}</h2>
          <button class="btn-fechar" @click="fecharModal">×</button>
        </div>
        <form @submit.prevent="salvarMuda" class="formulario-muda">
          <div class="form-row">
            <div class="form-group">
              <label for="especie">Espécie:</label>
              <select id="especie" v-model.number="formMuda.id_especie" required>
                <option value="">Selecione</option>
                <option v-for="e in especies" :key="e.id" :value="e.id">
                  {{ e.nome_popular || e.nome_cientifico }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="status">Status:</label>
              <select id="status" v-model="formMuda.status" required @change="filtrarCanteiros">
                <option value="SEMENTE">Semente</option>
                <option value="MUDA">Muda</option>
                <option value="JOVEM">Jovem</option>
                <option value="ADULTA">Adulta</option>
              </select>
            </div>
            <div v-if="!modoEdicao" class="form-group">
              <label for="origem">Origem:</label>
              <select id="origem" v-model="formMuda.origem">
                <option value="compra">Compra / estoque inicial</option>
                <option value="doacao">Doação</option>
                <option value="ajuste">Ajuste de inventário</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="data-semeadura">Data da Semeadura:</label>
              <input type="date" id="data-semeadura" v-model="formMuda.dataSemeadura" required>
            </div>
            
            <div class="form-group">
              <label for="canteiro">Canteiro:</label>
              <select id="canteiro" v-model.number="formMuda.id_canteiro" required>
                <option value="">Selecione</option>
                <option v-for="canteiro in canteirosFiltrados" :key="canteiro.id" :value="canteiro.id">
                  {{ canteiro.nome }} ({{ canteiro.tipo_local }})
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
import { ref, onMounted } from 'vue'
import { listEspecies } from '@/services/especies'
import { listCanteiros } from '@/services/canteiros'
import {
  listPlantasComRelacoes,
  cadastroLotePlantas,
  updatePlanta
} from '@/services/plantas'
import { useModalOverlayClose } from '@/composables/useModalOverlayClose'

const STATUS_MAP = {
  SEMENTE: 'Emergência',
  MUDA: 'Crescimento',
  JOVEM: 'Rustificação',
  ADULTA: 'Adulta'
}

const canteiros = ref([])
const canteirosFiltrados = ref([])
const especies = ref([])
const mudas = ref([])

const modalAberto = ref(false)
const modoEdicao = ref(false)

const formMuda = ref({
  id: null,
  id_especie: '',
  id_canteiro: '',
  dataSemeadura: '',
  quantidade: 1,
  status: 'MUDA',
  origem: 'compra',
  observacoes: ''
})

function filtrarCanteiros() {
  const tipo = formMuda.value.status === 'SEMENTE' ? 'sementeira' : 'canteiro'
  canteirosFiltrados.value = canteiros.value.filter((c) => c.tipo_local === tipo)
  if (
    formMuda.value.id_canteiro &&
    !canteirosFiltrados.value.some((c) => c.id === formMuda.value.id_canteiro)
  ) {
    formMuda.value.id_canteiro = canteirosFiltrados.value[0]?.id || ''
  }
}

function mapPlanta(p) {
  const parts = (p.especie_nome || '').split(' ')
  return {
    id: p.id,
    nomePopular: parts[0] || p.especie_nome,
    nomeCientifico: p.especie_nome,
    dataSemeadura: p.data_plantio,
    canteiro: p.nome_canteiro || '—',
    quantidade: 1,
    tamanho: p.status,
    estagio: STATUS_MAP[p.status] || p.status,
    taxaGerminacao: '—',
    observacoes: p.observacoes || '',
    id_especie: p.id_especie,
    id_canteiro: p.id_canteiro,
    status: p.status
  }
}

async function carregar() {
  const [pl, esp, cant] = await Promise.all([
    listPlantasComRelacoes({ limit: 500 }),
    listEspecies(),
    listCanteiros({ ativo: true })
  ])
  mudas.value = pl.filter((p) => !['VENDIDA', 'MORTA'].includes(p.status)).map(mapPlanta)
  especies.value = esp
  canteiros.value = cant
  filtrarCanteiros()
}

onMounted(carregar)

function abrirModalCadastro() {
  modoEdicao.value = false
  resetarFormulario()
  modalAberto.value = true
}

function editarMuda(muda) {
  modoEdicao.value = true
  formMuda.value = {
    id: muda.id,
    id_especie: muda.id_especie,
    id_canteiro: muda.id_canteiro || '',
    dataSemeadura: muda.dataSemeadura,
    quantidade: 1,
    status: muda.status,
    observacoes: muda.observacoes
  }
  modalAberto.value = true
}

function fecharModalInterno() {
  modalAberto.value = false
}

const {
  onModalPointerDown,
  onOverlayPointerDown,
  onOverlayPointerUp,
  cancelarFechamentoOverlay,
  resetOverlayPress,
} = useModalOverlayClose(fecharModalInterno)

function fecharModal() {
  resetOverlayPress()
  fecharModalInterno()
}

function resetarFormulario() {
  formMuda.value = {
    id: null,
    id_especie: especies.value[0]?.id || '',
    id_canteiro: canteiros.value[0]?.id || '',
    dataSemeadura: formatarDataAtual(),
    quantidade: 1,
    status: 'MUDA',
    origem: 'compra',
    observacoes: ''
  }
  filtrarCanteiros()
}

async function salvarMuda() {
  try {
    if (modoEdicao.value) {
      await updatePlanta(formMuda.value.id, {
        id_especie: Number(formMuda.value.id_especie),
        id_canteiro: formMuda.value.id_canteiro ? Number(formMuda.value.id_canteiro) : null,
        data_plantio: formMuda.value.dataSemeadura,
        status: formMuda.value.status,
        observacoes: formMuda.value.observacoes
      })
    } else {
      await cadastroLotePlantas({
        id_especie: Number(formMuda.value.id_especie),
        id_canteiro: Number(formMuda.value.id_canteiro),
        quantidade: Number(formMuda.value.quantidade),
        data_plantio: formMuda.value.dataSemeadura,
        status: formMuda.value.status,
        origem: formMuda.value.origem,
        observacoes: formMuda.value.observacoes
      })
    }
    fecharModal()
    await carregar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar muda.')
  }
}

function formatarData(dataString) {
  if (!dataString) return '—'
  return new Date(dataString + (String(dataString).includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR')
}

function formatarDataAtual() {
  return new Date().toISOString().substr(0, 10)
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
  background-color: var(--color-text-inverse);
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.secao-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
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
  border-bottom: 1px solid var(--color-border-subtle);
}

.tabela-mudas th {
  font-weight: 600;
  color: var(--color-text-primary);
  background-color: var(--color-surface-muted);
}

.tabela-mudas tbody tr:hover {
  background-color: var(--color-surface-muted);
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
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.estagio-crescimento {
  background-color: var(--color-info-bg);
  color: var(--color-info-dark);
}

.estagio-rustificação {
  background-color: var(--color-attention-bg);
  color: var(--color-attention);
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
  color: var(--color-text-inverse);
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
  background-color: var(--color-text-inverse);
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
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
  color: var(--color-text-muted);
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
  border: 1px solid var(--color-border);
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
  background-color: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-salvar {
  padding: 0.5rem 1rem;
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
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
  background-color: var(--color-surface-muted);
  border: 1px dashed var(--color-border);
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
  color: var(--color-text-muted);
  transition: all 0.2s;
}

.file-label:hover {
  background-color: var(--color-surface-muted);
  border-color: var(--color-border);
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
  border: 1px solid var(--color-border);
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