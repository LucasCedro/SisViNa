<template>
  <PageLayout>

    <p v-if="carregando" class="status-msg">Atualizando panorama…</p>
    <p v-else-if="erroResumo" class="alert alert-error">{{ erroResumo }}</p>

    <ProducaoFluxoBar
      v-if="resumo"
      :blocos="blocosFluxo"
      :bloco-ativo="guiaAtiva"
      @ir-etapa="irEtapa"
    />

    <nav class="guias-navegacao producao-guias" aria-label="Seções de produção">
      <button
        v-for="g in guias"
        :key="g.id"
        type="button"
        class="guia"
        :class="{ ativa: guiaAtiva === g.id }"
        @click="guiaAtiva = g.id"
      >
        {{ g.label }}
      </button>
    </nav>

    <ProducaoVisaoGeral v-show="guiaAtiva === 'visao'" :resumo="resumo" />

    <ProducaoSemeaduraPanel v-show="guiaAtiva === 'semeadura'" @atualizado="recarregar" />

    <ProducaoLiberarCanteiroPanel
      v-show="guiaAtiva === 'liberar_canteiro'"
      ref="liberarCanteiroRef"
      @atualizado="recarregar"
    />

    <ProducaoTransferenciaPanel
      v-show="guiaAtiva === 'transferencia'"
      ref="transferRef"
      @atualizado="recarregar"
      @ir-semeadura="guiaAtiva = 'semeadura'"
      @ir-estagios="guiaAtiva = 'liberar_canteiro'"
    />

    <ProducaoRustificacaoPanel
      v-show="guiaAtiva === 'rustificacao'"
      ref="rustificacaoRef"
      @atualizado="recarregar"
    />

    <ProducaoLiberarVendaPanel
      v-show="guiaAtiva === 'liberar_venda'"
      ref="liberarVendaRef"
      @atualizado="recarregar"
    />
  </PageLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PageLayout from '@/components/layout/PageLayout.vue'
import { usePageTab } from '@/composables/usePageTab'
import ProducaoFluxoBar from '@/components/producao/ProducaoFluxoBar.vue'
import ProducaoVisaoGeral from '@/components/producao/ProducaoVisaoGeral.vue'
import ProducaoSemeaduraPanel from '@/components/producao/ProducaoSemeaduraPanel.vue'
import ProducaoLiberarCanteiroPanel from '@/components/producao/ProducaoLiberarCanteiroPanel.vue'
import ProducaoTransferenciaPanel from '@/components/producao/ProducaoTransferenciaPanel.vue'
import ProducaoRustificacaoPanel from '@/components/producao/ProducaoRustificacaoPanel.vue'
import ProducaoLiberarVendaPanel from '@/components/producao/ProducaoLiberarVendaPanel.vue'
import { getProducaoResumo } from '@/services/producao'

const GUIAS_PRODUCAO = ['visao', 'semeadura', 'liberar_canteiro', 'transferencia', 'rustificacao', 'liberar_venda']
const guiaAtiva = usePageTab('producao', 'visao', { valid: GUIAS_PRODUCAO })
const resumo = ref(null)
const carregando = ref(true)
const erroResumo = ref('')
const transferRef = ref(null)
const liberarCanteiroRef = ref(null)
const rustificacaoRef = ref(null)
const liberarVendaRef = ref(null)

const guias = [
  { id: 'visao', label: 'Visão geral' },
  { id: 'semeadura', label: 'Transferir para sementeira' },
  { id: 'liberar_canteiro', label: 'Liberar para canteiro' },
  { id: 'transferencia', label: 'Transferir para canteiro' },
  { id: 'rustificacao', label: 'Rustificação' },
  { id: 'liberar_venda', label: 'Liberar para venda' },
]

const blocosFluxo = computed(() => {
  const r = resumo.value
  if (!r) return []
  return [
    {
      id: 'semeadura',
      titulo: 'Armazém',
      valorTotal: r.sementes_armazem,
      valorSufixo: 'Sementes',
      subtitulo: `${r.lotes_com_estoque} lote(s) · ${r.especies_armazem ?? 0} espécie(s)`,
    },
    {
      id: 'sementeira',
      titulo: 'Sementeira',
      cards: [
        {
          id: 'dev',
          valor: r.em_desenvolvimento_sementeira,
          label: 'Em desenvolvimento',
          tom: 'desenvolvimento',
          irPara: 'liberar_canteiro',
        },
        {
          id: 'apt-t',
          valor: r.aptas_transferencia,
          label: 'Aptas p/ canteiro',
          tom: 'acao',
          irPara: 'transferencia',
        },
      ],
    },
    {
      id: 'canteiro',
      titulo: 'Canteiro',
      cards: [
        {
          id: 'cresc',
          valor: r.em_crescimento_canteiro,
          label: 'Em crescimento',
          tom: 'crescimento',
          irPara: 'rustificacao',
        },
        {
          id: 'apt-r-c',
          valor: r.aptas_rustificacao_canteiro,
          label: 'Aptas p/ rustificação',
          tom: 'rustificacao',
          irPara: 'rustificacao',
        },
      ],
    },
    {
      id: 'rustificacao',
      titulo: 'Rustificação',
      cards: [
        {
          id: 'rust',
          valor: r.em_rustificacao,
          label: 'Em rustificação',
          tom: 'rustificacao',
          irPara: 'rustificacao',
        },
        {
          id: 'apt-v-r',
          valor: r.prontas_venda_rustificacao,
          label: 'Aptas p/ venda',
          tom: 'venda',
          irPara: 'liberar_venda',
        },
      ],
    },
    {
      id: 'vendidas',
      titulo: 'Vendidas',
      cards: [
        {
          id: 'mtd',
          valor: r.vendidas_mtd,
          label: 'MTD (mês)',
          tom: 'venda',
          irPara: 'visao',
        },
        {
          id: 'ytd',
          valor: r.vendidas_ytd,
          label: 'YTD (ano)',
          tom: 'neutro',
          irPara: 'visao',
        },
      ],
    },
  ]
})

function irEtapa(id) {
  const map = {
    semeadura: 'semeadura',
    sementeira: 'liberar_canteiro',
    liberar_canteiro: 'liberar_canteiro',
    transferencia: 'transferencia',
    canteiro: 'rustificacao',
    rustificacao: 'rustificacao',
    liberar_venda: 'liberar_venda',
    vendidas: 'visao',
  }
  const dest = map[id] || id
  guiaAtiva.value = dest
}

async function recarregar() {
  carregando.value = true
  erroResumo.value = ''
  try {
    resumo.value = await getProducaoResumo()
    transferRef.value?.carregar?.()
    liberarCanteiroRef.value?.carregar?.()
    rustificacaoRef.value?.carregar?.()
    liberarVendaRef.value?.carregar?.()
  } catch (e) {
    erroResumo.value = e.response?.data?.detail || 'Erro ao carregar resumo de produção.'
  } finally {
    carregando.value = false
  }
}

onMounted(recarregar)
</script>

<style scoped>
.producao-guias {
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
}
</style>
