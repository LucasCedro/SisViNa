<template>
  <div class="semeadura-panel">
    <header class="panel-intro">
      <h2 class="panel-title">Transferir para sementeira</h2>
      <p class="panel-lead">
        Registre sementes do armazém indo para a sementeira e crie as mudas SEMENTE.
      </p>
    </header>

    <ProducaoModoOperacao v-model:modo="modo">
      <template #default="{ modo: m }">
    <form v-if="m === PRODUCAO_MODO.INDIVIDUAL" class="form-card" @submit.prevent="salvarUnitario">
      <label class="field">
        Lote de sementes
        <select v-model.number="form.id_lote_sementes" required @change="aoTrocarLote">
          <option :value="null" disabled>Selecione o lote</option>
          <option v-for="l in lotesDisponiveis" :key="l.id" :value="l.id">
            {{ l.codigo_lote }} — {{ l.especie_nome }} ({{ l.quantidade_disponivel }} disp.)
          </option>
        </select>
      </label>

      <p v-if="loteSelecionado" class="lote-info">
        Matriz: {{ loteSelecionado.matriz_nome || '—' }} ·
        Disponível: {{ loteSelecionado.quantidade_disponivel }}
      </p>

      <div class="field-row">
        <label class="field">
          Data da semeadura
          <input v-model="form.data_semeadura" type="date" required />
        </label>
        <label class="field">
          Sementes usadas
          <input
            v-model.number="form.quantidade_sementes_usadas"
            type="number"
            min="1"
            :max="loteSelecionado?.quantidade_disponivel"
            required
          />
        </label>
      </div>

      <label class="field">
        Sementeira (local)
        <select v-model.number="form.id_canteiro" required>
          <option :value="null" disabled>Selecione</option>
          <option v-for="c in sementeiras" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
      </label>

      <label class="check">
        <input v-model="form.registrar_plantas" type="checkbox" />
        Criar registros de mudas (recomendado — habilita transferência para canteiro)
      </label>

      <p v-if="form.registrar_plantas && form.quantidade_sementes_usadas" class="plantas-hint">
        Serão criadas <strong>{{ form.quantidade_sementes_usadas }}</strong> mudas SEMENTE
        (1 por semente usada).
      </p>

      <label class="field">
        Observações
        <textarea v-model="form.observacoes" rows="2" placeholder="Bandeja, recipiente, etc." />
      </label>

      <p v-if="erro" class="alert alert-error">{{ erro }}</p>
      <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="salvando || !podeSemear">
          Registrar semeadura
        </button>
      </div>
    </form>

    <div v-else class="lote-wrap">
      <div class="form-card lote-config">
        <div class="field-row">
          <label class="field">
            Data da semeadura
            <input v-model="loteForm.data_semeadura" type="date" required />
          </label>
          <label class="field">
            Sementeira (local)
            <select v-model.number="loteForm.id_canteiro" required>
              <option :value="null" disabled>Selecione</option>
              <option v-for="c in sementeiras" :key="c.id" :value="c.id">{{ c.nome }}</option>
            </select>
          </label>
        </div>
        <label class="field">
          Observações gerais (opcional)
          <input
            v-model="loteForm.observacoes_gerais"
            type="text"
            placeholder="Ex.: semeadura do dia 10/06 — bandejas A1–A8"
          />
        </label>
        <label class="check">
          <input v-model="loteForm.registrar_plantas" type="checkbox" />
          Criar mudas SEMENTE (1 por semente — recomendado)
        </label>
      </div>

      <div class="toolbar">
        <label class="field field--sm">
          {{ PRODUCAO_ACOES_LOTE.filtrarEspecie }}
          <input v-model="filtroEspecie" type="search" placeholder="Angico, pequi…" />
        </label>
        <div class="toolbar-actions">
          <button type="button" class="btn btn-outline btn-sm" @click="marcarTodosVisiveis">
            {{ PRODUCAO_ACOES_LOTE.marcarTodos }}
          </button>
          <button type="button" class="btn btn-outline btn-sm" @click="usarDisponivelSelecionados">
            {{ PRODUCAO_ACOES_LOTE.preencherDisponivel }}
          </button>
          <button type="button" class="btn btn-outline btn-sm" @click="limparSelecao">
            {{ PRODUCAO_ACOES_LOTE.limpar }}
          </button>
        </div>
      </div>

      <div class="table-card">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-check">
                <input
                  type="checkbox"
                  :checked="todosVisiveisMarcados"
                  :disabled="!lotesFiltrados.length || !podeSemear"
                  @change="toggleTodosVisiveis"
                />
              </th>
              <th>Lote</th>
              <th>Espécie</th>
              <th>Matriz</th>
              <th class="col-num">Disponível</th>
              <th class="col-num">Quantidade</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="carregandoLotes">
              <td colspan="6" class="empty-cell">Carregando lotes…</td>
            </tr>
            <tr v-else-if="!lotesFiltrados.length">
              <td colspan="6" class="empty-cell">Nenhum lote com estoque disponível.</td>
            </tr>
            <tr
              v-for="l in lotesFiltrados"
              :key="l.id"
              :class="{ 'row--ativo': linhas[l.id]?.ativo }"
            >
              <td>
                <input
                  v-model="linhas[l.id].ativo"
                  type="checkbox"
                  :disabled="!podeSemear"
                  @change="aoMarcarLinha(l)"
                />
              </td>
              <td><code>{{ l.codigo_lote }}</code></td>
              <td>{{ l.especie_nome }}</td>
              <td>{{ l.matriz_nome || '—' }}</td>
              <td class="col-num">{{ l.quantidade_disponivel }}</td>
              <td class="col-num">
                <input
                  v-model.number="linhas[l.id].quantidade"
                  type="number"
                  class="input-qtd"
                  min="0"
                  :max="l.quantidade_disponivel"
                  :disabled="!linhas[l.id]?.ativo || !podeSemear"
                  @input="validarQtdLinha(l)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <footer class="lote-resumo">
        <div class="lote-resumo__nums">
          <span>{{ PRODUCAO_RESUMO.especies(resumoLote.especies) }}</span>
          <span>{{ PRODUCAO_RESUMO.sementes(resumoLote.sementes) }}</span>
          <span v-if="loteForm.registrar_plantas">
            {{ PRODUCAO_RESUMO.mudas(resumoLote.sementes) }} SEMENTE
          </span>
        </div>
        <p v-if="erro" class="alert alert-error">{{ erro }}</p>
        <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>
        <button
          type="button"
          class="btn btn-primary"
          :disabled="salvando || !podeSemear || !resumoLote.especies"
          @click="salvarLote"
        >
          Registrar semeadura — {{ PRODUCAO_RESUMO.sementes(resumoLote.sementes) }}
        </button>
      </footer>
    </div>
      </template>
    </ProducaoModoOperacao>

    <p v-if="!lotesDisponiveis.length && !carregandoLotes && modo === PRODUCAO_MODO.INDIVIDUAL" class="empty-hint">
      Nenhum lote com sementes disponíveis.
      <router-link to="/coleta">Cadastre coleta e lote</router-link>
      ou
      <router-link to="/estoques">entrada no armazém</router-link>.
    </p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { listLotesSementes } from '@/services/lotesSementes'
