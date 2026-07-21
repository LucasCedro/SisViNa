<template>
  <div class="financeiro-page premissas-page">
    <div class="prem-intro">
      <p class="financeiro-lead prem-intro__lead">
        Preencha os valores abaixo e clique em <strong>Salvar premissas</strong>.
        Premissas <strong>CUSTO</strong> alimentam o CMV da muda; premissas <strong>DRE</strong> entram automaticamente no OPEX do resultado (comissão + despesas fixas).
      </p>
      <ul class="prem-intro__lista">
        <li><span class="prem-tag prem-tag--cmv">CMV</span> coleta: horas × homem-hora; água, energia e folha: valor pago no mês ÷ mudas vivas</li>
        <li><span class="prem-tag prem-tag--dre">DRE</span> aplicado automaticamente na DRE — não precisa lançar OPEX manual</li>
        <li>
          Substrato: estoque em <strong>kg</strong> (saco), dosagem em <strong>gramas por recipiente</strong>
          — estimativa prática, sem densidade. Baixa automática na transferência para o canteiro.
          <router-link to="/estoques">Estoques → Insumos</router-link>
        </li>
      </ul>
    </div>

    <p v-if="carregando" class="alert alert-info">Carregando…</p>
    <p v-else-if="erro" class="alert alert-error">{{ erro }}</p>

    <template v-else>
      <section v-for="grupo in grupos" :key="grupo.id" class="prem-grupo">
        <header class="prem-grupo__head">
          <h2 class="fin-sec__titulo">{{ grupo.titulo }}</h2>
          <p class="prem-grupo__hint">{{ grupo.hint }}</p>
        </header>

        <div v-for="sec in grupo.secoes" :key="sec.id" class="prem-secao">
          <div class="prem-secao__head">
            <h3 class="prem-secao__titulo">{{ sec.titulo }}</h3>
            <p v-if="sec.descricao" class="prem-secao__desc">{{ sec.descricao }}</p>
            <div v-if="sec.configPremissa && editLocal[sec.configPremissa.id]" class="prem-recipiente">
              <span class="prem-recipiente__label">Como você semeia?</span>
              <div class="prem-recipiente__opcoes">
                <label
                  v-for="(meta, key) in RECIPIENTES_SEMEADURA"
                  :key="key"
                  class="prem-recipiente__opcao"
                  :class="{ 'prem-recipiente__opcao--ativa': recipienteAtual === key }"
                >
                  <input
                    v-model="editLocal[sec.configPremissa.id].unidade"
                    type="radio"
                    :value="key"
                    :disabled="!podeEditar"
                  />
                  <span>{{ meta.label }}</span>
                </label>
              </div>
            </div>
          </div>

          <div class="prem-cards">
            <article
              v-for="p in sec.itens"
              :key="p.id"
              class="prem-card"
              :class="grupo.id === 'CUSTO' ? 'prem-card--cmv' : 'prem-card--dre'"
            >
              <header class="prem-card__head">
                <div class="prem-card__titulos">
                  <span class="prem-tag" :class="badgeClasse(p)">{{ badgeDe(p) }}</span>
                  <h4>{{ p.nome }}</h4>
                </div>
              </header>
              <p v-if="p.descricao" class="prem-card__desc">{{ p.descricao }}</p>

              <div class="prem-card__campos">
                <label v-for="c in camposDe(p)" :key="c.key" class="prem-field">
                  <span class="prem-field__label">{{ c.label }}</span>
                  <p v-if="c.dica" class="prem-field__dica">{{ c.dica }}</p>
                  <div class="prem-field__input-row">
                    <template v-if="c.type === 'insumo'">
                      <select
                        v-if="insumosParaCampo(c).length"
                        v-model="editLocal[p.id][c.key]"
                        :disabled="!podeEditar"
                        class="prem-field__control"
                      >
                        <option :value="null">— Selecione —</option>
                        <option v-for="i in insumosParaCampo(c)" :key="i.id" :value="i.id">
                          {{ i.nome }} ({{ fmtMoeda(i.preco_unitario) }}/{{ i.unidade_medida || 'un' }})
                        </option>
                      </select>
                      <p v-else class="prem-field__aviso">
                        Nenhum item do tipo
                        <strong>{{ (c.insumoTipos || []).join(', ') }}</strong> no estoque.
                        <router-link to="/estoques">Cadastrar em Estoques</router-link>
                      </p>
                    </template>
                    <template v-else>
                      <input
                        v-model.number="editLocal[p.id][c.key]"
                        type="number"
                        step="any"
                        min="0"
                        :disabled="!podeEditar"
                        class="prem-field__control"
                      />
                      <span v-if="c.suffix" class="prem-field__suf">{{ c.suffix }}</span>
                    </template>
                  </div>
                </label>
              </div>

              <footer class="prem-card__calc">
                <span class="prem-card__calc-label">Prévia do cálculo</span>
                <strong>{{ textoCalculo(p) }}</strong>
              </footer>
            </article>
          </div>
        </div>
      </section>

      <footer v-if="podeEditar" class="prem-footer">
        <p v-if="temAlteracoes" class="prem-footer__hint">Há alterações não salvas</p>
        <p v-else class="prem-footer__hint prem-footer__hint--ok">Nenhuma alteração pendente</p>
        <div class="prem-footer__acoes">
          <button
            type="button"
            class="btn btn-secondary"
            :disabled="!temAlteracoes || salvando"
            @click="descartar"
          >
            Descartar
          </button>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="!temAlteracoes || salvando"
            @click="salvarTudo"
          >
            {{ salvando ? 'Salvando…' : 'Salvar premissas' }}
          </button>
        </div>
      </footer>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { listPremissas, updatePremissa } from '@/services/financeiro'
