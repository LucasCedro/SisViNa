<template>
  <div class="panel">
    <header class="panel-intro">
      <h2 class="panel-title">Área de rustificação</h2>
      <p class="panel-lead">
        Envie mudas <strong>já aptas</strong> do canteiro para a área de rustificação.
        Antecipar mudas ainda em crescimento é decisão gerencial — fica separada abaixo.
      </p>
    </header>

    <details class="info-box">
      <summary>O que é rustificação?</summary>
      <p>
        Adaptação ao sol e condições do plantio definitivo. Recomenda-se ~30 dias na área antes de
        liberar para venda.
      </p>
    </details>

    <div v-if="!podeOperar" class="alert alert-error">Seu perfil só permite visualização.</div>

    <div class="rust-kpis" aria-label="Resumo da rustificação">
      <article class="rust-kpi rust-kpi--crescimento">
        <span class="rust-kpi__valor">{{ totais.emCrescimento.toLocaleString('pt-BR') }}</span>
        <span class="rust-kpi__label">Em crescimento (canteiro)</span>
      </article>
      <article class="rust-kpi rust-kpi--aptas">
        <span class="rust-kpi__valor">{{ totais.aptasEnviar.toLocaleString('pt-BR') }}</span>
        <span class="rust-kpi__label">Aptas para enviar</span>
      </article>
      <article class="rust-kpi rust-kpi--area">
        <span class="rust-kpi__valor">{{ totais.naArea.toLocaleString('pt-BR') }}</span>
        <span class="rust-kpi__label">Na área de rustificação</span>
      </article>
    </div>

    <ProducaoModoOperacao v-model:modo="modo">
      <template #default="{ modo: m }">
        <template v-if="m === PRODUCAO_MODO.MASSA">
          <!-- 1. Fluxo principal -->
          <section class="rust-bloco rust-bloco--principal">
            <header class="rust-bloco__header">
              <span class="rust-badge rust-badge--principal">Fluxo usual</span>
              <h3 class="rust-bloco__titulo">Enviar à rustificação</h3>
              <p class="rust-bloco__desc">
                Mudas <strong>já aptas</strong>, ainda no canteiro. Esta ação move para a área de
                rustificação — é o passo que você faz na maioria dos dias.
              </p>
            </header>
            <ProducaoPainelLote
              ref="painelTransferirRef"
              etapa="canteiro_apta_rustificacao"
              titulo-botao="Enviar à rustificação"
              :pode-operar="podeOperar"
              :filtro-locais="canteiros"
              filtro-local-label="Canteiro de origem"
              vazio="Nenhuma muda apta aguardando envio no canteiro."
              mensagem-loading="Enviando à rustificação…"
              :on-executar="executarTransferirLote"
              @concluido="aoConcluirTransferir"
            />
          </section>

          <!-- 2. Decisão gerencial (depois, evidenciada) -->
          <section class="rust-bloco rust-bloco--sensivel">
            <header class="rust-bloco__header">
              <span class="rust-badge rust-badge--alerta">Decisão gerencial</span>
              <h3 class="rust-bloco__titulo">Antecipar mudas em crescimento</h3>
              <p class="rust-bloco__alerta">
                <strong>Atenção:</strong> aqui você marca mudas que <em>ainda estão em crescimento</em>
                como aptas — antes do tempo usual. Isso <strong>não envia</strong> à rustificação; só
                libera para o bloco acima. Use apenas quando a muda já estiver pronta na prática.
              </p>
            </header>
            <ProducaoPainelLote
              ref="painelMarcarRef"
              etapa="canteiro_crescimento"
              titulo-botao="Antecipar aptidão (em crescimento)"
              :pode-operar="podeOperar"
              :filtro-locais="canteiros"
              filtro-local-label="Canteiro"
              vazio="Nenhuma muda em crescimento no canteiro."
              mensagem-loading="Marcando aptas…"
              :on-executar="executarMarcarLote"
              @concluido="aoConcluirMarcar"
            />
          </section>
        </template>

        <template v-else>
          <div class="toolbar">
            <label class="field field--sm">
              Canteiro
              <select v-model="filtroCanteiro" @change="carregarDetalhe">
                <option value="">Todos</option>
                <option v-for="c in canteiros" :key="c.id" :value="c.id">{{ c.nome }}</option>
              </select>
            </label>
          </div>

          <!-- 1. Enviar aptas (principal) -->
          <section class="rust-bloco rust-bloco--principal">
            <header class="rust-bloco__header">
              <span class="rust-badge rust-badge--principal">Fluxo usual</span>
              <h3 class="rust-bloco__titulo">Enviar à rustificação</h3>
              <p class="rust-bloco__desc">
                Selecione mudas <strong>aptas</strong> no canteiro para mover à área de rustificação.
              </p>
            </header>
            <div class="stage-header">
              <button
                type="button"
                class="btn btn-primary"
                :disabled="!podeOperar || !selAptas.length || transferindo || marcando"
                @click="confirmarTransferir"
              >
                Enviar {{ selAptas.length || 0 }} muda(s) à rustificação
              </button>
            </div>
            <TabelaMudas
              v-model:selecionados="selAptas"
              :lista="aptasCanteiro"
              :pode-operar="podeOperar"
              empty="Nenhuma muda apta aguardando envio no canteiro."
            />
          </section>

          <section class="rust-bloco rust-bloco--info">
            <h3 class="rust-bloco__titulo">Na área de rustificação</h3>
            <p class="rust-bloco__desc">
              {{ naRust.length.toLocaleString('pt-BR') }} muda(s) em adaptação.
              Libere para venda na guia <strong>Liberar para venda</strong> após o período recomendado.
            </p>
            <TabelaMudas
              :lista="naRust"
              :selecionados="[]"
              :pode-operar="false"
              empty="Nenhuma muda na área de rustificação."
            />
          </section>

          <!-- 2. Antecipar crescimento (sensível, depois) -->
          <section class="rust-bloco rust-bloco--sensivel">
            <header class="rust-bloco__header">
              <span class="rust-badge rust-badge--alerta">Decisão gerencial</span>
              <h3 class="rust-bloco__titulo">Antecipar mudas em crescimento</h3>
              <p class="rust-bloco__alerta">
                <strong>Atenção:</strong> estas mudas ainda estão <em>em crescimento</em>. Ao marcar,
                você apenas as torna aptas — ainda precisará enviá-las no bloco acima.
                Não confunda com o envio à área de rustificação.
              </p>
            </header>
            <div class="stage-header">
              <button
                type="button"
                class="btn btn-warning"
                :disabled="!podeOperar || !selCrescimento.length || marcando || transferindo"
                @click="confirmarAntecipar"
              >
                Antecipar {{ selCrescimento.length || 0 }} muda(s) em crescimento
              </button>
            </div>
            <TabelaMudas
              v-model:selecionados="selCrescimento"
              :lista="pendentes"
              :pode-operar="podeOperar"
              empty="Nenhuma muda em crescimento no canteiro."
            />
          </section>
        </template>
      </template>
    </ProducaoModoOperacao>

    <dialog ref="dialogTransferir" class="app-dialog" @cancel.prevent="fecharDialog('dialogTransferir')">
      <form class="dialog-panel" @submit.prevent="executarTransferirConfirmado">
        <header class="dialog-panel__header">
          <h3>Enviar à rustificação</h3>
        </header>
        <div class="dialog-panel__body">
          <p>
            Mover <strong>{{ selAptas.length }}</strong> muda(s) <strong>aptas</strong> do canteiro
            para a área de rustificação?
          </p>
        </div>
        <footer class="dialog-panel__footer">
          <button type="button" class="btn btn-secondary" @click="fecharDialog('dialogTransferir')">
            Cancelar
          </button>
          <button type="submit" class="btn btn-primary">Confirmar envio</button>
        </footer>
      </form>
    </dialog>

    <dialog ref="dialogAntecipar" class="app-dialog" @cancel.prevent="fecharDialog('dialogAntecipar')">
      <form class="dialog-panel" @submit.prevent="executarAnteciparConfirmado">
        <header class="dialog-panel__header">
          <h3>Antecipar aptidão</h3>
        </header>
        <div class="dialog-panel__body">
          <p class="dialog-aviso">
            Você vai marcar <strong>{{ selCrescimento.length }}</strong> muda(s) que ainda estão
            <strong>em crescimento</strong> como aptas para rustificação.
          </p>
          <p>Elas <strong>não serão enviadas</strong> automaticamente — ficarão aptas no canteiro até você usar
            <em>Enviar à rustificação</em>.</p>
          <p>Confirma esta decisão gerencial?</p>
        </div>
        <footer class="dialog-panel__footer">
          <button type="button" class="btn btn-secondary" @click="fecharDialog('dialogAntecipar')">
            Cancelar
          </button>
          <button type="submit" class="btn btn-warning">Sim, antecipar aptidão</button>
        </footer>
      </form>
    </dialog>

    <ul v-if="avisos.length" class="alert alert-warning avisos-list">
      <li v-for="(a, i) in avisos" :key="i">{{ a }}</li>
    </ul>
    <p v-if="erro" class="alert alert-error">{{ erro }}</p>
    <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { listCanteiros } from '@/services/canteiros'