import { listCanteiros } from '@/services/canteiros'
import { createSemeadura, createSemeadurasLote } from '@/services/semeaduras'
import { usePermissions } from '@/composables/usePermissions'
import { useGlobalLoading } from '@/composables/useGlobalLoading'
import { PRODUCAO_MODO, PRODUCAO_ACOES_LOTE, PRODUCAO_RESUMO } from '@/constants/producaoUi'
import ProducaoModoOperacao from './ProducaoModoOperacao.vue'

const emit = defineEmits(['atualizado'])
const { runWithLoading } = useGlobalLoading()
const { can } = usePermissions()

const modo = ref(PRODUCAO_MODO.MASSA)
const lotes = ref([])
const sementeiras = ref([])
const carregandoLotes = ref(true)
const salvando = ref(false)
const erro = ref('')
const sucesso = ref('')
const filtroEspecie = ref('')
const linhas = reactive({})

const form = ref({
  id_lote_sementes: null,
  data_semeadura: new Date().toISOString().split('T')[0],
  quantidade_sementes_usadas: null,
  id_canteiro: null,
  registrar_plantas: true,
  observacoes: '',
})

const loteForm = ref({
  data_semeadura: new Date().toISOString().split('T')[0],
  id_canteiro: null,
  registrar_plantas: true,
  observacoes_gerais: '',
})

