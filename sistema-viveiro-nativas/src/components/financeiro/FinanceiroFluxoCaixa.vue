<template>
  <div class="financeiro-page">
    <header class="financeiro-toolbar">
      <div class="financeiro-toolbar__periodo">
        <label class="field-inline">
          <span>Mês</span>
          <select v-model.number="mesLocal" @change="emitPeriodo">
            <option v-for="(nome, idx) in meses" :key="idx" :value="idx + 1">{{ nome }}</option>
          </select>
        </label>
        <label class="field-inline">
          <span>Ano</span>
          <select v-model.number="anoLocal" @change="emitPeriodo">
            <option v-for="a in anosDisponiveis" :key="a" :value="a">{{ a }}</option>
          </select>
        </label>
      </div>
      <button type="button" class="btn btn-secondary btn-sm" :disabled="carregando" @click="$emit('atualizar')">
        {{ carregando ? 'Atualizando…' : 'Atualizar' }}
      </button>
    </header>

    <p v-if="carregando && !painel" class="alert alert-info">Carregando fluxo de caixa…</p>
    <p v-else-if="erro" class="alert alert-error">{{ erro }}</p>

    <template v-else-if="painel && dfc">
      <p class="financeiro-lead">
        <strong>Demonstração de Fluxo de Caixa (DFC)</strong> — só entra o que foi <em>efetivamente pago</em>.
        Vendas pendentes aparecem em «A receber»; a receita contábil está em
        <router-link to="/contabilidade">Contabilidade → DRE</router-link>.
      </p>

      <!-- DFC principal -->
      <section class="fin-sec fin-sec--dfc" aria-label="Fluxo de caixa do período">
        <h2 class="fin-sec__titulo fin-sec__titulo--dfc">
          Fluxo de caixa — {{ painel.periodo.label }}
        </h2>

        <div class="dfc-wrap">
          <div class="dfc-bloco dfc-bloco--op">
            <h3 class="dfc-bloco__titulo">Atividades operacionais</h3>
            <div class="dfc-linha dfc-linha--entrada">
              <button type="button" class="dfc-linha__btn" @click="toggleDetalhe('entradas')">
                <span class="dfc-linha__chev">{{ detalheAberto === 'entradas' ? '▾' : '▸' }}</span>
                <span>(+) Recebimentos de clientes</span>
                <strong>{{ fmt(dfc.operacional.entradas) }}</strong>
              </button>
              <span class="dfc-linha__meta">{{ dfc.qtd_recebimentos }} pagamento(s) · ticket {{ fmt(dfc.ticket_medio_recebido) }}</span>
              <FinanceiroDetalheBloco
                v-if="detalheAberto === 'entradas' && detalhesDfc"
                tipo="recebimentos"
                :bloco="detalhesDfc.recebimentos"
              />
            </div>
            <div class="dfc-linha dfc-linha--saida">
              <button type="button" class="dfc-linha__btn" @click="toggleDetalhe('saidas-op')">
                <span class="dfc-linha__chev">{{ detalheAberto === 'saidas-op' ? '▾' : '▸' }}</span>
                <span>(−) Pagamentos — compras de insumo</span>
                <strong>{{ fmtNeg(dfc.operacional.saidas) }}</strong>
              </button>
              <span class="dfc-linha__meta">{{ dfc.qtd_compras || 0 }} compra(s) paga(s)</span>
              <FinanceiroDetalheBloco
                v-if="detalheAberto === 'saidas-op' && detalhesDfc"
                tipo="compras_insumos"
                :bloco="detalhesDfc.compras"
              />
            </div>
            <div class="dfc-linha dfc-linha--subtotal dfc-linha--clicavel">
              <button type="button" class="dfc-linha__btn" @click="toggleDetalhe('operacional')">
                <span class="dfc-linha__chev">{{ detalheAberto === 'operacional' ? '▾' : '▸' }}</span>
                <span>(=) Caixa operacional</span>
                <strong>{{ fmt(dfc.operacional.subtotal) }}</strong>
              </button>
              <FinanceiroDetalheBloco
                v-if="detalheAberto === 'operacional' && detalhesDfc"
                tipo="dfc_operacional"
                :bloco="detalhesDfc.operacional"
              />
            </div>
          </div>

          <div class="dfc-bloco dfc-bloco--inv">
            <h3 class="dfc-bloco__titulo">Atividades de investimento</h3>
            <div class="dfc-linha dfc-linha--saida">
              <button type="button" class="dfc-linha__btn" @click="toggleDetalhe('saidas')">
                <span class="dfc-linha__chev">{{ detalheAberto === 'saidas' ? '▾' : '▸' }}</span>
                <span>(−) Pagamentos CAPEX</span>
                <strong>{{ fmtNeg(dfc.investimento.saidas) }}</strong>
              </button>
              <FinanceiroDetalheBloco
                v-if="detalheAberto === 'saidas' && detalhesDfc"
                tipo="capex"
                :bloco="detalhesDfc.capex"
              />
            </div>
            <div class="dfc-linha dfc-linha--subtotal dfc-linha--clicavel">
              <button type="button" class="dfc-linha__btn" @click="toggleDetalhe('investimento')">
                <span class="dfc-linha__chev">{{ detalheAberto === 'investimento' ? '▾' : '▸' }}</span>
                <span>(=) Caixa de investimento</span>
                <strong>{{ fmt(dfc.investimento.subtotal) }}</strong>
              </button>
              <FinanceiroDetalheBloco
                v-if="detalheAberto === 'investimento' && detalhesDfc"
                tipo="dfc_investimento"
                :bloco="detalhesDfc.investimento"
              />
            </div>
          </div>

          <div class="dfc-linha dfc-linha--total dfc-linha--clicavel" :class="sinalClass(dfc.variacao_caixa)">
            <button type="button" class="dfc-linha__btn dfc-linha__btn--total" @click="toggleDetalhe('variacao')">
              <span class="dfc-linha__chev">{{ detalheAberto === 'variacao' ? '▾' : '▸' }}</span>
              <span>(=) Variação líquida de caixa</span>
              <strong>{{ fmt(dfc.variacao_caixa) }}</strong>
            </button>
            <FinanceiroDetalheBloco
              v-if="detalheAberto === 'variacao' && detalhesDfc"
              tipo="dfc_variacao"
              :bloco="detalhesDfc.variacao"
            />
          </div>
        </div>

        <!-- KPIs caixa (não estoque) -->
        <div class="kpi-grid kpi-grid--dfc">
          <article
            v-for="kpi in kpisCaixa"
            :key="kpi.id"
            class="kpi-card"
            :class="kpi.classe"
          >
            <button type="button" class="kpi-card__btn" @click="abrirKpiModal(kpi)">
              <span class="kpi-card__label">{{ kpi.label }}</span>
              <strong class="kpi-card__valor">{{ kpi.valorFmt }}</strong>
              <span class="kpi-card__meta">{{ kpi.meta }}</span>
              <span v-if="kpi.hint" class="kpi-card__hint">{{ kpi.hint }}</span>
            </button>
          </article>
        </div>

        <AppModalOverlay
          :aberto="!!kpiModal"
          :handlers="modalCloseKpi"
          panel-class="app-modal-panel--xl"
        >
          <header class="fin-modal-header">
              <div>
                <p class="fin-modal-eyebrow">Composição do indicador</p>
                <h2>{{ kpiModal.label }}</h2>
                <p class="fin-modal-valor">{{ kpiModal.valorFmt }}</p>
              </div>
              <button type="button" class="fin-modal-fechar" aria-label="Fechar" @click="fecharKpiModal">×</button>
            </header>
            <div class="fin-modal-body">
              <FinanceiroDetalheBloco
                v-if="kpiModal.tipoDetalhe && blocoKpiModal"
                :tipo="kpiModal.tipoDetalhe"
                :bloco="blocoKpiModal"
                :embedded="false"
              />
              <p v-else class="dfc-modal-texto">{{ kpiModal.texto }}</p>
            </div>
            <footer class="fin-modal-footer">
              <button type="button" class="btn btn-secondary btn-sm" @click="fecharKpiModal">Fechar</button>
            </footer>
        </AppModalOverlay>

        <div v-if="painel.evolucao_caixa?.length" class="evolucao-wrap evolucao-wrap--dfc">
          <h3 class="fin-sub">Evolução do caixa — últimos 12 meses</h3>
          <div class="evolucao-chart evolucao-chart--dfc">
            <div
              v-for="p in painel.evolucao_caixa"
              :key="p.label"
              class="evolucao-col"
              :title="`${p.label}: saldo ${fmt(p.saldo)}`"
            >
              <div
                class="evolucao-bar evolucao-bar--entrada"
                :style="{ height: barPct(p.entradas) + '%', backgroundColor: coresDfc.entrada }"
              />
              <div
                class="evolucao-bar evolucao-bar--saida"
                :style="{
                  height: barPct(p.saidas) + '%',
                  backgroundColor: coresDfc.saida,
                  opacity: coresDfc.saidaOpacity,
                }"
              />
              <div
                class="evolucao-bar evolucao-bar--saldo"
                :style="{
                  height: barPct(Math.abs(p.saldo)) + '%',
                  backgroundColor: p.saldo >= 0 ? coresDfc.saldoPos : coresDfc.saldoNeg,
                }"
              />
              <span class="evolucao-label">{{ p.label.split('/')[0] }}</span>
            </div>
          </div>
          <div class="evolucao-legenda">
            <span><i class="dot" :style="{ backgroundColor: coresDfc.entrada }" /> Entradas</span>
            <span><i class="dot" :style="{ backgroundColor: coresDfc.saida }" /> Saídas</span>
            <span><i class="dot" :style="{ backgroundColor: coresDfc.saldoPos }" /> Saldo</span>
          </div>
        </div>
      </section>

      <!-- Comparativo competência vs caixa -->
      <section v-if="dfc.qtd_pendentes_periodo" class="fin-sec fin-sec--comparativo" aria-label="Diferença competência e caixa">
        <h2 class="fin-sec__titulo">Competência × Caixa</h2>
        <p class="dfc-comparativo">
          <strong>{{ dfc.qtd_pendentes_periodo }} venda(s)</strong> neste período ainda
          <strong>PENDENTE</strong> de pagamento — total
          <strong>{{ fmt(dfc.a_receber_periodo) }}</strong>.
          Na <router-link to="/contabilidade">Contabilidade (DRE)</router-link> esse valor já compõe a receita;
          aqui só entra quando for aprovado em <router-link to="/vendas">Vendas</router-link>.
        </p>
      </section>

      <FinanceiroGestao
        :painel="painel"
        :lancamentos="lancamentos"
        :pode-editar="podeEditar"
        @atualizar="$emit('atualizar')"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import FinanceiroGestao from './FinanceiroGestao.vue'
