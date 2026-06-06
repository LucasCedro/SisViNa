<template>
  <PageLayout>
    <header class="estoque-page-header">
      <div>
        <p class="page-lead">
          Sementes, insumos (média móvel), mudas por custo acumulado — do desenvolvimento à comercialização.
          <template v-if="resumo">
            CMV mudas vivas: <strong>R$ {{ formatMoeda(resumo.valor_total_mudas) }}</strong>
            · comercial: <strong>R$ {{ formatMoeda(resumo.valor_mudas_comercial) }}</strong>
            · sementes: <strong>R$ {{ formatMoeda(resumo.valor_total_sementes) }}</strong>
          </template>
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
            <p class="secao-sub">Aptas para venda na área de rustificação</p>
          </div>
        </template>
        <EstoqueComercialPanel
          :items="resumo.estoque_comercial"
          :pipeline="resumo.mudas_pipeline"
          @atualizado="carregar"
        />
        <EstoqueTimelinePanel :timeline-inicial="resumo.timeline_especies" />
        <details class="estoque-detalhes-extra">
          <summary>Detalhes tabulares (idade, CMV, muda a muda)</summary>
          <EstoqueAnaliticoPanel
            :analitico-viveiro="resumo.analitico_mudas"
            :analitico-rustificacao="resumo.analitico_mudas_rustificacao"
            :cmv="resumo.cmv_integridade"
          />
        </details>
      </PageSection>

      <!-- Sementes -->
      <PageSection v-show="guiaAtiva === 'sementes'">
        <template #header>
          <div class="secao-header-flex">
            <div>
              <h2 class="secao-titulo">Sementes no armazém</h2>
              <p class="secao-sub">
                {{ resumo.total_lotes_sementes_ativos }} lote(s) ·
                {{ resumo.total_sementes_disponiveis }} sementes ·
                valor CMV: <strong>R$ {{ formatMoeda(resumo.valor_total_sementes) }}</strong>
              </p>
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
                <th class="col-num">Consumido</th>
                <th class="col-num">Dias armaz.</th>
                <th class="col-num">Valor lote</th>
                <th class="col-num">Custo/un.</th>
                <th class="col-num">Germ. %</th>
                <th>Formação / coleta</th>
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
                <td class="col-num">
                  {{ l.percentual_consumido != null ? l.percentual_consumido + '%' : '—' }}
                </td>
                <td class="col-num">{{ l.dias_armazenamento ?? '—' }}</td>
                <td class="col-num">{{ l.valor_total != null ? 'R$ ' + formatMoeda(l.valor_total) : '—' }}</td>
                <td class="col-num">{{ l.custo_unitario != null ? 'R$ ' + Number(l.custo_unitario).toFixed(4) : '—' }}</td>
                <td class="col-num">
                  {{ l.ultimo_teste_germinacao != null ? l.ultimo_teste_germinacao + '%' : '—' }}
                </td>
                <td>
                  <span class="text-muted">{{ l.data_formacao_lote || '—' }}</span>
                  <span v-if="l.data_coleta" class="text-muted"> · coleta {{ l.data_coleta }}</span>
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
          <div class="secao-header-flex">
            <div>
              <h2 class="secao-titulo">Insumos e substratos</h2>
              <p class="secao-sub">
                Valor total: <strong>R$ {{ formatMoeda(resumo.valor_total_insumos) }}</strong>
                — registre compras com quantidade e valor pago (preço médio automático)
              </p>
            </div>
            <button type="button" class="btn btn-primary" @click="abrirCadastroInsumo">
              + Cadastrar insumo
            </button>
          </div>
        </template>

        <p class="estoque-info-box">
          <strong>Onde dar entrada:</strong> aba <strong>Insumos</strong> → botão
          <strong>Entrada</strong> na linha do item (ou cadastre um insumo primeiro).
          Informe quantidade comprada e valor total pago — o sistema atualiza o preço médio.
        </p>

        <div v-if="!resumo.insumos?.length" class="estoque-empty">
          <p class="estoque-empty__titulo">Nenhum insumo cadastrado</p>
          <p class="estoque-empty__texto">
            Cadastre substrato, NPK, embalagens etc. Depois use <strong>Entrada</strong> para registrar compras.
          </p>
          <button type="button" class="btn btn-primary" @click="abrirCadastroInsumo">
            Cadastrar primeiro insumo
          </button>
        </div>
        <div v-else class="estoque-table-card">
          <table class="estoque-table">
            <thead>
              <tr>
                <th>Insumo</th>
                <th>Tipo</th>
                <th class="col-num">Estoque</th>
                <th class="col-num">Preço médio</th>
                <th class="col-num">Valor CMV</th>
                <th>Fornecedor</th>
                <th>Última mov.</th>
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
                  <span v-if="i.descricao" class="text-muted insumo-desc">{{ i.descricao }}</span>
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
                <td>{{ i.fornecedor || '—' }}</td>
                <td>
                  <span v-if="i.ultima_movimentacao">{{ i.ultima_movimentacao }}</span>
                  <span v-else class="text-muted">—</span>
                  <span v-if="i.qtd_movimentacoes" class="text-muted"> ({{ i.qtd_movimentacoes }} mov.)</span>
                </td>
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
    </template>

    <!-- Modal cadastro insumo -->
    <div v-if="modalCadastroInsumo" class="estoque-modal-overlay" @click.self="modalCadastroInsumo = false">
      <div class="estoque-modal" role="dialog">
        <header class="estoque-modal__header">
          <h3>Cadastrar insumo</h3>
          <p>Ex.: Substrato, NPK 10-10-10, tubete</p>
        </header>
        <form class="estoque-modal__body estoque-form-grid" @submit.prevent="salvarCadastroInsumo">
          <label class="form-label">
            Nome
            <input v-model="formInsumo.nome" class="form-input" required type="text" />
          </label>
          <label class="form-label">
            Tipo
            <select v-model="formInsumo.tipo" class="form-input">
              <option value="Substrato">Substrato</option>
              <option value="Hidrogel">Hidrogel</option>
              <option value="Fertilizante">Fertilizante</option>
              <option value="Embalagem">Embalagem</option>
              <option value="Defensivo">Defensivo</option>
              <option value="Outro">Outro</option>
            </select>
          </label>
          <label class="form-label">
            Unidade de medida
            <input v-model="formInsumo.unidade_medida" class="form-input" placeholder="kg, L, un, saco…" />
          </label>
          <label class="form-label">
            Entrada inicial — quantidade
            <input v-model.number="formInsumo.quantidade_inicial" class="form-input" type="number" min="0" step="0.01" />
          </label>
          <label class="form-label">
            Valor total pago na compra (R$)
            <input v-model.number="formInsumo.valor_compra" class="form-input" type="number" min="0" step="0.01" />
          </label>
          <p v-if="erroModal" class="alert alert-error">{{ erroModal }}</p>
        </form>
        <footer class="estoque-modal__footer">
          <button type="button" class="btn btn-secondary" @click="modalCadastroInsumo = false">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="salvando" @click="salvarCadastroInsumo">
            {{ salvando ? 'Salvando…' : 'Cadastrar' }}
          </button>
        </footer>
      </div>
    </div>

    <!-- Modal sementes -->
    <div v-if="modalEntrada" class="estoque-modal-overlay" @click.self="modalEntrada = false">
      <div class="estoque-modal" role="dialog" aria-labelledby="modal-sementes-titulo">
        <header class="estoque-modal__header">
          <h3 id="modal-sementes-titulo">Entrada de sementes</h3>
          <p>Compra ou estoque guardado</p>
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
            Valor total pago (R$) — compra do lote
            <input v-model.number="formEntrada.valor_total" class="form-input" type="number" min="0" step="0.01" />
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
import EstoqueTimelinePanel from '@/components/estoques/EstoqueTimelinePanel.vue'
import EstoqueAnaliticoPanel from '@/components/estoques/EstoqueAnaliticoPanel.vue'
import EstoqueFluxoBar from '@/components/estoques/EstoqueFluxoBar.vue'
import { getResumoEstoques, entradaSementesArmazem, registrarMovimentacaoInsumo } from '@/services/estoques'
import { createInsumo } from '@/services/insumos'
import { listEspecies } from '@/services/especies'
import '@/components/estoques/estoques-shared.css'

