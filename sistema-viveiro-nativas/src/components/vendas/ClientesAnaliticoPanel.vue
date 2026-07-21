<template>
  <div class="clientes-analitico">
    <header class="module-header">
      <p class="module-header__lead">
        <template v-if="verResumoFinanceiro">
          Quem compra, quanto lucra e quem precisa de um oi —
          lucro = receita da venda menos CMV registrado no item.
        </template>
        <template v-else>
          Relacionamento com clientes — quem compra, fidelidade e quem precisa de um retorno.
          Valores por cliente na tabela; totais consolidados só para gestão.
        </template>
        Vendas canceladas não entram.
      </p>
      <div class="module-header__actions analitico-toolbar">
        <label class="field-inline">
          <span>Período</span>
          <select v-model.number="meses" @change="carregar">
            <option v-for="p in PERIODOS_CLIENTES" :key="p.meses" :value="p.meses">
              {{ p.label }}
            </option>
          </select>
        </label>
        <button type="button" class="btn btn-secondary btn-sm" :disabled="carregando" @click="carregar">
          {{ carregando ? '…' : 'Atualizar' }}
        </button>
        <CanAccess permission="vendas.create">
          <button type="button" class="btn btn-primary btn-sm" @click="$emit('novo')">
            + Novo cliente
          </button>
        </CanAccess>
      </div>
    </header>

    <p v-if="erro" class="alert-erro">{{ erro }}</p>
    <p v-if="carregando && !dados" class="status-msg">Carregando inteligência de clientes…</p>

    <template v-else-if="dados">
      <section v-if="verResumoFinanceiro" class="kpi-grid" aria-label="Indicadores do período">
        <article class="kpi-card">
          <span class="kpi-card__label">Clientes com compra</span>
          <strong class="kpi-card__valor">{{ dados.resumo.clientes_com_compra_periodo }}</strong>
          <span class="kpi-card__meta">de {{ dados.resumo.total_clientes_cadastro }} cadastrados</span>
        </article>
        <article class="kpi-card kpi-card--destaque">
          <span class="kpi-card__label">Faturamento</span>
          <strong class="kpi-card__valor">{{ fmtMoeda(dados.resumo.receita_periodo) }}</strong>
          <span class="kpi-card__meta">{{ dados.resumo.mudas_vendidas_periodo }} mudas · ticket {{ fmtMoeda(dados.resumo.ticket_medio_periodo) }}</span>
        </article>
        <article class="kpi-card kpi-card--lucro">
          <span class="kpi-card__label">Lucro estimado</span>
          <strong class="kpi-card__valor">{{ fmtMoeda(dados.resumo.lucro_periodo) }}</strong>
          <span class="kpi-card__meta">
            margem {{ dados.resumo.margem_media_pct != null ? dados.resumo.margem_media_pct + '%' : '—' }}
          </span>
        </article>
        <article class="kpi-card">
          <span class="kpi-card__label">Clientes fiéis</span>
          <strong class="kpi-card__valor">{{ dados.resumo.clientes_recorrentes }}</strong>
          <span class="kpi-card__meta">3+ compras no período ou histórico forte</span>
        </article>
        <article class="kpi-card kpi-card--alerta">
          <span class="kpi-card__label">Precisam atenção</span>
          <strong class="kpi-card__valor">{{ dados.resumo.clientes_atencao }}</strong>
          <span class="kpi-card__meta">sem compra há 90+ dias</span>
        </article>
        <article class="kpi-card">
          <span class="kpi-card__label">A receber</span>
          <strong class="kpi-card__valor">{{ fmtMoeda(dados.resumo.receita_pendente) }}</strong>
          <span class="kpi-card__meta">vendas com pagamento pendente</span>
        </article>
      </section>

      <div class="analitico-grid">
        <section class="analitico-card">
          <nav class="ranking-tabs" role="tablist">
            <button
              v-for="r in RANKINGS_CLIENTES"
              :key="r.id"
              type="button"
              class="ranking-tab"
              :class="{ 'ranking-tab--ativa': rankingAtivo === r.id }"
              :title="r.hint"
              @click="rankingAtivo = r.id"
            >
              {{ r.label }}
            </button>
          </nav>
          <p class="ranking-guia">{{ rankingGuia }}</p>
          <ol v-if="rankingLista.length" class="ranking-lista">
            <li v-for="(item, idx) in rankingLista" :key="item.id">
              <button type="button" class="ranking-item" @click="abrirDetalhe(item.id)">
                <span class="ranking-item__pos">{{ idx + 1 }}</span>
                <span class="ranking-item__corpo">
                  <strong>{{ item.nome }}</strong>
                  <span class="ranking-item__sub">
                    {{ item.cidade || '—' }}/{{ item.estado || '—' }} · {{ item.tipo }}
                  </span>
                </span>
                <span class="ranking-item__valor">
                  {{ fmtRankingValor(item) }}
                  <small v-if="item.valor_secundario != null">
                    {{ item.label_secundario }}: {{ fmtRankingSec(item) }}
                  </small>
                </span>
              </button>
            </li>
          </ol>
          <p v-else class="empty-hint">Nenhum cliente neste recorte ainda.</p>
        </section>

        <section class="analitico-card analitico-card--geo">
          <h3 class="analitico-card__titulo">Onde estão seus clientes</h3>
          <p class="analitico-card__sub">
            {{ verResumoFinanceiro ? 'Faturamento no período por UF' : 'Clientes com compra no período por UF' }}
          </p>
          <div v-if="dados.por_uf.length" class="barra-lista">
            <div v-for="uf in dados.por_uf.slice(0, 8)" :key="uf.chave" class="barra-item">
              <div class="barra-item__top">
                <span>{{ uf.uf }}</span>
                <span v-if="verResumoFinanceiro">{{ fmtMoeda(uf.receita) }} · {{ uf.clientes }} cli.</span>
                <span v-else>{{ uf.clientes }} cliente(s)</span>
              </div>
              <div class="barra-item__track">
                <div
                  class="barra-item__fill"
                  :style="{ width: pctUf(verResumoFinanceiro ? uf.receita : uf.clientes) + '%' }"
                />
              </div>
            </div>
          </div>
          <p v-else class="empty-hint">Sem vendas geolocalizadas no período.</p>

          <div v-if="dados.por_tipo.length" class="tipo-split">
            <article v-for="t in dados.por_tipo" :key="t.tipo" class="tipo-pill">
              <span class="tipo-pill__label">{{ t.tipo === 'PJ' ? 'Pessoa jurídica' : 'Pessoa física' }}</span>
              <strong>{{ t.clientes }} clientes</strong>
              <span v-if="verResumoFinanceiro">{{ fmtMoeda(t.receita) }} · lucro {{ fmtMoeda(t.lucro) }}</span>
            </article>
          </div>

          <h4 class="subtitulo-cidades">Top cidades</h4>
          <ul v-if="dados.por_cidade.length" class="cidade-lista">
            <li v-for="c in dados.por_cidade.slice(0, 6)" :key="c.chave">
              <span>{{ c.chave }}</span>
              <strong v-if="verResumoFinanceiro">{{ fmtMoeda(c.receita) }}</strong>
              <strong v-else>{{ c.clientes }} cli.</strong>
            </li>
          </ul>
        </section>
      </div>

      <section class="analitico-card analitico-card--tabela">
        <div class="tabela-toolbar">
          <h3 class="analitico-card__titulo">Carteira completa</h3>
          <div class="tabela-filtros">
            <input v-model="busca" type="search" placeholder="Buscar nome…" class="filtro-busca" />
            <select v-model="filtroStatus">
              <option value="">Todos os perfis</option>
              <option v-for="(s, k) in STATUS_RELACIONAMENTO" :key="k" :value="k">{{ s.label }}</option>
            </select>
            <select v-model="ordenacao">
              <option value="receita">Maior faturamento</option>
              <option value="lucro">Maior lucro</option>
              <option value="fidelidade">Mais compras</option>
              <option value="recencia">Mais recente</option>
              <option value="nome">Nome A–Z</option>
            </select>
          </div>
        </div>
        <div class="module-table-wrap">
          <table class="module-table">
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Perfil</th>
                <th>Local</th>
                <th class="col-num">Compras</th>
                <th class="col-num">Faturamento</th>
                <th class="col-num">Lucro</th>
                <th class="col-num">Última compra</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!clientesFiltrados.length">
                <td colspan="8" class="empty-cell">Nenhum cliente no filtro.</td>
              </tr>
              <tr
                v-for="c in clientesFiltrados"
                :key="c.id"
                class="linha-clicavel"
                @click="abrirDetalhe(c.id)"
              >
                <td>
                  <strong>{{ c.nome }}</strong>
                  <span class="tag-tipo">{{ c.tipo }}</span>
                </td>
                <td>
                  <span class="tag-perfil" :class="'tag-perfil--' + statusMeta(c).tone">
                    {{ statusMeta(c).label }}
                  </span>
                </td>
                <td>{{ c.cidade || '—' }}/{{ c.estado || '—' }}</td>
                <td class="col-num">{{ c.vendas_periodo }}</td>
                <td class="col-num">{{ fmtMoeda(c.receita_periodo) }}</td>
                <td class="col-num">{{ fmtMoeda(c.lucro_periodo) }}</td>
                <td class="col-num">{{ fmtRecencia(c) }}</td>
                <td class="col-acoes" @click.stop>
                  <button type="button" class="btn-link" @click="$emit('editar', c.id)">Editar</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <AppModalOverlay
      :aberto="detalheAberto"
      :handlers="overlayDetalhe"
      panel-class="app-modal-panel--wide"
      aria-labelledby="cliente-detalhe-titulo"
    >
      <template v-if="clienteDetalhe">
        <header class="app-modal-header">
          <div>
            <h3 id="cliente-detalhe-titulo">{{ clienteDetalhe.nome }}</h3>
            <p class="app-modal-sub">
              {{ clienteDetalhe.cidade || '—' }}/{{ clienteDetalhe.estado || '—' }} · {{ clienteDetalhe.tipo }}
              ·
              <span class="tag-perfil" :class="'tag-perfil--' + statusMeta(clienteDetalhe).tone">
                {{ statusMeta(clienteDetalhe).label }}
              </span>
            </p>
          </div>
          <button type="button" class="app-modal-fechar" aria-label="Fechar" @click="fecharDetalhe">×</button>
        </header>
        <div class="app-modal-body detalhe-grid">
          <div class="detalhe-bloco">
            <h4>No período ({{ dados?.resumo.periodo_label }})</h4>
            <ul class="detalhe-kpis">
              <li><span>Compras</span><strong>{{ clienteDetalhe.vendas_periodo }}</strong></li>
              <li><span>Faturamento</span><strong>{{ fmtMoeda(clienteDetalhe.receita_periodo) }}</strong></li>
              <li><span>Lucro</span><strong>{{ fmtMoeda(clienteDetalhe.lucro_periodo) }}</strong></li>
              <li><span>Margem</span><strong>{{ clienteDetalhe.margem_pct != null ? clienteDetalhe.margem_pct + '%' : '—' }}</strong></li>
              <li><span>Mudas</span><strong>{{ clienteDetalhe.mudas_periodo }}</strong></li>
            </ul>
          </div>
          <div class="detalhe-bloco">
            <h4>Histórico</h4>
            <ul class="detalhe-kpis">
              <li><span>Total de compras</span><strong>{{ clienteDetalhe.vendas_historico }}</strong></li>
              <li><span>Primeira compra</span><strong>{{ fmtData(clienteDetalhe.primeira_compra) }}</strong></li>
              <li><span>Última compra</span><strong>{{ fmtData(clienteDetalhe.ultima_compra) }}</strong></li>
              <li><span>Dias sem comprar</span><strong>{{ clienteDetalhe.dias_desde_ultima ?? '—' }}</strong></li>
              <li v-if="clienteDetalhe.receita_pendente > 0">
                <span>A receber</span><strong>{{ fmtMoeda(clienteDetalhe.receita_pendente) }}</strong>
              </li>
            </ul>
          </div>
          <div class="detalhe-bloco detalhe-bloco--full">
            <h4>Contato</h4>
            <p class="detalhe-contato">
              {{ clienteDetalhe.telefone || 'Sem telefone' }}
              <span v-if="clienteDetalhe.email"> · {{ clienteDetalhe.email }}</span>
            </p>
          </div>
        </div>
        <footer class="app-modal-footer">
          <button type="button" class="btn btn-secondary" @click="fecharDetalhe">Fechar</button>
          <button type="button" class="btn btn-primary" @click="editarDetalhe">Editar cadastro</button>
        </footer>
      </template>
    </AppModalOverlay>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import { useSimpleModalClose } from '@/composables/useSimpleModalClose'
