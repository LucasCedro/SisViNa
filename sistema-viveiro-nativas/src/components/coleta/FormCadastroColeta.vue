<template>
  <div
    v-if="aberto"
    class="modal-overlay"
    @pointerdown.self="onOverlayPointerDown"
    @pointerup.self="onOverlayPointerUp"
    @pointercancel.self="cancelarFechamentoOverlay"
  >
    <div class="modal-card" role="dialog" aria-labelledby="coleta-modal-title" @pointerdown="onModalPointerDown">
      <!-- Sucesso pós-coleta -->
      <template v-if="etapa === 'sucesso'">
        <header class="modal-header modal-header--ok">
          <div>
            <p class="modal-eyebrow">Coleta registrada</p>
            <h2 id="coleta-modal-title">Lote rastreável criado</h2>
          </div>
          <button type="button" class="btn-fechar" @click="fechar">×</button>
        </header>
        <div class="modal-body">
          <div v-if="loteGerado" class="lote-card">
            <span class="lote-card__label">Código do lote</span>
            <strong class="lote-card__code">{{ loteGerado.codigo_lote }}</strong>
            <p class="lote-card__meta">
              {{ loteGerado.especie_nome || matrizResumo?.especie_nome }} ·
              {{ quantidadeLote.toLocaleString('pt-BR') }} sementes no armazém
              <template v-if="form.sementes_reservadas_teste > 0">
                ({{ form.sementes_reservadas_teste.toLocaleString('pt-BR') }} reservadas p/ teste)
              </template>
            </p>
            <p v-if="custoCampoTotal > 0" class="lote-card__custo">
              CMV coleta: <strong>{{ fmtMoeda(custoCampoTotal) }}</strong>
              <span v-if="custoPorSemente"> · {{ fmtMoeda(custoPorSemente) }}/semente</span>
            </p>
          </div>

          <div class="fluxo-proximo">
            <h3>Próximo passo (depois, no laboratório)</h3>
            <p>
              O <strong>teste de germinação</strong> é registrado quando o resultado estiver disponível —
              geralmente dias após a coleta. Esse valor alimenta o KPI da espécie para previsão de perdas.
            </p>
            <p class="fluxo-proximo__futuro">
              Em breve: QR Code do lote para leitura em campo.
            </p>
          </div>

          <footer class="modal-footer modal-footer--stack">
            <button type="button" class="btn-prim" @click="irParaTeste">
              Registrar teste de germinação
            </button>
            <button type="button" class="btn-sec" @click="fechar">Concluir por agora</button>
          </footer>
        </div>
      </template>

      <!-- Formulário -->
      <template v-else>
        <header class="modal-header">
          <div>
            <p class="modal-eyebrow">Campo · Coleta</p>
            <h2 id="coleta-modal-title">Registrar coleta de sementes</h2>
          </div>
          <button type="button" class="btn-fechar" @click="fechar">×</button>
        </header>

        <form class="modal-body" @submit.prevent="salvar">
          <section class="form-secao">
            <h3 class="form-secao__title">Origem</h3>
            <label class="field">
              Árvore-matriz
              <select
                v-model="form.id_arvore_matriz"
                required
                :disabled="Boolean(matriz?.id)"
                @change="erro = ''"
              >
                <option value="">Selecione a matriz...</option>
                <option v-for="m in matrizesOpcoes" :key="m.id" :value="m.id">
                  {{ m.nome }} — {{ m.especie_nome || 'Espécie' }}
                  <template v-if="m.estado"> ({{ m.estado }})</template>
                </option>
              </select>
            </label>

            <div v-if="matrizResumo" class="matriz-resumo">
              <div class="matriz-resumo__item">
                <span>Espécie</span>
                <strong>{{ matrizResumo.especie_nome || '—' }}</strong>
              </div>
              <div class="matriz-resumo__item">
                <span>Local</span>
                <strong>{{ localMatriz }}</strong>
              </div>
              <div v-if="matrizResumo.taxa_germinacao != null" class="matriz-resumo__item">
                <span>Última germinação (matriz)</span>
                <strong>{{ matrizResumo.taxa_germinacao }}%</strong>
              </div>
            </div>
          </section>

          <section class="form-secao">
            <h3 class="form-secao__title">Dados da coleta</h3>
            <div class="field-row">
              <label class="field">
                Data da coleta
                <input v-model="form.data_coleta" type="date" required />
              </label>
              <label class="field">
                Quantidade coletada (total)
                <input
                  v-model.number="form.quantidade_sementes"
                  type="number"
                  min="1"
                  step="1"
                  required
                  placeholder="Ex.: 500"
                />
              </label>
            </div>

            <label class="field">
              Sementes reservadas para teste de germinação
              <input
                v-model.number="form.sementes_reservadas_teste"
                type="number"
                min="0"
                step="1"
                placeholder="0 — separadas antes do lote"
              />
              <small v-if="quantidadeLote > 0" class="field-hint">
                Entram no lote (armazém): <strong>{{ quantidadeLote.toLocaleString('pt-BR') }}</strong> sementes
              </small>
            </label>

            <label class="field">
              Observações de campo
              <textarea
                v-model="form.observacoes"
                rows="3"
                placeholder="Clima, acesso, maturidade dos frutos, equipe..."
              />
            </label>
          </section>

          <section v-if="form.gerar_lote" class="form-secao form-secao--custo">
            <h3 class="form-secao__title">Custo de campo (CMV)</h3>
            <p v-if="!refCusto.premissa_ativa" class="custo-aviso">
              Valor homem-hora ainda não configurado.
              <router-link v-if="auth.can('financeiro.view')" to="/financeiro">Financeiro → Premissas</router-link>
              <template v-else>Peça ao gestor para configurar em Financeiro → Premissas.</template>
            </p>
            <div v-else class="custo-ref">
              <span>Homem-hora</span>
              <strong>{{ fmtMoeda(refCusto.valor_hora) }}/h</strong>
            </div>
            <label class="field">
              Horas de trabalho nesta coleta
              <input
                v-model.number="form.horas_campo"
                type="number"
                min="0"
                step="0.25"
                placeholder="Ex.: 4"
              />
              <small class="field-hint">Deslocamento, coleta, beneficiamento e retorno.</small>
            </label>
            <div v-if="custoCampoTotal > 0 && quantidadeLote > 0" class="custo-preview">
              <div class="custo-preview__linha">
                <span>{{ fmtHoras(form.horas_campo) }} × {{ fmtMoeda(refCusto.valor_hora) }}/h</span>
                <strong>{{ fmtMoeda(custoCampoTotal) }}</strong>
              </div>
              <p class="custo-preview__rateio">
                Rateado em <strong>{{ quantidadeLote.toLocaleString('pt-BR') }}</strong> sementes do lote →
                <strong>{{ fmtMoeda(custoPorSemente) }}</strong>/semente no estoque
              </p>
            </div>
            <p v-else-if="refCusto.premissa_ativa" class="custo-opcional">
              Opcional — deixe em branco se ainda não quiser lançar custo.
            </p>
          </section>

          <section class="form-secao form-secao--muted">
            <h3 class="form-secao__title">Rastreabilidade</h3>
            <label class="check-card">
              <input v-model="form.gerar_lote" type="checkbox" />
              <span class="check-card__body">
                <strong>Gerar lote de sementes automaticamente</strong>
                <small>Cria código rastreável vinculado a esta coleta (recomendado).</small>
              </span>
            </label>
            <p class="dica-teste">
              As sementes do teste são separadas <em>antes</em> de formar o lote — informe acima.
              Registrar o teste depois <strong>não desconta</strong> o saldo do lote.
            </p>
          </section>

          <p v-if="auth.user" class="funcionario-info">
            Registrado por <strong>{{ auth.user.nome }}</strong>
          </p>

          <p v-if="erro" class="erro">{{ erro }}</p>

          <footer class="modal-footer">
            <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
            <button type="submit" class="btn-prim" :disabled="salvando">
              {{ salvando ? 'Salvando…' : 'Registrar coleta' }}
            </button>
          </footer>
        </form>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useColetaStore } from '@/store/coleta'
