<template>
  <div class="contab-root module-root">
    <div
      class="module-banner module-banner--mock"
      :class="{ 'contab-banner--prod': ambiente?.ambiente_emitente === 'producao' }"
    >
      <strong>{{ bannerTitulo }}</strong>
      <p>{{ ambiente?.mensagem || 'Carregando ambiente…' }}</p>
      <p v-if="ambiente?.modo_mock" class="contab-banner__sub">
        Modo mock — configure <code>FOCUS_NFE_TOKEN</code> no backend para homologação Focus.
      </p>
      <p v-else-if="ambiente?.focus_token_configurado" class="contab-banner__sub">
        Token Focus configurado · ambiente emitente: <strong>{{ ambiente.ambiente_emitente }}</strong>
      </p>
    </div>

    <header class="module-header">
      <div>
        <h2 class="module-header__title">Contabilidade</h2>
        <p class="module-header__lead">
          Demonstrações contábeis em <strong>regime de competência</strong> (fato gerador) e cockpit fiscal NF-e.
          O <router-link to="/financeiro">Financeiro</router-link> gerencial usa regime de <strong>caixa</strong>.
        </p>
      </div>
      <div class="module-header__actions">
        <button type="button" class="btn btn-secondary" :disabled="carregando" @click="recarregarTudo">
          Atualizar
        </button>
      </div>
    </header>

    <nav class="contab-grupos" aria-label="Grupos contabilidade">
      <button
        type="button"
        class="contab-grupo-btn"
        :class="{ ativo: grupo === 'contabil' }"
        @click="selecionarGrupo('contabil')"
      >
        Demonstrações contábeis
      </button>
      <button
        type="button"
        class="contab-grupo-btn"
        :class="{ ativo: grupo === 'fiscal' }"
        @click="selecionarGrupo('fiscal')"
      >
        Fiscal — NF-e
      </button>
    </nav>

    <nav v-if="grupo === 'contabil'" class="module-tabs" aria-label="Demonstrações contábeis">
      <button
        v-for="t in abasContabil"
        :key="t.id"
        type="button"
        class="module-tab"
        :class="{ ativo: aba === t.id }"
        @click="aba = t.id"
      >
        {{ t.label }}
      </button>
    </nav>

    <nav v-else class="module-tabs" aria-label="Fiscal NF-e">
      <button
        v-for="t in abasFiscal"
        :key="t.id"
        type="button"
        class="module-tab"
        :class="{ ativo: aba === t.id }"
        @click="aba = t.id"
      >
        {{ t.label }}
        <span v-if="t.badge != null" class="module-tab__badge">{{ t.badge }}</span>
      </button>
    </nav>

    <p v-if="erro" class="alert-erro">{{ erro }}</p>

    <!-- Demonstrações contábeis -->
    <template v-if="grupo === 'contabil'">
      <ContabilidadePeriodoToolbar
        :mes="mes"
        :ano="ano"
        :carregando="carregandoContabil"
        @periodo="onPeriodo"
        @atualizar="carregarContabil"
      >
        <section v-show="aba === 'dre'" class="contab-sec">
          <FinanceiroPainel
            :painel="painelContabil"
            :lancamentos="[]"
            :carregando="carregandoContabil"
            :erro="erroContabil"
            :mes="mes"
            :ano="ano"
            modo="competencia"
            :mostrar-gestao="false"
            ocultar-toolbar
            :pode-editar="false"
            @atualizar="carregarContabil"
            @periodo="onPeriodo"
          />
        </section>

        <section v-show="aba === 'bp'" class="contab-sec">
          <ContabilidadeBalanco :dados="balanco" :carregando="carregandoContabil" :erro="erroContabil" />
        </section>

        <section v-show="aba === 'livro-caixa'" class="contab-sec">
          <ContabilidadeLivroCaixa :dados="livroCaixa" :carregando="carregandoContabil" :erro="erroContabil" />
        </section>

        <section v-show="aba === 'inventario'" class="contab-sec">
          <ContabilidadeInventario :dados="inventario" :carregando="carregandoContabil" :erro="erroContabil" />
        </section>

        <section v-show="aba === 'notas'" class="contab-sec">
          <ContabilidadeNotas :dados="notasExplicativas" :carregando="carregandoContabil" :erro="erroContabil" />
        </section>
      </ContabilidadePeriodoToolbar>
    </template>

    <!-- Fiscal NF-e -->
    <template v-else>
      <section v-show="aba === 'visao'" class="contab-sec">
        <div v-if="resumo" class="contab-cards">
          <article class="contab-card">
            <span class="contab-card__label">Total NF-e</span>
            <strong class="contab-card__valor">{{ resumo.total_notas }}</strong>
          </article>
          <article class="contab-card contab-card--ok">
            <span class="contab-card__label">Autorizadas</span>
            <strong class="contab-card__valor">{{ resumo.por_status?.autorizada || 0 }}</strong>
          </article>
          <article class="contab-card contab-card--warn">
            <span class="contab-card__label">Vendas sem NF-e</span>
            <strong class="contab-card__valor">{{ resumo.vendas_sem_nfe }}</strong>
          </article>
          <article class="contab-card">
            <span class="contab-card__label">Valor autorizado</span>
            <strong class="contab-card__valor">R$ {{ formatMoeda(resumo.valor_autorizado) }}</strong>
          </article>
        </div>
        <div v-if="resumo?.por_status" class="contab-status-grid">
          <div v-for="(qtd, st) in resumo.por_status" :key="st" class="contab-status-item">
            <span :class="['status-pill', `status-pill--${st}`]">{{ labelStatus(st) }}</span>
            <strong>{{ qtd }}</strong>
          </div>
        </div>
        <p v-if="resumo?.vendas_sem_nfe" class="contab-hint">
          Há {{ resumo.vendas_sem_nfe }} venda(s) aguardando NF-e —
          <button type="button" class="btn-link" @click="irPendentesNfe">Ver pendentes</button>
        </p>
      </section>

      <section v-show="aba === 'notas-nfe'" class="contab-sec module-sec">
        <div class="module-toolbar">
          <label class="module-toolbar__field">
            Status
            <select v-model="filtroStatus" @change="carregarNotas">
              <option value="">Todos</option>
              <option value="autorizada">Autorizada</option>
              <option value="processando">Processando</option>
              <option value="rejeitada">Rejeitada</option>
              <option value="cancelada">Cancelada</option>
            </select>
          </label>
        </div>
        <div v-if="notasFiscais.length" class="module-table-wrap">
          <table class="module-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Venda</th>
                <th>Cliente</th>
                <th>Data</th>
                <th>Valor</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="n in notasFiscais" :key="n.id">
                <td>{{ n.numero || '—' }}/{{ n.serie || '—' }}</td>
                <td>#{{ n.id_venda }}</td>
                <td>{{ n.comprador_nome }}</td>
                <td>{{ formatData(n.data_emissao || n.data_venda) }}</td>
                <td>R$ {{ formatMoeda(n.valor_venda) }}</td>
                <td>
                  <span :class="['status-pill', `status-pill--${n.status}`]">{{ labelStatus(n.status) }}</span>
                  <small v-if="n.xmotivo" class="motivo">{{ n.xmotivo }}</small>
                </td>
                <td class="acoes">
                  <button
                    v-if="n.status === 'processando'"
                    type="button"
                    class="btn-link"
                    @click="atualizarStatus(n)"
                  >
                    Atualizar
                  </button>
                  <a v-if="n.url_danfe" :href="n.url_danfe" target="_blank" rel="noopener" class="btn-link">DANFE</a>
                  <a v-if="n.url_xml" :href="n.url_xml" target="_blank" rel="noopener" class="btn-link">XML</a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty">Nenhuma NF-e encontrada.</p>
      </section>

      <section v-show="aba === 'pendentes'" class="contab-sec module-sec">
        <p class="contab-hint">
          Vendas sem NF-e autorizada ou em processamento. O contador pode emitir daqui; o vendedor também em Vendas.
        </p>
        <div v-if="pendentes.length" class="module-table-wrap">
          <table class="module-table">
            <thead>
              <tr>
                <th>Venda</th>
                <th>Cliente</th>
                <th>Data</th>
                <th>Valor</th>
                <th>Status venda</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="v in pendentes" :key="v.id">
                <td>#{{ v.id }}</td>
                <td>{{ v.comprador_nome }}</td>
                <td>{{ formatData(v.data_venda) }}</td>
                <td>R$ {{ formatMoeda(v.valor_total) }}</td>
                <td>{{ v.status }}</td>
                <td>
                  <button
                    v-if="podeEmitirNfe"
                    type="button"
                    class="btn btn-primary btn-sm"
                    :disabled="emitindoId === v.id"
                    @click="emitir(v.id)"
                  >
                    {{ emitindoId === v.id ? 'Emitindo…' : 'Emitir NF-e' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty">Nenhuma venda pendente de NF-e.</p>
      </section>

      <section v-show="aba === 'regras'" class="contab-sec">
        <FinanceiroFiscal :pode-editar="podeEditar" />
      </section>

      <section v-show="aba === 'emitente'" class="contab-sec">
        <ContabilidadeEmitente :pode-editar="podeEditar" :ambiente="ambiente" @salvo="carregarAmbiente" />
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, toRefs } from 'vue'
import { usePageTabBundle } from '@/composables/usePageTab'
import FinanceiroFiscal from '@/components/financeiro/FinanceiroFiscal.vue'
import FinanceiroPainel from '@/components/financeiro/FinanceiroPainel.vue'
import ContabilidadeEmitente from '@/components/contabilidade/ContabilidadeEmitente.vue'
import ContabilidadePeriodoToolbar from '@/components/contabilidade/ContabilidadePeriodoToolbar.vue'
import ContabilidadeBalanco from '@/components/contabilidade/ContabilidadeBalanco.vue'
import ContabilidadeLivroCaixa from '@/components/contabilidade/ContabilidadeLivroCaixa.vue'
import ContabilidadeInventario from '@/components/contabilidade/ContabilidadeInventario.vue'
import ContabilidadeNotas from '@/components/contabilidade/ContabilidadeNotas.vue'
import {
  getAmbienteNfe,
  getResumoFiscal,
  listNotasFiscais,
  vendasPendentesNfe,
} from '@/services/fiscal'
import {
  getPainelContabil,
  getBalancoPatrimonial,
  getLivroCaixa,
  getLivroInventario,
  getNotasExplicativas,
} from '@/services/contabilidade'
import { emitirNfe, getNfeStatus } from '@/services/nfe'
import { usePermissions } from '@/composables/usePermissions'

const { can } = usePermissions()
const podeEmitirNfe = computed(() => can('fiscal.emit'))
const podeEditar = computed(() => can('contabilidade.edit'))

const ABAS_CONTABIL_IDS = ['dre', 'bp', 'livro-caixa', 'inventario', 'notas']
const ABAS_FISCAL_IDS = ['visao', 'notas-nfe', 'pendentes', 'regras', 'emitente']

const tabState = usePageTabBundle('contabilidade', { grupo: 'contabil', aba: 'dre' }, {
  validate: (s) => {
    if (s?.grupo === 'contabil') return ABAS_CONTABIL_IDS.includes(s.aba)
    if (s?.grupo === 'fiscal') return ABAS_FISCAL_IDS.includes(s.aba)
    return false
  },
})
const { grupo, aba } = toRefs(tabState)

function selecionarGrupo(g) {
  if (grupo.value === g) return
  grupo.value = g
  aba.value = g === 'contabil' ? 'dre' : 'visao'
}

const hoje = new Date()
const mes = ref(hoje.getMonth() + 1)
const ano = ref(hoje.getFullYear())

const carregando = ref(false)
const carregandoContabil = ref(false)
const erro = ref(null)
const erroContabil = ref(null)
const ambiente = ref(null)
const resumo = ref(null)
const notasFiscais = ref([])
const pendentes = ref([])
const filtroStatus = ref('')
const emitindoId = ref(null)

const painelContabil = ref(null)
const balanco = ref(null)
const livroCaixa = ref(null)
const inventario = ref(null)
const notasExplicativas = ref(null)

const abasContabil = [
  { id: 'dre', label: 'DRE' },
  { id: 'bp', label: 'Balanço patrimonial' },
  { id: 'livro-caixa', label: 'Livro caixa' },
  { id: 'inventario', label: 'Livro de inventário' },
  { id: 'notas', label: 'Notas explicativas' },
]

const abasFiscal = computed(() => [
  { id: 'visao', label: 'Visão geral' },
  { id: 'notas-nfe', label: 'Todas as NF-e' },
  { id: 'pendentes', label: 'Pendentes NF-e', badge: resumo.value?.vendas_sem_nfe || null },
  { id: 'regras', label: 'Regras fiscais' },
  { id: 'emitente', label: 'Emitente' },
])

const bannerTitulo = computed(() => {
  if (!ambiente.value) return 'NF-e'
  if (ambiente.value.ambiente_emitente === 'producao') {
    return ambiente.value.producao_permitida_sistema ? 'PRODUÇÃO' : 'PRODUÇÃO BLOQUEADA'
  }
  return 'HOMOLOGAÇÃO — sem valor fiscal'
})

function formatMoeda(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatData(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR')
}

function labelStatus(st) {
  const map = {
    autorizada: 'Autorizada',
    simulacao: 'Simulação',
    processando: 'Processando',
    rejeitada: 'Rejeitada',
    cancelada: 'Cancelada',
  }
  return map[st] || st
}

function onPeriodo({ mes: m, ano: a }) {
  mes.value = m
  ano.value = a
  carregarContabil()
}

function irPendentesNfe() {
  grupo.value = 'fiscal'
  aba.value = 'pendentes'
}

async function carregarAmbiente() {
  ambiente.value = await getAmbienteNfe()
}

async function carregarResumo() {
  resumo.value = await getResumoFiscal()
}

async function carregarNotas() {
  const params = { limit: 200 }
  if (filtroStatus.value) params.status = filtroStatus.value
  notasFiscais.value = await listNotasFiscais(params)
}

async function carregarPendentes() {
  pendentes.value = await vendasPendentesNfe()
}

async function carregarContabil() {
  carregandoContabil.value = true
  erroContabil.value = null
  const params = { mes: mes.value, ano: ano.value }
  try {
    const [painel, bp, lc, inv, nt] = await Promise.all([
      getPainelContabil(params),
      getBalancoPatrimonial(params),
      getLivroCaixa(params),
      getLivroInventario(params),
      getNotasExplicativas(params),
    ])
    painelContabil.value = painel
    balanco.value = bp
    livroCaixa.value = lc
    inventario.value = inv
    notasExplicativas.value = nt
  } catch (e) {
    erroContabil.value = e.response?.data?.detail || 'Falha ao carregar demonstrações contábeis.'
    painelContabil.value = null
  } finally {
    carregandoContabil.value = false
  }
}

async function recarregarTudo() {
  carregando.value = true
  erro.value = null
  try {
    await Promise.all([
      carregarAmbiente(),
      carregarResumo(),
      carregarNotas(),
      carregarPendentes(),
      carregarContabil(),
    ])
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha ao carregar dados de contabilidade.'
  } finally {
    carregando.value = false
  }
}

async function atualizarStatus(nota) {
  try {
    await getNfeStatus(nota.id)
    await carregarNotas()
    await carregarResumo()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao consultar status.')
  }
}

async function emitir(vendaId) {
  if (!podeEmitirNfe.value) return
  emitindoId.value = vendaId
  try {
    const res = await emitirNfe(vendaId)
    alert(res.mensagem || 'NF-e enviada.')
    await recarregarTudo()
    grupo.value = 'fiscal'
    aba.value = 'notas-nfe'
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao emitir NF-e.')
  } finally {
    emitindoId.value = null
  }
}

onMounted(recarregarTudo)
</script>

<style scoped>
.contab-banner__sub {
  font-size: 0.875rem !important;
  opacity: 0.9;
  margin: 0.35rem 0 0;
}
.contab-banner--prod {
  background: var(--color-error-bg);
  border-color: color-mix(in srgb, var(--color-error) 40%, var(--color-border));
  color: var(--color-error);
}
.contab-grupos {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: var(--spacing-sm);
}
.contab-grupo-btn {
  padding: 0.45rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-subtle);
  background: var(--color-surface);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
}
.contab-grupo-btn.ativo {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: transparent;
}
.contab-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}
.contab-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.contab-card--ok {
  border-color: var(--color-success);
}
.contab-card--warn {
  border-color: var(--color-attention);
}
.contab-card__label {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}
.contab-card__valor {
  font-size: 1.35rem;
}
.contab-status-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}
.contab-status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}
.contab-hint {
  font-size: 0.875rem;
  color: var(--color-text-muted);
}
.status-pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}
.status-pill--simulacao {
  background: var(--color-attention-bg);
  color: var(--color-text-secondary);
}
.status-pill--autorizada {
  background: var(--color-success-bg);
  color: var(--color-success);
}
.status-pill--processando {
  background: var(--color-info-bg);
  color: var(--color-info-dark);
}
.status-pill--rejeitada {
  background: var(--color-error-bg);
  color: var(--color-error);
}
.status-pill--cancelada {
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
}
.motivo {
  display: block;
  color: var(--color-text-muted);
  margin-top: 0.2rem;
}
.acoes {
  white-space: nowrap;
}
.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.8125rem;
}
.empty {
  color: var(--color-text-muted);
}
</style>
