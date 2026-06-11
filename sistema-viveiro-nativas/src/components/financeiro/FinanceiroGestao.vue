<template>
  <section class="fin-sec gestao-sec" aria-label="Gestão financeira">
    <h2 class="fin-sec__titulo">Gestão — receitas e despesas</h2>

    <div class="gestao-abas" role="tablist">
      <button
        v-for="t in abas"
        :key="t.id"
        type="button"
        role="tab"
        :class="['gestao-aba', { ativo: aba === t.id }]"
        @click="aba = t.id"
      >
        {{ t.label }}
      </button>
    </div>

    <!-- Receitas (read-only) -->
    <div v-if="aba === 'receitas'" class="gestao-painel">
      <p class="financeiro-lead">
        Vendas com status <strong>PAGO</strong> no período — registradas em
        <router-link to="/vendas">Vendas</router-link>.
      </p>
      <div v-if="painel.receitas?.length" class="tabela-wrap">
        <table class="gestao-tabela">
          <thead>
            <tr>
              <th>Data</th>
              <th>Comprador</th>
              <th class="num">Itens</th>
              <th class="num">Valor</th>
              <th>Pagamento</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in painel.receitas" :key="r.id">
              <td>{{ fmtData(r.data_venda) }}</td>
              <td>{{ r.comprador_nome || '—' }}</td>
              <td class="num">{{ r.total_itens }}</td>
              <td class="num">{{ fmt(r.valor_total) }}</td>
              <td>{{ r.forma_pagamento || '—' }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="3" class="num"><strong>Total</strong></td>
              <td class="num"><strong>{{ fmt(totalReceitas) }}</strong></td>
              <td />
            </tr>
          </tfoot>
        </table>
      </div>
      <p v-else class="fin-empty">Nenhuma receita (venda paga) neste período.</p>
    </div>

    <!-- Gráficos OPEX/CAPEX do período -->
    <div v-if="aba === 'capex' || aba === 'opex'" class="gestao-grid-graficos">
      <article class="grafico-card">
        <h3>{{ aba === 'opex' ? 'OPEX por categoria' : 'CAPEX por categoria' }}</h3>
        <div v-if="distribuicaoAtual.length">
          <div v-for="(item, i) in distribuicaoAtual" :key="item.categoria" class="barra-h">
            <div class="barra-h__top">
              <span>{{ item.categoria }}</span>
              <span>{{ fmt(item.valor) }} ({{ item.porcentagem }}%)</span>
            </div>
            <div class="barra-h__track">
              <div
                class="barra-h__fill"
                :style="{ width: item.porcentagem + '%', backgroundColor: cores[i % cores.length] }"
              />
            </div>
          </div>
        </div>
        <p v-else class="fin-empty">Sem lançamentos neste período.</p>
      </article>
      <article class="grafico-card">
        <h3>Comparativo por categoria</h3>
        <div v-if="distribuicaoAtual.length" class="barra-v-grid">
          <div v-for="(item, i) in distribuicaoAtual" :key="'v-' + item.categoria" class="barra-v">
            <div
              class="barra-v__col"
              :style="{ height: Math.max(8, item.porcentagem) + '%', backgroundColor: cores[i % cores.length] }"
              :title="fmt(item.valor)"
            />
            <span class="barra-v__lbl">{{ abrev(item.categoria) }}</span>
          </div>
        </div>
        <p v-else class="fin-empty">—</p>
      </article>
    </div>

    <!-- Tabela CAPEX / OPEX -->
    <div v-if="aba === 'capex' || aba === 'opex'" class="gestao-painel">
      <div class="gestao-toolbar">
        <div class="gestao-filtros">
          <label>
            De
            <input v-model="filtros.dataInicial" type="date" />
          </label>
          <label>
            Até
            <input v-model="filtros.dataFinal" type="date" />
          </label>
          <label>
            Categoria
            <select v-model="filtros.categoria">
              <option value="">Todas</option>
              <option v-for="c in categoriasAtivas" :key="c" :value="c">{{ c }}</option>
            </select>
          </label>
          <button type="button" class="btn btn-secondary btn-sm" @click="limparFiltros">Limpar</button>
        </div>
        <button
          v-if="podeEditar"
          type="button"
          class="btn btn-primary btn-sm"
          @click="abrirModalNovo"
        >
          Novo {{ aba.toUpperCase() }}
        </button>
      </div>

      <div class="tabela-wrap">
        <table class="gestao-tabela">
          <thead>
            <tr>
              <th>Descrição</th>
              <th>Categoria</th>
              <th>Data</th>
              <th class="num">Valor</th>
              <th>Pagamento</th>
              <th v-if="podeEditar">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in itensFiltrados" :key="item.id">
              <td>{{ item.descricao }}</td>
              <td>{{ item.categoria }}</td>
              <td>{{ fmtData(item.data) }}</td>
              <td class="num">{{ fmt(item.valor) }}</td>
              <td>{{ item.formaPagamento || '—' }}</td>
              <td v-if="podeEditar" class="gestao-acoes">
                <button type="button" class="btn-icon" title="Editar" @click="editar(item)">✎</button>
                <button type="button" class="btn-icon btn-icon--danger" title="Excluir" @click="excluir(item.id)">✕</button>
              </td>
            </tr>
            <tr v-if="!itensFiltrados.length">
              <td :colspan="podeEditar ? 6 : 5" class="fin-empty">Nenhum lançamento.</td>
            </tr>
          </tbody>
          <tfoot v-if="itensFiltrados.length">
            <tr>
              <td colspan="3" class="num"><strong>Total filtrado</strong></td>
              <td class="num"><strong>{{ fmt(totalFiltrado) }}</strong></td>
              <td :colspan="podeEditar ? 2 : 1" />
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Modal lançamento -->
    <div
      v-if="modalAberto"
      class="modal-overlay"
      @pointerdown.self="onOverlayPointerDown"
      @pointerup.self="onOverlayPointerUp"
      @pointercancel.self="cancelarFechamentoOverlay"
    >
      <div class="modal-box" @pointerdown="onModalPointerDown">
        <div class="modal-head">
          <h3>{{ form.id ? 'Editar' : 'Novo' }} {{ form.tipo }}</h3>
          <button type="button" class="btn-icon" @click="fecharModal">✕</button>
        </div>
        <form class="modal-body" @submit.prevent="salvar">
          <label>
            Descrição
            <input v-model="form.descricao" required type="text" />
          </label>
          <label>
            Categoria
            <select v-model="form.categoria" required>
              <option v-for="c in categoriasForm" :key="c" :value="c">{{ c }}</option>
            </select>
          </label>
          <label>
            Data
            <input v-model="form.data" required type="date" />
          </label>
          <label>
            Valor (R$)
            <input v-model.number="form.valor" required type="number" min="0" step="0.01" />
          </label>
          <label>
            Forma de pagamento
            <select v-model="form.formaPagamento" required>
              <option v-for="fp in formasPagamento" :key="fp" :value="fp">{{ fp }}</option>
            </select>
          </label>
          <label>
            Observações
            <textarea v-model="form.observacoes" rows="3" />
          </label>
          <div class="modal-foot">
            <button type="button" class="btn btn-secondary btn-sm" @click="fecharModal">Cancelar</button>
            <button type="submit" class="btn btn-primary btn-sm">Salvar</button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  createLancamento,
  updateLancamento,
  deleteLancamento,
} from '@/services/lancamentosFinanceiros'
import { CHART_PALETTE } from '@/constants/chartColors'
import { useModalOverlayClose } from '@/composables/useModalOverlayClose'