import CanAccess from '@/components/shared/CanAccess.vue'
import { usePermissions } from '@/composables/usePermissions'
import { getCompradoresAnalitico } from '@/services/compradores'
import {
  PERIODOS_CLIENTES,
  RANKINGS_CLIENTES,
  ROLES_RESUMO_FINANCEIRO_CLIENTES,
  STATUS_RELACIONAMENTO,
  fmtMoeda,
  fmtData,
} from '@/constants/clientesAnalitico'

const emit = defineEmits(['novo', 'editar'])

const { hasAnyRole } = usePermissions()

const meses = ref(12)
const carregando = ref(false)
const erro = ref(null)
const dados = ref(null)
const rankingAtivo = ref('por_lucro')
const busca = ref('')
const filtroStatus = ref('')
const ordenacao = ref('receita')
const detalheAberto = ref(false)
const clienteDetalhe = ref(null)

/** API filtra totais; fallback local por perfil enquanto carrega. */
const verResumoFinanceiro = computed(() => {
  if (dados.value != null) return Boolean(dados.value.mostrar_resumo_financeiro)
  return hasAnyRole(...ROLES_RESUMO_FINANCEIRO_CLIENTES)
})

const rankingGuia = computed(
  () => RANKINGS_CLIENTES.find((r) => r.id === rankingAtivo.value)?.hint || ''
)

