<template>

  <div class="estagios-panel">

    <header class="panel-intro">

      <h2 class="panel-title">Liberar estágios</h2>

      <p class="panel-lead">

        Nem toda plântula na sementeira está pronta para o canteiro — e nem toda muda no canteiro

        está pronta para venda. Marque aqui quando cada lote atingir o ponto de avançar.

      </p>

    </header>



    <div v-if="!podeOperar" class="alert alert-error">

      Seu perfil só permite visualização. Liberação de estágios exige permissão de operação.

    </div>



    <nav class="sub-guias" aria-label="Estágios">

      <button

        type="button"

        class="sub-guia"

        :class="{ ativa: subGuia === 'sementeira' }"

        @click="subGuia = 'sementeira'"

      >

        Sementeira

        <span v-if="desenvolvimento.length" class="badge">{{ desenvolvimento.length }}</span>

      </button>

      <button

        type="button"

        class="sub-guia"

        :class="{ ativa: subGuia === 'canteiro' }"

        @click="subGuia = 'canteiro'"

      >

        Canteiro

        <span v-if="crescimento.length" class="badge">{{ crescimento.length }}</span>

      </button>

    </nav>



    <!-- Sementeira -->

    <section v-show="subGuia === 'sementeira'" class="stage-section">

      <div class="stage-header">

        <div>

          <h3>{{ ESTAGIOS.em_desenvolvimento.label }}</h3>

          <p>{{ ESTAGIOS.em_desenvolvimento.descricao }}</p>

        </div>

        <button

          type="button"

          class="btn btn-primary btn-sm"

          :disabled="!podeOperar || !selDev.length || processando"

          @click="liberarTransferencia"

        >

          Marcar {{ selDev.length || 0 }} como apta(s) p/ transferência

        </button>

      </div>



      <div class="toolbar">

        <label class="field field--sm">

          Sementeira

          <select v-model="filtroSementeira" @change="carregarSementeira">

            <option value="">Todas</option>

            <option v-for="c in sementeiras" :key="c.id" :value="c.id">{{ c.nome }}</option>

          </select>

        </label>

        <label class="field field--sm">

          Espécie

          <select v-model="filtroEspDev" @change="carregarSementeira">

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

                  :checked="todosDev"

                  :disabled="!podeOperar || !desenvolvimento.length"

                  @change="toggleTodosDev"

                />

              </th>

              <th>Código</th>

              <th>Espécie</th>

              <th>Matriz</th>

              <th>Sementeira</th>

              <th>Plantio</th>

              <th>Dias</th>

            </tr>

          </thead>

          <tbody>

            <tr v-if="!carregandoDev && !desenvolvimento.length">

              <td colspan="7" class="empty-cell">Nenhuma plântula em desenvolvimento.</td>

            </tr>

            <tr v-for="p in desenvolvimento" :key="p.id">

              <td>

                <input

                  v-model="selDev"

                  type="checkbox"

                  :value="p.id"

                  :disabled="!podeOperar"

                />

              </td>

              <td><code>{{ p.codigo_rastreio }}</code></td>

              <td>{{ p.especie_nome }}</td>

              <td>{{ p.matriz_nome || '—' }}</td>

              <td>{{ p.nome_canteiro }}</td>

              <td>{{ formatarData(p.data_plantio) }}</td>

              <td>{{ diasDesde(p.data_plantio) }}</td>

            </tr>

          </tbody>

        </table>

      </div>

    </section>



    <!-- Canteiro -->

    <section v-show="subGuia === 'canteiro'" class="stage-section">

      <div class="stage-header">

        <div>

          <h3>{{ ESTAGIOS.em_crescimento.label }}</h3>

          <p>{{ ESTAGIOS.em_crescimento.descricao }}</p>

        </div>

        <button

          type="button"

          class="btn btn-primary btn-sm"

          :disabled="!podeOperar || !selCresc.length || processando"

          @click="liberarVenda"

        >

          Marcar {{ selCresc.length || 0 }} como apta(s) p/ venda

        </button>

      </div>



      <div class="toolbar">

        <label class="field field--sm">

          Canteiro

          <select v-model="filtroCanteiro" @change="carregarCanteiro">

            <option value="">Todos</option>

            <option v-for="c in canteiros" :key="c.id" :value="c.id">{{ c.nome }}</option>

          </select>

        </label>

        <label class="field field--sm">

          Espécie

          <select v-model="filtroEspCresc" @change="carregarCanteiro">

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

                  :checked="todosCresc"

                  :disabled="!podeOperar || !crescimento.length"

                  @change="toggleTodosCresc"

                />

              </th>

              <th>Código</th>

              <th>Espécie</th>

              <th>Canteiro</th>

              <th>Status</th>

              <th>Germinação</th>

              <th>Dias</th>

            </tr>

          </thead>

          <tbody>

            <tr v-if="!carregandoCresc && !crescimento.length">

              <td colspan="7" class="empty-cell">Nenhuma muda em crescimento no canteiro.</td>

            </tr>

            <tr v-for="p in crescimento" :key="p.id">

              <td>

                <input

                  v-model="selCresc"

                  type="checkbox"

                  :value="p.id"

                  :disabled="!podeOperar"

                />

              </td>

              <td><code>{{ p.codigo_rastreio }}</code></td>

              <td>{{ p.especie_nome }}</td>

              <td>{{ p.nome_canteiro }}</td>

              <td><span class="tag">{{ p.status }}</span></td>

              <td>{{ formatarData(p.data_germinacao || p.data_plantio) }}</td>

              <td>{{ diasDesde(p.data_germinacao || p.data_plantio) }}</td>

            </tr>

          </tbody>

        </table>

      </div>

    </section>



    <p v-if="carregandoDev || carregandoCresc" class="status-msg">Carregando…</p>

    <p v-if="erro" class="alert alert-error">{{ erro }}</p>

    <p v-if="sucesso" class="alert alert-success">{{ sucesso }}</p>

  </div>