import { listInsumos } from '@/services/insumos'
import { useGlobalLoading } from '@/composables/useGlobalLoading'
import {
  uiPremissa,
  secoesPremissas,
  insumosParaCampo as filtrarInsumos,
  RECIPIENTES_SEMEADURA,
  CHAVE_RECIPIENTE,
  CHAVE_SUBSTRATO,
  normalizarRecipiente,
  unidadePremissaSubstrato,
} from '@/constants/premissasUi'

const props = defineProps({
  podeEditar: { type: Boolean, default: false },
  faturamento: { type: Number, default: 0 },
  mudasVivas: { type: Number, default: 0 },
})

const emit = defineEmits(['atualizar'])
const { runWithLoading } = useGlobalLoading()

const lista = ref([])
const insumos = ref([])
const carregando = ref(true)
const salvando = ref(false)
const erro = ref('')
const editLocal = reactive({})
const original = reactive({})

const recipienteAtual = computed(() => {
  const p = lista.value.find((x) => x.chave === CHAVE_RECIPIENTE)
  if (!p) return 'tubete'
  const loc = editLocal[p.id]
  return normalizarRecipiente(loc?.unidade ?? p.unidade)
})

const ctx = computed(() => ({
  faturamento: props.faturamento || 0,
  mudasVivas: props.mudasVivas || 0,
  recipiente: recipienteAtual.value,
  insumos: insumos.value,
}))

const grupos = computed(() => [
  {
    id: 'CUSTO',
    titulo: 'Custos de produção (CMV)',
    hint: 'Rateados automaticamente quando você semeia um lote.',
    secoes: secoesPremissas('CUSTO', lista.value, recipienteAtual.value),
  },
  {
    id: 'DESPESA',
    titulo: 'Despesas operacionais (DRE)',
    hint: 'Referência para o resultado do período — não entram no custo unitário da muda.',
    secoes: secoesPremissas('DESPESA', lista.value, recipienteAtual.value),
  },
])

function snapPremissa(p) {
  return {
    valor: valorPremissa(p.valor),
    quantidade: quantidadePremissa(p.quantidade),
    id_insumo: p.id_insumo,
    unidade:
      p.chave === CHAVE_RECIPIENTE ? normalizarRecipiente(p.unidade) : p.unidade,
  }
}

