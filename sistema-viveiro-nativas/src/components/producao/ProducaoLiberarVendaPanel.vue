<template>
  <div class="panel">
    <header class="panel-intro">
      <h2 class="panel-title">Liberar para venda</h2>
      <p class="panel-lead">
        Libere mudas que concluíram a rustificação para o estoque comercial.
        Mudas com <strong>menos de {{ RUSTIFICACAO_DIAS_MINIMO }} dias</strong> na área ficam
        separadas — liberá-las é decisão gerencial.
      </p>
    </header>

    <details class="info-box">
      <summary>Quando liberar para venda?</summary>
      <p>
        Recomenda-se aguardar pelo menos {{ RUSTIFICACAO_DIAS_MINIMO }} dias na rustificação para
        adaptação ao sol. O sistema permite liberar antes, mas o gerente deve estar ciente do risco
        operacional.
      </p>
    </details>

    <div v-if="!podeOperar" class="alert alert-error">Seu perfil só permite visualização.</div>

    <div class="prod-kpis" aria-label="Resumo para liberação">
      <article class="prod-kpi prod-kpi--principal">
        <span class="prod-kpi__valor">{{ totais.prontas.toLocaleString('pt-BR') }}</span>
        <span class="prod-kpi__label">≥ {{ RUSTIFICACAO_DIAS_MINIMO }} dias (fluxo usual)</span>
      </article>
      <article class="prod-kpi prod-kpi--alerta">
        <span class="prod-kpi__valor">{{ totais.antesPrazo.toLocaleString('pt-BR') }}</span>
        <span class="prod-kpi__label">&lt; {{ RUSTIFICACAO_DIAS_MINIMO }} dias (decisão gerencial)</span>
      </article>
      <article class="prod-kpi prod-kpi--muted">
        <span class="prod-kpi__valor">{{ totais.total.toLocaleString('pt-BR') }}</span>
        <span class="prod-kpi__label">Total em rustificação</span>
      </article>
    </div>

    <ProducaoModoOperacao v-model:modo="modo">
      <template #default="{ modo: m }">
        <template v-if="m === PRODUCAO_MODO.MASSA">
          <section class="prod-bloco prod-bloco--principal">
            <header class="prod-bloco__header">
              <span class="prod-badge prod-badge--principal">Fluxo usual</span>
              <h3 class="prod-bloco__titulo">Liberar mudas no prazo</h3>
              <p class="prod-bloco__desc">
                Mudas com <strong>{{ RUSTIFICACAO_DIAS_MINIMO }} dias ou mais</strong> na área de
                rustificação — prontas para o estoque comercial.
              </p>
            </header>
            <ProducaoPainelLote
              ref="painelProntasRef"
              etapa="rustificacao_pronta_venda"
              titulo-botao="Liberar para venda"
              :pode-operar="podeOperar"
              :mostrar-busca="true"
              vazio="Nenhuma muda com prazo mínimo cumprido."
              mensagem-loading="Liberando para venda…"
              :on-executar="executarLoteProntas"
              @concluido="aoConcluirLote"
            />
          </section>

          <section class="prod-bloco prod-bloco--sensivel">
            <header class="prod-bloco__header">
              <span class="prod-badge prod-badge--alerta">Decisão gerencial</span>
              <h3 class="prod-bloco__titulo">Liberar antes do prazo</h3>
              <p class="prod-bloco__alerta">
                <strong>Atenção:</strong> estas mudas ainda têm <em>menos de
                {{ RUSTIFICACAO_DIAS_MINIMO }} dias</em> na rustificação. Liberar para venda agora
                exige ciência do gerente — a adaptação ao sol pode estar incompleta.
              </p>
            </header>
            <ProducaoPainelLote
              ref="painelAntesPrazoRef"
              etapa="rustificacao_antes_prazo"
              titulo-botao="Liberar antes do prazo (gerencial)"
              :pode-operar="podeOperar"
              :mostrar-busca="true"
              vazio="Nenhuma muda abaixo do prazo recomendado."
              mensagem-loading="Liberando para venda…"
              :on-executar="executarLoteAntesPrazo"
              @concluido="aoConcluirLote"
            />
          </section>
        </template>

        <template v-else>
          <section class="prod-bloco prod-bloco--principal">
            <header class="prod-bloco__header">
              <span class="prod-badge prod-badge--principal">Fluxo usual</span>
              <h3 class="prod-bloco__titulo">Liberar mudas no prazo</h3>
              <p class="prod-bloco__desc">
                Selecione mudas com <strong>{{ RUSTIFICACAO_DIAS_MINIMO }} dias ou mais</strong> na
                rustificação.
              </p>
            </header>
            <div class="stage-header">
              <button
                type="button"
                class="btn btn-primary"
                :disabled="!podeOperar || !selProntas.length || processando"
                @click="confirmarLiberarProntas"
              >
                Liberar {{ selProntas.length || 0 }} muda(s) para venda
              </button>
            </div>
            <TabelaMudas
              v-model:selecionados="selProntas"
              :lista="prontas"
              :pode-operar="podeOperar"
              rotulo-dias="Dias rust."
              empty="Nenhuma muda com prazo mínimo cumprido."
            />
          </section>

          <section class="prod-bloco prod-bloco--sensivel">
            <header class="prod-bloco__header">
              <span class="prod-badge prod-badge--alerta">Decisão gerencial</span>
              <h3 class="prod-bloco__titulo">Liberar antes do prazo</h3>
              <p class="prod-bloco__alerta">
                <strong>Atenção:</strong> mudas com <em>menos de {{ RUSTIFICACAO_DIAS_MINIMO }}
                dias</em> na rustificação. Confirme apenas se o gerente estiver ciente.
              </p>
            </header>
            <div class="stage-header">
              <button
                type="button"
                class="btn btn-warning"
                :disabled="!podeOperar || !selAntesPrazo.length || processando"
                @click="confirmarLiberarAntesPrazo"
              >
                Liberar {{ selAntesPrazo.length || 0 }} muda(s) antes do prazo
              </button>
            </div>
            <TabelaMudas
              v-model:selecionados="selAntesPrazo"
              :lista="antesPrazo"
              :pode-operar="podeOperar"
              rotulo-dias="Dias rust."
              destacar-abaixo-prazo
              empty="Nenhuma muda abaixo do prazo recomendado."
            />
          </section>
        </template>
      </template>
    </ProducaoModoOperacao>

    <dialog ref="dialogProntas" class="app-dialog" @cancel.prevent="fecharDialog('dialogProntas')">
      <form class="dialog-panel" @submit.prevent="executarLiberarProntas">
        <header class="dialog-panel__header">
          <h3>Liberar para venda</h3>
        </header>
        <div class="dialog-panel__body">
          <p>
            Liberar <strong>{{ selProntas.length }}</strong> muda(s) com prazo de rustificação
            cumprido para o estoque comercial?
          </p>
        </div>
        <footer class="dialog-panel__footer">
          <button type="button" class="btn btn-secondary" @click="fecharDialog('dialogProntas')">
            Cancelar
          </button>
          <button type="submit" class="btn btn-primary">Confirmar liberação</button>
        </footer>
      </form>
    </dialog>

    <dialog ref="dialogAntesPrazo" class="app-dialog" @cancel.prevent="fecharDialog('dialogAntesPrazo')">
      <form class="dialog-panel" @submit.prevent="executarLiberarAntesPrazo">
        <header class="dialog-panel__header">
          <h3>Liberar antes do prazo</h3>
        </header>
        <div class="dialog-panel__body">
          <p class="dialog-aviso">
            Você vai liberar <strong>{{ selAntesPrazo.length }}</strong> muda(s) com
            <strong>menos de {{ RUSTIFICACAO_DIAS_MINIMO }} dias</strong> na rustificação.
          </p>
          <p>O gerente está ciente de que a adaptação ao sol pode estar incompleta?</p>
        </div>
        <footer class="dialog-panel__footer">
          <button type="button" class="btn btn-secondary" @click="fecharDialog('dialogAntesPrazo')">
            Cancelar
          </button>
          <button type="submit" class="btn btn-warning">Sim, liberar (decisão gerencial)</button>
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
import {
  listEmRustificacao,
  getResumoOperacaoLote,
  atualizarEstagioProducao,
  atualizarEstagioLote,
} from '@/services/plantas'
import { usePermissions } from '@/composables/usePermissions'
import { useGlobalLoading } from '@/composables/useGlobalLoading'
import { PRODUCAO_MODO, RUSTIFICACAO_DIAS_MINIMO } from '@/constants/producaoUi'
import ProducaoModoOperacao from './ProducaoModoOperacao.vue'
import ProducaoPainelLote from './ProducaoPainelLote.vue'
import TabelaMudas from './ProducaoTabelaMudas.vue'