const props = defineProps({
  painel: { type: Object, required: true },
  lancamentos: { type: Array, default: () => [] },
  podeEditar: { type: Boolean, default: false },
})

const emit = defineEmits(['atualizar'])

const abas = [
  { id: 'receitas', label: 'Receitas' },
  { id: 'opex', label: 'OPEX' },
  { id: 'capex', label: 'CAPEX' },
]

const aba = ref('receitas')
const modalAberto = ref(false)
const cores = CHART_PALETTE

const categoriasCapex = [
  'Construção e Infraestrutura',
  'Máquinas e Equipamentos',
  'Sistemas de Irrigação',
  'Veículos',
  'Terrenos',
  'Ferramentas Permanentes',
  'Estufas e Estruturas',
  'Tecnologia e Software',
]

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
  'Administrativo',
]

const formasPagamento = [
  'Dinheiro',
  'Cartão de Crédito',
  'Cartão de Débito',
  'Transferência Bancária',
  'Pix',
  'Boleto Bancário',
]

const filtros = ref({ dataInicial: '', dataFinal: '', categoria: '' })

const form = ref(emptyForm('OPEX'))

function emptyForm(tipo) {
  return {
    id: null,
    tipo,
    descricao: '',
    categoria: tipo === 'CAPEX' ? categoriasCapex[0] : categoriasOpex[0],
    data: new Date().toISOString().slice(0, 10),
    valor: 0,
    formaPagamento: 'Transferência Bancária',
    observacoes: '',
  }
}

