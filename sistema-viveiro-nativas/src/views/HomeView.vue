<template>
  <div class="home">
    <section class="home-hero">
      <div class="home-hero__pattern" aria-hidden="true" />
      <div class="home-hero__content">
        <p class="home-hero__greeting">{{ saudacao }}, {{ primeiroNome }}</p>
        <h1 class="home-hero__title">{{ nomeViveiro }}</h1>
        <p class="home-hero__summary">
          <template v-if="carregando">Carregando panorama do viveiro…</template>
          <template v-else-if="pendenciasVisiveis.length">
            Hoje: <strong>{{ pendenciasVisiveis.length }}</strong>
            {{ pendenciasVisiveis.length === 1 ? 'pendência' : 'pendências' }}
            <span v-if="alertasAlto"> · <span class="home-hero__alert">{{ alertasAlto }} alerta(s) prioritário(s)</span></span>
          </template>
          <template v-else>Tudo em dia no viveiro. Bom trabalho!</template>
        </p>
      </div>
    </section>

    <p v-if="acessoNegado" class="alert alert-error home-erro" role="alert">
      Você não tem permissão para acessar
      <strong>{{ rotaNegadaLabel }}</strong>.
      <span v-if="rotaNegada"> O painel inicial continua disponível.</span>
    </p>

    <p v-if="erroApi" class="alert alert-error home-erro" role="alert">
      Não foi possível carregar todos os dados. Verifique se a API está no ar.
    </p>

    <section v-if="acoesRapidas.length" class="home-block" aria-label="Ações rápidas">
      <h2 class="home-block__title">Ações rápidas</h2>
      <div class="quick-actions">
        <button
          v-for="acao in acoesRapidas"
          :key="acao.id"
          type="button"
          class="quick-action"
          :class="`quick-action--${acao.variant}`"
          @click="ir(acao.rota)"
        >
          <span class="quick-action__label">{{ acao.label }}</span>
          <span class="quick-action__hint">{{ acao.hint }}</span>
        </button>
      </div>
    </section>

    <div class="home-grid">
      <section class="home-block home-block--pendencias" aria-label="Pendências">
        <h2 class="home-block__title">Pendências</h2>
        <ul v-if="pendenciasVisiveis.length" class="pendencias-list">
          <li
            v-for="p in pendenciasVisiveis"
            :key="p.id"
            class="pendencia-item"
            :class="`pendencia-item--${p.nivel}`"
          >
            <div class="pendencia-item__body">
              <strong>{{ p.titulo }}</strong>
              <p>{{ p.descricao }}</p>
            </div>
            <button type="button" class="btn btn-primary btn-sm" @click="ir(p.rota)">Resolver</button>
          </li>
        </ul>
        <p v-else class="home-empty-inline">Nenhuma pendência urgente no momento.</p>
      </section>

      <section class="home-block home-block--card" aria-label="Resumo do viveiro">
        <h2 class="home-block__title">Resumo do viveiro</h2>
        <div class="stats-grid">
          <button
            v-for="stat in statsVisiveis"
            :key="stat.id"
            type="button"
            class="stat-card"
            @click="ir(stat.rota)"
          >
            <span class="stat-card__value">{{ stat.value }}</span>
            <span class="stat-card__label">{{ stat.label }}</span>
            <span class="stat-card__hint">{{ stat.hint }}</span>
          </button>
        </div>
      </section>
    </div>

    <section v-if="fluxoVisivel.length" class="home-block" aria-label="Fluxo do viveiro">
      <h2 class="home-block__title">Fluxo da produção</h2>
      <p class="home-block__lead">Da matriz à venda — clique em cada etapa para ir ao módulo.</p>
      <div class="fluxo-track">
        <template v-for="(etapa, index) in fluxoVisivel" :key="etapa.id">
          <button type="button" class="fluxo-step" @click="ir(etapa.rota)">
            <span class="fluxo-step__count">{{ etapa.count }}</span>
            <span class="fluxo-step__label">{{ etapa.label }}</span>
          </button>
          <span v-if="index < fluxoVisivel.length - 1" class="fluxo-arrow" aria-hidden="true">→</span>
        </template>
      </div>
    </section>

    <section v-if="mostrarOnboarding" class="home-onboarding">
      <div class="home-onboarding__icon" aria-hidden="true">🌱</div>
      <h2>Vamos começar?</h2>
      <p>Cadastre sua primeira árvore matriz e registre uma coleta para ativar o rastreio completo.</p>
      <div class="home-onboarding__actions">
        <button v-if="can('coleta.create')" type="button" class="btn btn-primary" @click="ir('/coleta')">Cadastrar matriz</button>
        <button v-if="can('biblioteca.view')" type="button" class="btn btn-outline" @click="ir('/biblioteca')">Ver biblioteca de espécies</button>
      </div>
    </section>

    <section v-if="atividade.length" class="home-block" aria-label="Atividade recente">
      <h2 class="home-block__title">Atividade recente</h2>
      <ul class="atividade-list">
        <li v-for="(ev, i) in atividade" :key="i" class="atividade-item">
          <span class="atividade-item__badge" :class="`atividade-item__badge--${ev.tipo}`" />
          <div class="atividade-item__text">
            <p>{{ ev.texto }}</p>
            <time>{{ ev.quando }}</time>
          </div>
          <button type="button" class="atividade-item__link" @click="ir(ev.rota)">Ver</button>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { usePermissions } from '@/composables/usePermissions'