</template>



<script setup>

import { ref, computed, onMounted } from 'vue'

import { listCanteiros } from '@/services/canteiros'

import { listEspecies } from '@/services/especies'

import {

  listEmDesenvolvimentoSementeira,

  listEmCrescimentoCanteiro,

  atualizarEstagioProducao,

} from '@/services/plantas'

import { usePermissions } from '@/composables/usePermissions'

import { ESTAGIOS } from '@/constants/estagiosProducao'



const emit = defineEmits(['atualizado'])

const { can } = usePermissions()

const podeOperar = computed(() => can('producao.transfer'))



const subGuia = ref('sementeira')

const desenvolvimento = ref([])

const crescimento = ref([])

const sementeiras = ref([])

const canteiros = ref([])

const especies = ref([])

const filtroSementeira = ref('')

const filtroCanteiro = ref('')

const filtroEspDev = ref('')

const filtroEspCresc = ref('')

const selDev = ref([])

const selCresc = ref([])

const carregandoDev = ref(false)

const carregandoCresc = ref(false)

const processando = ref(false)

const erro = ref('')

const sucesso = ref('')



const todosDev = computed(

  () => desenvolvimento.value.length > 0 && selDev.value.length === desenvolvimento.value.length

)

const todosCresc = computed(

  () => crescimento.value.length > 0 && selCresc.value.length === crescimento.value.length

)



async function carregarSementeira() {

  carregandoDev.value = true

  erro.value = ''

  try {

    const params = {}

    if (filtroSementeira.value) params.id_canteiro = Number(filtroSementeira.value)

    if (filtroEspDev.value) params.id_especie = Number(filtroEspDev.value)

    desenvolvimento.value = await listEmDesenvolvimentoSementeira(params)

    selDev.value = []

  } catch (e) {

    erro.value = e.response?.data?.detail || 'Erro ao carregar sementeira.'

    desenvolvimento.value = []

  } finally {

    carregandoDev.value = false

  }

}



async function carregarCanteiro() {

  carregandoCresc.value = true

  erro.value = ''

  try {

    const params = {}

    if (filtroCanteiro.value) params.id_canteiro = Number(filtroCanteiro.value)

    if (filtroEspCresc.value) params.id_especie = Number(filtroEspCresc.value)

    crescimento.value = await listEmCrescimentoCanteiro(params)

    selCresc.value = []

  } catch (e) {

    erro.value = e.response?.data?.detail || 'Erro ao carregar canteiro.'

    crescimento.value = []

  } finally {

    carregandoCresc.value = false

  }

}



async function carregar() {

  await Promise.all([carregarSementeira(), carregarCanteiro()])

}



onMounted(async () => {

  try {

    const [cant, esp] = await Promise.all([listCanteiros({ ativo: true }), listEspecies()])

    sementeiras.value = cant.filter((c) => c.tipo_local === 'sementeira')

    canteiros.value = cant.filter((c) => c.tipo_local === 'canteiro')

    especies.value = esp

  } catch {

    erro.value = 'Erro ao carregar canteiros ou espécies.'

  }

  await carregar()

})



function toggleTodosDev(e) {

  selDev.value = e.target.checked ? desenvolvimento.value.map((p) => p.id) : []

}



