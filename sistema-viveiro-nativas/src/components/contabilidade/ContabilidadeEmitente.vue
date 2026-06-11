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
        <MaskedInput v-model="form.cnpj" mask="cnpj" label="CNPJ" required />
        <MaskedInput
          v-model="form.inscricao_estadual"
          mask="ie"
          label="Inscrição estadual (IE)"
          required
          hint="Somente números, sem pontuação"
        />
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
        <MaskedInput v-model="form.uf" mask="uf" label="UF" required />
        <MaskedInput v-model="form.codigo_municipio_ibge" mask="ibge" label="Código IBGE" required />
      </div>
      <div class="module-form-row">
        <MaskedInput v-model="form.telefone" mask="telefone" label="Telefone" />
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
import MaskedInput from '@/components/form/MaskedInput.vue'
import { getEmitenteFiscal, saveEmitenteFiscal } from '@/services/fiscal'
import { aplicarEnderecoCep } from '@/utils/cepAutofill'
import { formatUf, onlyDigits, parseInscricaoEstadual } from '@/utils/inputMasks'
import { mensagemErroApi } from '@/utils/apiError'

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

function normalizarEmitente(dados) {
  if (!dados) return dados
  return {
    ...dados,
    cnpj: onlyDigits(dados.cnpj).slice(0, 14),
    inscricao_estadual: parseInscricaoEstadual(dados.inscricao_estadual),
    cep: onlyDigits(dados.cep).slice(0, 8),
    telefone: onlyDigits(dados.telefone).slice(0, 11),
    codigo_municipio_ibge: onlyDigits(dados.codigo_municipio_ibge).slice(0, 7),
    uf: formatUf(dados.uf),
  }
}

/** Apenas campos aceitos pelo PUT /fiscal/emitente (sem id, ativo, etc.). */
function payloadEmitente(dados) {
  const n = normalizarEmitente(dados)
  return {
    razao_social: (n.razao_social || '').trim(),
    nome_fantasia: (n.nome_fantasia || '').trim() || null,
    cnpj: n.cnpj,
    inscricao_estadual: n.inscricao_estadual,
    crt: Math.min(3, Math.max(1, Number(n.crt) || 1)),
    cnae: (n.cnae || '').trim() || null,
    logradouro: (n.logradouro || '').trim(),
    numero: String(n.numero ?? '').trim(),
    complemento: (n.complemento || '').trim() || null,
    bairro: (n.bairro || '').trim(),
    codigo_municipio_ibge: n.codigo_municipio_ibge,
    municipio: (n.municipio || '').trim(),
    uf: n.uf,
    cep: n.cep,
    telefone: n.telefone || null,
    email: (n.email || '').trim() || null,
    serie_nfe: Math.max(1, Number(n.serie_nfe) || 1),
    proximo_numero_nfe: Math.max(1, Number(n.proximo_numero_nfe) || 1),
    ambiente: n.ambiente || 'homologacao',
  }
}

function validarEmitenteLocal(dados) {
  const n = normalizarEmitente(dados)
  const erros = []
  if (n.cnpj.length !== 14) erros.push('CNPJ deve ter 14 dígitos')
  if (!n.inscricao_estadual) erros.push('Inscrição estadual obrigatória')
  if (n.cep.length !== 8) erros.push('CEP deve ter 8 dígitos')
  if (n.codigo_municipio_ibge.length !== 7) erros.push('Código IBGE deve ter 7 dígitos')
  if (n.uf.length !== 2) erros.push('UF deve ter 2 letras')
  return erros
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
    form.value = normalizarEmitente(await getEmitenteFiscal())
  } catch (e) {
    if (e.response?.status === 404) {
      form.value = emitenteVazio()
    } else {
      erroCarregar.value = mensagemErroApi(e, 'Falha ao carregar emitente.')
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
  const errosLocal = validarEmitenteLocal(form.value)
  if (errosLocal.length) {
    alert(errosLocal.join('\n'))
    return
  }
  salvando.value = true
  try {
    const salvo = await saveEmitenteFiscal(payloadEmitente(form.value))
    form.value = { ...form.value, ...normalizarEmitente(salvo) }
    emit('salvo')
    alert('Emitente salvo.')
  } catch (e) {
    alert(mensagemErroApi(e, 'Erro ao salvar emitente.'))
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