/** Campo vazio ou inválido → 0 (comissão, faturas, folha etc.). */
function valorPremissa(v) {
  if (v === null || v === undefined || v === '') return 0
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

/** Opcional — vazio permanece null (ex.: L/muda/mês de referência). */
function quantidadePremissa(v) {
  if (v === null || v === undefined || v === '') return null
  const n = Number(v)
  return Number.isFinite(n) ? n : null
}

function premissaAlterada(p) {
  const loc = editLocal[p.id]
  const orig = original[p.id]
  if (!loc || !orig) return false
  return (
    valorPremissa(loc.valor) !== valorPremissa(orig.valor) ||
    quantidadePremissa(loc.quantidade) !== quantidadePremissa(orig.quantidade) ||
    loc.id_insumo !== orig.id_insumo ||
    loc.unidade !== orig.unidade
  )
}

function syncEditLocal() {
  for (const p of lista.value) {
    const snap = snapPremissa(p)
    editLocal[p.id] = { ...snap }
    original[p.id] = { ...snap }
  }
}

const temAlteracoes = computed(() => lista.value.some(premissaAlterada))

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    lista.value = await listPremissas()
    insumos.value = await listInsumos({ limit: 200 })
    syncEditLocal()
    for (const p of lista.value) {
      if (p.id_insumo) {
        const ins = insumos.value.find((i) => i.id === p.id_insumo)
        if (ins) p.preco_medio_insumo = ins.preco_unitario
      }
    }
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar premissas.'
  } finally {
    carregando.value = false
  }
}

function ctxPremissa(p) {
  return { ...ctx.value, premissaLocal: editLocal[p.id] }
}

function camposDe(p) {
  return uiPremissa(p, ctxPremissa(p)).campos
}

function badgeDe(p) {
  return uiPremissa(p, ctx.value).badge || (p.natureza === 'CUSTO' ? 'CMV' : 'DRE')
}

function badgeClasse(p) {
  return badgeDe(p) === 'CMV' ? 'prem-tag--cmv' : 'prem-tag--dre'
}

function insumosParaCampo(campo) {
  return filtrarInsumos(insumos.value, campo)
}

function textoCalculo(p) {
  const ui = uiPremissa(p, ctxPremissa(p))
  const local = editLocal[p.id] || p
  const merged = { ...p, ...local }
  if (merged.id_insumo) {
    const ins = insumos.value.find((i) => i.id === merged.id_insumo)
    merged.preco_medio_insumo = ins?.preco_unitario
    merged.insumo_nome = ins?.nome
    merged.insumo_unidade_medida = ins?.unidade_medida
  }
  return ui.calculo(merged, ctxPremissa(p))
}