import {
  listEmCrescimentoCanteiro,
  listAptasRustificacaoCanteiro,
  listEmRustificacao,
  getResumoOperacaoLote,
  transferirRustificacao,
  transferirRustificacaoLote,
  atualizarEstagioProducao,
  atualizarEstagioLote,
} from '@/services/plantas'
import { usePermissions } from '@/composables/usePermissions'
import { useGlobalLoading } from '@/composables/useGlobalLoading'
import { PRODUCAO_MODO } from '@/constants/producaoUi'
import ProducaoModoOperacao from './ProducaoModoOperacao.vue'
import ProducaoPainelLote from './ProducaoPainelLote.vue'
import TabelaMudas from './ProducaoTabelaMudas.vue'

const emit = defineEmits(['atualizado'])
const { runWithLoading } = useGlobalLoading()
const { can } = usePermissions()
const podeOperar = computed(() => can('producao.transfer'))

const modo = ref(PRODUCAO_MODO.MASSA)
const pendentes = ref([])
const aptasCanteiro = ref([])
const naRust = ref([])
const canteiros = ref([])
const totais = ref({ emCrescimento: 0, aptasEnviar: 0, naArea: 0 })
const selCrescimento = ref([])
const selAptas = ref([])
const filtroCanteiro = ref('')
const marcando = ref(false)
const transferindo = ref(false)
const erro = ref('')
const sucesso = ref('')
const avisos = ref([])
const painelMarcarRef = ref(null)
const painelTransferirRef = ref(null)
const dialogTransferir = ref(null)
const dialogAntecipar = ref(null)

