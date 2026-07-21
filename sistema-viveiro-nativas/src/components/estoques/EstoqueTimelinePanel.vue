<template>
  <section class="timeline-panel">
    <header class="timeline-panel__header">
      <div>
        <h3 class="timeline-panel__titulo">Visão por espécie</h3>
        <p class="timeline-panel__sub">
          Tempo médio em cada etapa · armazém → sementeira → canteiro → rustificação
          <span v-if="isVisaoTodas" class="timeline-panel__hint">
            · barras com mesma largura; o verde mais escuro indica onde o tempo se concentra
          </span>
        </p>
      </div>
      <div v-if="cicloGlobal" class="timeline-panel__ciclo">
        <span class="timeline-panel__ciclo-label">Ciclo médio (visão atual)</span>
        <strong>{{ cicloGlobal }} dias</strong>
      </div>
    </header>

    <!-- Filtro espécies -->
    <div class="timeline-filtros" role="group" aria-label="Filtrar espécie">
      <button
        type="button"
        class="filtro-chip"
        :class="{ 'filtro-chip--ativa': !filtroEspecie }"
        @click="selecionarEspecie(null)"
      >
        Todas
        <span class="filtro-chip__badge">{{ timeline?.especies?.length || 0 }}</span>
      </button>
      <button
        v-for="e in timeline?.especies || []"
        :key="e.id_especie"
        type="button"
        class="filtro-chip"
        :class="{ 'filtro-chip--ativa': filtroEspecie === e.id_especie }"
        @click="selecionarEspecie(e.id_especie)"
      >
        {{ e.nome_popular || e.nome_cientifico }}
        <span class="filtro-chip__badge">{{ e.quantidade_plantas }}</span>
      </button>
    </div>

    <!-- Timeline global (todas ou filtrada única) -->
    <article v-if="visaoPrincipal" class="timeline-hero">
      <div class="timeline-hero__head">
        <h4>{{ tituloVisao }}</h4>
        <p v-if="visaoPrincipal.quantidade_plantas">
          {{ visaoPrincipal.quantidade_plantas }} mudas vivas
          <span v-if="visaoPrincipal.onde_agora?.armazem">
            · {{ visaoPrincipal.onde_agora.armazem }} sementes no armazém
          </span>
        </p>
      </div>

      <div
        class="pipeline-track"
        :class="{ 'pipeline-track--equal': isVisaoTodas }"
        aria-label="Timeline do pipeline"
      >
        <template v-for="(etapaKey, idx) in ordemEtapas" :key="etapaKey">
          <div
            v-if="idx > 0"
            class="pipeline-arrow"
            aria-hidden="true"
          >
            →
          </div>
          <div
            class="pipeline-stage"
            :class="{ 'pipeline-stage--equal': isVisaoTodas }"
            :style="isVisaoTodas ? undefined : { flex: flexEtapa(etapaData(visaoPrincipal, etapaKey)) }"
          >
            <div
              class="pipeline-stage__bar"
              :class="{ 'pipeline-stage__bar--equal': isVisaoTodas }"
              :style="barStyle(etapaData(visaoPrincipal, etapaKey), !isVisaoTodas, maxDiasVisao, etapaKey)"
            >
              <span class="pipeline-stage__dias">
                {{ fmtDias(etapaData(visaoPrincipal, etapaKey)?.dias_medio) }}
              </span>
            </div>
            <span class="pipeline-stage__nome">{{ labelEtapa(etapaKey) }}</span>
            <span class="pipeline-stage__meta">
              {{ metaEtapa(visaoPrincipal, etapaKey) }}
            </span>
          </div>
        </template>
      </div>

      <!-- Onde está agora -->
      <div class="onde-agora">
        <span class="onde-agora__label">Estoque agora nesta visão:</span>
        <span
          v-for="key in ordemEtapas"
          :key="'oa-' + key"
          class="onde-badge"
          :style="{ borderColor: corEtapa(key), background: corEtapa(key) + '18' }"
        >
          {{ labelEtapa(key) }}: <strong>{{ visaoPrincipal.onde_agora?.[key] ?? 0 }}</strong>
        </span>
      </div>
    </article>

    <!-- Lista por espécie (quando "Todas") -->
    <div v-if="!filtroEspecie && (timeline?.especies?.length || 0) > 1" class="timeline-lista">
      <h4 class="timeline-lista__titulo">Detalhe por espécie</h4>
      <article
        v-for="e in timeline.especies"
        :key="e.id_especie"
        class="timeline-card"
        @click="selecionarEspecie(e.id_especie)"
      >
        <div class="timeline-card__head">
          <strong>{{ e.nome_popular || e.nome_cientifico }}</strong>
          <span class="timeline-card__qtd">{{ e.quantidade_plantas }} mudas</span>
          <span v-if="e.ciclo_total_medio" class="timeline-card__ciclo">{{ e.ciclo_total_medio }} d ciclo</span>
        </div>
        <div class="pipeline-track pipeline-track--compact">
          <template v-for="(etapaKey, idx) in ordemEtapas" :key="etapaKey">
            <div v-if="idx > 0" class="pipeline-arrow pipeline-arrow--sm">→</div>
            <div class="pipeline-stage pipeline-stage--compact">
              <div
                class="pipeline-stage__bar pipeline-stage__bar--sm"
                :style="barStyle(etapaData(e, etapaKey), true, maxDiasEntidade(e), etapaKey)"
              />
              <span class="pipeline-stage__mini">{{ fmtDias(etapaData(e, etapaKey)?.dias_medio) }}</span>
            </div>
          </template>
        </div>
        <span class="timeline-card__cta">Clique para filtrar →</span>
      </article>
    </div>

    <p v-if="carregando" class="alert alert-info">Atualizando timeline…</p>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getTimelineEstoques } from '@/services/estoques'