import FinanceiroDetalheBloco from './FinanceiroDetalheBloco.vue'
import { useSimpleModalClose } from '@/composables/useSimpleModalClose'
import { CHART_DFC } from '@/constants/chartColors'

const coresDfc = CHART_DFC

const props = defineProps({
  painel: { type: Object, default: null },
  lancamentos: { type: Array, default: () => [] },
  carregando: { type: Boolean, default: false },
  erro: { type: String, default: null },
  mes: { type: Number, required: true },
  ano: { type: Number, required: true },
  podeEditar: { type: Boolean, default: false },
})

const emit = defineEmits(['atualizar', 'periodo'])

const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
const mesLocal = ref(props.mes)
const anoLocal = ref(props.ano)
const detalheAberto = ref(null)
const kpiModal = ref(null)

watch(() => [props.mes, props.ano], ([m, a]) => {
  mesLocal.value = m
  anoLocal.value = a
  detalheAberto.value = null
  kpiModal.value = null
})

const dfc = computed(() => props.painel?.dfc)
const detalhesDfc = computed(() => props.painel?.detalhes_dfc)

const blocoKpiModal = computed(() => {
  const d = detalhesDfc.value
  const k = kpiModal.value
  if (!d || !k?.blocoId) return null
  return d[k.blocoId] || null
})

