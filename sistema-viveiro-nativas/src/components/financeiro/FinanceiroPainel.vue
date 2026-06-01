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

    <p v-if="carregando && !painel" class="alert alert-info">Carregando indicadores…</p>
    <p v-else-if="erro" class="alert alert-error">{{ erro }}</p>

    <template v-else-if="painel">
      <p class="financeiro-lead">
        CMV = custo das mudas vendidas (lote na semeadura + atividades + fitossanidade).
        <strong>Despesas</strong> (faturas, comissão) entram na DRE — não no custo da muda.
        Estoque de insumos e sementes usa <strong>preço médio móvel</strong> (<router-link to="/estoques">Estoques</router-link>).
      </p>

      <!-- Camada 1 — DRE -->
      <section class="fin-sec" aria-label="DRE do período">
        <h2 class="fin-sec__titulo">Resultado do período — {{ painel.periodo.label }}</h2>
        <div class="dre-flow">
          <article class="dre-linha dre-linha--receita">
            <span class="dre-linha__label">Faturamento (vendas pagas)</span>
            <strong class="dre-linha__valor">{{ fmt(painel.dre.faturamento) }}</strong>
            <span class="dre-linha__meta">{{ painel.dre.mudas_vendidas }} muda(s) · ticket {{ fmt(painel.dre.ticket_medio) }}</span>
          </article>
          <article class="dre-linha dre-linha--custo">
            <span class="dre-linha__label">(−) CMV — custo das mudas vendidas</span>
            <strong class="dre-linha__valor">{{ fmt(painel.dre.cmv) }}</strong>
          </article>
          <article class="dre-linha dre-linha--destaque">
            <span class="dre-linha__label">(=) Lucro bruto</span>
            <strong class="dre-linha__valor" :class="sinalClass(painel.dre.lucro_bruto)">{{ fmt(painel.dre.lucro_bruto) }}</strong>
            <span v-if="painel.dre.margem_bruta_pct != null" class="dre-linha__meta">Margem {{ painel.dre.margem_bruta_pct }}%</span>
          </article>
          <article class="dre-linha dre-linha--custo">
            <span class="dre-linha__label">(−) OPEX — despesas operacionais (lançamentos)</span>
            <strong class="dre-linha__valor">{{ fmt(painel.dre.opex) }}</strong>
            <span
              v-if="painel.despesas_estimadas?.total_despesas_estimadas"
              class="dre-linha__meta"
            >
              Referência premissas: {{ fmt(painel.despesas_estimadas.total_despesas_estimadas) }}/mês
              (comissão {{ fmt(painel.despesas_estimadas.comissao_estimada) }})
            </span>
          </article>
          <article class="dre-linha dre-linha--resultado">
            <span class="dre-linha__label">(=) Resultado operacional</span>
            <strong class="dre-linha__valor" :class="sinalClass(painel.dre.resultado_operacional)">{{ fmt(painel.dre.resultado_operacional) }}</strong>
          </article>
        </div>

        <div class="kpi-grid kpi-grid--4">
          <article class="kpi-card">
            <span class="kpi-card__label">Estoque mudas (custo acumulado)</span>
            <strong class="kpi-card__valor">{{ fmt(painel.estoque.valor_mudas_vivas) }}</strong>
            <span class="kpi-card__meta">{{ painel.estoque.mudas_vivas }} vivas · média {{ fmt(painel.estoque.custo_medio_muda_viva) }}/muda</span>
          </article>
          <article class="kpi-card">
            <span class="kpi-card__label">Insumos (média móvel)</span>
            <strong class="kpi-card__valor">{{ fmt(painel.estoque.valor_insumos) }}</strong>
            <span class="kpi-card__meta">{{ painel.estoque.total_insumos }} item(ns)</span>
          </article>
          <article class="kpi-card">
            <span class="kpi-card__label">Sementes em estoque</span>
            <strong class="kpi-card__valor">{{ fmt(painel.estoque.valor_sementes) }}</strong>
            <span class="kpi-card__meta">Valor dos lotes ativos</span>
          </article>
          <article class="kpi-card">
            <span class="kpi-card__label">CAPEX no período</span>
            <strong class="kpi-card__valor">{{ fmt(painel.dre.capex) }}</strong>
            <span class="kpi-card__meta">Investimentos lançados</span>
          </article>
        </div>

        <div v-if="painel.evolucao_mensal?.length" class="evolucao-wrap">
          <h3 class="fin-sub">Evolução — últimos 12 meses</h3>
          <div class="evolucao-chart">
            <div
              v-for="p in painel.evolucao_mensal"
              :key="p.label"
              class="evolucao-col"
              :title="`${p.label}: fat. ${fmt(p.faturamento)}`"
            >
              <div class="evolucao-bar evolucao-bar--fat" :style="{ height: barPct(p.faturamento) + '%' }" />
              <div class="evolucao-bar evolucao-bar--cmv" :style="{ height: barPct(p.cmv) + '%' }" />
              <span class="evolucao-label">{{ p.label.split('/')[0] }}</span>
            </div>
          </div>
          <div class="evolucao-legenda">
            <span><i class="dot dot--fat" /> Faturamento</span>
            <span><i class="dot dot--cmv" /> CMV</span>
          </div>
        </div>
      </section>

      <!-- Camada 2 — Margem -->
      <section class="fin-sec" aria-label="Margem por espécie">
        <h2 class="fin-sec__titulo">Margem por espécie</h2>
        <ul v-if="painel.avisos?.length" class="avisos-list">
          <li v-for="(a, i) in painel.avisos" :key="i" :class="'aviso--' + a.tipo">{{ a.mensagem }}</li>
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
        <p v-else class="fin-empty">Nenhuma venda paga neste período.</p>
      </section>

      <!-- Camada 3 — Gestão -->
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
import FinanceiroGestao from './FinanceiroGestao.vue'

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

watch(() => [props.mes, props.ano], ([m, a]) => {
  mesLocal.value = m
  anoLocal.value = a
})

const anosDisponiveis = computed(() => {
  const y = new Date().getFullYear()
  return [y - 1, y, y + 1]
})

const maxEvolucao = computed(() => {
  if (!props.painel?.evolucao_mensal?.length) return 1
  return Math.max(...props.painel.evolucao_mensal.map((p) => p.faturamento || 0), 1)
})

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