function somarResumo(rows) {
  return (rows || []).reduce((s, r) => s + (r.disponivel || 0), 0)
}

async function carregarTotais() {
  const [cresc, aptas, naArea] = await Promise.all([
    getResumoOperacaoLote('canteiro_crescimento'),
    getResumoOperacaoLote('canteiro_apta_rustificacao'),
    getResumoOperacaoLote('rustificacao'),
  ])
  totais.value = {
    emCrescimento: somarResumo(cresc),
    aptasEnviar: somarResumo(aptas),
    naArea: somarResumo(naArea),
  }
}

async function carregar() {
  await carregarTotais()
  if (modo.value === PRODUCAO_MODO.MASSA) {
    await nextTick()
    painelTransferirRef.value?.carregarResumo?.()
    painelMarcarRef.value?.carregarResumo?.()
    return
  }
  await carregarDetalhe()
}

async function carregarDetalhe() {
  erro.value = ''
  const params = { limit: 2000 }
  if (filtroCanteiro.value) params.id_canteiro = Number(filtroCanteiro.value)
  const [c, a, r] = await Promise.all([
    listEmCrescimentoCanteiro(params),
    listAptasRustificacaoCanteiro(params),
    listEmRustificacao({ limit: 2000 }),
  ])
  pendentes.value = c
  aptasCanteiro.value = a
  naRust.value = r
  selCrescimento.value = []
  selAptas.value = []
  totais.value = {
    emCrescimento: c.length,
    aptasEnviar: a.length,
    naArea: r.length,
  }
}

async function executarMarcarLote(grupos) {
  return atualizarEstagioLote({ estagio_producao: 'apta_rustificacao', grupos })
}

async function executarTransferirLote(grupos) {
  return transferirRustificacaoLote({ grupos })
}

function aoConcluirMarcar() {
  carregarTotais()
  painelTransferirRef.value?.carregarResumo?.()
  emit('atualizado')
}

function aoConcluirTransferir() {
  carregar()
  emit('atualizado')
}

function fecharDialog(nome) {
  if (nome === 'dialogTransferir') dialogTransferir.value?.close()
  if (nome === 'dialogAntecipar') dialogAntecipar.value?.close()
}

function confirmarTransferir() {
  dialogTransferir.value?.showModal()
}

function confirmarAntecipar() {
  dialogAntecipar.value?.showModal()
}

