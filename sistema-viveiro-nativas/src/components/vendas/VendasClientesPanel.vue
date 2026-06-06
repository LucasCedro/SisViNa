<template>
  <div class="clientes-panel">
    <header class="module-header">
      <p class="module-header__lead">
        Cadastro de clientes (compradores) — dados usados na venda e na NF-e.
        Campos de endereço e IBGE são obrigatórios para emissão fiscal.
      </p>
      <div class="module-header__actions">
        <button type="button" class="btn btn-primary" @click="abrirNovo">+ Novo cliente</button>
      </div>
    </header>

    <div class="module-toolbar">
      <label class="module-toolbar__field">
        Buscar
        <input v-model="busca" type="search" placeholder="Nome, CPF/CNPJ…" />
      </label>
      <label class="module-toolbar__field">
        Tipo
        <select v-model="filtroTipo" @change="carregar">
          <option value="">Todos</option>
          <option value="PF">PF</option>
          <option value="PJ">PJ</option>
        </select>
      </label>
    </div>

    <p v-if="erro" class="alert-erro">{{ erro }}</p>
    <p v-if="carregando" class="status-msg">Carregando…</p>

    <div v-else class="module-table-wrap">
      <table class="module-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Doc.</th>
            <th>Cidade/UF</th>
            <th>NF-e</th>
            <th>Vendas</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!filtrados.length">
            <td colspan="6" class="empty-cell">Nenhum cliente cadastrado.</td>
          </tr>
          <tr v-for="c in filtrados" :key="c.id">
            <td>
              <strong>{{ c.nome }}</strong>
              <span class="tag-tipo">{{ c.tipo }}</span>
            </td>
            <td>{{ c.cpf_cnpj }}</td>
            <td>{{ c.cidade || '—' }}/{{ c.estado || '—' }}</td>
            <td>
              <span
                class="tag-nfe"
                :class="nfeStatus[c.id]?.pronto ? 'tag-nfe--ok' : 'tag-nfe--pend'"
                :title="(nfeStatus[c.id]?.faltando || []).join('; ')"
              >
                {{ nfeStatus[c.id]?.pronto ? 'Pronto' : 'Incompleto' }}
              </span>
            </td>
            <td>{{ c.total_vendas ?? 0 }}</td>
            <td class="acoes">
              <button type="button" class="btn-link" @click="editar(c)">Editar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <dialog ref="dialogCliente" class="app-dialog app-dialog--wide">
      <form class="dialog-panel" @submit.prevent="salvar">
        <header class="dialog-panel__header">
          <h3>{{ form.id ? 'Editar cliente' : 'Novo cliente' }}</h3>
        </header>

        <div class="dialog-panel__body">
          <div class="module-form-row">
            <label class="module-field">
              Tipo
              <select v-model="form.tipo" required>
                <option value="PF">Pessoa física</option>
                <option value="PJ">Pessoa jurídica</option>
              </select>
            </label>
            <label class="module-field">
              {{ form.tipo === 'PJ' ? 'CNPJ' : 'CPF' }}
              <input v-model="form.cpf_cnpj" required />
            </label>
          </div>

          <label class="module-field">
            Nome / Razão social
            <input v-model="form.nome" required />
          </label>

          <div class="module-form-row">
            <label class="module-field">
              Telefone
              <input v-model="form.telefone" />
            </label>
            <label class="module-field">
              E-mail
              <input v-model="form.email" type="email" />
            </label>
          </div>

          <CepInput v-model="form.cep" required @endereco="onCep" />

          <label class="module-field">
            Logradouro
            <input v-model="form.endereco" required />
          </label>

          <div class="module-form-row">
            <label class="module-field">
              Nº
              <input v-model="form.numero" required />
            </label>
            <label class="module-field">
              Bairro
              <input v-model="form.bairro" required />
            </label>
          </div>

          <div class="module-form-row">
            <label class="module-field">
              Cidade
              <input v-model="form.cidade" required />
            </label>
            <label class="module-field">
              UF
              <input v-model="form.estado" maxlength="2" required />
            </label>
          </div>

          <label class="module-field">
            Cód. IBGE município (7 dígitos)
            <input v-model="form.codigo_municipio_ibge" maxlength="7" required placeholder="Ex.: 5208707" />
          </label>

          <div class="module-form-row">
            <label class="module-field">
              Inscrição estadual
              <input v-model="form.inscricao_estadual" />
            </label>
            <label class="module-field">
              Indicador IE
              <select v-model="form.indicador_ie">
                <option value="9">9 — Não contribuinte</option>
                <option value="1">1 — Contribuinte</option>
                <option value="2">2 — Isento</option>
              </select>
            </label>
          </div>

          <aside v-if="readinessForm && !readinessForm.pronto" class="module-banner module-banner--warn">
            <strong>Para NF-e, falta:</strong>
            <ul class="aviso-lista">
              <li v-for="(f, i) in readinessForm.faltando" :key="i">{{ f }}</li>
            </ul>
          </aside>
          <p v-else-if="readinessForm?.pronto" class="status-ok">✓ Dados completos para NF-e</p>
        </div>

        <footer class="dialog-panel__footer">
          <button type="button" class="btn btn-secondary" @click="fecharDialog">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="salvando">
            {{ salvando ? 'Salvando…' : 'Salvar' }}
          </button>
        </footer>
      </form>
    </dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import CepInput from '@/components/form/CepInput.vue'