import { QUICK_ACTIONS } from '@/constants/homeActions'
import { loadHomeData, fmtMoeda } from '@/services/home'

const router = useRouter()
const route = useRoute()
const acessoNegado = ref(false)
const rotaNegada = ref('')
const auth = useAuthStore()
const { can } = usePermissions()

const nomeViveiro = import.meta.env.VITE_VIVEIRO_NOME || 'Viveiro Nativas'

const carregando = ref(true)
const erroApi = ref(false)
const pendencias = ref([])
const atividade = ref([])
const fluxo = ref([])
const resumo = ref(null)

const primeiroNome = computed(() => {
  const n = auth.user?.nome || 'colega'
  return n.split(' ')[0]
})

const saudacao = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Bom dia'
  if (h < 18) return 'Boa tarde'
  return 'Boa noite'
})

const acoesRapidas = computed(() =>
  QUICK_ACTIONS.filter((a) => can(a.permission))
)

const pendenciasVisiveis = computed(() =>
  pendencias.value.filter((p) => can(p.permissao))
)

const alertasAlto = computed(() =>
  pendenciasVisiveis.value.filter((p) => p.nivel === 'alto').length
)

const fluxoVisivel = computed(() =>
  fluxo.value.filter((e) => can(e.permissao))
)

const mostrarOnboarding = computed(
  () => !carregando.value && resumo.value && resumo.value.matrizes === 0
    && (can('coleta.create') || can('biblioteca.view'))
)

const rotaNegadaLabel = computed(() => {
  const map = {
    '/financeiro': 'Financeiro',
    '/coleta': 'Coleta de Sementes',
    '/producao': 'Produção',
    '/viveiro': 'Viveiro',
    '/estoques': 'Compras e Estoques',
    '/vendas': 'Vendas',
    '/biblioteca': 'Biblioteca',
    '/fitossanidade': 'Fitossanidade',
    '/fertilizacao': 'Fertilização',
    '/contabilidade': 'Contabilidade',
    '/configuracoes': 'Configurações',
    '/admin/god-mode': 'God Mode (admin)',
  }
  const path = String(rotaNegada.value || '').split('?')[0]
  return map[path] || (path ? path : 'essa área')
})

function capturarAcessoNegado() {
  if (route.query.acesso !== 'negado') return
  acessoNegado.value = true
  rotaNegada.value = typeof route.query.de === 'string' ? route.query.de : ''
  router.replace({ path: '/', query: {} })
}

const statsVisiveis = computed(() => {
  if (!resumo.value) return []
  const r = resumo.value
  const items = [
    {
      id: 'especies',
      label: 'Espécies',
      value: r.especies,
      hint: 'Biblioteca',
      rota: '/biblioteca',
      permission: 'biblioteca.view',
    },
    {
      id: 'matrizes',
      label: 'Matrizes',
      value: r.matrizes,
      hint: 'Coleta',
      rota: '/coleta',
      permission: 'coleta.view',
    },
    {
      id: 'mudas',
      label: 'Mudas ativas',
      value: r.mudas_ativas,
      hint: 'Planta baixa',
      rota: '/viveiro',
      permission: 'viveiro.view',
    },
    {
      id: 'lotes',
      label: 'Lotes ativos',
      value: r.lotes_ativos,
      hint: 'Compras e Estoques',
      rota: '/estoques',
      permission: 'estoques.view',
    },
    {
      id: 'coletas',
      label: 'Coletas',
      value: r.coletas,
      hint: 'Histórico',
      rota: '/coleta',
      permission: 'coleta.view',
    },
  ]
  if (can('financeiro.view')) {
    items.push({
      id: 'vendas',
      label: 'Vendas (mês)',
      value: fmtMoeda(r.vendas_mes),
      hint: 'Financeiro',
      rota: '/financeiro',
      permission: 'financeiro.view',
    })
  }
  return items.filter((i) => can(i.permission))
})

function ir(path) {
  const raw = String(path || '')
  const q = raw.indexOf('?')
  if (q === -1) {
    router.push(raw)
    return
  }
  router.push({
    path: raw.slice(0, q),
    query: Object.fromEntries(new URLSearchParams(raw.slice(q + 1))),
  })
}

watch(
  () => route.query.acesso,
  (v) => {
    if (v === 'negado') capturarAcessoNegado()
  },
  { immediate: true }
)

onMounted(async () => {
  carregando.value = true
  try {
    const data = await loadHomeData()
    resumo.value = data.resumo
    pendencias.value = data.pendencias
    atividade.value = data.atividade
    fluxo.value = data.fluxo
    erroApi.value = data.erroApi
  } finally {
    carregando.value = false
  }
})
</script>