const emit = defineEmits(['atualizado'])
const { runWithLoading } = useGlobalLoading()
const { can } = usePermissions()
const podeOperar = computed(() => can('producao.transfer'))

const modo = ref(PRODUCAO_MODO.MASSA)
const todas = ref([])
const selProntas = ref([])
const selAntesPrazo = ref([])
const totais = ref({ prontas: 0, antesPrazo: 0, total: 0 })
const processando = ref(false)
const erro = ref('')
const sucesso = ref('')
const avisos = ref([])
const painelProntasRef = ref(null)
const painelAntesPrazoRef = ref(null)
const dialogProntas = ref(null)
const dialogAntesPrazo = ref(null)

const prontas = computed(() =>
  todas.value.filter((p) => p.rustificacao_ok !== false)
)
const antesPrazo = computed(() =>
  todas.value.filter((p) => p.rustificacao_ok === false)
)

function somarResumo(rows) {
  return (rows || []).reduce((s, r) => s + (r.disponivel || 0), 0)
}

async function carregarTotais() {
  const [ok, antes, total] = await Promise.all([
    getResumoOperacaoLote('rustificacao_pronta_venda'),
    getResumoOperacaoLote('rustificacao_antes_prazo'),
    getResumoOperacaoLote('rustificacao'),
  ])
  totais.value = {
    prontas: somarResumo(ok),
    antesPrazo: somarResumo(antes),
    total: somarResumo(total),
  }
}

