<template>
  <div class="panel">
    <header class="panel-intro">
      <h2 class="panel-title">Liberar p/ venda</h2>
      <p class="panel-lead">
        Marque mudas aptas para comercialização. O sistema só permite após a <strong>rustificação</strong>
        (controle operacional e estoque).
      </p>
    </header>

    <div v-if="!podeOperar" class="alert alert-error">Seu perfil só permite visualização.</div>

    <section>
      <p class="info-box">
        Mudas que completaram a adaptação ao sol na área de rustificação.
      </p>
      <div class="stage-header">
        <button
          type="button"
          class="btn btn-primary"
          :disabled="!podeOperar || !selRust.length || processando"
          @click="liberarVenda(selRust)"
        >
          Liberar {{ selRust.length || 0 }} da rustificação
        </button>
      </div>
      <TabelaMudas
        v-model:selecionados="selRust"
        :lista="rustificacao"
        :pode-operar="podeOperar"
        empty="Nenhuma muda em rustificação."
      />
    </section>

    <ul v-if="avisos.length" class="alert alert-warning avisos-list">
      <li v-for="(a, i) in avisos" :key="i">{{ a }}</li>
    </ul>
    <p v-if="erro" class="alert alert-error">{{ erro }}</p>
    <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  listEmRustificacao,
  atualizarEstagioProducao,
} from '@/services/plantas'
import { usePermissions } from '@/composables/usePermissions'
import TabelaMudas from './ProducaoTabelaMudas.vue'

const emit = defineEmits(['atualizado'])
const { can } = usePermissions()
const podeOperar = computed(() => can('producao.transfer'))

const rustificacao = ref([])
const selRust = ref([])
const processando = ref(false)
const erro = ref('')
const sucesso = ref('')
const avisos = ref([])

async function carregar() {
  const r = await listEmRustificacao({})
  rustificacao.value = r
  selRust.value = []
}

onMounted(carregar)
defineExpose({ carregar })

async function liberarVenda(ids) {
  processando.value = true
  erro.value = ''
  sucesso.value = ''
  avisos.value = []
  try {
    const res = await atualizarEstagioProducao({
      ids_plantas: ids.map(Number),
      estagio_producao: 'apta_venda',
    })
    avisos.value = res.avisos || []
    sucesso.value = `${res.atualizadas} muda(s) liberada(s) para venda.`
    await carregar()
    emit('atualizado')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao liberar.'
  } finally {
    processando.value = false
  }
}
</script>

<style scoped>
@import './producao-panel-shared.css';
</style>
