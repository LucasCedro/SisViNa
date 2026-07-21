<template>
  <div class="painel-lote">
    <div v-if="filtroLocais?.length" class="toolbar">
      <label class="field field--sm">
        {{ filtroLocalLabel || 'Local' }}
        <select v-model="filtroCanteiro" @change="carregarResumo">
          <option value="">Todos</option>
          <option v-for="c in filtroLocais" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
      </label>
      <label v-if="mostrarBusca" class="field field--sm">
        {{ PRODUCAO_ACOES_LOTE.filtrarEspecie }}
        <input v-model="busca" type="search" placeholder="Nome da espécie…" />
      </label>
      <div class="toolbar-actions">
        <button type="button" class="btn btn-outline btn-sm" @click="marcarTodos">
          {{ PRODUCAO_ACOES_LOTE.marcarTodos }}
        </button>
        <button type="button" class="btn btn-outline btn-sm" @click="usarDisponivel">
          {{ PRODUCAO_ACOES_LOTE.preencherDisponivel }}
        </button>
        <button type="button" class="btn btn-outline btn-sm" @click="limpar">
          {{ PRODUCAO_ACOES_LOTE.limpar }}
        </button>
      </div>
    </div>

    <div v-if="camposExtras" class="form-card form-card--inline">
      <slot name="campos" />
    </div>

    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-check">
              <input
                type="checkbox"
                :checked="todosMarcados"
                :disabled="!podeOperar || !gruposVisiveis.length"
                @change="toggleTodos"
              />
            </th>
            <th>Espécie</th>
            <th>Local</th>
            <th class="col-num">Disponível</th>
            <th class="col-num">Quantidade</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="carregando">
            <td colspan="5" class="empty-cell">Carregando resumo…</td>
          </tr>
          <tr v-else-if="!gruposVisiveis.length">
            <td colspan="5" class="empty-cell">{{ vazio }}</td>
          </tr>
          <tr
            v-for="g in gruposVisiveis"
            :key="chaveGrupo(g)"
            :class="{ 'row--ativo': linhas[chaveGrupo(g)]?.ativo }"
          >
            <td>
              <input
                v-model="linhas[chaveGrupo(g)].ativo"
                type="checkbox"
                :disabled="!podeOperar"
                @change="aoMarcar(g)"
              />
            </td>
            <td>{{ g.especie_nome }}</td>
            <td>{{ g.nome_canteiro || '—' }}</td>
            <td class="col-num">{{ g.disponivel.toLocaleString('pt-BR') }}</td>
            <td class="col-num">
              <input
                v-model.number="linhas[chaveGrupo(g)].quantidade"
                type="number"
                class="input-qtd"
                min="0"
                :max="g.disponivel"
                :disabled="!linhas[chaveGrupo(g)]?.ativo || !podeOperar"
                @input="validarQtd(g)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <footer class="lote-resumo">
      <div class="lote-resumo__nums">
        <span>{{ PRODUCAO_RESUMO.especies(resumo.especies) }}</span>
        <span>{{ PRODUCAO_RESUMO.mudas(resumo.total) }}</span>
      </div>
      <p v-if="erro" class="alert alert-error">{{ erro }}</p>
      <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>
      <button
        type="button"
        class="btn btn-primary"
        :disabled="processando || !podeOperar || !resumo.especies"
        @click="executar"
      >
        {{ tituloBotao }} — {{ PRODUCAO_RESUMO.mudas(resumo.total) }}
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { getResumoOperacaoLote } from '@/services/plantas'
import { PRODUCAO_ACOES_LOTE, PRODUCAO_RESUMO } from '@/constants/producaoUi'
import { useGlobalLoading } from '@/composables/useGlobalLoading'

const { runWithLoading } = useGlobalLoading()

const props = defineProps({
  etapa: { type: String, required: true },
  tituloBotao: { type: String, required: true },
  podeOperar: { type: Boolean, default: true },
  filtroLocais: { type: Array, default: () => [] },
  filtroLocalLabel: { type: String, default: 'Local' },
  mostrarBusca: { type: Boolean, default: true },
  camposExtras: { type: Boolean, default: false },
  vazio: { type: String, default: 'Nenhuma muda pendente nesta etapa.' },
  mensagemLoading: { type: String, default: 'Processando mudas…' },
  /** (grupos) => Promise<resposta API> */
  onExecutar: { type: Function, required: true },
})

const emit = defineEmits(['concluido'])

const resumoGrupos = ref([])
const linhas = reactive({})
const filtroCanteiro = ref('')
const busca = ref('')
const carregando = ref(false)
const processando = ref(false)
const erro = ref('')
const sucesso = ref('')

function chaveGrupo(g) {
  return `${g.id_especie}-${g.id_canteiro ?? 0}`
}

