<template>
  <div class="clientes-cadastro">
    <header class="module-header">
      <p class="module-header__lead">
        Cadastro de clientes (compradores) — dados usados na venda e na NF-e.
        Campos de endereço e IBGE são obrigatórios para emissão fiscal.
      </p>
      <div class="module-header__actions">
        <CanAccess permission="vendas.create">
          <button type="button" class="btn btn-primary" @click="abrirNovo">+ Novo cliente</button>
        </CanAccess>
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
              <CanAccess permission="vendas.edit">
                <button type="button" class="btn-link" @click="editar(c)">Editar</button>
              </CanAccess>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppModalOverlay
      :aberto="dialogClienteAberto"
      :handlers="overlayCliente"
      panel-class="app-modal-panel--wide"
      :aria-labelledby="form.id ? 'cliente-editar-titulo' : 'cliente-novo-titulo'"
    >
      <form class="dialog-panel" @submit.prevent="salvar">
        <header class="app-modal-header">
          <div>
            <h3 :id="form.id ? 'cliente-editar-titulo' : 'cliente-novo-titulo'">
              {{ form.id ? 'Editar cliente' : 'Novo cliente' }}
            </h3>
          </div>
          <button type="button" class="app-modal-fechar" aria-label="Fechar" @click="fecharCliente">×</button>
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
            <MaskedInput
              v-model="form.cpf_cnpj"
              :mask="form.tipo === 'PJ' ? 'cnpj' : 'cpf'"
              :label="form.tipo === 'PJ' ? 'CNPJ' : 'CPF'"
              required
            />
          </div>

          <label class="module-field">
            Nome / Razão social
            <input v-model="form.nome" required />
          </label>

          <div class="module-form-row">
            <MaskedInput v-model="form.telefone" mask="telefone" label="Telefone" />
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
            <MaskedInput v-model="form.estado" mask="uf" label="UF" required />
          </div>

          <MaskedInput
            v-model="form.codigo_municipio_ibge"
            mask="ibge"
            label="Cód. IBGE município (7 dígitos)"
            required
            placeholder="Ex.: 5208707"
          />

          <div class="module-form-row">
            <MaskedInput
              v-model="form.inscricao_estadual"
              mask="ie"
              label="Inscrição estadual"
              hint="Somente números"
            />
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

        <footer class="app-modal-footer">
          <button type="button" class="btn btn-secondary" @click="fecharCliente">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="salvando">
            {{ salvando ? 'Salvando…' : 'Salvar' }}
          </button>
        </footer>
      </form>
    </AppModalOverlay>

    <ConfirmSaidaModal
      :aberto="confirmAberto"
      @confirmar="confirmarSaida"
      @cancelar="cancelarSaida"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import CanAccess from '@/components/shared/CanAccess.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { usePermissions } from '@/composables/usePermissions'
import { useFormDirty } from '@/utils/formDirty'
import CepInput from '@/components/form/CepInput.vue'
import MaskedInput from '@/components/form/MaskedInput.vue'
import { compradorVazio, normalizarCompradorCampos } from '@/constants/compradorForm'
import {
  listCompradoresWithVendas,
  createComprador,
  updateComprador,
  getComprador,
  getCompradorNfeReadiness,
} from '@/services/compradores'
import { aplicarEnderecoCep } from '@/utils/cepAutofill'
import { errosCompradorLocal } from '@/utils/compradorNfeCheck'
import { onlyDigits } from '@/utils/inputMasks'

const emit = defineEmits(['salvou'])

const { can } = usePermissions()
const carregando = ref(true)
const salvando = ref(false)
const erro = ref(null)
const clientes = ref([])
const busca = ref('')
const filtroTipo = ref('')
const nfeStatus = ref({})
const dialogClienteAberto = ref(false)
const form = ref({ ...compradorVazio(), id: null })
const readinessForm = ref(null)

const { isDirty, rebase } = useFormDirty(form, () => dialogClienteAberto.value)

function fecharClienteInterno() {
  dialogClienteAberto.value = false
}

const overlayCliente = useModalFormClose(
  fecharClienteInterno,
  () => isDirty.value,
  () => dialogClienteAberto.value
)

const {
  confirmAberto,
  confirmarSaida,
  cancelarSaida,
  sairSemConfirmar,
} = overlayCliente

function fecharCliente() {
  overlayCliente.resetOverlayPress()
  overlayCliente.requestClose()
}

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
  if (!can('vendas.create')) return
  form.value = { ...compradorVazio(), id: null }
  readinessForm.value = null
  dialogClienteAberto.value = true
  nextTick().then(rebase)
}

function editar(c) {
  if (!can('vendas.edit')) return
  form.value = normalizarCompradorCampos({
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
  })
  readinessForm.value = nfeStatus.value[c.id] || null
  dialogClienteAberto.value = true
  nextTick().then(rebase)
}

async function editarPorId(id) {
  await carregar()
  const c = clientes.value.find((x) => x.id === id)
  if (c) {
    editar(c)
    return
  }
  try {
    const full = await getComprador(id)
    editar(full)
  } catch (e) {
    alert(e.response?.data?.detail || 'Cliente não encontrado.')
  }
}

async function salvar() {
  salvando.value = true
  const payload = normalizarCompradorCampos({ ...form.value })
  delete payload.id
  try {
    if (form.value.id) {
      await updateComprador(form.value.id, payload)
    } else {
      await createComprador(payload)
    }
    sairSemConfirmar()
    await carregar()
    emit('salvou')
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar cliente.')
  } finally {
    salvando.value = false
  }
}

watch(
  () => form.value.tipo,
  (tipo) => {
    const d = onlyDigits(form.value.cpf_cnpj)
    form.value.cpf_cnpj = tipo === 'PJ' ? d.slice(0, 14) : d.slice(0, 11)
  }
)

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

defineExpose({ abrirNovo, editarPorId, carregar })
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
  background: var(--color-success-bg);
  color: var(--color-success);
}
.tag-nfe--pend {
  background: var(--color-attention-bg);
  color: var(--color-text-secondary);
}
.acoes {
  white-space: nowrap;
}
.aviso-lista {
  margin: 0.35rem 0 0;
  padding-left: 1.1rem;
}
.status-ok {
  color: var(--color-success);
  font-size: 0.8125rem;
  margin: 0;
}
</style>