const podeSemear = computed(() => can('producao.transfer') || can('producao.create'))

const lotesDisponiveis = computed(() =>
  lotes.value.filter((l) => l.status === 'ativo' && (l.quantidade_disponivel || 0) > 0)
)

const loteSelecionado = computed(() =>
  lotesDisponiveis.value.find((l) => l.id === form.value.id_lote_sementes)
)

const lotesFiltrados = computed(() => {
  const q = filtroEspecie.value.trim().toLowerCase()
  if (!q) return lotesDisponiveis.value
  return lotesDisponiveis.value.filter(
    (l) =>
      (l.especie_nome || '').toLowerCase().includes(q) ||
      (l.codigo_lote || '').toLowerCase().includes(q) ||
      (l.matriz_nome || '').toLowerCase().includes(q)
  )
})

const resumoLote = computed(() => {
  let especies = 0
  let sementes = 0
  for (const l of lotesDisponiveis.value) {
    const row = linhas[l.id]
    if (!row?.ativo || !row.quantidade) continue
    especies += 1
    sementes += row.quantidade
  }
  return { especies, sementes }
})

const todosVisiveisMarcados = computed(() => {
  const vis = lotesFiltrados.value
  return vis.length > 0 && vis.every((l) => linhas[l.id]?.ativo)
})

function garantirLinhas() {
  for (const l of lotesDisponiveis.value) {
    if (!linhas[l.id]) {
      linhas[l.id] = { ativo: false, quantidade: null }
    }
  }
}

watch(lotesDisponiveis, garantirLinhas, { immediate: true })

function aoTrocarLote() {
  const l = loteSelecionado.value
  if (!l) return
  form.value.quantidade_sementes_usadas = l.quantidade_disponivel
}

function aoMarcarLinha(lote) {
  const row = linhas[lote.id]
  if (row.ativo && !row.quantidade) {
    row.quantidade = lote.quantidade_disponivel
  }
  if (!row.ativo) {
    row.quantidade = null
  }
}

function validarQtdLinha(lote) {
  const row = linhas[lote.id]
  if (!row) return
  if (row.quantidade > lote.quantidade_disponivel) {
    row.quantidade = lote.quantidade_disponivel
  }
  if (row.quantidade > 0) row.ativo = true
}

function marcarTodosVisiveis() {
  for (const l of lotesFiltrados.value) {
    linhas[l.id].ativo = true
    linhas[l.id].quantidade = l.quantidade_disponivel
  }
}

function toggleTodosVisiveis(ev) {
  if (ev.target.checked) marcarTodosVisiveis()
  else {
    for (const l of lotesFiltrados.value) {
      linhas[l.id].ativo = false
      linhas[l.id].quantidade = null
    }
  }
}

function usarDisponivelSelecionados() {
  for (const l of lotesDisponiveis.value) {
    const row = linhas[l.id]
    if (row?.ativo) row.quantidade = l.quantidade_disponivel
  }
}

function limparSelecao() {
  for (const l of lotesDisponiveis.value) {
    linhas[l.id].ativo = false
    linhas[l.id].quantidade = null
  }
}

function parseErroApi(e) {
  const detail = e.response?.data?.detail
  return (
    (typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map((d) => d.msg || d).join(' · ')
        : null) ||
    (e.message?.includes('Network Error')
      ? 'Falha de conexão com a API. Verifique se o backend está no ar.'
      : null) ||
    'Erro ao registrar semeadura.'
  )
}

async function recarregarLotes() {
  lotes.value = await listLotesSementes({ limit: 500 })
  garantirLinhas()
}

onMounted(async () => {
  try {
    const [lot, cant] = await Promise.all([
      listLotesSementes({ limit: 500 }),
      listCanteiros({ ativo: true, tipo_local: 'sementeira' }),
    ])
    lotes.value = lot
    sementeiras.value = cant.length
      ? cant
      : (await listCanteiros({ ativo: true })).filter((c) => c.tipo_local === 'sementeira')
    if (sementeiras.value.length === 1) {
      form.value.id_canteiro = sementeiras.value[0].id
      loteForm.value.id_canteiro = sementeiras.value[0].id
    }
  } finally {
    carregandoLotes.value = false
  }
})

