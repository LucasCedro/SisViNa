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
        Recebimentos com status <strong>PAGO</strong> no período (data de pagamento) —
        registrados em <router-link to="/vendas">Vendas</router-link>.
        Vendas pendentes aparecem na DRE contábil em <router-link to="/contabilidade">Contabilidade</router-link>.
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

    <!-- Gráficos OPEX (premissas) / CAPEX (lançamentos) -->
    <div v-if="aba === 'capex' || aba === 'opex'" class="gestao-grid-graficos">
      <article class="grafico-card">
        <h3>{{ aba === 'opex' ? 'OPEX — premissas DRE' : 'CAPEX por categoria' }}</h3>
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
        <p v-else class="fin-empty">
          {{ aba === 'opex' ? 'Nenhuma premissa DESPESA configurada.' : 'Sem lançamentos neste período.' }}
        </p>
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

    <!-- OPEX automático (premissas) -->
    <div v-if="aba === 'opex'" class="gestao-painel">
      <p class="financeiro-lead">
        OPEX entra na DRE <strong>automaticamente</strong> — comissão (% sobre faturamento do período)
        + despesas mensais fixas das premissas DESPESA.
        Não é necessário lançar OPEX manualmente.
        <router-link to="/financeiro">Editar premissas</router-link>
      </p>
      <div class="tabela-wrap">
        <table class="gestao-tabela">
          <thead>
            <tr>
              <th>Premissa</th>
              <th>Tipo</th>
              <th class="num">Valor no período</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in itensOpexPremissas" :key="item.chave">
              <td>{{ item.nome }}</td>
              <td>{{ item.tipo === 'comissao' ? 'Comissão (% receita)' : 'Despesa fixa/mês' }}</td>
              <td class="num">{{ fmt(item.valor) }}</td>
            </tr>
            <tr v-if="!itensOpexPremissas.length">
              <td colspan="3" class="fin-empty">Configure premissas DESPESA em Financeiro → Premissas.</td>
            </tr>
          </tbody>
          <tfoot v-if="itensOpexPremissas.length">
            <tr>
              <td colspan="2" class="num"><strong>Total OPEX (DRE)</strong></td>
              <td class="num"><strong>{{ fmt(painel.dre.opex) }}</strong></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Tabela CAPEX (lançamentos manuais) -->
    <div v-if="aba === 'capex'" class="gestao-painel">
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
          v-if="podeCriar && aba === 'capex'"
          type="button"
          class="btn btn-primary btn-sm"
          @click="abrirModalNovo"
        >
          Novo CAPEX
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
              <th v-if="podeEditarFin || podeExcluir">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in itensFiltrados" :key="item.id">
              <td>{{ item.descricao }}</td>
              <td>{{ item.categoria }}</td>
              <td>{{ fmtData(item.data) }}</td>
              <td class="num">{{ fmt(item.valor) }}</td>
              <td>{{ item.formaPagamento || '—' }}</td>
              <td v-if="podeEditarFin || podeExcluir" class="gestao-acoes">
                <button v-if="podeEditarFin" type="button" class="btn-icon" title="Editar" @click="editar(item)">✎</button>
                <button v-if="podeExcluir" type="button" class="btn-icon btn-icon--danger" title="Excluir" @click="excluir(item.id)">✕</button>
              </td>
            </tr>
            <tr v-if="!itensFiltrados.length">
              <td :colspan="(podeEditarFin || podeExcluir) ? 6 : 5" class="fin-empty">Nenhum lançamento.</td>
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
    <AppModalOverlay
      :aberto="modalAberto"
      :handlers="modalClose"
      panel-class="app-modal-panel--md"
    >
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
    </AppModalOverlay>
    <ConfirmSaidaModal
      :aberto="confirmAberto"
      @confirmar="confirmarSaida"
      @cancelar="cancelarSaida"
    />
  </section>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { useFormDirty } from '@/utils/formDirty'
import {
  createLancamento,
  updateLancamento,
  deleteLancamento,
} from '@/services/lancamentosFinanceiros'
import { CHART_PALETTE } from '@/constants/chartColors'
import { usePermissions } from '@/composables/usePermissions'

const { can } = usePermissions()
const podeCriar = computed(() => can('financeiro.create'))
const podeEditarFin = computed(() => can('financeiro.edit'))
const podeExcluir = computed(() => can('financeiro.delete'))

const props = defineProps({
  painel: { type: Object, required: true },
  lancamentos: { type: Array, default: () => [] },
  podeEditar: { type: Boolean, default: false },
})

const emit = defineEmits(['atualizar'])

const abas = [
  { id: 'receitas', label: 'Receitas' },
  { id: 'opex', label: 'OPEX (automático)' },
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

const { isDirty, rebase } = useFormDirty(form, () => modalAberto.value)

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

const itensOpexPremissas = computed(() =>
  (props.painel?.despesas_estimadas?.itens || []).filter((i) => Number(i.valor) > 0)
)

const itensFiltrados = computed(() => {
  if (aba.value !== 'capex') return []
  let list = props.lancamentos.filter((l) => l.tipo === 'CAPEX')
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
  if (!podeCriar.value) return
  form.value = emptyForm(aba.value.toUpperCase())
  modalAberto.value = true
  nextTick().then(rebase)
}

function editar(item) {
  if (!podeEditarFin.value) return
  form.value = { ...item }
  modalAberto.value = true
  nextTick().then(rebase)
}

function fecharModalInterno() {
  modalAberto.value = false
}

const modalClose = useModalFormClose(fecharModalInterno, () => isDirty.value, () => modalAberto.value)
const {
  resetOverlayPress,
  confirmAberto,
  confirmarSaida,
  cancelarSaida,
  requestClose,
  sairSemConfirmar,
} = modalClose

function fecharModal() {
  resetOverlayPress()
  requestClose()
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
    sairSemConfirmar()
    emit('atualizar')
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar.')
  }
}

async function excluir(id) {
  if (!podeExcluir.value) return
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