const rankingLista = computed(() => dados.value?.rankings?.[rankingAtivo.value] || [])

const maxUfReceita = computed(() => {
  const rows = dados.value?.por_uf || []
  if (verResumoFinanceiro.value) {
    return Math.max(...rows.map((u) => u.receita), 1)
  }
  return Math.max(...rows.map((u) => u.clientes), 1)
})

const clientesFiltrados = computed(() => {
  let lista = [...(dados.value?.clientes || [])]
  const q = busca.value.trim().toLowerCase()
  if (q) lista = lista.filter((c) => (c.nome || '').toLowerCase().includes(q))
  if (filtroStatus.value) {
    lista = lista.filter((c) => c.status_relacionamento === filtroStatus.value)
  }
  const ord = ordenacao.value
  lista.sort((a, b) => {
    if (ord === 'lucro') return b.lucro_periodo - a.lucro_periodo
    if (ord === 'fidelidade') return b.vendas_periodo - a.vendas_periodo
    if (ord === 'recencia') return (a.dias_desde_ultima ?? 9999) - (b.dias_desde_ultima ?? 9999)
    if (ord === 'nome') return (a.nome || '').localeCompare(b.nome || '', 'pt-BR')
    return b.receita_periodo - a.receita_periodo
  })
  return lista
})

