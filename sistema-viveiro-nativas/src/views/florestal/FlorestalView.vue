<template>
  <PageLayout>
    <PageSection>
      <template #header>
        <div class="fl-head">
          <div>
            <p class="fl-head__eyebrow">Brotare Viveiros · Florestal</p>
            <h2 class="fl-head__title">Produção por lote</h2>
            <p class="fl-head__sub">Genótipos, lotes e movimentação — controle por quantidade.</p>
          </div>
        </div>
      </template>

      <p v-if="erro" class="fl-erro">{{ erro }}</p>

      <div v-if="carregando" class="fl-loading">Carregando…</div>
      <template v-else>
        <div class="fl-cards">
          <article v-for="c in cards" :key="c.label" class="fl-card">
            <span class="fl-card__label">{{ c.label }}</span>
            <strong class="fl-card__value">{{ c.value }}</strong>
          </article>
        </div>

        <div class="fl-grid">
          <section class="fl-panel">
            <header class="fl-panel__head">
              <h3>Genótipos</h3>
              <button v-if="podeCriar" type="button" class="fl-btn fl-btn--primary" @click="mostrarGenotipo = true">
                + Genótipo
              </button>
            </header>
            <table class="fl-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Nome</th>
                  <th>Fornecedor</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="g in genotipos" :key="g.id">
                  <td><code>{{ g.codigo }}</code></td>
                  <td>{{ g.nome || '—' }}</td>
                  <td>{{ g.fornecedor || '—' }}</td>
                </tr>
                <tr v-if="!genotipos.length">
                  <td colspan="3" class="fl-muted">Nenhum genótipo cadastrado.</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section class="fl-panel">
            <header class="fl-panel__head">
              <h3>Lotes de produção</h3>
              <button v-if="podeCriar" type="button" class="fl-btn fl-btn--primary" @click="mostrarLote = true">
                + Lote
              </button>
            </header>
            <table class="fl-table">
              <thead>
                <tr>
                  <th>Lote</th>
                  <th>Genótipo</th>
                  <th>Estágio</th>
                  <th>Qtd</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="l in lotes" :key="l.id">
                  <td><code>{{ l.codigo_lote }}</code></td>
                  <td>{{ l.genotipo_codigo }}</td>
                  <td>{{ l.estagio_label }}</td>
                  <td>{{ l.quantidade_atual }}</td>
                  <td>
                    <button
                      v-if="podeTransferir && l.quantidade_atual > 0"
                      type="button"
                      class="fl-btn fl-btn--ghost fl-btn--sm"
                      @click="abrirTransferencia(l)"
                    >
                      Avançar
                    </button>
                  </td>
                </tr>
                <tr v-if="!lotes.length">
                  <td colspan="5" class="fl-muted">Nenhum lote ativo.</td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>
      </template>

      <AppModalOverlay v-if="mostrarGenotipo" @close="mostrarGenotipo = false">
        <div class="fl-modal">
          <h3>Novo genótipo</h3>
          <form class="fl-form" @submit.prevent="salvarGenotipo">
            <label>Código<input v-model="formGenotipo.codigo" required maxlength="50" /></label>
            <label>Nome<input v-model="formGenotipo.nome" maxlength="100" /></label>
            <label>Fornecedor<input v-model="formGenotipo.fornecedor" maxlength="100" /></label>
            <label>Material genético<input v-model="formGenotipo.material_genetico" maxlength="100" /></label>
            <div class="fl-form__actions">
              <button type="button" class="fl-btn" @click="mostrarGenotipo = false">Cancelar</button>
              <button type="submit" class="fl-btn fl-btn--primary">Salvar</button>
            </div>
          </form>
        </div>
      </AppModalOverlay>

      <AppModalOverlay v-if="mostrarLote" @close="mostrarLote = false">
        <div class="fl-modal">
          <h3>Novo lote</h3>
          <form class="fl-form" @submit.prevent="salvarLote">
            <label>
              Genótipo
              <select v-model.number="formLote.id_genotipo" required>
                <option v-for="g in genotipos" :key="g.id" :value="g.id">{{ g.codigo }}</option>
              </select>
            </label>
            <label>Código lote<input v-model="formLote.codigo_lote" required maxlength="30" /></label>
            <label>Data entrada<input v-model="formLote.data_entrada" type="date" required /></label>
            <label>Quantidade<input v-model.number="formLote.quantidade_inicial" type="number" min="1" required /></label>
            <div class="fl-form__actions">
              <button type="button" class="fl-btn" @click="mostrarLote = false">Cancelar</button>
              <button type="submit" class="fl-btn fl-btn--primary">Criar</button>
            </div>
          </form>
        </div>
      </AppModalOverlay>

      <AppModalOverlay v-if="loteTransferir" @close="loteTransferir = null">
        <div class="fl-modal">
          <h3>Avançar lote {{ loteTransferir.codigo_lote }}</h3>
          <form class="fl-form" @submit.prevent="confirmarTransferencia">
            <label>
              Estágio destino
              <select v-model="formTransfer.estagio_destino" required>
                <option value="casa_vegetacao">Casa de vegetação</option>
                <option value="endurecimento">Endurecimento</option>
                <option value="expedicao">Expedição</option>
                <option value="descartado">Descartado</option>
              </select>
            </label>
            <label>Quantidade<input v-model.number="formTransfer.quantidade" type="number" min="1" :max="loteTransferir.quantidade_atual" required /></label>
            <div class="fl-form__actions">
              <button type="button" class="fl-btn" @click="loteTransferir = null">Cancelar</button>
              <button type="submit" class="fl-btn fl-btn--primary">Confirmar</button>
            </div>
          </form>
        </div>
      </AppModalOverlay>
    </PageSection>
  </PageLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import PageLayout from '@/components/layout/PageLayout.vue'