async function salvarUnitario() {
  if (!podeSemear.value) return
  erro.value = ''
  sucesso.value = ''
  salvando.value = true
  try {
    await createSemeadura({
      id_lote_sementes: form.value.id_lote_sementes,
      data_semeadura: form.value.data_semeadura,
      quantidade_sementes_usadas: form.value.quantidade_sementes_usadas,
      id_canteiro: form.value.id_canteiro,
      registrar_plantas: form.value.registrar_plantas,
      quantidade_plantas_registrar: form.value.registrar_plantas
        ? form.value.quantidade_sementes_usadas
        : null,
      observacoes: form.value.observacoes || null,
    })
    sucesso.value = 'Semeadura registrada. Mudas SEMENTE criadas na sementeira.'
    await recarregarLotes()
    form.value.id_lote_sementes = null
    emit('atualizado')
  } catch (e) {
    erro.value = parseErroApi(e)
  } finally {
    salvando.value = false
  }
}

async function salvarLote() {
  if (!podeSemear.value) return
  erro.value = ''
  sucesso.value = ''

  if (!loteForm.value.id_canteiro) {
    erro.value = 'Selecione a sementeira.'
    return
  }

  const itens = []
  for (const l of lotesDisponiveis.value) {
    const row = linhas[l.id]
    if (!row?.ativo || !row.quantidade || row.quantidade <= 0) continue
    if (row.quantidade > l.quantidade_disponivel) {
      erro.value = `Lote ${l.codigo_lote}: quantidade maior que o disponível (${l.quantidade_disponivel}).`
      return
    }
    itens.push({
      id_lote_sementes: l.id,
      quantidade_sementes_usadas: row.quantidade,
    })
  }

  if (!itens.length) {
    erro.value = 'Marque ao menos um lote e informe a quantidade.'
    return
  }

  salvando.value = true
  try {
    await runWithLoading(async () => {
      const resp = await createSemeadurasLote({
        data_semeadura: loteForm.value.data_semeadura,
        id_canteiro: loteForm.value.id_canteiro,
        registrar_plantas: loteForm.value.registrar_plantas,
        observacoes_gerais: loteForm.value.observacoes_gerais || null,
        itens,
      })
      sucesso.value =
        `${resp.itens.length} semeadura(s) registrada(s): ` +
        `${resp.total_sementes.toLocaleString('pt-BR')} sementes` +
        (resp.total_plantas
          ? ` → ${resp.total_plantas.toLocaleString('pt-BR')} mudas SEMENTE`
          : '') +
        `.`
      limparSelecao()
      await recarregarLotes()
      emit('atualizado')
    }, 'Registrando semeaduras…')
  } catch (e) {
    erro.value = parseErroApi(e)
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.panel-intro {
  margin-bottom: var(--spacing-md);
}

.panel-title {
  margin: 0 0 0.35rem;
  font-size: 1.125rem;
  font-weight: 600;
}

.panel-lead {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.45;
}

.modo-nav {
  display: flex;
  gap: 0.35rem;
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
}

.form-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  max-width: 560px;
}

.lote-wrap {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.lote-config {
  max-width: none;
}

.field-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8125rem;
  font-weight: 500;
  flex: 1;
  min-width: 140px;
}

.field--sm {
  min-width: 180px;
  max-width: 280px;
}

.field select,
.field input,
.field textarea {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 400;
}

.check {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.lote-info,
.plantas-hint {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
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

.table-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  overflow: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.data-table th,
.data-table td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid var(--color-border-subtle);
  text-align: left;
}

.data-table th {
  font-weight: 600;
  background: var(--color-surface-muted, #f8f9fa);
  white-space: nowrap;
}

.col-check {
  width: 2.5rem;
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

.empty-cell {
  text-align: center;
  color: var(--color-text-muted);
  padding: 1.5rem !important;
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

.form-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-hint {
  margin-top: var(--spacing-md);
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.empty-hint a {
  color: var(--color-primary);
  font-weight: 600;
}
</style>
