<template>
  <div class="financeiro-page">
    <header v-if="!ocultarToolbar" class="financeiro-toolbar">
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

    <p v-if="carregando && !painel" class="alert alert-info">Carregando indicadores…</p>
    <p v-else-if="erro" class="alert alert-error">{{ erro }}</p>

    <template v-else-if="painel">
      <p class="financeiro-lead">
        <strong>DRE contábil</strong> — regime de competência (fato gerador na data da venda).
        Vendas <strong>PENDENTE</strong> entram na receita. O caixa efetivo está em
        <router-link to="/financeiro">Financeiro → Fluxo de caixa</router-link>.
      </p>

      <!-- Integridade CMV -->
      <section
        v-if="temIntegridade"
        class="fin-sec fin-sec--integridade"
        aria-label="Integridade de custos"
      >
        <h2 class="fin-sec__titulo">Integridade de custos</h2>
        <ul class="integridade-list">
          <li v-if="!painel.integridade.premissa_coleta_campo_ok" class="integridade-item integridade-item--alerta">
            Premissa <strong>Mão de obra de coleta</strong> zerada ou inativa ({{ fmt(painel.integridade.valor_hora_coleta_campo) }}/h) —
            <router-link to="/financeiro">Premissas</router-link>
          </li>
          <li v-if="painel.integridade.lotes_sementes_sem_custo" class="integridade-item integridade-item--alerta">
            <strong>{{ painel.integridade.lotes_sementes_sem_custo }}</strong>
            lote(s) ativo(s) com custo zero no estoque —
            <router-link to="/coleta">Coleta Sementes</router-link>
          </li>
          <li v-if="painel.integridade.coletas_sem_horas_campo" class="integridade-item integridade-item--alerta">
            <strong>{{ painel.integridade.coletas_sem_horas_campo }}</strong>
            coleta(s) com lote ativo ainda sem horas —
            <router-link to="/coleta">Coleta Sementes</router-link>
          </li>
          <li v-if="painel.integridade.lotes_armazem_sem_coleta" class="integridade-item integridade-item--alerta">
            <strong>{{ painel.integridade.lotes_armazem_sem_coleta }}</strong>
            lote(s) do armazém sem coleta (custo não vem de horas de campo)
          </li>
          <li v-if="painel.integridade.mudas_vivas_sem_custo" class="integridade-item integridade-item--alerta">
            <strong>{{ painel.integridade.mudas_vivas_sem_custo }}</strong>
            muda(s) vivas sem custo —
            <router-link to="/estoques">Estoques</router-link>
          </li>
          <li v-if="!temIntegridadeAlerta" class="integridade-item integridade-item--ok">
            Premissas CMV e registros operacionais consistentes.
          </li>
        </ul>
      </section>

      <!-- Camada 1 — DRE / Caixa -->
      <section class="fin-sec" :aria-label="tituloSecao">
        <h2 class="fin-sec__titulo">{{ tituloSecao }} — {{ painel.periodo.label }}</h2>
        <div class="dre-flow">
          <article
            v-for="linha in linhasDre"
            :key="linha.id"
            class="dre-linha"
            :class="[linha.classe, { 'dre-linha--aberta': detalheAberto === linha.id, 'dre-linha--clicavel': linha.clicavel }]"
          >
            <button
              v-if="linha.clicavel"
              type="button"
              class="dre-linha__btn"
              :aria-expanded="detalheAberto === linha.id"
              @click="toggleDetalhe(linha.id)"
            >
              <span class="dre-linha__chev">{{ detalheAberto === linha.id ? '▾' : '▸' }}</span>
              <span class="dre-linha__label">{{ linha.label }}</span>
              <strong class="dre-linha__valor" :class="linha.sinal ? sinalClass(linha.valor) : ''">{{ fmt(linha.valor) }}</strong>
              <span v-if="linha.meta" class="dre-linha__meta">{{ linha.meta }}</span>
            </button>
            <template v-else>
              <span class="dre-linha__label">{{ linha.label }}</span>
              <strong class="dre-linha__valor" :class="linha.sinal ? sinalClass(linha.valor) : ''">{{ fmt(linha.valor) }}</strong>
              <span v-if="linha.meta" class="dre-linha__meta">{{ linha.meta }}</span>
            </template>
            <FinanceiroDetalheBloco
              v-if="linha.clicavel && detalheAberto === linha.id && painel.detalhes"
              :tipo="linha.id"
              :bloco="blocoDetalhe(linha.id)"
              :receitas="painel.receitas"
              :estoque="linha.id === 'estoque' ? painel.detalhes.estoque : null"
            />
          </article>
        </div>

        <div class="kpi-grid kpi-grid--5">
          <article
            v-for="kpi in kpisEstoque"
            :key="kpi.id"
            class="kpi-card"
            :class="kpi.classe"
          >
            <button type="button" class="kpi-card__btn" @click="abrirKpiModal(kpi)">
              <span class="kpi-card__label">{{ kpi.label }}</span>
              <strong class="kpi-card__valor">{{ fmt(kpi.valor) }}</strong>
              <span class="kpi-card__meta" v-html="kpi.meta" />
              <span class="kpi-card__hint">Ver composição</span>
            </button>
          </article>
        </div>

        <!-- Modal detalhe KPI -->
        <AppModalOverlay
          :aberto="!!kpiModal"
          :handlers="modalCloseKpi"
          panel-class="app-modal-panel--xl"
          aria-labelledby="fin-kpi-modal-title"
        >
          <header class="fin-modal-header">
              <div>
                <p class="fin-modal-eyebrow">Composição do indicador</p>
                <h2 id="fin-kpi-modal-title">{{ kpiModal.label }}</h2>
                <p class="fin-modal-valor">{{ fmt(kpiModal.valor) }}</p>
              </div>
              <button type="button" class="fin-modal-fechar" aria-label="Fechar" @click="fecharKpiModal">×</button>
            </header>
            <div class="fin-modal-body">
              <FinanceiroDetalheBloco
                v-if="painel.detalhes"
                :tipo="kpiModal.tipoDetalhe"
                :bloco="kpiModal.tipoDetalhe === 'capex' ? painel.detalhes.capex : null"
                :estoque="kpiModal.tipoDetalhe === 'estoque' ? painel.detalhes.estoque : null"
                :estoque-foco="kpiModal.estoqueFoco"
                :embedded="false"
              />
            </div>
            <footer class="fin-modal-footer">
              <button type="button" class="btn btn-secondary btn-sm" @click="fecharKpiModal">Fechar</button>
            </footer>
        </AppModalOverlay>

        <div v-if="painel.evolucao_mensal?.length" class="evolucao-wrap">
          <h3 class="fin-sub">{{ tituloEvolucao }}</h3>
          <div class="evolucao-chart">
            <div
              v-for="p in painel.evolucao_mensal"
              :key="p.label"
              class="evolucao-col"
              :title="`${p.label}: fat. ${fmt(p.faturamento)}`"
            >
              <div
                class="evolucao-bar evolucao-bar--fat"
                :style="{ height: barPct(p.faturamento) + '%', backgroundColor: coresDre.faturamento }"
              />
              <div
                class="evolucao-bar evolucao-bar--cmv"
                :style="{
                  height: barPct(p.cmv) + '%',
                  backgroundColor: coresDre.cmv,
                  opacity: coresDre.cmvOpacity,
                }"
              />
              <span class="evolucao-label">{{ p.label.split('/')[0] }}</span>
            </div>
          </div>
          <div class="evolucao-legenda">
            <span><i class="dot" :style="{ backgroundColor: coresDre.faturamento }" /> Faturamento</span>
            <span><i class="dot" :style="{ backgroundColor: coresDre.cmv }" /> CMV</span>
          </div>
        </div>
      </section>

      <!-- Camada 2 — Margem -->
      <section class="fin-sec" aria-label="Margem por espécie">
        <h2 class="fin-sec__titulo">Margem por espécie</h2>
        <ul v-if="avisosMargem.length" class="avisos-list">
          <li v-for="(a, i) in avisosMargem" :key="i" :class="'aviso--' + a.tipo">{{ a.mensagem }}</li>
        </ul>
        <div v-if="painel.margem_especies?.length" class="tabela-wrap">
          <table class="tabela-fin">
            <thead>
              <tr>
                <th>Espécie</th>
                <th class="num">Qtd</th>
                <th class="num">Receita</th>
                <th class="num">CMV</th>
                <th class="num">Lucro</th>
                <th class="num">Margem</th>
                <th class="num">Preço méd.</th>
                <th class="num">Custo méd.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in painel.margem_especies" :key="e.id_especie" :class="{ 'linha-alerta': e.margem_pct != null && e.margem_pct < 0 }">
                <td>{{ e.nome }}</td>
                <td class="num">{{ e.quantidade_vendida }}</td>
                <td class="num">{{ fmt(e.receita) }}</td>
                <td class="num">{{ fmt(e.cmv) }}</td>
                <td class="num" :class="sinalClass(e.lucro_bruto)">{{ fmt(e.lucro_bruto) }}</td>
                <td class="num">{{ e.margem_pct != null ? e.margem_pct + '%' : '—' }}</td>
                <td class="num">{{ fmt(e.preco_medio) }}</td>
                <td class="num">{{ fmt(e.custo_medio) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="fin-empty">{{ msgSemVendas }}</p>
      </section>

      <!-- Camada 3 — Gestão (só Financeiro caixa) -->
      <FinanceiroGestao
        v-if="mostrarGestao"
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
import { CHART_DRE } from '@/constants/chartColors'

const coresDre = CHART_DRE

const props = defineProps({
  painel: { type: Object, default: null },
  lancamentos: { type: Array, default: () => [] },
  carregando: { type: Boolean, default: false },
  erro: { type: String, default: null },
  mes: { type: Number, required: true },
  ano: { type: Number, required: true },
  podeEditar: { type: Boolean, default: false },
  /** caixa = Financeiro gerencial; competencia = Contabilidade DRE */
  modo: { type: String, default: 'caixa' },
  mostrarGestao: { type: Boolean, default: true },
  ocultarToolbar: { type: Boolean, default: false },
})

const emit = defineEmits(['atualizar', 'periodo'])

const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
const mesLocal = ref(props.mes)
const anoLocal = ref(props.ano)

watch(() => [props.mes, props.ano], ([m, a]) => {
  mesLocal.value = m
  anoLocal.value = a
})

const anosDisponiveis = computed(() => {
  const y = new Date().getFullYear()
  return [y - 1, y, y + 1]
})

const detalheAberto = ref(null)
const kpiModal = ref(null)

const tituloSecao = computed(() =>
  props.modo === 'competencia' ? 'DRE do período' : 'Resultado em caixa'
)

const tituloEvolucao = computed(() => {
  if (props.painel?.periodo?.mes === 0) {
    return `Evolução mensal — ${props.painel.periodo.label}`
  }
  return 'Evolução — últimos 12 meses'
})

const msgSemVendas = computed(() =>
  props.modo === 'competencia'
    ? 'Nenhuma venda efetivada neste período.'
    : 'Nenhum recebimento neste período.'
)

watch(() => [props.mes, props.ano], () => {
  detalheAberto.value = null
  kpiModal.value = null
})

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

const linhasDre = computed(() => {
  const d = props.painel?.dre
  if (!d) return []
  const fatLabel =
    props.modo === 'competencia'
      ? 'Receita (vendas efetivadas)'
      : 'Entradas (vendas pagas)'
  return [
    {
      id: 'faturamento',
      label: fatLabel,
      valor: d.faturamento,
      classe: 'dre-linha--receita',
      clicavel: true,
      sinal: false,
      meta: `${d.mudas_vendidas} muda(s) · ticket ${fmt(d.ticket_medio)}`,
    },
    {
      id: 'cmv',
      label: '(−) CMV — custo das mudas vendidas',
      valor: d.cmv,
      classe: 'dre-linha--custo',
      clicavel: true,
      sinal: false,
      meta: 'Clique para ver item a item',
    },
    {
      id: 'lucro_bruto',
      label: '(=) Lucro bruto',
      valor: d.lucro_bruto,
      classe: 'dre-linha--destaque',
      clicavel: true,
      sinal: true,
      meta: d.margem_bruta_pct != null ? `Margem ${d.margem_bruta_pct}%` : null,
    },
    {
      id: 'compras_insumos',
      label: '(−) Compras de insumos',
      valor: d.compras_insumos,
      classe: 'dre-linha--custo',
      clicavel: true,
      sinal: false,
      meta: 'Entradas em Estoques → Insumos',
    },
    {
      id: 'opex',
      label: '(−) OPEX — premissas DRE (automático)',
      valor: d.opex,
      classe: 'dre-linha--custo',
      clicavel: true,
      sinal: false,
      meta: `Comissão ${fmt(d.opex_comissao)} · Fixas ${fmt(d.opex_fixo)}`,
    },
    {
      id: 'resultado',
      label: '(=) Resultado operacional',
      valor: d.resultado_operacional,
      classe: 'dre-linha--resultado',
      clicavel: true,
      sinal: true,
      meta: 'Lucro bruto − compras − OPEX',
    },
  ]
})

const kpisEstoque = computed(() => {
  const e = props.painel?.estoque
  const d = props.painel?.dre
  const i = props.painel?.integridade
  if (!e || !d) return []
  const alertaSementes = i?.lotes_sementes_sem_custo
    ? ` · <strong class="fin-kpi-alerta">${i.lotes_sementes_sem_custo} lote(s) zerado(s)</strong>`
    : ''
  return [
    {
      id: 'kpi-parque',
      tipoDetalhe: 'estoque',
      estoqueFoco: 'parque',
      label: 'Parque (todas vivas)',
      valor: e.valor_mudas_vivas,
      classe: '',
      meta: `${e.mudas_vivas} mudas · média ${fmt(e.custo_medio_muda_viva)}/muda`,
    },
    {
      id: 'kpi-comercial',
      tipoDetalhe: 'estoque',
      estoqueFoco: 'comercial',
      label: 'Estoque comercial (aptas venda)',
      valor: e.valor_mudas_comercial,
      classe: 'kpi-card--comercial',
      meta: `${e.mudas_comercial} em rustificação · média ${fmt(e.custo_medio_muda_comercial)}/muda`,
    },
    {
      id: 'kpi-insumos',
      tipoDetalhe: 'estoque',
      estoqueFoco: 'insumos',
      label: 'Insumos (média móvel)',
      valor: e.valor_insumos,
      classe: '',
      meta: `${e.total_insumos} item(ns)`,
    },
    {
      id: 'kpi-sementes',
      tipoDetalhe: 'estoque',
      estoqueFoco: 'sementes',
      label: 'Sementes em estoque',
      valor: e.valor_sementes,
      classe: alertaSementes ? 'kpi-card--alerta' : '',
      meta: `Horas de coleta × homem-hora${alertaSementes}`,
    },
    {
      id: 'capex',
      tipoDetalhe: 'capex',
      estoqueFoco: null,
      label: 'CAPEX no período',
      valor: d.capex,
      classe: '',
      meta: 'Investimentos lançados',
    },
  ]
})

function toggleDetalhe(id) {
  detalheAberto.value = detalheAberto.value === id ? null : id
}

function blocoDetalhe(id) {
  const det = props.painel?.detalhes
  if (!det) return null
  if (id === 'estoque') return det.estoque
  return det[id] || null
}

const maxEvolucao = computed(() => {
  if (!props.painel?.evolucao_mensal?.length) return 1
  return Math.max(...props.painel.evolucao_mensal.map((p) => p.faturamento || 0), 1)
})

const temIntegridadeAlerta = computed(() => {
  const i = props.painel?.integridade
  if (!i) return false
  return (
    !i.premissa_coleta_campo_ok ||
    (i.lotes_sementes_sem_custo || 0) > 0 ||
    (i.coletas_sem_horas_campo || 0) > 0 ||
    (i.lotes_armazem_sem_coleta || 0) > 0 ||
    (i.mudas_vivas_sem_custo || 0) > 0
  )
})

const temIntegridade = computed(() => Boolean(props.painel?.integridade))

const avisosMargem = computed(() =>
  (props.painel?.avisos || []).filter((a) =>
    ['venda_abaixo_custo', 'especie_prejuizo', 'resultado_negativo'].includes(a.tipo)
  )
)

function emitPeriodo() {
  emit('periodo', { mes: mesLocal.value, ano: anoLocal.value })
}

function fmt(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
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
