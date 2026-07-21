<template>
  <section
    class="analitico-panel"
    :class="metrica === 'rustificacao' ? 'analitico-panel--rust' : 'analitico-panel--viveiro'"
  >
    <div class="analitico-toolbar">
      <h3 class="analitico-toolbar__titulo">Estoque em detalhe</h3>
      <div class="analitico-metrica" role="group" aria-label="Como contar a idade">
        <button
          type="button"
          class="metrica-btn metrica-btn--viveiro"
          :class="{ 'metrica-btn--ativa': metrica === 'viveiro' }"
          @click="setMetrica('viveiro')"
        >
          Idade no viveiro
        </button>
        <button
          type="button"
          class="metrica-btn metrica-btn--rust"
          :class="{ 'metrica-btn--ativa': metrica === 'rustificacao' }"
          @click="setMetrica('rustificacao')"
        >
          Dias na rustificação
        </button>
      </div>
    </div>

    <nav class="visao-tabs" aria-label="Tipo de visão">
      <button
        v-for="v in visoes"
        :key="v.id"
        type="button"
        class="visao-tab"
        :class="{ 'visao-tab--ativa': visaoAtiva === v.id }"
        @click="visaoAtiva = v.id"
      >
        {{ v.label }}
      </button>
      <button type="button" class="btn-detalhe-tudo" @click="abrirDetalhe()">
        Ver todas muda a muda
      </button>
    </nav>

    <!-- Por espécie -->
    <Transition name="metrica-fade" mode="out-in">
      <div v-if="visaoAtiva === 'especie'" :key="'esp-' + metrica">
        <p class="tabela-guia">{{ guiaTabelaAtiva }}</p>
        <div class="estoque-table-card analitico-table-wrap">
        <table class="estoque-table">
          <thead>
            <tr>
              <th>Espécie</th>
              <th class="col-num" title="Todas as mudas vivas desta espécie">Mudas vivas</th>
              <th class="col-num" title="Liberadas para venda comercial">Prontas venda</th>
              <th class="col-num col-idade" :class="{ 'col-idade--ativa': metrica === 'viveiro' }" title="Dias desde o plantio">
                Dias no viveiro
              </th>
              <th class="col-num col-idade" :class="{ 'col-idade--ativa': metrica === 'rustificacao' }" title="Dias na área de rustificação">
                Dias rustificação
              </th>
              <th class="col-num" title="Custo acumulado médio por muda">Custo méd.</th>
              <th class="col-num" title="Soma do custo de todas as mudas vivas">Valor total</th>
              <th class="col-acoes"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in porEspecie" :key="e.id_especie">
              <td>
                <span class="estoque-especie">{{ e.nome_popular || e.nome_cientifico }}</span>
                <span v-if="e.nome_popular" class="estoque-especie-cient">{{ e.nome_cientifico }}</span>
              </td>
              <td class="col-num"><strong>{{ e.quantidade_total }}</strong></td>
              <td class="col-num">{{ e.quantidade_comercial }}</td>
              <td class="col-num col-idade" :class="{ 'col-idade--ativa': metrica === 'viveiro' }">
                {{ fmtIdade(e.dias_viveiro_medio, e.dias_viveiro_min, e.dias_viveiro_max) }}
              </td>
              <td class="col-num col-idade" :class="{ 'col-idade--ativa': metrica === 'rustificacao' }">
                {{ fmtIdade(e.dias_rustificacao_medio, e.dias_rustificacao_min, e.dias_rustificacao_max) }}
              </td>
              <td class="col-num">R$ {{ fmt(e.custo_medio) }}</td>
              <td class="col-num">R$ {{ fmt(e.valor_custo_total) }}</td>
              <td class="col-acoes">
                <button type="button" class="btn-detalhe-linha" @click="abrirDetalhe({ id_especie: e.id_especie, titulo: e.nome_popular || e.nome_cientifico })">
                  Detalhe
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

      <!-- Por idade -->
      <div v-else-if="visaoAtiva === 'idade'" :key="'idade-' + metrica" class="analitico-idade">
        <p class="tabela-guia">{{ guiaTabelaAtiva }}</p>
        <div class="faixa-grid">
          <button
            v-for="f in porIdade"
            :key="f.faixa"
            type="button"
            class="faixa-card faixa-card--click"
            :class="metrica === 'rustificacao' ? 'faixa-card--rust' : 'faixa-card--viveiro'"
            @click="abrirDetalhe({ faixa: f.faixa, titulo: f.faixa })"
          >
            <span class="faixa-card__label">{{ f.faixa }}</span>
            <strong class="faixa-card__qtd">{{ f.quantidade }}</strong>
            <span class="faixa-card__pct">{{ f.percentual }}% do estoque</span>
            <span class="faixa-card__custo">CMV R$ {{ fmt(f.valor_custo_total) }}</span>
            <div class="faixa-card__bar" aria-hidden="true">
              <div class="faixa-card__bar-fill" :style="{ width: f.percentual + '%' }" />
            </div>
            <span class="faixa-card__acao">Clique para ver muda a muda →</span>
          </button>
        </div>
      </div>

      <!-- Espécie × idade -->
      <div v-else :key="'cruz-' + metrica">
        <p class="tabela-guia">{{ guiaTabelaAtiva }}</p>
        <div class="estoque-table-card analitico-table-wrap">
        <div class="filtro-especie">
          <label>
            Filtrar espécie
            <select v-model="filtroEspecie">
              <option value="">Todas</option>
              <option v-for="e in porEspecie" :key="e.id_especie" :value="String(e.id_especie)">
                {{ e.nome_popular || e.nome_cientifico }}
              </option>
            </select>
          </label>
        </div>
        <table class="estoque-table">
          <thead>
            <tr>
              <th>Espécie</th>
              <th>Faixa ({{ metricaCurta }})</th>
              <th class="col-num">Qtd</th>
              <th class="col-num">Custo méd.</th>
              <th class="col-num">Valor CMV</th>
              <th class="col-acoes"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in cruzadaFiltrada" :key="`${row.id_especie}-${row.faixa}`">
              <td>{{ row.nome_popular || row.nome_cientifico }}</td>
              <td><span class="estoque-tag estoque-tag--info">{{ row.faixa }}</span></td>
              <td class="col-num"><strong>{{ row.quantidade }}</strong></td>
              <td class="col-num">R$ {{ fmt(row.custo_medio) }}</td>
              <td class="col-num">R$ {{ fmt(row.valor_custo_total) }}</td>
              <td class="col-acoes">
                <button
                  type="button"
                  class="btn-detalhe-linha"
                  @click="abrirDetalhe({
                    id_especie: row.id_especie,
                    faixa: row.faixa,
                    titulo: `${row.nome_popular || row.nome_cientifico} · ${row.faixa}`,
                  })"
                >
                  Detalhe
                </button>
              </td>
            </tr>
            <tr v-if="!cruzadaFiltrada.length">
              <td colspan="6" class="empty-cell">Nenhum dado para o filtro selecionado.</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </Transition>

    <!-- Modal detalhe -->
    <AppModalOverlay
      :aberto="detalheAberto"
      :handlers="overlayDetalhe"
      panel-class="app-modal-panel--xl"
      aria-labelledby="analitico-detalhe-titulo"
    >
      <div class="dialog-panel">
        <header class="app-modal-header">
          <div>
            <h3 id="analitico-detalhe-titulo">Detalhe — {{ detalheTitulo }}</h3>
            <p class="app-modal-sub">
              {{ detalhe?.total_mudas ?? 0 }} muda(s) · métrica:
              <strong>{{ metricaLabel }}</strong>
            </p>
          </div>
          <button type="button" class="app-modal-fechar" aria-label="Fechar" @click="fecharDetalhe">×</button>
        </header>

        <div class="detalhe-modos">
          <button
            type="button"
            class="modo-btn"
            :class="{ 'modo-btn--ativa': modoDetalhe === 'muda' }"
            @click="modoDetalhe = 'muda'"
          >
            Muda a muda
          </button>
          <button
            type="button"
            class="modo-btn"
            :class="{ 'modo-btn--ativa': modoDetalhe === 'lote' }"
            @click="modoDetalhe = 'lote'"
          >
            Por lote de sementes
          </button>
        </div>

        <div v-if="carregandoDetalhe" class="dialog-panel__body">
          <p class="alert alert-info">Carregando detalhe…</p>
        </div>
        <div v-else-if="erroDetalhe" class="dialog-panel__body">
          <p class="alert alert-error">{{ erroDetalhe }}</p>
        </div>
        <div v-else class="dialog-panel__body detalhe-body">
          <!-- Por lote -->
          <template v-if="modoDetalhe === 'lote'">
            <div v-if="!detalhe?.itens_lote?.length" class="empty-cell">Nenhum lote neste filtro.</div>
            <div v-for="lote in detalhe?.itens_lote || []" :key="lote.id_lote_sementes ?? lote.codigo_lote" class="lote-bloco">
              <button type="button" class="lote-bloco__head" @click="toggleLote(lote.codigo_lote)">
                <code>{{ lote.codigo_lote }}</code>
                <span>{{ lote.quantidade }} muda(s)</span>
                <span class="lote-bloco__idade">
                  {{ lote.dias_metrica_medio ?? '—' }} d ({{ lote.dias_metrica_min }}–{{ lote.dias_metrica_max }})
                </span>
                <span class="lote-bloco__cmv">CMV R$ {{ fmt(lote.valor_custo_total) }}</span>
                <span class="lote-bloco__chev">{{ loteAberto === lote.codigo_lote ? '▾' : '▸' }}</span>
              </button>
              <table v-if="loteAberto === lote.codigo_lote" class="estoque-table estoque-table--compact">
                <thead>
                  <tr>
                    <th>Rastreio</th>
                    <th>Canteiro</th>
                    <th class="col-num">Viveiro</th>
                    <th class="col-num">Rust.</th>
                    <th class="col-num">CMV</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="m in lote.plantas" :key="m.id">
                    <td><code>{{ m.codigo_rastreio || m.id }}</code></td>
                    <td>{{ m.canteiro_nome }}</td>
                    <td class="col-num">{{ m.dias_viveiro }} d</td>
                    <td class="col-num">{{ m.dias_rustificacao != null ? m.dias_rustificacao + ' d' : '—' }}</td>
                    <td class="col-num">R$ {{ fmt(m.custo_atual) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>

          <!-- Muda a muda -->
          <template v-else>
            <div class="estoque-table-card">
              <table class="estoque-table estoque-table--compact">
                <thead>
                  <tr>
                    <th>Rastreio</th>
                    <th>Espécie</th>
                    <th>Lote</th>
                    <th>Canteiro</th>
                    <th class="col-num">Viveiro</th>
                    <th class="col-num">Rust.</th>
                    <th class="col-num">CMV</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="m in detalhe?.itens_muda || []" :key="m.id">
                    <td><code>{{ m.codigo_rastreio || m.id }}</code></td>
                    <td>{{ m.nome_popular || m.nome_cientifico }}</td>
                    <td>{{ m.codigo_lote || '—' }}</td>
                    <td>{{ m.canteiro_nome }}</td>
                    <td class="col-num" :class="{ 'col-idade--ativa': metrica === 'viveiro' }">
                      {{ m.dias_viveiro }} d
                    </td>
                    <td class="col-num" :class="{ 'col-idade--ativa': metrica === 'rustificacao' }">
                      {{ m.dias_rustificacao != null ? m.dias_rustificacao + ' d' : '—' }}
                    </td>
                    <td class="col-num">R$ {{ fmt(m.custo_atual) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </div>

        <footer class="app-modal-footer">
          <button type="button" class="btn btn-secondary" @click="fecharDetalhe">Fechar</button>
        </footer>
      </div>
    </AppModalOverlay>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import { useSimpleModalClose } from '@/composables/useSimpleModalClose'
import { getAnaliticoDetalhe } from '@/services/estoques'
import './estoques-shared.css'

const props = defineProps({
  analiticoViveiro: { type: Object, default: null },
  analiticoRustificacao: { type: Object, default: null },
})

const metrica = ref('viveiro')
const visaoAtiva = ref('especie')
const filtroEspecie = ref('')

const detalheAberto = ref(false)
const detalhe = ref(null)
const detalheTitulo = ref('')
const detalheFiltro = ref({})
const carregandoDetalhe = ref(false)
const erroDetalhe = ref('')
const modoDetalhe = ref('muda')
const loteAberto = ref(null)

const visoes = [
  { id: 'especie', label: 'Por espécie' },
  { id: 'idade', label: 'Por idade' },
  { id: 'cruzada', label: 'Espécie × idade' },
]

const dadosAtivos = computed(() =>
  metrica.value === 'rustificacao' ? props.analiticoRustificacao : props.analiticoViveiro
)

const totais = computed(() => dadosAtivos.value?.totais || {})
const porEspecie = computed(() => dadosAtivos.value?.por_especie || [])
const porIdade = computed(() => dadosAtivos.value?.por_idade || [])
const especieIdade = computed(() => dadosAtivos.value?.especie_idade || [])

const metricaLabel = computed(() =>
  metrica.value === 'rustificacao' ? 'Dias na rustificação' : 'Idade no viveiro'
)
const metricaCurta = computed(() =>
  metrica.value === 'rustificacao' ? 'rust.' : 'viveiro'
)
const mediaAtiva = computed(() => {
  const t = totais.value
  if (metrica.value === 'rustificacao') return t.dias_medio_rustificacao ?? '—'
  return t.dias_medio_viveiro ?? '—'
})

const guiaTabelaAtiva = computed(() => {
  const media = mediaAtiva.value
  if (visaoAtiva.value === 'especie') {
    if (metrica.value === 'rustificacao') {
      return `Uma linha por espécie. Coluna em destaque = dias na rustificação (média do parque: ${media} d). Custo méd. = gasto acumulado por muda.`
    }
    return `Uma linha por espécie. Mudas vivas = todo o parque; Prontas venda = liberadas comercialmente. Coluna em destaque = dias desde o plantio (média: ${media} d).`
  }
  if (visaoAtiva.value === 'idade') {
    return `Mudas agrupadas por faixa de ${metrica.value === 'rustificacao' ? 'tempo na rustificação' : 'idade no viveiro'}. Clique em um card para abrir a lista muda a muda.`
  }
  return `Cada linha cruza uma espécie com uma faixa de idade. Use o filtro acima ou clique em Detalhe para ver as mudas.`
})

const cruzadaFiltrada = computed(() => {
  if (!filtroEspecie.value) return especieIdade.value
  const id = Number(filtroEspecie.value)
  return especieIdade.value.filter((r) => r.id_especie === id)
})

function setMetrica(m) {
  metrica.value = m
}

function fmt(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function fmtIdade(media, min, max) {
  if (media == null) return '—'
  return `${media} d (${min}–${max})`
}

async function abrirDetalhe(filtro = {}) {
  detalheFiltro.value = filtro
  detalheTitulo.value = filtro.titulo || 'Todas as mudas vivas'
  modoDetalhe.value = 'muda'
  loteAberto.value = null
  erroDetalhe.value = ''
  detalheAberto.value = true
  await carregarDetalhe()
}

async function carregarDetalhe() {
  carregandoDetalhe.value = true
  erroDetalhe.value = ''
  try {
    const params = {
      metrica_idade: metrica.value,
      agrupar: modoDetalhe.value === 'lote' ? 'lote' : 'muda',
    }
    if (detalheFiltro.value.id_especie) params.id_especie = detalheFiltro.value.id_especie
    if (detalheFiltro.value.faixa) params.faixa = detalheFiltro.value.faixa
    detalhe.value = await getAnaliticoDetalhe(params)
  } catch (e) {
    erroDetalhe.value = e.response?.data?.detail || 'Erro ao carregar detalhe.'
    detalhe.value = null
  } finally {
    carregandoDetalhe.value = false
  }
}

watch(modoDetalhe, () => {
  if (detalheAberto.value) carregarDetalhe()
})

function fecharDetalheInterno() {
  detalheAberto.value = false
}

const overlayDetalhe = useSimpleModalClose(fecharDetalheInterno, () => detalheAberto.value)

function fecharDetalhe() {
  overlayDetalhe.resetOverlayPress()
  fecharDetalheInterno()
}

function toggleLote(codigo) {
  loteAberto.value = loteAberto.value === codigo ? null : codigo
}
</script>

<style scoped>
.analitico-panel {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-subtle);
}

.analitico-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.analitico-toolbar__titulo {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.tabela-guia {
  margin: 0 0 var(--spacing-sm);
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-text-secondary);
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-primary);
}

.analitico-panel--rust .tabela-guia {
  border-left-color: #e6a817;
}

.analitico-metrica {
  display: flex;
  gap: 0.5rem;
  padding: 0.35rem;
  border-radius: var(--radius-lg);
  border: 2px solid var(--color-border-subtle);
  background: var(--color-surface);
}

.metrica-btn {
  border: 2px solid transparent;
  background: var(--color-surface-muted);
  padding: 0.55rem 1rem;
  font-size: 0.875rem;
  font-weight: 700;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-secondary);
  font-family: inherit;
  transition: all 0.2s;
}

.metrica-btn--viveiro.metrica-btn--ativa {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary);
  color: var(--color-primary-800, var(--color-primary-700));
  box-shadow: 0 0 0 3px rgba(76, 120, 80, 0.15);
}

.metrica-btn--rust.metrica-btn--ativa {
  background: #fff8e6;
  border-color: #e6a817;
  color: #7a5a00;
  box-shadow: 0 0 0 3px rgba(230, 168, 23, 0.2);
}

.metrica-fade-enter-active,
.metrica-fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.metrica-fade-enter-from,
.metrica-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

.col-idade {
  opacity: 0.45;
  transition: opacity 0.2s, background 0.2s;
}

.col-idade--ativa {
  opacity: 1;
  background: rgba(76, 120, 80, 0.08);
  font-weight: 700;
}

.analitico-panel--rust :deep(.col-idade--ativa) {
  background: rgba(230, 168, 23, 0.12);
}

.analitico-table-wrap {
  border-left: 4px solid var(--color-primary);
}

.analitico-panel--rust .analitico-table-wrap {
  border-left-color: #e6a817;
}

.faixa-card--click {
  cursor: pointer;
  text-align: left;
  width: 100%;
  font-family: inherit;
  transition: transform 0.15s, box-shadow 0.15s;
}

.faixa-card--click:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.faixa-card--viveiro {
  border-color: var(--color-primary-100);
}

.faixa-card--rust {
  border-color: #e6a817;
  background: #fffdf8;
}

.faixa-card__acao {
  font-size: 0.6875rem;
  color: var(--color-primary-700);
  margin-top: 0.25rem;
}

.btn-detalhe-linha,
.btn-detalhe-tudo {
  padding: 0.3rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid var(--color-primary);
  background: transparent;
  color: var(--color-primary-700);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: inherit;
}

.btn-detalhe-tudo {
  margin-left: auto;
  align-self: center;
  margin-bottom: -1px;
}

.visao-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border-subtle);
  align-items: flex-end;
}