import PageSection from '@/components/layout/PageSection.vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import { usePermissions } from '@/composables/usePermissions'
import {
  createGenotipo,
  createLoteProducao,
  fetchFlorestalResumo,
  listGenotipos,
  listLotesProducao,
  transferirLote,
} from '@/services/florestal'

const { can } = usePermissions()
const podeCriar = computed(() => can('florestal.create'))
const podeTransferir = computed(() => can('florestal.transfer'))

const carregando = ref(true)
const erro = ref('')
const resumo = ref(null)
const genotipos = ref([])
const lotes = ref([])
const mostrarGenotipo = ref(false)
const mostrarLote = ref(false)
const loteTransferir = ref(null)

const formGenotipo = reactive({ codigo: '', nome: '', fornecedor: '', material_genetico: '' })
const formLote = reactive({
  id_genotipo: null,
  codigo_lote: '',
  data_entrada: new Date().toISOString().slice(0, 10),
  quantidade_inicial: 1000,
})
const formTransfer = reactive({ estagio_destino: 'casa_vegetacao', quantidade: 0 })

const cards = computed(() => [
  { label: 'Genótipos', value: resumo.value?.genotipos_ativos ?? 0 },
  { label: 'Lotes ativos', value: resumo.value?.lotes_ativos ?? 0 },
  { label: 'Mudas em produção', value: resumo.value?.mudas_em_producao ?? 0 },
  { label: 'Expedição', value: resumo.value?.mudas_expedicao ?? 0 },
])

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const [r, g, l] = await Promise.all([
      fetchFlorestalResumo(),
      listGenotipos(),
      listLotesProducao(),
    ])
    resumo.value = r
    genotipos.value = g
    lotes.value = l
    if (g.length && !formLote.id_genotipo) formLote.id_genotipo = g[0].id
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha ao carregar módulo florestal.'
  } finally {
    carregando.value = false
  }
}

async function salvarGenotipo() {
  try {
    await createGenotipo({ ...formGenotipo })
    mostrarGenotipo.value = false
    Object.assign(formGenotipo, { codigo: '', nome: '', fornecedor: '', material_genetico: '' })
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao salvar genótipo.'
  }
}

async function salvarLote() {
  try {
    await createLoteProducao({ ...formLote })
    mostrarLote.value = false
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao criar lote.'
  }
}

function abrirTransferencia(lote) {
  loteTransferir.value = lote
  formTransfer.quantidade = lote.quantidade_atual
  formTransfer.estagio_destino = 'casa_vegetacao'
}

async function confirmarTransferencia() {
  try {
    await transferirLote(loteTransferir.value.id, { ...formTransfer })
    loteTransferir.value = null
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro na transferência.'
  }
}

onMounted(carregar)
</script>

<style scoped>
.fl-head__eyebrow { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-text-secondary); margin: 0 0 0.25rem; }
.fl-head__title { margin: 0; font-size: 1.5rem; }
.fl-head__sub { margin: 0.35rem 0 0; color: var(--color-text-secondary); }
.fl-erro { color: #b42318; margin-bottom: 1rem; }
.fl-loading { padding: 2rem; text-align: center; color: var(--color-text-secondary); }
.fl-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.75rem; margin-bottom: 1.25rem; }
.fl-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 12px; padding: 1rem; }
.fl-card__label { display: block; font-size: 0.75rem; color: var(--color-text-secondary); }
.fl-card__value { font-size: 1.5rem; }
.fl-grid { display: grid; gap: 1rem; grid-template-columns: 1fr; }
@media (min-width: 1024px) { .fl-grid { grid-template-columns: 1fr 1.4fr; } }
.fl-panel { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 12px; padding: 1rem; }
.fl-panel__head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.fl-panel__head h3 { margin: 0; font-size: 1rem; }
.fl-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.fl-table th, .fl-table td { padding: 0.5rem; border-bottom: 1px solid var(--color-border); text-align: left; }
.fl-muted { color: var(--color-text-secondary); font-style: italic; }
.fl-btn { border: 1px solid var(--color-border); background: var(--color-surface); border-radius: 8px; padding: 0.4rem 0.75rem; cursor: pointer; }
.fl-btn--primary { background: var(--color-primary, #596247); color: #fff; border-color: transparent; }
.fl-btn--ghost { background: transparent; }
.fl-btn--sm { font-size: 0.8125rem; padding: 0.25rem 0.5rem; }
.fl-modal { background: var(--color-surface); border-radius: 12px; padding: 1.25rem; width: min(420px, 92vw); }
.fl-form { display: grid; gap: 0.75rem; margin-top: 1rem; }
.fl-form label { display: grid; gap: 0.25rem; font-size: 0.875rem; }
.fl-form input, .fl-form select { padding: 0.5rem; border-radius: 8px; border: 1px solid var(--color-border); }
.fl-form__actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.5rem; }
</style>
