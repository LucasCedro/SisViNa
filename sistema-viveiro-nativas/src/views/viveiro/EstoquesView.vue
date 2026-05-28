<template>
  <PageLayout>
    <header class="estoque-page-header">
      <div>
        <h1 class="estoque-page-header__titulo">Estoques</h1>
        <p class="page-lead">
          Sementes, insumos com custo (CMV) e mudas por estágio — do desenvolvimento até a venda após
          rustificação.
        </p>
      </div>
      <div class="estoque-page-header__acoes">
        <button
          type="button"
          class="btn btn-secondary"
          :disabled="carregando"
          @click="carregar"
        >
          {{ carregando ? 'Atualizando…' : 'Atualizar' }}
        </button>
      </div>
    </header>

    <p v-if="carregando && !resumo" class="alert alert-info">Carregando resumo de estoques…</p>
    <p v-else-if="erroPagina" class="alert alert-error">
      {{ erroPagina }}
      <button type="button" class="btn btn-outline btn-sm" style="margin-left: 0.5rem" @click="carregar">
        Tentar novamente
      </button>
    </p>

    <template v-else-if="resumo">
      <EstoqueFluxoBar :resumo="resumo" :guia-ativa="guiaAtiva" @ir-guia="guiaAtiva = $event" />

      <nav class="guias-navegacao estoque-guias" aria-label="Seções de estoque">
        <button
          v-for="g in guias"
          :key="g.id"
          type="button"
          class="guia"
          :class="{ ativa: guiaAtiva === g.id }"
          @click="guiaAtiva = g.id"
        >
          {{ g.label }}
          <span v-if="g.badge != null" class="guia-badge">{{ g.badge }}</span>
        </button>
      </nav>

      <!-- Mudas -->
      <PageSection v-show="guiaAtiva === 'mudas'">
        <template #header>
          <div class="secao-titulo-wrap">
            <h2 class="secao-titulo">Mudas — estoque comercial</h2>
            <p class="secao-sub">Prontas para venda após rustificação (referência Embrapa)</p>
          </div>
        </template>
        <EstoqueComercialPanel
          :items="resumo.estoque_comercial"
          :pipeline="resumo.mudas_pipeline"
          @atualizado="carregar"
        />
      </PageSection>

      <!-- Sementes -->
      <PageSection v-show="guiaAtiva === 'sementes'">
        <template #header>
          <div class="secao-header-flex">
            <div>
              <h2 class="secao-titulo">Sementes no armazém</h2>
              <p class="secao-sub">Lotes ativos com saldo disponível</p>
            </div>
            <button type="button" class="btn btn-primary" @click="modalEntrada = true">
              + Entrada no armazém
            </button>
          </div>
        </template>

        <div v-if="!resumo.lotes_sementes?.length" class="estoque-empty">
          <p class="estoque-empty__titulo">Nenhum lote com saldo</p>
          <p class="estoque-empty__texto">
            Registre entrada de sementes (compra, armazém ou ajuste) ou forme lotes a partir da coleta.
          </p>
          <div class="estoque-empty__acoes">
            <button type="button" class="btn btn-primary" @click="modalEntrada = true">
              Registrar entrada
            </button>
            <router-link to="/coleta" class="btn btn-outline">Módulo Coleta</router-link>
          </div>
        </div>
        <div v-else class="estoque-table-card">
          <table class="estoque-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Origem</th>
                <th>Espécie</th>
                <th>Matriz</th>
                <th class="col-num">Disponível</th>
                <th>Armazenamento</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="l in resumo.lotes_sementes" :key="l.id">
                <td><code>{{ l.codigo_lote }}</code></td>
                <td><span class="estoque-tag estoque-tag--info">{{ l.origem_lote }}</span></td>
                <td>{{ l.especie_nome || '—' }}</td>
                <td>{{ l.matriz_nome || '—' }}</td>
                <td class="col-num">
                  <strong>{{ l.quantidade_disponivel }}</strong>
                  <span class="text-muted"> / {{ l.quantidade_inicial }}</span>
                </td>
                <td>{{ l.condicoes_armazenamento || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </PageSection>

      <!-- Insumos -->
      <PageSection v-show="guiaAtiva === 'insumos'">
        <template #header>
          <div>
            <h2 class="secao-titulo">Insumos e substratos</h2>
            <p class="secao-sub">
              Valor total em estoque: <strong>R$ {{ formatMoeda(resumo.valor_total_insumos) }}</strong>
              — entradas com valor pago atualizam o preço médio (CMV)
            </p>
          </div>
        </template>

        <p class="estoque-info-box">
          Use <strong>Entrada</strong> ao comprar (informe quantidade e valor total pago). Use
          <strong>Saída</strong> para consumo ou perda. Alertas exigem limites mín/máx no cadastro do insumo.
        </p>

        <div v-if="!resumo.insumos?.length" class="estoque-empty">
          <p class="estoque-empty__titulo">Nenhum insumo cadastrado</p>
          <p class="estoque-empty__texto">Cadastre NPK, substrato, combustível e demais itens no módulo de insumos.</p>
        </div>
        <div v-else class="estoque-table-card">
          <table class="estoque-table">
            <thead>
              <tr>
                <th>Insumo</th>
                <th>Tipo</th>
                <th class="col-num">Estoque</th>
                <th class="col-num">Preço médio</th>
                <th class="col-num">Valor total</th>
                <th>Situação</th>
                <th class="col-acoes">Movimentação</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="i in resumo.insumos"
                :key="i.id"
                :class="{
                  'estoque-linha--alerta': i.alerta_estoque === 'abaixo_minimo',
                  'estoque-linha--max': i.alerta_estoque === 'acima_maximo',
                }"
              >
                <td>
                  <span class="estoque-especie">{{ i.nome }}</span>
                  <span class="estoque-especie-cient">{{ i.unidade_medida || 'unidade' }}</span>
                  <div
                    v-if="i.estoque_maximo && i.estoque_maximo > 0"
                    class="estoque-saldo-bar"
                    :title="`Mín: ${i.estoque_minimo} · Máx: ${i.estoque_maximo}`"
                  >
                    <div
                      class="estoque-saldo-bar__fill"
                      :class="barraClasse(i)"
                      :style="{ width: barraPct(i) + '%' }"
                    />
                  </div>
                </td>
                <td>{{ i.tipo }}</td>
                <td class="col-num">
                  <span class="estoque-qtd-destaque">{{ i.quantidade_estoque }}</span>
                </td>
                <td class="col-num">
                  {{
                    i.preco_unitario != null
                      ? `R$ ${Number(i.preco_unitario).toFixed(2)}`
                      : '—'
                  }}
                </td>
                <td class="col-num">R$ {{ formatMoeda(i.valor_estoque) }}</td>
                <td>
                  <span v-if="i.alerta_estoque === 'abaixo_minimo'" class="estoque-tag estoque-tag--warn">
                    Abaixo do mínimo
                  </span>
                  <span v-else-if="i.alerta_estoque === 'acima_maximo'" class="estoque-tag estoque-tag--max">
                    Acima do máximo
                  </span>
                  <span v-else class="estoque-tag estoque-tag--ok">Normal</span>
                </td>
                <td class="col-acoes">
                  <div class="estoque-acoes-grupo">
                    <button type="button" class="btn btn-primary btn-sm" @click="abrirMov(i, 'entrada')">
                      Entrada
                    </button>
                    <button
                      type="button"
                      class="btn btn-secondary btn-sm"
                      :disabled="!i.quantidade_estoque"
                      @click="abrirMov(i, 'saida')"
                    >
                      Saída
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </PageSection>

      <!-- Locais -->
      <PageSection v-show="guiaAtiva === 'locais'">
        <template #header>
          <div>
            <h2 class="secao-titulo">Locais do viveiro</h2>
            <p class="secao-sub">Classifique cada área para o fluxo de produção e estoque</p>
          </div>
        </template>

        <p class="estoque-info-box">
          O tipo do local define onde as mudas entram no pipeline: sementeira → canteiro → rustificação.
          Armazém é para sementes secas.
        </p>

        <div v-if="!locais.length" class="estoque-empty">
          <p class="estoque-empty__titulo">Nenhum local cadastrado</p>
        </div>
        <div v-else class="estoque-table-card">
          <table class="estoque-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Tipo do local</th>
                <th class="col-acoes"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in locais" :key="c.id">
                <td class="estoque-especie">{{ c.nome }}</td>
                <td>
                  <select v-model="c.tipo_local" class="estoque-select-inline">
                    <option value="sementeira">Sementeira</option>
                    <option value="canteiro">Canteiro de mudas</option>
                    <option value="rustificacao">Rustificação</option>
                    <option value="armazem">Armazém de sementes</option>
                  </select>
                </td>
                <td class="col-acoes">
                  <button type="button" class="btn btn-outline btn-sm" @click="salvarLocal(c)">
                    Salvar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </PageSection>
    </template>

    <!-- Modal sementes -->
    <div v-if="modalEntrada" class="estoque-modal-overlay" @click.self="modalEntrada = false">
      <div class="estoque-modal" role="dialog" aria-labelledby="modal-sementes-titulo">
        <header class="estoque-modal__header">
          <h3 id="modal-sementes-titulo">Entrada de sementes</h3>
          <p>Compra ou estoque guardado — sem vínculo obrigatório com coleta.</p>
        </header>
        <form class="estoque-modal__body estoque-form-grid" @submit.prevent="salvarEntrada">
          <label class="form-label">
            Espécie
            <select v-model.number="formEntrada.id_especie" class="form-input" required>
              <option v-for="e in especies" :key="e.id" :value="e.id">
                {{ e.nome_popular || e.nome_cientifico }}
              </option>
            </select>
          </label>
          <label class="form-label">
            Quantidade
            <input v-model.number="formEntrada.quantidade" class="form-input" type="number" min="1" required />
          </label>
          <label class="form-label">
            Origem do lote
            <select v-model="formEntrada.origem_lote" class="form-input">
              <option value="armazem">Armazém</option>
              <option value="compra">Compra</option>
              <option value="ajuste">Ajuste / inventário</option>
            </select>
          </label>
          <label class="form-label">
            Condições de armazenamento
            <input v-model="formEntrada.condicoes_armazenamento" class="form-input" type="text" />
          </label>
          <label class="form-label">
            Observações
            <textarea v-model="formEntrada.observacoes" class="form-input" rows="2" />
          </label>
          <p v-if="erroModal" class="alert alert-error">{{ erroModal }}</p>
        </form>
        <footer class="estoque-modal__footer">
          <button type="button" class="btn btn-secondary" @click="modalEntrada = false">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="salvando" @click="salvarEntrada">
            {{ salvando ? 'Salvando…' : 'Registrar entrada' }}
          </button>
        </footer>
      </div>
    </div>

    <!-- Modal insumo -->
    <div v-if="modalMov" class="estoque-modal-overlay" @click.self="fecharMov">
      <div class="estoque-modal" role="dialog">
        <header class="estoque-modal__header">
          <h3>{{ formMov.tipo === 'entrada' ? 'Entrada de insumo' : 'Saída de insumo' }}</h3>
          <p>{{ insumoSelecionado?.nome }} · saldo atual {{ insumoSelecionado?.quantidade_estoque }} {{ insumoSelecionado?.unidade_medida || 'un.' }}</p>
        </header>
        <form class="estoque-modal__body estoque-form-grid" @submit.prevent="salvarMov">
          <label class="form-label">
            Quantidade ({{ insumoSelecionado?.unidade_medida || 'un.' }})
            <input
              v-model.number="formMov.quantidade"
              class="form-input"
              type="number"
              min="0.01"
              step="0.01"
              required
            />
          </label>
          <label v-if="formMov.tipo === 'entrada'" class="form-label">
            Valor total pago (R$)
            <input
              v-model.number="formMov.valor_total"
              class="form-input"
              type="number"
              min="0"
              step="0.01"
              placeholder="Ex.: 1000,00"
            />
            <span class="field-hint">Atualiza o preço médio (CMV) do estoque</span>
          </label>
          <label class="form-label">
            Data da movimentação
            <input v-model="formMov.data_movimento" class="form-input" type="date" required />
          </label>
          <label class="form-label">
            Observação (opcional)
            <input v-model="formMov.observacao" class="form-input" type="text" />
          </label>
          <p v-if="erroModal" class="alert alert-error">{{ erroModal }}</p>
        </form>
        <footer class="estoque-modal__footer">
          <button type="button" class="btn btn-secondary" @click="fecharMov">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="salvando" @click="salvarMov">
            {{ salvando ? 'Salvando…' : 'Confirmar' }}
          </button>
        </footer>
      </div>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PageLayout from '@/components/layout/PageLayout.vue'
import PageSection from '@/components/layout/PageSection.vue'
import EstoqueComercialPanel from '@/components/estoques/EstoqueComercialPanel.vue'
import EstoqueFluxoBar from '@/components/estoques/EstoqueFluxoBar.vue'
import { getResumoEstoques, entradaSementesArmazem, registrarMovimentacaoInsumo } from '@/services/estoques'
import { listEspecies } from '@/services/especies'
import { listCanteiros, updateCanteiro } from '@/services/canteiros'
import '@/components/estoques/estoques-shared.css'

const resumo = ref(null)
const locais = ref([])
const especies = ref([])
const guiaAtiva = ref('mudas')
const carregando = ref(true)
const erroPagina = ref('')
const modalEntrada = ref(false)
const modalMov = ref(false)
const salvando = ref(false)
const erroModal = ref('')
const insumoSelecionado = ref(null)

const formEntrada = ref({
  id_especie: null,
  quantidade: 100,
  origem_lote: 'armazem',
  condicoes_armazenamento: '',
  observacoes: '',
})

const formMov = ref({
  tipo: 'entrada',
  quantidade: 1,
  valor_total: null,
  data_movimento: new Date().toISOString().slice(0, 10),
  observacao: '',
})

const guias = computed(() => {
  const r = resumo.value
  const alertas = (r?.insumos || []).filter((i) => i.alerta_estoque).length
  return [
    { id: 'mudas', label: 'Mudas', badge: r?.total_mudas_aptas_venda || null },
    { id: 'sementes', label: 'Sementes', badge: r?.total_lotes_sementes_ativos || null },
    { id: 'insumos', label: 'Insumos', badge: alertas > 0 ? alertas : r?.total_insumos || null },
    { id: 'locais', label: 'Locais', badge: locais.value.length || null },
  ]
})

function formatMoeda(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function barraPct(i) {
  const max = Number(i.estoque_maximo) || 0
  if (max <= 0) return 0
  return Math.min(100, (Number(i.quantidade_estoque) / max) * 100)
}

function barraClasse(i) {
  if (i.alerta_estoque === 'abaixo_minimo') return 'estoque-saldo-bar__fill--danger'
  if (i.alerta_estoque === 'acima_maximo') return 'estoque-saldo-bar__fill--warn'
  const pct = barraPct(i)
  if (pct < 30) return 'estoque-saldo-bar__fill--warn'
  return ''
}

async function carregar() {
  carregando.value = true
  erroPagina.value = ''
  try {
    resumo.value = await getResumoEstoques()
  } catch (e) {
    erroPagina.value =
      e.response?.data?.detail || 'Não foi possível carregar o resumo de estoques.'
    resumo.value = null
  } finally {
    carregando.value = false
  }
}

onMounted(async () => {
  try {
    especies.value = await listEspecies()
    if (especies.value.length) formEntrada.value.id_especie = especies.value[0].id
    locais.value = await listCanteiros({ ativo: true, limit: 200 })
  } catch {
    /* secundário */
  }
  await carregar()
})

async function salvarLocal(c) {
  await updateCanteiro(c.id, { tipo_local: c.tipo_local })
  await carregar()
}

async function salvarEntrada() {
  erroModal.value = ''
  salvando.value = true
  try {
    await entradaSementesArmazem(formEntrada.value)
    modalEntrada.value = false
    guiaAtiva.value = 'sementes'
    await carregar()
  } catch (e) {
    erroModal.value = e.response?.data?.detail || 'Erro ao registrar entrada.'
  } finally {
    salvando.value = false
  }
}

function abrirMov(insumo, tipo) {
  insumoSelecionado.value = insumo
  formMov.value = {
    tipo,
    quantidade: 1,
    valor_total: null,
    data_movimento: new Date().toISOString().slice(0, 10),
    observacao: '',
  }
  erroModal.value = ''
  modalMov.value = true
}

function fecharMov() {
  modalMov.value = false
  insumoSelecionado.value = null
}

async function salvarMov() {
  erroModal.value = ''
  salvando.value = true
  try {
    const payload = {
      tipo: formMov.value.tipo,
      quantidade: formMov.value.quantidade,
      data_movimento: formMov.value.data_movimento,
      observacao: formMov.value.observacao || undefined,
    }
    if (formMov.value.tipo === 'entrada' && formMov.value.valor_total != null) {
      payload.valor_total = formMov.value.valor_total
    }
    await registrarMovimentacaoInsumo(insumoSelecionado.value.id, payload)
    fecharMov()
    await carregar()
  } catch (e) {
    const d = e.response?.data?.detail
    erroModal.value = typeof d === 'string' ? d : 'Erro na movimentação.'
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.secao-titulo-wrap,
.secao-header-flex {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
  width: 100%;
}

.secao-titulo {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.secao-sub {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.guia-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.25rem;
  height: 1.25rem;
  padding: 0 0.35rem;
  margin-left: 0.35rem;
  font-size: 0.6875rem;
  font-weight: 700;
  background: var(--color-primary-subtle);
  color: var(--color-primary-700);
  border-radius: var(--radius-full);
}

.guia.ativa .guia-badge {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.text-muted {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  font-weight: 400;
}

.field-hint {
  font-size: 0.8125rem;
  font-weight: 400;
  color: var(--color-text-muted);
}

code {
  font-size: 0.8125rem;
  color: var(--color-primary-700);
  background: var(--color-primary-subtle);
  padding: 0.15rem 0.4rem;
  border-radius: var(--radius-sm);
}
</style>