import { compradorVazio } from '@/constants/compradorForm'
import {
  listCompradoresWithVendas,
  createComprador,
  updateComprador,
  getCompradorNfeReadiness,
} from '@/services/compradores'
import { aplicarEnderecoCep } from '@/utils/cepAutofill'
import { errosCompradorLocal } from '@/utils/compradorNfeCheck'

const carregando = ref(true)
const salvando = ref(false)
const erro = ref(null)
const clientes = ref([])
const busca = ref('')
const filtroTipo = ref('')
const nfeStatus = ref({})
const dialogCliente = ref(null)
const form = ref({ ...compradorVazio(), id: null })
const readinessForm = ref(null)

const filtrados = computed(() => {
  const q = busca.value.trim().toLowerCase()
  if (!q) return clientes.value
  return clientes.value.filter(
    (c) =>
      (c.nome || '').toLowerCase().includes(q) ||
      (c.cpf_cnpj || '').replace(/\D/g, '').includes(q.replace(/\D/g, ''))
  )
})

function onCep(end) {
  aplicarEnderecoCep(form.value, end)
}

async function carregarNfeStatus(lista) {
  const map = {}
  await Promise.all(
    (lista || []).slice(0, 100).map(async (c) => {
      try {
        map[c.id] = await getCompradorNfeReadiness(c.id)
      } catch {
        map[c.id] = { pronto: false, faltando: ['Erro ao verificar'] }
      }
    })
  )
  nfeStatus.value = map
}

async function carregar() {
  carregando.value = true
  erro.value = null
  try {
    const params = { limit: 500, ativo: true }
    if (filtroTipo.value) params.tipo = filtroTipo.value
    const lista = await listCompradoresWithVendas(params)
    clientes.value = lista
    await carregarNfeStatus(lista)
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha ao carregar clientes.'
  } finally {
    carregando.value = false
  }
}

function abrirNovo() {
  form.value = { ...compradorVazio(), id: null }
  readinessForm.value = null
  dialogCliente.value?.showModal()
}

function editar(c) {
  form.value = {
    id: c.id,
    tipo: c.tipo,
    nome: c.nome,
    cpf_cnpj: c.cpf_cnpj,
    telefone: c.telefone || '',
    email: c.email || '',
    endereco: c.endereco || '',
    numero: c.numero || '',
    bairro: c.bairro || '',
    cidade: c.cidade || '',
    estado: c.estado || '',
    cep: c.cep || '',
    codigo_municipio_ibge: c.codigo_municipio_ibge || '',
    inscricao_estadual: c.inscricao_estadual || '',
    indicador_ie: c.indicador_ie || '9',
    ativo: c.ativo !== false,
  }
  readinessForm.value = nfeStatus.value[c.id] || null
  dialogCliente.value?.showModal()
}

function fecharDialog() {
  dialogCliente.value?.close()
}

async function salvar() {
  salvando.value = true
  const payload = { ...form.value }
  delete payload.id
  try {
    if (form.value.id) {
      await updateComprador(form.value.id, payload)
    } else {
      await createComprador(payload)
    }
    fecharDialog()
    await carregar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar cliente.')
  } finally {
    salvando.value = false
  }
}

watch(
  form,
  () => {
    readinessForm.value = {
      pronto: errosCompradorLocal(form.value).length === 0,
      faltando: errosCompradorLocal(form.value),
    }
  },
  { deep: true }
)

onMounted(carregar)
</script>

<style scoped>
.tag-tipo {
  display: inline-block;
  margin-left: 0.35rem;
  font-size: 0.6875rem;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  background: var(--color-border-subtle);
  font-weight: 600;
}
.tag-nfe {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
}
.tag-nfe--ok {
  background: #d1e7dd;
  color: #0f5132;
}
.tag-nfe--pend {
  background: #fff3cd;
  color: #664d03;
}
.acoes {
  white-space: nowrap;
}
.aviso-lista {
  margin: 0.35rem 0 0;
  padding-left: 1.1rem;
}
.status-ok {
  color: #0f5132;
  font-size: 0.8125rem;
  margin: 0;
}
</style>