<style scoped>
.home {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: var(--spacing-md) var(--spacing-lg) var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  box-sizing: border-box;
}

.home-hero {
  position: relative;
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: linear-gradient(135deg, var(--color-primary-50) 0%, var(--color-surface) 55%);
  border: 1px solid var(--color-border-subtle);
  box-shadow: var(--shadow-md);
}

.home-hero__pattern {
  position: absolute;
  inset: 0;
  opacity: 0.07;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 8c4 8 12 10 12 18s-8 14-12 22c-4-8-12-10-12-18s8-14 12-22z' fill='%23596247'/%3E%3C/svg%3E");
  background-size: 60px 60px;
}

.home-hero__content {
  position: relative;
  padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-md);
}

.home-hero__greeting {
  margin: 0 0 0.25rem;
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
}

.home-hero__title {
  margin: 0 0 0.5rem;
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 700;
  color: var(--color-primary-700);
}

.home-hero__summary {
  margin: 0;
  font-size: 1rem;
  color: var(--color-text-primary);
}

.home-hero__alert {
  color: var(--color-error);
  font-weight: 600;
}

.home-erro {
  margin: 0;
}

.home-block__title {
  margin: 0 0 var(--spacing-md);
  font-size: 1.125rem;
  font-weight: 600;
}

.home-block__lead {
  margin: -0.5rem 0 var(--spacing-md);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.quick-action {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.1rem;
  padding: 0.45rem 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: background-color 0.15s, border-color 0.15s;
  min-height: 0;
}

.quick-action:hover {
  border-color: var(--color-primary-100);
  background: var(--color-primary-subtle);
}

.quick-action--primary {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.quick-action--primary:hover {
  background: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.quick-action--primary .quick-action__hint {
  color: rgba(255, 255, 255, 0.8);
}

.quick-action__label {
  font-weight: 600;
  font-size: 0.8125rem;
  line-height: 1.2;
}

.quick-action__hint {
  font-size: 0.6875rem;
  line-height: 1.2;
  color: var(--color-text-muted);
}

.home-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
  align-items: start;
}

.home-block--pendencias {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow);
  border: 1px solid var(--color-border-subtle);
}

.home-block--card,
.home-block--pendencias {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow);
  border: 1px solid var(--color-border-subtle);
}

.pendencias-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.pendencia-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--color-primary);
  background: var(--color-surface-muted);
}

.pendencia-item--alto {
  border-left-color: var(--color-error);
  background: var(--color-error-bg);
}

.pendencia-item--medio {
  border-left-color: var(--color-attention);
  background: var(--color-attention-bg);
}

.pendencia-item__body p {
  margin: 0.25rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.home-empty-inline {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--spacing-md);
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  background: var(--color-background);
  cursor: pointer;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  border-color: var(--color-primary-100);
  box-shadow: var(--shadow-sm);
}

.stat-card__value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-card__label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.stat-card__hint {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
}

.fluxo-track {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
}

.fluxo-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 88px;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  cursor: pointer;
  font-family: inherit;
}

.fluxo-step:hover {
  border-color: var(--color-primary);
}

.fluxo-step__count {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-primary);
}

.fluxo-step__label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  text-align: center;
}

.fluxo-arrow {
  color: var(--color-text-muted);
  font-size: 1.25rem;
}

.home-onboarding {
  text-align: center;
  padding: var(--spacing-2xl);
  background: var(--color-primary-subtle);
  border-radius: var(--radius-xl);
  border: 1px dashed var(--color-primary-100);
}

.home-onboarding__icon {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-md);
}

.home-onboarding h2 {
  margin: 0 0 0.5rem;
}

.home-onboarding p {
  margin: 0 0 var(--spacing-lg);
  color: var(--color-text-secondary);
}

.home-onboarding__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  justify-content: center;
}

.atividade-list {
  list-style: none;
  margin: 0;
  padding: 0;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-subtle);
  overflow: hidden;
}

.atividade-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-subtle);
}

.atividade-item:last-child {
  border-bottom: none;
}

.atividade-item__badge {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--color-primary);
}

.atividade-item__badge--praga {
  background: var(--color-error);
}

.atividade-item__badge--venda {
  background: var(--color-attention);
}

.atividade-item__badge--coleta {
  background: var(--color-info);
}

.atividade-item__text {
  flex: 1;
  min-width: 0;
}

.atividade-item__text p {
  margin: 0;
  font-size: 0.875rem;
}

.atividade-item__text time {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.atividade-item__link {
  border: none;
  background: none;
  color: var(--color-primary);
  font-weight: 600;
  font-size: 0.8125rem;
  cursor: pointer;
  font-family: inherit;
}

@media (max-width: 900px) {
  .home-grid {
    grid-template-columns: 1fr;
  }

  .home {
    padding: var(--spacing-md);
  }
}
</style>