import { useAuthStore } from '@/store/auth'
import { useModalOverlayClose } from '@/composables/useModalOverlayClose'
import { getCustoCampoReferencia } from '@/services/coletasSementes'

const props = defineProps({
  aberto: { type: Boolean, default: false },
  matriz: { type: Object, default: null }
})

const emit = defineEmits(['fechar', 'salvo', 'registrar-teste'])

const store = useColetaStore()
const auth = useAuthStore()
const salvando = ref(false)
const erro = ref('')
const etapa = ref('form')
const loteGerado = ref(null)
const coletaSalva = ref(null)
const refCusto = ref({ valor_hora: 0, premissa_ativa: false, nome: 'Mão de obra de coleta' })

const matrizesOpcoes = computed(() =>
  [...store.arvoresMatriz].sort((a, b) => (a.nome || '').localeCompare(b.nome || ''))
)

const matrizResumo = computed(() => {
  const id = form.value.id_arvore_matriz
  if (!id) return props.matriz || null
  return store.arvoresMatriz.find((m) => m.id === Number(id)) || props.matriz
})

const localMatriz = computed(() => {
  const m = matrizResumo.value
  if (!m) return '—'
  const cidade = m.municipio || m.cidade
  if (cidade && m.estado) return `${cidade} / ${m.estado}`
  return cidade || m.estado || '—'
})