import { CHART_ESTOQUE_ETAPA, CHART_NEUTRAL, estoqueTimelineBarStyle } from '@/constants/chartColors'

const props = defineProps({
  timelineInicial: { type: Object, default: null },
})

const timeline = ref(props.timelineInicial)
const filtroEspecie = ref(null)
const carregando = ref(false)

const ordemEtapas = computed(() => timeline.value?.etapas_ordem || [
  'armazem', 'sementeira', 'canteiro', 'rustificacao',
])

const cicloGlobal = computed(() => {
  if (filtroEspecie.value && especieFiltrada.value) {
    return especieFiltrada.value.ciclo_total_medio
  }
  return timeline.value?.resumo_global?.ciclo_total_medio
})

const especieFiltrada = computed(() =>
  (timeline.value?.especies || []).find((e) => e.id_especie === filtroEspecie.value)
)

const visaoPrincipal = computed(() => {
  if (filtroEspecie.value && especieFiltrada.value) {
    return {
      ...especieFiltrada.value,
      etapas: especieFiltrada.value.etapas,
    }
  }
  const g = timeline.value?.resumo_global
  if (!g) return null
  return {
    nome_popular: 'Todas as espécies',
    quantidade_plantas: (timeline.value?.especies || []).reduce(
      (s, e) => s + (e.quantidade_plantas || 0), 0
    ),
    onde_agora: (timeline.value?.especies || []).reduce((acc, e) => {
      const o = e.onde_agora || {}
      for (const k of ordemEtapas.value) {
        acc[k] = (acc[k] || 0) + (o[k] || 0)
      }
      return acc
    }, {}),
    etapas: g.etapas,
    ciclo_total_medio: g.ciclo_total_medio,
  }
})

const tituloVisao = computed(() => {
  if (filtroEspecie.value && especieFiltrada.value) {
    return especieFiltrada.value.nome_popular || especieFiltrada.value.nome_cientifico
  }
  return 'Todas as espécies'
})

const isVisaoTodas = computed(() => !filtroEspecie.value)

const maxDiasVisao = computed(() =>
  visaoPrincipal.value ? maxDiasEntidade(visaoPrincipal.value) : 0,
)

watch(
  () => props.timelineInicial,
  (v) => {
    timeline.value = v
  }
)

async function selecionarEspecie(id) {
  filtroEspecie.value = id
  carregando.value = true
  try {
    timeline.value = await getTimelineEstoques(id || undefined)
  } catch {
    /* mantém anterior */
  } finally {
    carregando.value = false
  }
}

function etapaData(entidade, key) {
  return entidade?.etapas?.[key]
}

function labelEtapa(key) {
  return etapaData({ etapas: timeline.value?.resumo_global?.etapas }, key)?.label
    || { armazem: 'Armazém', sementeira: 'Sementeira', canteiro: 'Canteiro', rustificacao: 'Rustificação' }[key]
    || key
}

function maxDiasEntidade(entidade) {
  return Math.max(
    0,
    ...ordemEtapas.value.map((k) => etapaData(entidade, k)?.dias_medio || 0),
  )
}

function corEtapa(key) {
  const fromGlobal = timeline.value?.resumo_global?.etapas?.[key]?.cor
  return fromGlobal || CHART_ESTOQUE_ETAPA[key] || CHART_NEUTRAL
}

function barStyle(etapa, proporcional = true, maxDias = 0, etapaKey = null) {
  const dias = etapa?.dias_medio || 0
  const intensidade = estoqueTimelineBarStyle(dias, maxDias)
  const style = {
    width: '100%',
    ...intensidade,
    textShadow: intensidade.color === '#fff' ? '0 1px 2px rgba(0, 0, 0, 0.25)' : 'none',
  }
  if (etapaKey) {
    style.borderLeft = `4px solid ${corEtapa(etapaKey)}`
  }
  if (!proporcional) {
    style.height = '3rem'
  } else {
    const altura = Math.min(100, Math.max(35, 35 + dias * 1.2))
    style.height = `${altura}px`
  }
  return style
}

