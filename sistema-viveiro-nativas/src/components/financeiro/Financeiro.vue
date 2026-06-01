<template>
  <div class="financeiro-root">
    <nav class="fin-abas" aria-label="Seções do financeiro">
      <button
        v-for="t in abas"
        :key="t.id"
        type="button"
        class="fin-aba"
        :class="{ ativo: aba === t.id }"
        @click="aba = t.id"
      >
        {{ t.label }}
      </button>
    </nav>

    <FinanceiroPainel
      v-show="aba === 'resultado'"
      :painel="painel"
      :lancamentos="lancamentos"
      :carregando="carregando"
      :erro="erro"
      :mes="mes"
      :ano="ano"
      :pode-editar="podeEditar"
      @atualizar="carregar"
      @periodo="onPeriodo"
    />

    <FinanceiroPremissas
      v-show="aba === 'premissas'"
      :pode-editar="podeEditar"
      :faturamento="painel?.dre?.faturamento"
      :mudas-vivas="painel?.estoque?.mudas_vivas"
      @atualizar="carregar"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import FinanceiroPainel from './FinanceiroPainel.vue'
import FinanceiroPremissas from './FinanceiroPremissas.vue'
import { getPainelFinanceiro } from '@/services/financeiro'
import { listLancamentos } from '@/services/lancamentosFinanceiros'
import { usePermissions } from '@/composables/usePermissions'

const { can } = usePermissions()
const podeEditar = computed(() => can('financeiro.edit'))

const aba = ref('resultado')
const abas = [
  { id: 'resultado', label: 'Resultado' },
  { id: 'premissas', label: 'Premissas' },
]

const hoje = new Date()
const mes = ref(hoje.getMonth() + 1)
const ano = ref(hoje.getFullYear())

const painel = ref(null)
const lancamentos = ref([])
const carregando = ref(false)
const erro = ref(null)

function mapLancamento(l) {
  return {
    id: l.id,
    tipo: l.tipo,
    descricao: l.descricao,
    categoria: l.categoria,
    data: l.data_lancamento,
    valor: Number(l.valor),
    formaPagamento: l.forma_pagamento || '',
    observacoes: l.observacoes || '',
  }
}

async function carregar() {
  carregando.value = true
  erro.value = null
  try {
    const [p, lanc] = await Promise.all([
      getPainelFinanceiro({ mes: mes.value, ano: ano.value }),
      listLancamentos(),
    ])
    painel.value = p
    lancamentos.value = lanc.map(mapLancamento)
  } catch (e) {
    console.error(e)
    erro.value = e.response?.data?.detail || 'Não foi possível carregar o painel financeiro.'
    painel.value = null
  } finally {
    carregando.value = false
  }
}

function onPeriodo({ mes: m, ano: a }) {
  mes.value = m
  ano.value = a
  carregar()
}

onMounted(carregar)
</script>

<style scoped>
.fin-abas {
  @apply flex gap-1 border-b border-primary-100 mb-6 max-w-7xl mx-auto px-4 md:px-6;
}

.fin-aba {
  @apply px-4 py-2.5 text-sm font-medium text-text-secondary border-b-2 border-transparent -mb-px hover:text-primary;
}

.fin-aba.ativo {
  @apply text-primary border-primary font-semibold;
}
</style>
