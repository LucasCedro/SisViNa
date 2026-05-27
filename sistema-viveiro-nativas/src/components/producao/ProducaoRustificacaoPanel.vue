<template>
  <div class="panel">
    <header class="panel-intro">
      <h2 class="panel-title">Área de rustificação</h2>
      <p class="panel-lead">
        Transfira mudas do canteiro para adaptação ao sol e condições do campo.
        Recomenda-se permanência mínima de <strong>30 dias</strong> antes de liberar para venda.
      </p>
    </header>

    <details class="info-box">
      <summary>O que é rustificação?</summary>
      <p>
        Preparação das mudas para condições adversas no plantio definitivo: maior exposição ao sol,
        redução gradual de irrigação e adubação. Inicie a retirada da cobertura cerca de 60 dias antes
        do plantio em campo, de forma gradual para evitar queima foliar.
      </p>
    </details>

    <div v-if="!podeOperar" class="alert alert-error">Seu perfil só permite visualização.</div>

    <div class="toolbar">
      <label class="field field--sm">
        Canteiro (origem)
        <select v-model="filtroCanteiro" @change="carregar">
          <option value="">Todos</option>
          <option v-for="c in canteiros" :key="c.id" :value="c.id">{{ c.nome }}</option>
        </select>
      </label>
    </div>

    <section class="rust-step">
      <h3 class="sub-titulo">Canteiro: marcar aptas p/ rustificação</h3>
      <p class="info-box">
        As mudas em crescimento no canteiro viram “aptas p/ rustificação” aqui (passam a entrar no fluxo correto
        antes da venda).
      </p>
      <div class="stage-header">
        <button
          type="button"
          class="btn btn-primary"
          :disabled="!podeOperar || !selCrescimento.length || marcando || transferindo"
          @click="marcarAptasRustificacao"
        >
          Marcar {{ selCrescimento.length || 0 }} como aptas p/ rustificação
        </button>
      </div>
      <TabelaMudas
        v-model:selecionados="selCrescimento"
        :lista="pendentes"
        :pode-operar="podeOperar"
        empty="Nenhuma muda em crescimento no canteiro para marcar."
      />
    </section>

    <section class="rust-step">
      <h3 class="sub-titulo">Canteiro: transferir aptas p/ rustificação</h3>
      <p class="info-box">
        Só as mudas já marcadas como aptas p/ rustificação podem entrar na área de rustificação.
      </p>
      <div class="stage-header">
        <button
          type="button"
          class="btn btn-primary"
          :disabled="!podeOperar || !selAptas.length || transferindo || marcando"
          @click="transferirAptasRustificacao"
        >
          Transferir {{ selAptas.length || 0 }} muda(s) à rustificação
        </button>
      </div>
      <TabelaMudas
        v-model:selecionados="selAptas"
        :lista="aptasCanteiro"
        :pode-operar="podeOperar"
        empty="Nenhuma muda apta p/ rustificação no canteiro para enviar."
      />
    </section>

    <h3 class="sub-titulo">Já na rustificação ({{ naRust.length }})</h3>
    <TabelaMudas
      :lista="naRust"
      :selecionados="[]"
      :pode-operar="false"
      empty="Nenhuma muda na área de rustificação."
    />

    <p v-if="erro" class="alert alert-error">{{ erro }}</p>
    <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listCanteiros } from '@/services/canteiros'
import {
  listEmCrescimentoCanteiro,
  listAptasRustificacaoCanteiro,
  listEmRustificacao,
  transferirRustificacao,
  atualizarEstagioProducao,
} from '@/services/plantas'
import { usePermissions } from '@/composables/usePermissions'
import TabelaMudas from './ProducaoTabelaMudas.vue'

const emit = defineEmits(['atualizado'])
const { can } = usePermissions()
const podeOperar = computed(() => can('producao.transfer'))

const pendentes = ref([]) // em crescimento (canteiro) -> marcar aptas p/ rustificação
const aptasCanteiro = ref([]) // aptas p/ rustificação (canteiro) -> transferir
const naRust = ref([]) // em rustificação (rustificação)
const canteiros = ref([])
const selCrescimento = ref([])
const selAptas = ref([])
const filtroCanteiro = ref('')
const marcando = ref(false)
const transferindo = ref(false)
const erro = ref('')
const sucesso = ref('')

async function carregar() {
  erro.value = ''
  const params = {}
  if (filtroCanteiro.value) params.id_canteiro = Number(filtroCanteiro.value)
  const [c, a, r] = await Promise.all([
    listEmCrescimentoCanteiro(params),
    listAptasRustificacaoCanteiro(params),
    listEmRustificacao({}),
  ])
  pendentes.value = c
  aptasCanteiro.value = a
  naRust.value = r
  selCrescimento.value = []
  selAptas.value = []
}

onMounted(async () => {
  const cant = await listCanteiros({ ativo: true })
  canteiros.value = cant.filter((c) => c.tipo_local === 'canteiro')
  await carregar()
})

defineExpose({ carregar })

async function marcarAptasRustificacao() {
  marcando.value = true
  erro.value = ''
  sucesso.value = ''
  try {
    const res = await atualizarEstagioProducao({
      ids_plantas: selCrescimento.value.map(Number),
      estagio_producao: 'apta_rustificacao',
    })
    sucesso.value = `${res.atualizadas} muda(s) marcada(s) como aptas p/ rustificação.`
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro na transferência.'
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
  try {
    const res = await transferirRustificacao({
      ids_plantas: selAptas.value.map(Number),
    })
    sucesso.value = `${res.transferidas} muda(s) enviada(s) à rustificação.`
    await carregar()
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
.sub-titulo { margin: var(--spacing-lg) 0 var(--spacing-md); font-size: 1rem; font-weight: 600; }
.rust-step { display: flex; flex-direction: column; gap: var(--spacing-md); }
.stage-header { display: flex; flex-wrap: wrap; gap: var(--spacing-md); align-items: flex-end; margin: var(--spacing-md) 0; }
details.info-box { cursor: pointer; }
details.info-box p { margin-top: 0.5rem; }
details.info-box summary { font-weight: 600; }
</style>
