<template>
  <div class="emitente-form module-sec">
    <p v-if="!podeEditar" class="hint">Somente leitura — perfil financeiro/admin edita.</p>
    <p v-if="erroCarregar" class="alert-erro">{{ erroCarregar }}</p>

    <form v-if="form" class="emitente-form__grid" @submit.prevent="salvar">
      <div class="module-form-row">
        <label class="module-field">Razão social <input v-model="form.razao_social" required /></label>
        <label class="module-field">Nome fantasia <input v-model="form.nome_fantasia" /></label>
      </div>
      <div class="module-form-row">
        <label class="module-field">CNPJ <input v-model="form.cnpj" required /></label>
        <label class="module-field">IE <input v-model="form.inscricao_estadual" required /></label>
        <label class="module-field">CRT (1=Simples) <input v-model.number="form.crt" type="number" min="1" max="3" /></label>
      </div>

      <CepInput v-model="form.cep" required @endereco="onCep" />

      <div class="module-form-row">
        <label class="module-field">Logradouro <input v-model="form.logradouro" required /></label>
        <label class="module-field">Nº <input v-model="form.numero" required /></label>
        <label class="module-field">Complemento <input v-model="form.complemento" /></label>
      </div>
      <div class="module-form-row">
        <label class="module-field">Bairro <input v-model="form.bairro" required /></label>
        <label class="module-field">Município <input v-model="form.municipio" required /></label>
        <label class="module-field">UF <input v-model="form.uf" maxlength="2" required /></label>
        <label class="module-field">IBGE <input v-model="form.codigo_municipio_ibge" required maxlength="7" /></label>
      </div>
      <div class="module-form-row">
        <label class="module-field">Telefone <input v-model="form.telefone" /></label>
        <label class="module-field">E-mail <input v-model="form.email" type="email" /></label>
        <label class="module-field">Série NF-e <input v-model.number="form.serie_nfe" type="number" min="1" /></label>
        <label class="module-field">Próximo número <input v-model.number="form.proximo_numero_nfe" type="number" min="1" /></label>
      </div>

      <label class="module-field">
        Ambiente
        <select v-model="form.ambiente" :disabled="!producaoPermitida">
          <option value="homologacao">Homologação (padrão — testes Focus)</option>
          <option value="producao" :disabled="!producaoPermitida">Produção</option>
        </select>
      </label>
      <p v-if="!producaoPermitida" class="module-banner module-banner--warn">
        Produção bloqueada no servidor (<code>NFE_ALLOW_PRODUCAO=false</code>). Mantenha homologação até liberação consciente.
      </p>

      <div class="emitente-form__actions">
        <button v-if="podeEditar" type="submit" class="btn btn-primary" :disabled="salvando">
          {{ salvando ? 'Salvando…' : 'Salvar emitente' }}
        </button>
      </div>
    </form>
    <p v-else-if="!erroCarregar" class="empty">Cadastre o emitente para habilitar emissão de NF-e.</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import CepInput from '@/components/form/CepInput.vue'
import { getEmitenteFiscal, saveEmitenteFiscal } from '@/services/fiscal'
import { aplicarEnderecoCep } from '@/utils/cepAutofill'

const props = defineProps({
  podeEditar: { type: Boolean, default: false },
  ambiente: { type: Object, default: null },
})

const emit = defineEmits(['salvo'])

const form = ref(null)
const erroCarregar = ref(null)
const salvando = ref(false)

const producaoPermitida = computed(() => props.ambiente?.producao_permitida_sistema === true)

function onCep(end) {
  aplicarEnderecoCep(form.value, end, 'emitente')
}

function emitenteVazio() {
  return {
    razao_social: '',
    nome_fantasia: '',
    cnpj: '',
    inscricao_estadual: '',
    crt: 1,
    logradouro: '',
    numero: '',
    complemento: '',
    bairro: '',
    codigo_municipio_ibge: '',
    municipio: '',
    uf: 'GO',
    cep: '',
    telefone: '',
    email: '',
    serie_nfe: 1,
    proximo_numero_nfe: 1,
    ambiente: 'homologacao',
  }
}

async function carregar() {
  erroCarregar.value = null
  try {
    form.value = await getEmitenteFiscal()
  } catch (e) {
    if (e.response?.status === 404) {
      form.value = emitenteVazio()
    } else {
      erroCarregar.value = e.response?.data?.detail || 'Falha ao carregar emitente.'
    }
  }
}

async function salvar() {
  if (!props.podeEditar) return
  if (form.value.ambiente === 'producao' && !producaoPermitida.value) {
    alert('Produção bloqueada. Use homologação.')
    form.value.ambiente = 'homologacao'
    return
  }
  salvando.value = true
  try {
    form.value = await saveEmitenteFiscal(form.value)
    emit('salvo')
    alert('Emitente salvo.')
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar emitente.')
  } finally {
    salvando.value = false
  }
}

watch(
  () => props.ambiente,
  (a) => {
    if (form.value && a && !a.producao_permitida_sistema && form.value.ambiente === 'producao') {
      form.value.ambiente = 'homologacao'
    }
  }
)

onMounted(carregar)
</script>

<style scoped>
.emitente-form {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}
.emitente-form__grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.emitente-form__actions {
  display: flex;
  justify-content: flex-end;
  padding-top: var(--spacing-sm);
}
.hint,
.empty {
  color: var(--color-text-muted);
  font-size: 0.875rem;
}
</style>