function toggleTodosCresc(e) {

  selCresc.value = e.target.checked ? crescimento.value.map((p) => p.id) : []

}



async function liberarTransferencia() {

  await aplicarEstagio(selDev.value, 'apta_transferencia', 'apta(s) para transferência')

  subGuia.value = 'sementeira'

}



async function liberarVenda() {

  await aplicarEstagio(selCresc.value, 'apta_venda', 'apta(s) para venda')

  subGuia.value = 'canteiro'

}



async function aplicarEstagio(ids, estagio, labelSucesso) {

  erro.value = ''

  sucesso.value = ''

  processando.value = true

  try {

    const res = await atualizarEstagioProducao({

      ids_plantas: ids.map(Number),

      estagio_producao: estagio,

    })

    sucesso.value = `${res.atualizadas} planta(s) marcada(s) como ${labelSucesso}.`

    await carregar()

    emit('atualizado')

  } catch (e) {

    erro.value = e.response?.data?.detail || 'Erro ao atualizar estágio.'

  } finally {

    processando.value = false

  }

}



function formatarData(d) {

  if (!d) return '—'

  return new Date(d + (String(d).includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR')

}



function diasDesde(d) {

  if (!d) return '—'

  const dt = new Date(String(d).includes('T') ? d : `${d}T12:00:00`)

  const dias = Math.floor((Date.now() - dt.getTime()) / 86400000)

  return dias >= 0 ? `${dias}d` : '—'

}



defineExpose({ carregar, abrirSubGuia: (g) => { subGuia.value = g } })

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



.sub-guias {

  display: flex;

  gap: 0.5rem;

  margin-bottom: var(--spacing-md);

}



.sub-guia {

  display: inline-flex;

  align-items: center;

  gap: 0.35rem;

  padding: 0.45rem 0.85rem;

  border: 1px solid var(--color-border-subtle);

  border-radius: var(--radius-full);

  background: var(--color-surface);

  font-family: inherit;

  font-size: 0.8125rem;

  font-weight: 600;

  cursor: pointer;

  color: var(--color-text-secondary);

}



.sub-guia.ativa {

  background: var(--color-primary-subtle);

  border-color: var(--color-primary-100);

  color: var(--color-primary-700);

}



.badge {

  background: var(--color-attention-bg);

  color: var(--color-attention);

  font-size: 0.6875rem;

  padding: 0.1rem 0.4rem;

  border-radius: var(--radius-full);

}



.stage-section {

  margin-bottom: var(--spacing-md);

}



.stage-header {

  display: flex;

  flex-wrap: wrap;

  justify-content: space-between;

  align-items: flex-start;

  gap: var(--spacing-md);

  margin-bottom: var(--spacing-md);

}



.stage-header h3 {

  margin: 0 0 0.25rem;

  font-size: 1rem;

}



.stage-header p {

  margin: 0;

  font-size: 0.8125rem;

  color: var(--color-text-secondary);

}



.toolbar {

  display: flex;

  flex-wrap: wrap;

  gap: var(--spacing-md);

  margin-bottom: var(--spacing-md);

}



.field {

  display: flex;

  flex-direction: column;

  gap: 0.25rem;

  font-size: 0.75rem;

  font-weight: 600;

  color: var(--color-text-secondary);

}



.field select {

  padding: 0.45rem 0.5rem;

  border: 1px solid var(--color-border);

  border-radius: var(--radius-sm);

  font-family: inherit;

  font-size: 0.875rem;

  min-width: 160px;

}



.table-card {

  overflow-x: auto;

  background: var(--color-surface);

  border: 1px solid var(--color-border-subtle);

  border-radius: var(--radius-lg);

  box-shadow: var(--shadow-sm);

}



.data-table {

  width: 100%;

  border-collapse: collapse;

  font-size: 0.875rem;

}



.data-table th,

.data-table td {

  padding: 0.65rem 0.85rem;

  border-bottom: 1px solid var(--color-border-subtle);

  text-align: left;

}



.data-table th {

  background: var(--color-surface-muted);

  font-weight: 600;

  font-size: 0.75rem;

  text-transform: uppercase;

  letter-spacing: 0.03em;

  color: var(--color-text-secondary);

}



.col-check {

  width: 2.5rem;

}



.empty-cell {

  text-align: center;

  padding: 2rem;

  color: var(--color-text-muted);

}



.tag {

  font-size: 0.6875rem;

  padding: 0.15rem 0.45rem;

  border-radius: var(--radius-full);

  background: var(--color-surface-muted);

}



code {

  font-size: 0.8125rem;

  color: var(--color-primary-700);

}

</style>