async function carregar() {
  await carregarTotais()
  if (modo.value === PRODUCAO_MODO.MASSA) {
    await nextTick()
    painelProntasRef.value?.carregarResumo?.()
    painelAntesPrazoRef.value?.carregarResumo?.()
    return
  }
  todas.value = await listEmRustificacao({ limit: 2000 })
  selProntas.value = []
  selAntesPrazo.value = []
  totais.value = {
    prontas: prontas.value.length,
    antesPrazo: antesPrazo.value.length,
    total: todas.value.length,
  }
}

async function executarLoteProntas(grupos) {
  return atualizarEstagioLote({
    estagio_producao: 'apta_venda',
    etapa_origem: 'rustificacao_pronta_venda',
    grupos,
  })
}

async function executarLoteAntesPrazo(grupos) {
  const res = await atualizarEstagioLote({
    estagio_producao: 'apta_venda',
    etapa_origem: 'rustificacao_antes_prazo',
    grupos,
  })
  if (res.avisos?.length) avisos.value = res.avisos
  return res
}

function aoConcluirLote() {
  carregar()
  emit('atualizado')
}

function fecharDialog(nome) {
  if (nome === 'dialogProntas') dialogProntas.value?.close()
  if (nome === 'dialogAntesPrazo') dialogAntesPrazo.value?.close()
}

function confirmarLiberarProntas() {
  dialogProntas.value?.showModal()
}

function confirmarLiberarAntesPrazo() {
  dialogAntesPrazo.value?.showModal()
}

async function executarLiberarProntas() {
  fecharDialog('dialogProntas')
  await liberarDetalhe(selProntas, 'prontas')
}

async function executarLiberarAntesPrazo() {
  fecharDialog('dialogAntesPrazo')
  await liberarDetalhe(selAntesPrazo, 'antes')
}

async function liberarDetalhe(selecaoRef, tipo) {
  processando.value = true
  erro.value = ''
  sucesso.value = ''
  if (tipo === 'antes') avisos.value = []
  try {
    await runWithLoading(async () => {
      const res = await atualizarEstagioProducao({
        ids_plantas: selecaoRef.value.map(Number),
        estagio_producao: 'apta_venda',
      })
      if (res.avisos?.length) avisos.value = res.avisos
      const msg =
        tipo === 'antes'
          ? `${res.atualizadas} muda(s) liberada(s) antes do prazo (decisão gerencial).`
          : `${res.atualizadas} muda(s) liberada(s) para venda.`
      sucesso.value = msg
      await carregar()
      emit('atualizado')
    }, 'Liberando para venda…')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao liberar.'
  } finally {
    processando.value = false
    selecaoRef.value = []
  }
}

watch(modo, carregar)
onMounted(carregar)
defineExpose({ carregar })
</script>

<style scoped>
@import './producao-panel-shared.css';
@import './producao-panel-blocks.css';
</style>