const anosDisponiveis = computed(() => {
  const y = new Date().getFullYear()
  return [y - 1, y, y + 1]
})

const kpisCaixa = computed(() => {
  const d = dfc.value
  if (!d) return []
  return [
    {
      id: 'entrada',
      label: 'Recebimentos',
      valorFmt: fmt(d.operacional.entradas),
      classe: 'kpi-card--dfc-entrada',
      meta: `${d.qtd_recebimentos} pagamento(s) no período`,
      hint: 'Ver composição',
      texto: 'Soma dos valores recebidos de clientes (vendas PAGO) pela data de pagamento.',
      tipoDetalhe: 'recebimentos',
      blocoId: 'recebimentos',
    },
    {
      id: 'compras',
      label: 'Compras insumo',
      valorFmt: fmt(d.operacional.saidas),
      classe: 'kpi-card--dfc-saida',
      meta: `${d.qtd_compras || 0} compra(s) paga(s)`,
      hint: 'Ver composição',
      texto: 'Compras de insumo pagas no período (entradas em Compras e Estoques com status PAGO).',
      tipoDetalhe: 'compras_insumos',
      blocoId: 'compras',
    },
    {
      id: 'saida',
      label: 'Saídas CAPEX',
      valorFmt: fmt(d.investimento.saidas),
      classe: 'kpi-card--dfc-saida',
      meta: `${d.saidas?.length || 0} lançamento(s) CAPEX`,
      hint: 'Ver composição',
      texto: 'Investimentos pagos no período (lançamentos manuais tipo CAPEX).',
      tipoDetalhe: 'capex',
      blocoId: 'capex',
    },
    {
      id: 'saldo',
      label: 'Saldo do período',
      valorFmt: fmt(d.variacao_caixa),
      classe: d.variacao_caixa >= 0 ? 'kpi-card--dfc-saldo-pos' : 'kpi-card--dfc-saldo-neg',
      meta: 'Operacional + investimento',
      hint: 'Ver composição',
      texto: 'Variação líquida de caixa no mês (operacional + investimento).',
      tipoDetalhe: 'dfc_variacao',
      blocoId: 'variacao',
    },
    {
      id: 'pendente-periodo',
      label: 'A receber (período)',
      valorFmt: fmt(d.a_receber_periodo),
      classe: 'kpi-card--dfc-pendente',
      meta: `${d.qtd_pendentes_periodo} venda(s) PENDENTE`,
      hint: 'Ver composição',
      texto:
        'Vendas do período ainda não pagas. Reconhecidas na Contabilidade; aqui aguardam aprovação de pagamento.',
      tipoDetalhe: 'a_receber',
      blocoId: 'a_receber_periodo',
    },
    {
      id: 'pendente-aberto',
      label: 'A receber (em aberto)',
      valorFmt: fmt(d.a_receber_aberto),
      classe: 'kpi-card--dfc-aberto',
      meta: `${d.qtd_vendas_pendentes} venda(s) total`,
      hint: 'Ver composição',
      texto: 'Todas as vendas PENDENTE no sistema — ainda não entraram no caixa.',
      tipoDetalhe: 'a_receber',
      blocoId: 'a_receber_aberto',
    },
  ]
})