function statusMeta(c) {
  return STATUS_RELACIONAMENTO[c.status_relacionamento] || STATUS_RELACIONAMENTO.lead
}

function pctUf(receita) {
  return Math.max(4, Math.round((receita / maxUfReceita.value) * 100))
}

function fmtRankingValor(item) {
  if (rankingAtivo.value === 'precisam_atencao') return `${Math.round(item.valor)} dias`
  if (rankingAtivo.value === 'por_fidelidade') return `${item.valor} compras`
  return fmtMoeda(item.valor)
}

function fmtRankingSec(item) {
  if (rankingAtivo.value === 'por_lucro') return `${item.valor_secundario}%`
  if (rankingAtivo.value === 'por_fidelidade') return fmtMoeda(item.valor_secundario)
  return item.valor_secundario
}

function fmtRecencia(c) {
  if (!c.ultima_compra) return '—'
  if (c.dias_desde_ultima === 0) return 'Hoje'
  if (c.dias_desde_ultima != null && c.dias_desde_ultima <= 30) return `${c.dias_desde_ultima} d`
  return fmtData(c.ultima_compra)
}

function abrirDetalhe(id) {
  const c = dados.value?.clientes?.find((x) => x.id === id)
  if (!c) return
  clienteDetalhe.value = c
  detalheAberto.value = true
}

function fecharDetalheInterno() {
  detalheAberto.value = false
  clienteDetalhe.value = null
}

const overlayDetalhe = useSimpleModalClose(fecharDetalheInterno, () => detalheAberto.value)

function fecharDetalhe() {
  overlayDetalhe.resetOverlayPress()
  fecharDetalheInterno()
}

function editarDetalhe() {
  const id = clienteDetalhe.value?.id
  fecharDetalheInterno()
  if (id) emit('editar', id)
}

async function carregar() {
  carregando.value = true
  erro.value = null
  try {
    dados.value = await getCompradoresAnalitico(meses.value)
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha ao carregar análise de clientes.'
  } finally {
    carregando.value = false
  }
}

onMounted(carregar)

defineExpose({ carregar })
</script>

<style scoped>
.analitico-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.5rem;
}