.visao-tab {
  border: none;
  background: transparent;
  padding: 0.5rem 0.85rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  font-family: inherit;
}

.visao-tab--ativa {
  color: var(--color-primary-700);
  border-bottom-color: var(--color-primary);
}

.faixa-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
  gap: var(--spacing-md);
}

.faixa-card {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  background: var(--color-surface-muted);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.faixa-card__label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.faixa-card__qtd {
  font-size: 1.5rem;
  color: var(--color-primary-700);
}

.faixa-card__pct,
.faixa-card__custo {
  font-size: 0.75rem;
}

.faixa-card__bar {
  height: 4px;
  background: var(--color-border-subtle);
  border-radius: 2px;
  margin-top: 0.35rem;
  overflow: hidden;
}

.faixa-card__bar-fill {
  height: 100%;
  background: var(--color-primary);
  min-width: 2px;
}

.faixa-card--rust .faixa-card__bar-fill {
  background: #e6a817;
}

.filtro-especie {
  padding: 0.65rem 0.85rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.empty-cell {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--spacing-lg);
}

.detalhe-modos {
  display: flex;
  gap: 0.35rem;
  padding: 0 var(--spacing-lg);
  margin-bottom: var(--spacing-sm);
}

.modo-btn {
  border: 2px solid var(--color-border-subtle);
  background: var(--color-surface-muted);
  padding: 0.4rem 0.85rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: inherit;
}

.modo-btn--ativa {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
  color: var(--color-primary-700);
}

.detalhe-body {
  max-height: 60vh;
  overflow: auto;
}

.lote-bloco {
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-sm);
  overflow: hidden;
}

.lote-bloco__head {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 1rem;
  padding: 0.65rem 0.85rem;
  border: none;
  background: var(--color-surface-muted);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.8125rem;
  text-align: left;
}

.lote-bloco__chev {
  margin-left: auto;
  color: var(--color-text-muted);
}

.estoque-table--compact {
  font-size: 0.8125rem;
}

.estoque-table--compact th,
.estoque-table--compact td {
  padding: 0.35rem 0.5rem;
}
</style>
