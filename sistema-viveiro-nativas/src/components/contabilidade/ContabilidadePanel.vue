<template>
  <div class="contab-root module-root">
    <div class="module-banner module-banner--mock" :class="{ 'contab-banner--prod': ambiente?.ambiente_emitente === 'producao' }">
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
          Cockpit do contador: consolidar NF-e, emitir pendentes, parâmetros fiscais e emitente.
          O vendedor continua emitindo em <router-link to="/vendas">Vendas</router-link>.
        </p>
      </div>
      <div class="module-header__actions">
        <button type="button" class="btn btn-secondary" :disabled="carregando" @click="recarregarTudo">
          Atualizar
        </button>
      </div>
    </header>

    <nav class="module-tabs" aria-label="Seções contabilidade">
      <button
        v-for="t in abas"
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

    <!-- Visão geral -->
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
        <button type="button" class="btn-link" @click="aba = 'pendentes'">Ver pendentes</button>
      </p>
    </section>

    <!-- Todas as NF-e -->
    <section v-show="aba === 'notas'" class="contab-sec module-sec">
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
      <div v-if="notas.length" class="module-table-wrap">
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
          <tr v-for="n in notas" :key="n.id">
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

    <!-- Vendas pendentes -->
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
                v-if="podeEditar"
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

    <!-- Regras fiscais -->
    <section v-show="aba === 'regras'" class="contab-sec">
      <FinanceiroFiscal :pode-editar="podeEditar" />
    </section>

    <!-- Emitente -->
    <section v-show="aba === 'emitente'" class="contab-sec">
      <ContabilidadeEmitente :pode-editar="podeEditar" :ambiente="ambiente" @salvo="carregarAmbiente" />
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import FinanceiroFiscal from '@/components/financeiro/FinanceiroFiscal.vue'
import ContabilidadeEmitente from '@/components/contabilidade/ContabilidadeEmitente.vue'
import {
  getAmbienteNfe,
  getResumoFiscal,
  listNotasFiscais,
  vendasPendentesNfe,
} from '@/services/fiscal'
import { emitirNfe, getNfeStatus } from '@/services/nfe'
import { usePermissions } from '@/composables/usePermissions'

const { can } = usePermissions()
const podeEditar = computed(() => can('contabilidade.edit'))

const aba = ref('visao')
const carregando = ref(false)
const erro = ref(null)
const ambiente = ref(null)
const resumo = ref(null)
const notas = ref([])
const pendentes = ref([])
const filtroStatus = ref('')
const emitindoId = ref(null)

const abas = computed(() => [
  { id: 'visao', label: 'Visão geral' },
  { id: 'notas', label: 'Todas as NF-e' },
  { id: 'pendentes', label: 'Pendentes', badge: resumo.value?.vendas_sem_nfe || null },
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

async function carregarAmbiente() {
  ambiente.value = await getAmbienteNfe()
}

async function carregarResumo() {
  resumo.value = await getResumoFiscal()
}

async function carregarNotas() {
  const params = { limit: 200 }
  if (filtroStatus.value) params.status = filtroStatus.value
  notas.value = await listNotasFiscais(params)
}

async function carregarPendentes() {
  pendentes.value = await vendasPendentesNfe()
}

async function recarregarTudo() {
  carregando.value = true
  erro.value = null
  try {
    await Promise.all([carregarAmbiente(), carregarResumo(), carregarNotas(), carregarPendentes()])
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
  emitindoId.value = vendaId
  try {
    const res = await emitirNfe(vendaId)
    alert(res.mensagem || 'NF-e enviada.')
    await recarregarTudo()
    aba.value = 'notas'
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao emitir NF-e.')
  } finally {
    emitindoId.value = null
  }
}

onMounted(recarregarTudo)
</script>

<style scoped>
.contab-root {
  /* module-root handles gap */
}
.contab-banner__sub {
  font-size: 0.875rem !important;
  opacity: 0.9;
  margin: 0.35rem 0 0;
}
.contab-banner--prod {
  background: #f8d7da;
  border-color: #dc3545;
  color: #842029;
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
  border-color: #198754;
}
.contab-card--warn {
  border-color: #ffc107;
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
  background: #fff3cd;
  color: #664d03;
}
.status-pill--autorizada {
  background: #d1e7dd;
  color: #0f5132;
}
.status-pill--processando {
  background: #cff4fc;
  color: #055160;
}
.status-pill--rejeitada {
  background: #f8d7da;
  color: #842029;
}
.status-pill--cancelada {
  background: #e2e3e5;
  color: #41464b;
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