const resumo = ref(null)
const especies = ref([])
const guiaAtiva = ref('mudas')
const carregando = ref(true)
const erroPagina = ref('')
const modalEntrada = ref(false)
const modalMov = ref(false)
const modalCadastroInsumo = ref(false)
const salvando = ref(false)
const erroModal = ref('')
const insumoSelecionado = ref(null)

const formInsumo = ref({
  nome: '',
  tipo: 'Substrato',
  unidade_medida: 'kg',
  quantidade_inicial: null,
  valor_compra: null,
})

const formEntrada = ref({
  id_especie: null,
  quantidade: 100,
  valor_total: null,
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
  } catch {
    /* secundário */
  }
  await carregar()
})

function abrirCadastroInsumo() {
  formInsumo.value = {
    nome: '',
    tipo: 'Substrato',
    unidade_medida: 'kg',
    quantidade_inicial: null,
    valor_compra: null,
  }
  erroModal.value = ''
  modalCadastroInsumo.value = true
}

async function salvarCadastroInsumo() {
  erroModal.value = ''
  salvando.value = true
  try {
    const ins = await createInsumo({
      nome: formInsumo.value.nome,
      tipo: formInsumo.value.tipo,
      unidade_medida: formInsumo.value.unidade_medida,
      quantidade_estoque: 0,
    })
    if (formInsumo.value.quantidade_inicial > 0) {
      await registrarMovimentacaoInsumo(ins.id, {
        tipo: 'entrada',
        quantidade: formInsumo.value.quantidade_inicial,
        valor_total: formInsumo.value.valor_compra || undefined,
        data_movimento: new Date().toISOString().slice(0, 10),
        observacao: 'Entrada inicial',
      })
    }
    modalCadastroInsumo.value = false
    guiaAtiva.value = 'insumos'
    await carregar()
  } catch (e) {
    erroModal.value = e.response?.data?.detail || 'Erro ao cadastrar insumo.'
  } finally {
    salvando.value = false
  }
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

.insumo-desc {
  display: block;
  font-size: 0.75rem;
  margin-top: 0.15rem;
}

code {
  font-size: 0.8125rem;
  color: var(--color-primary-700);
  background: var(--color-primary-subtle);
  padding: 0.15rem 0.4rem;
  border-radius: var(--radius-sm);
}

.estoque-detalhes-extra {
  margin-top: var(--spacing-lg);
}

.estoque-detalhes-extra summary {
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  padding: var(--spacing-sm) 0;
}

.estoque-detalhes-extra[open] summary {
  margin-bottom: var(--spacing-md);
  color: var(--color-primary-700);
}
</style>