function flexEtapa(etapa) {
  const pct = etapa?.percentual_timeline || 1
  return `${Math.max(pct, 5)} 1 0`
}

function fmtDias(v) {
  if (v == null) return '—'
  return `${v}d`
}

function metaEtapa(entidade, key) {
  const et = etapaData(entidade, key)
  const onde = entidade?.onde_agora?.[key] ?? 0
  const n = et?.amostras ?? 0
  if (key === 'armazem') {
    return onde ? `${onde} sementes · média ${fmtDias(et?.dias_medio)}` : (n ? `${n} amostras` : 'sem dados')
  }
  return `${onde} aqui agora · ${n} amostra(s)`
}
</script>

<style scoped>
.timeline-panel {
  margin-top: var(--spacing-xl);
  padding: var(--spacing-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.timeline-panel__header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.timeline-panel__titulo {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
}

.timeline-panel__sub {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.timeline-panel__ciclo {
  text-align: right;
}

.timeline-panel__ciclo-label {
  display: block;
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.timeline-panel__ciclo strong {
  font-size: 1.5rem;
  color: var(--color-primary-700);
}

.timeline-filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: var(--spacing-lg);
}

.filtro-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.85rem;
  border: 2px solid var(--color-border-subtle);
  border-radius: var(--radius-full);
  background: var(--color-surface-muted);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}

.filtro-chip:hover {
  border-color: var(--color-primary);
}

.filtro-chip--ativa {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary);
  color: var(--color-primary-800, var(--color-primary-700));
}

.filtro-chip__badge {
  font-size: 0.6875rem;
  padding: 0.1rem 0.4rem;
  border-radius: var(--radius-full);
  background: rgba(0, 0, 0, 0.06);
}

.timeline-hero {
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, var(--color-surface) 60%);
  border: 2px solid var(--color-primary-100);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
}

.timeline-hero__head h4 {
  margin: 0;
  font-size: 1.25rem;
}

.timeline-hero__head p {
  margin: 0.35rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.pipeline-track {
  display: flex;
  align-items: flex-end;
  gap: 0.35rem;
  margin: var(--spacing-lg) 0 var(--spacing-md);
  min-height: 7rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.pipeline-track--compact {
  min-height: 3.5rem;
  margin: var(--spacing-sm) 0;
}

.pipeline-arrow {
  flex-shrink: 0;
  align-self: center;
  font-size: 1.5rem;
  color: var(--color-text-muted);
  padding: 0 0.25rem;
}

.pipeline-arrow--sm {
  font-size: 1rem;
}

.pipeline-stage {
  flex: 1 1 0;
  min-width: 5.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
}

.pipeline-stage--compact {
  min-width: 3rem;
}

.pipeline-track--equal {
  min-height: auto;
  align-items: stretch;
}

.pipeline-stage--equal {
  flex: 1 1 0;
  min-width: 4.5rem;
}

.pipeline-stage__bar--equal {
  height: 3rem !important;
  min-height: 3rem;
}

.timeline-panel__hint {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 400;
}

.pipeline-stage__bar {
  width: 100%;
  min-height: 2.5rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.25rem;
  transition: height 0.4s ease, opacity 0.3s, background 0.35s ease, color 0.35s ease;
  box-shadow: inset 0 -3px 0 rgba(0, 0, 0, 0.12);
}

.pipeline-stage__bar--sm {
  min-height: 2.25rem;
  font-size: 0;
}

.pipeline-stage__dias {
  padding: 0.25rem;
  font-size: 1.25rem;
  line-height: 1.1;
}

.pipeline-stage__nome {
  font-size: 0.8125rem;
  font-weight: 700;
  text-align: center;
  color: var(--color-text-primary);
}

.pipeline-stage__meta {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  text-align: center;
  line-height: 1.3;
  max-width: 9rem;
}

.pipeline-stage__mini {
  font-size: 0.875rem;
  font-weight: 800;
  line-height: 1.2;
  margin-top: 0.1rem;
}

.onde-agora {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  padding-top: var(--spacing-md);
  border-top: 1px dashed var(--color-border-subtle);
}

.onde-agora__label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.onde-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  border: 1px solid;
}

.timeline-lista__titulo {
  margin: 0 0 var(--spacing-md);
  font-size: 0.9375rem;
  font-weight: 600;
}

.timeline-card {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-sm);
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.timeline-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.timeline-card__head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.5rem 1rem;
  margin-bottom: 0.35rem;
}

.timeline-card__qtd {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.timeline-card__ciclo {
  margin-left: auto;
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-primary-700);
}

.timeline-card__cta {
  font-size: 0.6875rem;
  color: var(--color-primary);
  font-weight: 600;
}
</style>
