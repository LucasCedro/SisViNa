<template>
  <div class="panel">
    <header class="panel-intro">
      <h2 class="panel-title">Liberar para canteiro</h2>
      <p class="panel-lead">
        Marque mudas germinadas na sementeira como <strong>aptas para transferência</strong> ao
        canteiro. É o passo anterior à movimentação física.
      </p>
    </header>

    <details class="info-box">
      <summary>O que acontece aqui?</summary>
      <p>
        Você apenas muda o estágio operacional — a muda continua na sementeira até alguém usar a
        guia <strong>Transferir para o canteiro</strong>.
      </p>
    </details>

    <div v-if="!podeOperar" class="alert alert-error">Seu perfil só permite visualização.</div>

    <div class="prod-kpis prod-kpis--2" aria-label="Resumo sementeira">
      <article class="prod-kpi prod-kpi--muted">
        <span class="prod-kpi__valor">{{ totais.emDesenvolvimento.toLocaleString('pt-BR') }}</span>
        <span class="prod-kpi__label">Em desenvolvimento (sementeira)</span>
      </article>
      <article class="prod-kpi prod-kpi--principal">
        <span class="prod-kpi__valor">{{ totais.aptas.toLocaleString('pt-BR') }}</span>
        <span class="prod-kpi__label">Aptas aguardando transferência</span>
      </article>
    </div>

    <ProducaoModoOperacao v-model:modo="modo">
      <template #default="{ modo: m }">
        <section class="prod-bloco prod-bloco--principal">
          <header class="prod-bloco__header">
            <span class="prod-badge prod-badge--principal">Fluxo usual</span>
            <h3 class="prod-bloco__titulo">Liberar para transferência</h3>
            <p class="prod-bloco__desc">
              Mudas em desenvolvimento na sementeira que já podem ir ao canteiro.
            </p>
          </header>

          <ProducaoPainelLote
            v-if="m === PRODUCAO_MODO.MASSA"
            ref="painelLoteRef"
            etapa="sementeira_desenvolvimento"
            titulo-botao="Liberar para transferência"
            :pode-operar="podeOperar"
            :filtro-locais="sementeiras"
            filtro-local-label="Sementeira"
            vazio="Nenhuma muda em desenvolvimento na sementeira."
            mensagem-loading="Liberando mudas…"
            :on-executar="executarLote"
            @concluido="aoConcluir"
          />

          <template v-else>
            <div class="stage-header">
              <button
                type="button"
                class="btn btn-primary"
                :disabled="!podeOperar || !sel.length || processando"
                @click="liberarDetalhe"
              >
                Marcar {{ sel.length || 0 }} muda(s) para transferência
              </button>
            </div>

            <div class="toolbar">
              <label class="field field--sm">
                Sementeira
                <select v-model="filtroCanteiro" @change="carregar">
                  <option value="">Todas</option>
                  <option v-for="c in sementeiras" :key="c.id" :value="c.id">{{ c.nome }}</option>
                </select>
              </label>
              <label class="field field--sm">
                Espécie
                <select v-model="filtroEsp" @change="carregar">
                  <option value="">Todas</option>
                  <option v-for="e in especies" :key="e.id" :value="e.id">
                    {{ e.nome_popular || e.nome_cientifico }}
                  </option>
                </select>
              </label>
            </div>

            <div class="table-card">
              <table class="data-table">
                <thead>
                  <tr>
                    <th class="col-check">
                      <input
                        type="checkbox"
                        :checked="todos"
                        :disabled="!podeOperar || !lista.length"
                        @change="toggleTodos"
                      />
                    </th>
                    <th>Código</th>
                    <th>Espécie</th>
                    <th>Sementeira</th>
                    <th>Plantio</th>
                    <th>Dias</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!carregando && !lista.length">
                    <td colspan="6" class="empty-cell">Nenhuma muda em desenvolvimento.</td>
                  </tr>
                  <tr v-for="p in lista" :key="p.id">
                    <td>
                      <input v-model="sel" type="checkbox" :value="p.id" :disabled="!podeOperar" />
                    </td>
                    <td><code>{{ p.codigo_rastreio }}</code></td>
                    <td>{{ p.especie_nome }}</td>
                    <td>{{ p.nome_canteiro }}</td>
                    <td>{{ formatarData(p.data_plantio) }}</td>
                    <td>{{ diasDesde(p.data_plantio) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p v-if="erro" class="alert alert-error">{{ erro }}</p>
            <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>
          </template>
        </section>
      </template>
    </ProducaoModoOperacao>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { listCanteiros } from '@/services/canteiros'
import { listEspecies } from '@/services/especies'
import {
  listEmDesenvolvimentoSementeira,
  getResumoOperacaoLote,
  atualizarEstagioProducao,
  atualizarEstagioLote,
} from '@/services/plantas'
import { usePermissions } from '@/composables/usePermissions'
import { useGlobalLoading } from '@/composables/useGlobalLoading'
import { PRODUCAO_MODO } from '@/constants/producaoUi'
import ProducaoModoOperacao from './ProducaoModoOperacao.vue'
import ProducaoPainelLote from './ProducaoPainelLote.vue'

const emit = defineEmits(['atualizado'])
const { runWithLoading } = useGlobalLoading()
const { can } = usePermissions()
const podeOperar = computed(() => can('producao.transfer'))

const modo = ref(PRODUCAO_MODO.MASSA)
const lista = ref([])
const sementeiras = ref([])
const especies = ref([])
const totais = ref({ emDesenvolvimento: 0, aptas: 0 })
const sel = ref([])
const filtroCanteiro = ref('')
const filtroEsp = ref('')
const carregando = ref(false)
const processando = ref(false)
const erro = ref('')
const sucesso = ref('')
const painelLoteRef = ref(null)

const todos = computed(() => lista.value.length > 0 && sel.value.length === lista.value.length)

function somarResumo(rows) {
  return (rows || []).reduce((s, r) => s + (r.disponivel || 0), 0)
}

async function carregarTotais() {
  const [dev, aptas] = await Promise.all([
    getResumoOperacaoLote('sementeira_desenvolvimento'),
    getResumoOperacaoLote('sementeira_apta_transferencia'),
  ])
  totais.value = {
    emDesenvolvimento: somarResumo(dev),
    aptas: somarResumo(aptas),
  }
}

async function carregar() {
  await carregarTotais()
  if (modo.value === PRODUCAO_MODO.MASSA) {
    await nextTick()
    painelLoteRef.value?.carregarResumo?.()
    return
  }
  carregando.value = true
  erro.value = ''
  try {
    const params = { limit: 2000 }
    if (filtroCanteiro.value) params.id_canteiro = Number(filtroCanteiro.value)
    if (filtroEsp.value) params.id_especie = Number(filtroEsp.value)
    lista.value = await listEmDesenvolvimentoSementeira(params)
    sel.value = []
    totais.value.emDesenvolvimento = lista.value.length
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar.'
    lista.value = []
  } finally {
    carregando.value = false
  }
}

async function executarLote(grupos) {
  return atualizarEstagioLote({
    estagio_producao: 'apta_transferencia',
    grupos,
  })
}

function aoConcluir() {
  carregar()
  emit('atualizado')
}

onMounted(async () => {
  const [cant, esp] = await Promise.all([listCanteiros({ ativo: true }), listEspecies()])
  sementeiras.value = cant.filter((c) => c.tipo_local === 'sementeira')
  especies.value = esp
  await carregar()
})

watch(modo, carregar)

defineExpose({ carregar })

function toggleTodos(e) {
  sel.value = e.target.checked ? lista.value.map((p) => p.id) : []
}

async function liberarDetalhe() {
  processando.value = true
  erro.value = ''
  sucesso.value = ''
  try {
    await runWithLoading(async () => {
      const res = await atualizarEstagioProducao({
        ids_plantas: sel.value.map(Number),
        estagio_producao: 'apta_transferencia',
      })
      sucesso.value = `${res.atualizadas} muda(s) liberada(s) para transferência.`
      await carregar()
      emit('atualizado')
    }, 'Liberando mudas…')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao liberar.'
  } finally {
    processando.value = false
  }
}

function formatarData(d) {
  if (!d) return '—'
  return new Date(String(d).includes('T') ? d : `${d}T12:00:00`).toLocaleDateString('pt-BR')
}

function diasDesde(d) {
  if (!d) return '—'
  const dt = new Date(String(d).includes('T') ? d : `${d}T12:00:00`)
  const dias = Math.floor((Date.now() - dt.getTime()) / 86400000)
  return dias >= 0 ? `${dias}d` : '—'
}
</script>

<style scoped>
@import './producao-panel-shared.css';
@import './producao-panel-blocks.css';
</style>
