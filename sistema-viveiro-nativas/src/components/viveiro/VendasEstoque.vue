<template>
  <div class="vendas-estoque-container">
    <aside class="estoque-aviso" role="note">
      <strong>Estoque comercial</strong> — só entram mudas marcadas como
      <em>aptas p/ venda</em> em Produção. A venda aqui dá baixa automática (planta →
      <code>VENDIDA</code>), reduz o estoque e registra receita para o financeiro.
      Não é possível vender pela tela de Produção.
    </aside>

    <p v-if="erro" class="alert-erro">{{ erro }}</p>

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
              <td>{{ formatarData(venda.data_venda) }}</td>
              <td>{{ venda.total_itens }} planta(s)</td>
              <td>{{ venda.total_itens }}</td>
              <td>R$ {{ Number(venda.valor_total).toFixed(2) }}</td>
              <td>{{ venda.comprador_nome }}</td>
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
        <span class="estoque-total">{{ totalUnidadesEstoque }} unidade(s) aptas p/ venda</span>
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
            <tr v-for="item in estoqueItems" :key="item.id_especie" :class="{ 'estoque-baixo': item.quantidade < 20 }">
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
    <AppModalOverlay
      :aberto="modalEstoqueAberto"
      :handlers="overlayEstoque"
      panel-class="app-modal-panel--md"
    >
      <div class="modal-header">
          <h2 class="modal-title">Preço de venda da espécie</h2>
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
              <label for="quantidade">Quantidade (estoque real):</label>
              <input
                type="number"
                id="quantidade"
                v-model.number="formEstoque.quantidade"
                disabled
                title="Quantidade vem das plantas aptas; altere em Produção ou registre vendas"
              >
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="valor-unitario">Valor Unitário (R$):</label>
              <input type="number" id="valor-unitario" v-model.number="formEstoque.valorUnitario" step="0.01" min="0" required>
            </div>
            
            <div class="form-group">
              <label for="localizacao">Localização:</label>
              <input type="text" id="localizacao" v-model="formEstoque.localizacao" disabled>
            </div>
          </div>
          
          <div class="form-buttons">
            <button type="button" class="btn-cancelar" @click="fecharModalEstoque">Cancelar</button>
            <button type="submit" class="btn-salvar">Salvar</button>
          </div>
        </form>
    </AppModalOverlay>
    <ConfirmSaidaModal
      :aberto="confirmAbertoEstoque"
      @confirmar="confirmarSaidaEstoque"
      @cancelar="cancelarSaidaEstoque"
    />
    
    <!-- Modal de Nova Venda -->
    <AppModalOverlay
      :aberto="modalVendaAberto"
      :handlers="overlayVenda"
      panel-class="app-modal-panel--md"
    >
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
                <option v-for="item in estoqueDisponivel" :key="item.id_especie" :value="item.id_especie">
                  {{ item.nomePopular || item.nomeCientifico }} ({{ item.quantidade }} disponíveis)
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
              <label for="comprador">Comprador:</label>
              <select id="comprador" v-model.number="formVenda.idComprador" required>
                <option value="">Selecione</option>
                <option v-for="c in compradores" :key="c.id" :value="c.id">{{ c.nome }}</option>
              </select>
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
    </AppModalOverlay>
    <ConfirmSaidaModal
      :aberto="confirmAbertoVenda"
      @confirmar="confirmarSaidaVenda"
      @cancelar="cancelarSaidaVenda"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { useFormDirty } from '@/utils/formDirty'
import { useAuthStore } from '@/store/auth'
import {
  getEstoqueResumo,
  atualizarPrecoEspecie,
} from '@/services/plantas'
import { listVendas, createVenda } from '@/services/vendas'
import { listCompradores } from '@/services/compradores'

const auth = useAuthStore()
const carregando = ref(true)
const erro = ref(null)

const estoqueItems = ref([])
const historicoVendas = ref([])
const compradores = ref([])

// Estado para modais
const modalVendaAberto = ref(false)
const modalEstoqueAberto = ref(false)
const formEstoque = ref({
  id_especie: null,
  nomePopular: '',
  nomeCientifico: '',
  quantidade: 0,
  valorUnitario: 0,
  localizacao: ''
})

// Formulários
const formVenda = ref({
  data: new Date().toISOString().substr(0, 10),
  especieId: '',
  quantidade: 1,
  valorTotal: 0,
  idComprador: '',
  formaPagamento: 'PIX',
  observacoes: ''
})

const { isDirty: isDirtyEstoque, rebase: rebaseEstoque } = useFormDirty(
  formEstoque,
  () => modalEstoqueAberto.value
)
const { isDirty: isDirtyVenda, rebase: rebaseVenda } = useFormDirty(
  formVenda,
  () => modalVendaAberto.value
)

// Computed properties
const estoqueDisponivel = computed(() => {
  return estoqueItems.value.filter((item) => item.quantidade > 0)
})

const totalUnidadesEstoque = computed(() =>
  estoqueItems.value.reduce((s, i) => s + (i.quantidade || 0), 0)
)

const especieSelecionada = computed(() => {
  if (!formVenda.value.especieId) return null
  return estoqueItems.value.find((item) => item.id_especie === Number(formVenda.value.especieId))
})