const formPadrao = () => ({
  id_arvore_matriz: '',
  data_coleta: new Date().toISOString().split('T')[0],
  quantidade_sementes: null,
  sementes_reservadas_teste: 0,
  horas_campo: null,
  observacoes: '',
  gerar_lote: true
})

const quantidadeLote = computed(() => {
  const total = Number(form.value.quantidade_sementes) || 0
  const reserva = Number(form.value.sementes_reservadas_teste) || 0
  return Math.max(0, total - reserva)
})

const custoCampoTotal = computed(() => {
  const h = Number(form.value.horas_campo) || 0
  const vh = Number(refCusto.value.valor_hora) || 0
  if (h <= 0 || vh <= 0) return 0
  return Math.round(h * vh * 100) / 100
})

const custoPorSemente = computed(() => {
  if (!custoCampoTotal.value || !quantidadeLote.value) return 0
  return Math.round((custoCampoTotal.value / quantidadeLote.value) * 10000) / 10000
})

function fmtMoeda(v) {
  return Number(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function fmtHoras(h) {
  const n = Number(h) || 0
  return n.toLocaleString('pt-BR', { maximumFractionDigits: 2 })
}

async function carregarRefCusto() {
  try {
    refCusto.value = await getCustoCampoReferencia()
  } catch {
    refCusto.value = { valor_hora: 0, premissa_ativa: false, nome: 'Mão de obra de coleta' }
  }
}

const form = ref(formPadrao())

watch(
  () => [props.aberto, props.matriz],
  ([aberto]) => {
    if (!aberto) return
    erro.value = ''
    etapa.value = 'form'
    loteGerado.value = null
    coletaSalva.value = null
    form.value = formPadrao()
    if (props.matriz?.id) {
      form.value.id_arvore_matriz = props.matriz.id
    }
    carregarRefCusto()
  }
)

function fecharInterno() {
  emit('fechar')
}

const {
  onModalPointerDown,
  onOverlayPointerDown,
  onOverlayPointerUp,
  cancelarFechamentoOverlay,
  resetOverlayPress,
} = useModalOverlayClose(fecharInterno)

function fechar() {
  resetOverlayPress()
  fecharInterno()
}

function irParaTeste() {
  if (loteGerado.value) {
    emit('registrar-teste', loteGerado.value)
  }
  fechar()
}

async function salvar() {
  erro.value = ''
  if (!form.value.id_arvore_matriz) {
    erro.value = 'Selecione a matriz.'
    return
  }
  if (!form.value.quantidade_sementes || form.value.quantidade_sementes < 1) {
    erro.value = 'Informe a quantidade coletada (mínimo 1).'
    return
  }
  const reserva = Number(form.value.sementes_reservadas_teste) || 0
  if (reserva < 0) {
    erro.value = 'Reserva para teste não pode ser negativa.'
    return
  }
  if (reserva >= form.value.quantidade_sementes) {
    erro.value = 'A reserva para teste deve ser menor que a quantidade coletada.'
    return
  }
  if (form.value.gerar_lote && quantidadeLote.value < 1) {
    erro.value = 'O lote precisa de ao menos 1 semente após a reserva para teste.'
    return
  }
  salvando.value = true
  try {
    const resultado = await store.registrarColeta({
      id_arvore_matriz: Number(form.value.id_arvore_matriz),
      data_coleta: form.value.data_coleta,
      quantidade_sementes: form.value.quantidade_sementes,
      sementes_reservadas_teste: reserva,
      horas_campo: form.value.horas_campo > 0 ? form.value.horas_campo : null,
      observacoes: form.value.observacoes || null,
      gerar_lote: form.value.gerar_lote
    })
    coletaSalva.value = resultado
    emit('salvo', resultado)

    if (form.value.gerar_lote && resultado.lotes?.length) {
      loteGerado.value = resultado.lotes[0]
      etapa.value = 'sucesso'
    } else {
      fechar()
    }
  } catch (e) {
    const detail = e.response?.data?.detail
    erro.value = Array.isArray(detail)
      ? detail.map((d) => d.msg || d).join(', ')
      : detail || e.message || 'Erro ao registrar coleta'
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1500;
  background: rgba(34, 42, 28, 0.48);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 520px;
  max-height: 92vh;
  overflow: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.modal-header--ok {
  background: linear-gradient(180deg, var(--color-success-bg) 0%, var(--color-surface) 100%);
}

.modal-eyebrow {
  margin: 0 0 0.2rem;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.btn-fechar {
  border: none;
  background: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-muted);
  line-height: 1;
}

.modal-body {
  padding: 1.25rem 1.5rem 1.5rem;
}

.form-secao {
  margin-bottom: 1.25rem;
}

.form-secao--muted {
  padding: 1rem;
  border-radius: var(--radius-md);
  background: var(--color-background);
  border: 1px solid var(--color-border-subtle);
}

.form-secao__title {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-secondary);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.875rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.field input,
.field select,
.field textarea {
  font-weight: 400;
  padding: 0.6rem 0.75rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

.field-hint {
  font-size: 0.8125rem;
  font-weight: 400;
  color: var(--color-text-muted);
  margin-top: 0.15rem;
}

.field-hint strong {
  color: var(--color-primary-700);
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.matriz-resumo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.65rem;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary-100);
}

.matriz-resumo__item span {
  display: block;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  margin-bottom: 0.15rem;
}

.matriz-resumo__item strong {
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.check-card {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  cursor: pointer;
  margin-bottom: 0.75rem;
}

.check-card input {
  margin-top: 0.2rem;
  accent-color: var(--color-primary);
}

.check-card__body strong {
  display: block;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.check-card__body small {
  display: block;
  margin-top: 0.15rem;
  font-size: 0.8125rem;
  font-weight: 400;
  color: var(--color-text-muted);
  line-height: 1.4;
}

.dica-teste {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-text-muted);
}

.funcionario-info {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  margin: 0 0 1rem;
}

.form-secao--custo {
  background: var(--color-success-bg);
  border: 1px solid var(--color-primary-100);
  border-radius: var(--radius-md);
  padding: 0.875rem 1rem;
}

.custo-aviso {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-analog-2);
  line-height: 1.45;
}

.custo-aviso a {
  color: var(--color-primary);
  font-weight: 600;
}

.custo-ref {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.65rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.custo-ref strong {
  font-size: 1rem;
  color: var(--color-success);
}

.custo-preview {
  margin-top: 0.35rem;
  padding: 0.65rem 0.75rem;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.custo-preview__linha {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.custo-preview__rateio {
  margin: 0.35rem 0 0;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  line-height: 1.45;
}

.custo-opcional {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.lote-card__custo {
  margin: 0.5rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.lote-card {
  text-align: center;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
  border-radius: var(--radius-lg);
  background: var(--color-primary-subtle);
  border: 1px dashed var(--color-primary-200);
}

.lote-card__label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
}

.lote-card__code {
  display: block;
  margin: 0.35rem 0;
  font-size: 1.375rem;
  font-family: var(--font-mono, monospace);
  color: var(--color-primary-700);
  letter-spacing: 0.02em;
}

.lote-card__meta {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.fluxo-proximo {
  margin-bottom: 1.25rem;
}

.fluxo-proximo h3 {
  margin: 0 0 0.5rem;
  font-size: 0.9375rem;
}

.fluxo-proximo p {
  margin: 0 0 0.65rem;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-secondary);
}

.fluxo-proximo__futuro {
  font-size: 0.8125rem !important;
  color: var(--color-text-muted) !important;
  font-style: italic;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.modal-footer--stack {
  flex-direction: column;
  align-items: stretch;
}

.btn-sec,
.btn-prim {
  padding: 0.65rem 1.1rem;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
}

.btn-sec {
  background: var(--color-surface-muted);
  color: var(--color-text-secondary);
}

.btn-prim {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-prim:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.erro {
  color: var(--color-error-dark);
  font-size: 0.875rem;
  background: var(--color-error-bg);
  padding: 0.6rem 0.75rem;
  border-radius: var(--radius-md);
}

@media (max-width: 520px) {
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