.field-inline {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.field-inline select {
  min-width: 8rem;
  padding: 0.4rem 0.55rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  font-family: inherit;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(10.5rem, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.kpi-card {
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-subtle);
  background: var(--color-surface-muted);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.kpi-card--destaque {
  border-color: var(--color-primary-100);
  background: var(--color-primary-subtle);
}

.kpi-card--lucro {
  border-color: var(--color-success);
  background: var(--color-success-bg);
}

.kpi-card--alerta {
  border-color: var(--color-attention);
  background: var(--color-attention-bg);
}

.kpi-card__label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.kpi-card__valor {
  font-size: 1.25rem;
  color: var(--color-primary-700);
  line-height: 1.1;
}

.kpi-card__meta {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  line-height: 1.35;
}

.analitico-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

@media (max-width: 900px) {
  .analitico-grid {
    grid-template-columns: 1fr;
  }
}

.analitico-card {
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  padding: var(--spacing-md);
}

.analitico-card--tabela {
  padding: 0;
  overflow: hidden;
}

.analitico-card__titulo {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
}

.analitico-card__sub {
  margin: 0.2rem 0 var(--spacing-md);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.ranking-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.5rem;
}

.ranking-tab {
  border: 1px solid var(--color-border-subtle);
  background: var(--color-surface-muted);
  padding: 0.35rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  color: var(--color-text-secondary);
}

.ranking-tab--ativa {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
  color: var(--color-primary-700);
}

.ranking-guia {
  margin: 0 0 var(--spacing-sm);
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.ranking-lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.ranking-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  background: var(--color-surface-muted);
  cursor: pointer;
  text-align: left;
  font-family: inherit;
}

.ranking-item:hover {
  border-color: var(--color-primary-100);
  background: var(--color-primary-subtle);
}

.ranking-item__pos {
  width: 1.5rem;
  font-weight: 700;
  color: var(--color-primary-700);
}

.ranking-item__corpo {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.ranking-item__corpo strong {
  font-size: 0.875rem;
}

.ranking-item__sub {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
}

.ranking-item__valor {
  font-size: 0.8125rem;
  font-weight: 700;
  text-align: right;
  color: var(--color-primary-700);
}

.ranking-item__valor small {
  display: block;
  font-weight: 500;
  color: var(--color-text-muted);
}

.barra-lista {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: var(--spacing-md);
}

.barra-item__top {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  margin-bottom: 0.2rem;
}

.barra-item__track {
  height: 6px;
  background: var(--color-border-subtle);
  border-radius: 3px;
  overflow: hidden;
}

.barra-item__fill {
  height: 100%;
  background: var(--color-primary);
  min-width: 2px;
}

.tipo-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: var(--spacing-md);
}

.tipo-pill {
  padding: 0.55rem 0.65rem;
  border-radius: var(--radius-md);
  background: var(--color-surface-muted);
  font-size: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.tipo-pill__label {
  font-weight: 600;
  color: var(--color-text-secondary);
}

.subtitulo-cidades {
  margin: 0 0 0.35rem;
  font-size: 0.8125rem;
}

.cidade-lista {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 0.8125rem;
}

.cidade-lista li {
  display: flex;
  justify-content: space-between;
  padding: 0.3rem 0;
  border-bottom: 1px solid var(--color-border-subtle);
}

.tabela-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border-subtle);
}

.tabela-filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filtro-busca,
.tabela-filtros select {
  padding: 0.35rem 0.55rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
  font-family: inherit;
}

.col-num {
  text-align: right;
  white-space: nowrap;
}

.col-acoes {
  text-align: right;
}

.linha-clicavel {
  cursor: pointer;
}

.linha-clicavel:hover td {
  background: var(--color-primary-subtle);
}

.tag-tipo {
  display: inline-block;
  margin-left: 0.35rem;
  font-size: 0.6875rem;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  background: var(--color-border-subtle);
  font-weight: 600;
}

.tag-perfil {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
}

.tag-perfil--muted {
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
}

.tag-perfil--info {
  background: var(--color-info-bg);
  color: var(--color-info);
}

.tag-perfil--ok {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.tag-perfil--success {
  background: var(--color-primary-subtle);
  color: var(--color-primary-700);
  border: 1px solid var(--color-primary-100);
}

.tag-perfil--warn {
  background: var(--color-attention-bg);
  color: var(--color-text-secondary);
}

.tag-perfil--danger {
  background: #fdecea;
  color: #a63d3d;
}

.empty-hint {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  margin: 0;
}

.detalhe-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.detalhe-bloco--full {
  grid-column: 1 / -1;
}

.detalhe-bloco h4 {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
}

.detalhe-kpis {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.35rem;
}

.detalhe-kpis li {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--color-border-subtle);
}

.detalhe-contato {
  margin: 0;
  font-size: 0.9375rem;
}

@media (max-width: 640px) {
  .detalhe-grid {
    grid-template-columns: 1fr;
  }
  .tipo-split {
    grid-template-columns: 1fr;
  }
}
</style>