async function carregar() {
  carregando.value = true
  erro.value = null
  try {
    const [estoque, vendas, comps] = await Promise.all([
      getEstoqueResumo(),
      listVendas({ limit: 200 }),
      listCompradores({ ativo: true, limit: 200 })
    ])
    estoqueItems.value = estoque.map((e) => ({
      id_especie: e.id_especie,
      nomePopular: e.nome_popular,
      nomeCientifico: e.nome_cientifico,
      tamanho: e.status_predominante || '—',
      quantidade: e.quantidade,
      valorUnitario: Number(e.valor_unitario) || 0,
      localizacao: e.localizacao || '—'
    }))
    historicoVendas.value = vendas
    compradores.value = comps
  } catch (e) {
    erro.value = 'Falha ao carregar vendas/estoque.'
    console.error(e)
  } finally {
    carregando.value = false
  }
}

onMounted(carregar)

// Métodos para o registro de vendas
function abrirFormularioNovaVenda() {
  formVenda.value = {
    data: new Date().toISOString().substr(0, 10),
    especieId: '',
    quantidade: 1,
    valorTotal: 0,
    idComprador: compradores.value[0]?.id || '',
    formaPagamento: 'PIX',
    observacoes: ''
  }
  modalVendaAberto.value = true
  nextTick().then(rebaseVenda)
}

function fecharModalVendaInterno() {
  modalVendaAberto.value = false
}

const overlayVenda = useModalFormClose(fecharModalVendaInterno, () => isDirtyVenda.value, () => modalVendaAberto.value)
const {
  confirmAberto: confirmAbertoVenda,
  confirmarSaida: confirmarSaidaVenda,
  cancelarSaida: cancelarSaidaVenda,
  requestClose: requestCloseVenda,
  sairSemConfirmar: sairSemConfirmarVenda,
} = overlayVenda

function fecharModalVenda() {
  overlayVenda.resetOverlayPress()
  requestCloseVenda()
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

async function salvarVenda() {
  if (!especieSelecionada.value || formVenda.value.quantidade > especieSelecionada.value.quantidade) {
    alert('Quantidade indisponível no estoque!')
    return
  }
  if (!formVenda.value.idComprador || !auth.user?.id) {
    alert('Selecione comprador e faça login.')
    return
  }
  try {
    const valorUnit = especieSelecionada.value.valorUnitario
    await createVenda({
      id_comprador: Number(formVenda.value.idComprador),
      id_funcionario: auth.user.id,
      data_venda: `${formVenda.value.data}T12:00:00`,
      forma_pagamento: formVenda.value.formaPagamento,
      status: 'PAGO',
      observacoes: formVenda.value.observacoes,
      itens_por_especie: [
        {
          id_especie: especieSelecionada.value.id_especie,
          quantidade: formVenda.value.quantidade,
          valor_unitario: valorUnit,
          desconto: 0,
        },
      ],
    })
    sairSemConfirmarVenda()
    await carregar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao registrar venda.')
  }
}

function editarEstoque(item) {
  formEstoque.value = { ...item }
  modalEstoqueAberto.value = true
  nextTick().then(rebaseEstoque)
}

function fecharModalEstoqueInterno() {
  modalEstoqueAberto.value = false
}

const overlayEstoque = useModalFormClose(fecharModalEstoqueInterno, () => isDirtyEstoque.value, () => modalEstoqueAberto.value)
const {
  confirmAberto: confirmAbertoEstoque,
  confirmarSaida: confirmarSaidaEstoque,
  cancelarSaida: cancelarSaidaEstoque,
  requestClose: requestCloseEstoque,
  sairSemConfirmar: sairSemConfirmarEstoque,
} = overlayEstoque

function fecharModalEstoque() {
  overlayEstoque.resetOverlayPress()
  requestCloseEstoque()
}

async function salvarEstoque() {
  try {
    await atualizarPrecoEspecie(formEstoque.value.id_especie, formEstoque.value.valorUnitario)
    sairSemConfirmarEstoque()
    await carregar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao atualizar preço.')
  }
}

// Função para formatar data
function formatarData(dataString) {
  const data = new Date(dataString);
  return data.toLocaleDateString('pt-BR');
}
</script>

<style>
.estoque-aviso {
  margin: 0 0 1.25rem;
  padding: 0.85rem 1rem;
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary-100);
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.45;
}

.estoque-aviso code {
  font-size: 0.8125rem;
  color: var(--color-primary-700);
}

.alert-erro {
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  background: var(--color-error-bg);
  color: var(--color-error);
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
}

.estoque-total {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

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
  border-bottom: 1px solid var(--color-border-subtle);
}

.tabela-estoque th,
.tabela-vendas th {
  font-weight: 600;
  color: var(--color-text-primary);
  background-color: var(--color-surface-muted);
}

.tabela-estoque tbody tr:hover,
.tabela-vendas tbody tr:hover {
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

.estoque-baixo {
  background-color: rgba(255, 193, 7, 0.1);
}

.qtd-alerta {
  color: var(--color-error);
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

.tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.pagamento-tag {
  background-color: var(--color-info-bg);
  color: var(--color-info);
}

/* Estilos para o modal */
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

.info-texto {
  font-size: 0.75rem;
  color: var(--color-text-muted);
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