function fmtMoeda(v) {
  if (v == null) return '—'
  return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function descartar() {
  for (const p of lista.value) {
    if (original[p.id]) editLocal[p.id] = { ...original[p.id] }
  }
}

async function salvarTudo() {
  if (!props.podeEditar || !temAlteracoes.value) return
  salvando.value = true
  try {
    await runWithLoading(async () => {
      const updates = lista.value.filter(premissaAlterada).map((p) => {
        const local = editLocal[p.id]
        const payload = {
          valor: valorPremissa(local.valor),
          quantidade: quantidadePremissa(local.quantidade),
          id_insumo: local.id_insumo,
        }
        if (p.chave === CHAVE_RECIPIENTE) {
          payload.unidade = normalizarRecipiente(local.unidade)
        }
        return updatePremissa(p.id, payload)
      })

      const recPrem = lista.value.find((x) => x.chave === CHAVE_RECIPIENTE)
      const recMudou = recPrem && premissaAlterada(recPrem)
      if (recMudou) {
        const sub = lista.value.find((x) => x.chave === CHAVE_SUBSTRATO)
        if (sub) {
          updates.push(
            updatePremissa(sub.id, {
              unidade: unidadePremissaSubstrato(normalizarRecipiente(editLocal[recPrem.id].unidade)),
            })
          )
        }
      }

      await Promise.all(updates)
      await carregar()
      emit('atualizar')
    }, 'Salvando premissas…')
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar.')
  } finally {
    salvando.value = false
  }
}

onMounted(carregar)
</script>

<style scoped>
@import './financeiro-shared.css';

.premissas-page {
  @apply pt-2 pb-24;
}

.prem-intro {
  @apply mb-8 p-4 rounded-lg border border-primary-100 bg-primary-50/40;
}

.prem-intro__lead {
  @apply mb-3;
}

.prem-intro__lista {
  @apply text-sm text-text-secondary space-y-1.5 m-0 pl-0 list-none;
}

.prem-intro__lista a {
  @apply text-primary-700 font-semibold;
}

.prem-tag {
  @apply inline-block text-[0.65rem] font-bold uppercase tracking-wide px-2 py-0.5 rounded;
}

.prem-tag--cmv {
  background: var(--color-attention-bg);
  color: var(--color-text-secondary);
}

.prem-tag--dre {
  background: var(--color-info-bg);
  color: var(--color-info-dark);
}

.prem-grupo {
  @apply mb-12;
}

.prem-grupo__head {
  @apply mb-6;
}

.prem-grupo__hint {
  @apply text-sm text-text-muted m-0;
}

.prem-secao {
  @apply mb-8;
}

.prem-secao__head {
  @apply mb-4 pb-2 border-b border-primary-50;
}

.prem-secao__titulo {
  @apply text-base font-semibold text-text-primary m-0 mb-1;
}

.prem-secao__desc {
  @apply text-sm text-text-muted m-0 max-w-3xl;
}

.prem-recipiente {
  @apply mt-3 flex flex-wrap items-center gap-3;
}

.prem-recipiente__label {
  @apply text-sm font-medium text-text-primary;
}

.prem-recipiente__opcoes {
  @apply flex flex-wrap gap-2;
}

.prem-recipiente__opcao {
  @apply inline-flex items-center gap-2 px-3 py-2 rounded-md border border-primary-100 bg-surface text-sm cursor-pointer transition-colors;
}

.prem-recipiente__opcao--ativa {
  @apply border-primary bg-primary-50 text-primary-700;
}

.prem-recipiente__opcao input {
  @apply accent-primary-600;
}

.prem-cards {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-4;
}

.prem-card {
  @apply bg-surface border rounded-lg p-4 shadow-sm flex flex-col;
}

.prem-card--cmv {
  border-color: color-mix(in srgb, var(--color-attention) 45%, var(--color-border));
}

.prem-card--dre {
  border-color: color-mix(in srgb, var(--color-info) 35%, var(--color-border));
}

.prem-card__head {
  @apply mb-2;
}

.prem-card__titulos h4 {
  @apply text-base font-semibold text-text-primary m-1 mt-0;
}

.prem-card__desc {
  @apply text-xs text-text-secondary mb-3 leading-relaxed;
}

.prem-card__campos {
  @apply space-y-4 mb-3 flex-1;
}

.prem-field {
  @apply block text-sm;
}

.prem-field__label {
  @apply font-medium text-text-primary block;
}

.prem-field__dica {
  @apply text-xs text-text-muted m-0 mb-1.5 leading-snug;
}

.prem-field__input-row {
  @apply flex items-center gap-2 mt-1;
}

.prem-field__control {
  @apply flex-1 min-w-0 px-3 py-2 border border-primary-100 rounded-md text-sm w-full;
}

.prem-field__suf {
  @apply text-xs text-text-muted whitespace-nowrap shrink-0;
}

.prem-field__aviso {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  background: var(--color-attention-bg);
  border: 1px solid var(--color-primary-100);
  border-radius: var(--radius-md);
  padding: 0.5rem;
  margin: 0;
}

.prem-field__aviso a {
  @apply font-semibold text-primary-700 ml-1;
}

.prem-card__calc {
  @apply pt-3 mt-auto border-t border-primary-50 text-sm;
}

.prem-card__calc-label {
  @apply block text-xs text-text-muted mb-1;
}

.prem-footer {
  @apply sticky bottom-0 mt-8 py-4 px-4 -mx-4 bg-surface/95 border-t border-primary-100 backdrop-blur-sm flex flex-wrap items-center justify-between gap-3 z-10;
}

.prem-footer__hint {
  font-size: 0.875rem;
  color: var(--color-attention);
  margin: 0;
}

.prem-footer__hint--ok {
  @apply text-text-muted;
}

.prem-footer__acoes {
  @apply flex gap-2 ml-auto;
}
</style>