const gruposVisiveis = computed(() => {
  const q = busca.value.trim().toLowerCase()
  if (!q) return resumoGrupos.value
  return resumoGrupos.value.filter((g) => (g.especie_nome || '').toLowerCase().includes(q))
})

const resumo = computed(() => {
  let especies = 0
  let total = 0
  for (const g of resumoGrupos.value) {
    const row = linhas[chaveGrupo(g)]
    if (!row?.ativo || !row.quantidade) continue
    especies += 1
    total += row.quantidade
  }
  return { especies, total }
})

const todosMarcados = computed(
  () =>
    gruposVisiveis.value.length > 0 &&
    gruposVisiveis.value.every((g) => linhas[chaveGrupo(g)]?.ativo)
)

function garantirLinhas() {
  for (const g of resumoGrupos.value) {
    const k = chaveGrupo(g)
    if (!linhas[k]) linhas[k] = { ativo: false, quantidade: null }
  }
}

async function carregarResumo() {
  carregando.value = true
  erro.value = ''
  try {
    const params = {}
    if (filtroCanteiro.value) params.id_canteiro = Number(filtroCanteiro.value)
    resumoGrupos.value = await getResumoOperacaoLote(props.etapa, params)
    garantirLinhas()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar resumo.'
    resumoGrupos.value = []
  } finally {
    carregando.value = false
  }
}

function aoMarcar(g) {
  const row = linhas[chaveGrupo(g)]
  if (row.ativo && !row.quantidade) row.quantidade = g.disponivel
  if (!row.ativo) row.quantidade = null
}

function validarQtd(g) {
  const row = linhas[chaveGrupo(g)]
  if (row.quantidade > g.disponivel) row.quantidade = g.disponivel
  if (row.quantidade > 0) row.ativo = true
}

function marcarTodos() {
  for (const g of gruposVisiveis.value) {
    const row = linhas[chaveGrupo(g)]
    row.ativo = true
    row.quantidade = g.disponivel
  }
}

function toggleTodos(ev) {
  if (ev.target.checked) marcarTodos()
  else limparVisiveis()
}

function limparVisiveis() {
  for (const g of gruposVisiveis.value) {
    linhas[chaveGrupo(g)].ativo = false
    linhas[chaveGrupo(g)].quantidade = null
  }
}

function usarDisponivel() {
  for (const g of resumoGrupos.value) {
    const row = linhas[chaveGrupo(g)]
    if (row?.ativo) row.quantidade = g.disponivel
  }
}

function limpar() {
  for (const g of resumoGrupos.value) {
    linhas[chaveGrupo(g)].ativo = false
    linhas[chaveGrupo(g)].quantidade = null
  }
}

function montarGrupos() {
  const grupos = []
  for (const g of resumoGrupos.value) {
    const row = linhas[chaveGrupo(g)]
    if (!row?.ativo || !row.quantidade || row.quantidade <= 0) continue
    if (row.quantidade > g.disponivel) {
      throw new Error(`${g.especie_nome}: quantidade maior que disponível (${g.disponivel}).`)
    }
    grupos.push({
      id_especie: g.id_especie,
      quantidade: row.quantidade,
      id_canteiro_origem: g.id_canteiro || null,
    })
  }
  if (!grupos.length) throw new Error('Marque ao menos uma espécie e informe a quantidade.')
  return grupos
}

async function executar() {
  erro.value = ''
  sucesso.value = ''
  processando.value = true
  try {
    const grupos = montarGrupos()
    await runWithLoading(async () => {
      const resp = await props.onExecutar(grupos)
      let msg = `${resp.total?.toLocaleString('pt-BR') || 0} muda(s) processada(s)`
      if (resp.baixa_substrato) {
        const b = resp.baixa_substrato
        msg += `. Baixa substrato: ${b.quantidade} ${b.unidade}`
      }
      if (resp.avisos?.length) msg += ` · ${resp.avisos.join(' ')}`
      sucesso.value = msg
      limpar()
      await carregarResumo()
      emit('concluido', resp)
    }, props.mensagemLoading)
  } catch (e) {
    erro.value = e.response?.data?.detail || e.message || 'Erro na operação.'
  } finally {
    processando.value = false
  }
}

onMounted(carregarResumo)
defineExpose({ carregarResumo, limpar })

watch(
  () => props.etapa,
  () => carregarResumo()
)
</script>

<style scoped>
@import './producao-panel-shared.css';

.painel-lote {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: var(--spacing-md);
  justify-content: space-between;
}

.toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.form-card--inline {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md) var(--spacing-lg);
}

.col-num {
  text-align: right;
  white-space: nowrap;
}

.input-qtd {
  width: 5.5rem;
  padding: 0.35rem 0.45rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
  text-align: right;
}

.row--ativo {
  background: color-mix(in srgb, var(--color-primary) 6%, transparent);
}

.lote-resumo {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.lote-resumo__nums {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}
</style>