function periodoBounds() {
  const { mes, ano } = props.painel?.periodo || {}
  if (!mes || !ano) return { ini: '', fim: '' }
  const ultimo = new Date(ano, mes, 0).getDate()
  const pad = (n) => String(n).padStart(2, '0')
  return {
    ini: `${ano}-${pad(mes)}-01`,
    fim: `${ano}-${pad(mes)}-${pad(ultimo)}`,
  }
}

watch(
  () => props.painel?.periodo,
  () => {
    const { ini, fim } = periodoBounds()
    filtros.value.dataInicial = ini
    filtros.value.dataFinal = fim
    filtros.value.categoria = ''
  },
  { immediate: true, deep: true }
)

const categoriasAtivas = computed(() => (aba.value === 'capex' ? categoriasCapex : categoriasOpex))
const categoriasForm = computed(() => (form.value.tipo === 'CAPEX' ? categoriasCapex : categoriasOpex))

const distribuicaoAtual = computed(() => {
  if (aba.value === 'opex') return props.painel?.opex_por_categoria || []
  if (aba.value === 'capex') return props.painel?.capex_por_categoria || []
  return []
})

const itensFiltrados = computed(() => {
  const tipo = aba.value.toUpperCase()
  let list = props.lancamentos.filter((l) => l.tipo === tipo)
  if (filtros.value.dataInicial) list = list.filter((l) => l.data >= filtros.value.dataInicial)
  if (filtros.value.dataFinal) list = list.filter((l) => l.data <= filtros.value.dataFinal)
  if (filtros.value.categoria) list = list.filter((l) => l.categoria === filtros.value.categoria)
  return list.sort((a, b) => (b.data > a.data ? 1 : -1))
})

const totalFiltrado = computed(() => itensFiltrados.value.reduce((s, i) => s + i.valor, 0))
const totalReceitas = computed(() =>
  (props.painel?.receitas || []).reduce((s, r) => s + Number(r.valor_total || 0), 0)
)

function fmt(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function fmtData(iso) {
  if (!iso) return '—'
  const d = iso.includes('T') ? iso.slice(0, 10) : iso
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y}`
}

function abrev(s) {
  return (s || '').split(' ')[0].slice(0, 8)
}

function limparFiltros() {
  const { ini, fim } = periodoBounds()
  filtros.value = { dataInicial: ini, dataFinal: fim, categoria: '' }
}

function abrirModalNovo() {
  form.value = emptyForm(aba.value.toUpperCase())
  modalAberto.value = true
}

function editar(item) {
  form.value = { ...item }
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

async function salvar() {
  const payload = {
    tipo: form.value.tipo,
    descricao: form.value.descricao,
    categoria: form.value.categoria,
    data_lancamento: form.value.data,
    valor: form.value.valor,
    forma_pagamento: form.value.formaPagamento,
    observacoes: form.value.observacoes,
  }
  try {
    if (form.value.id) await updateLancamento(form.value.id, payload)
    else await createLancamento(payload)
    fecharModal()
    emit('atualizar')
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar.')
  }
}

async function excluir(id) {
  if (!confirm('Excluir este lançamento?')) return
  try {
    await deleteLancamento(id)
    emit('atualizar')
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir.')
  }
}
</script>

<style scoped>
@import './financeiro-shared.css';

.num {
  @apply text-right tabular-nums;
}
</style>