async function executarTransferirConfirmado() {
  fecharDialog('dialogTransferir')
  await transferirAptasRustificacao()
}

async function executarAnteciparConfirmado() {
  fecharDialog('dialogAntecipar')
  await marcarAptasRustificacao()
}

onMounted(async () => {
  const cant = await listCanteiros({ ativo: true })
  canteiros.value = cant.filter((c) => c.tipo_local === 'canteiro')
  await carregar()
})

watch(modo, carregar)

defineExpose({ carregar })

async function marcarAptasRustificacao() {
  marcando.value = true
  erro.value = ''
  sucesso.value = ''
  try {
    await runWithLoading(async () => {
      const res = await atualizarEstagioProducao({
        ids_plantas: selCrescimento.value.map(Number),
        estagio_producao: 'apta_rustificacao',
      })
      sucesso.value = `${res.atualizadas} muda(s) antecipada(s). Agora estão aptas — use "Enviar à rustificação" quando for o caso.`
      await carregarDetalhe()
    }, 'Marcando aptas…')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro na operação.'
  } finally {
    marcando.value = false
    selCrescimento.value = []
  }
  emit('atualizado')
}

async function transferirAptasRustificacao() {
  transferindo.value = true
  erro.value = ''
  sucesso.value = ''
  avisos.value = []
  try {
    await runWithLoading(async () => {
      const res = await transferirRustificacao({ ids_plantas: selAptas.value.map(Number) })
      avisos.value = res.avisos || []
      sucesso.value = `${res.transferidas} muda(s) enviada(s) à área de rustificação.`
      await carregarDetalhe()
    }, 'Enviando à rustificação…')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao transferir.'
  } finally {
    transferindo.value = false
    selAptas.value = []
  }
  emit('atualizado')
}
</script>

<style scoped>
@import './producao-panel-shared.css';
@import './producao-panel-blocks.css';

.rust-kpis { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-lg); }
.rust-kpi { background: var(--color-surface); border: 1px solid var(--color-border-subtle); border-radius: var(--radius-lg); padding: 1rem 1.125rem; display: flex; flex-direction: column; gap: 0.25rem; }
.rust-kpi__valor { font-size: 1.5rem; font-weight: 700; line-height: 1.2; }
.rust-kpi__label { font-size: 0.75rem; color: var(--color-text-muted); line-height: 1.35; }
.rust-kpi--crescimento .rust-kpi__valor { color: var(--color-text-secondary); }
.rust-kpi--aptas { border-color: color-mix(in srgb, var(--color-primary) 35%, var(--color-border-subtle)); background: color-mix(in srgb, var(--color-primary) 5%, var(--color-surface)); }
.rust-kpi--aptas .rust-kpi__valor { color: var(--color-primary); }
.rust-kpi--area .rust-kpi__valor { color: var(--color-text-primary); }
.rust-bloco { border-radius: var(--radius-lg); padding: var(--spacing-lg); margin-bottom: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-md); }
.rust-bloco--principal { border: 2px solid color-mix(in srgb, var(--color-primary) 40%, transparent); background: color-mix(in srgb, var(--color-primary) 4%, var(--color-surface)); }
.rust-bloco--sensivel { border: 2px solid color-mix(in srgb, #d97706 45%, transparent); background: color-mix(in srgb, #fef3c7 50%, var(--color-surface)); }
.rust-bloco--info { border: 1px solid var(--color-border-subtle); background: var(--color-surface-muted, #f8f9fa); }
.rust-bloco__header { display: flex; flex-direction: column; gap: 0.35rem; }
.rust-bloco__titulo { margin: 0; font-size: 1.0625rem; font-weight: 600; }
.rust-bloco__desc { margin: 0; font-size: 0.875rem; color: var(--color-text-secondary); line-height: 1.45; }
.rust-bloco__alerta { margin: 0; font-size: 0.875rem; color: #92400e; line-height: 1.5; padding: 0.65rem 0.85rem; background: #fffbeb; border-radius: var(--radius-md); border: 1px solid #fcd34d; }
.rust-badge { align-self: flex-start; font-size: 0.6875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; padding: 0.2rem 0.55rem; border-radius: var(--radius-full); }
.rust-badge--principal { background: var(--color-primary-subtle); color: var(--color-primary-700, var(--color-primary)); }
.rust-badge--alerta { background: #fef3c7; color: #92400e; }
@media (max-width: 720px) { .rust-kpis { grid-template-columns: 1fr; } }
</style>