const maxEvolucao = computed(() => {
  if (!props.painel?.evolucao_caixa?.length) return 1
  return Math.max(
    ...props.painel.evolucao_caixa.flatMap((p) => [p.entradas, p.saidas, Math.abs(p.saldo)]),
    1
  )
})

function toggleDetalhe(id) {
  detalheAberto.value = detalheAberto.value === id ? null : id
}

function fecharKpiModalInterno() {
  kpiModal.value = null
}

const modalCloseKpi = useSimpleModalClose(fecharKpiModalInterno, () => !!kpiModal.value)

function abrirKpiModal(kpi) {
  kpiModal.value = kpi
}

function fecharKpiModal() {
  modalCloseKpi.resetOverlayPress()
  fecharKpiModalInterno()
}

function emitPeriodo() {
  emit('periodo', { mes: mesLocal.value, ano: anoLocal.value })
}

function fmt(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function fmtNeg(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  const n = Number(v)
  if (n === 0) return fmt(0)
  return '− ' + fmt(n)
}

function fmtData(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR')
}

function sinalClass(v) {
  if (v == null) return ''
  return Number(v) >= 0 ? 'positivo' : 'negativo'
}

function barPct(v) {
  return Math.max(4, Math.round((Number(v || 0) / maxEvolucao.value) * 100))
}
</script>

<style scoped>
@import './financeiro-shared.css';
</style>
