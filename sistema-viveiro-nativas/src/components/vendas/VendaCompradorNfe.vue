<template>
  <section class="comprador-nfe">
    <div class="comprador-modo">
      <label class="modo-opt">
        <input v-model="modo" type="radio" value="cadastrado" />
        Cliente cadastrado
      </label>
      <label class="modo-opt">
        <input v-model="modo" type="radio" value="novo" />
        Cliente novo (cadastrar na venda)
      </label>
    </div>

    <template v-if="modo === 'cadastrado'">
      <label class="module-field">
        Comprador
        <select v-model.number="idLocal" required @change="onCompradorChange">
          <option :value="null">Selecione</option>
          <option v-for="c in compradores" :key="c.id" :value="c.id">
            {{ c.nome }} — {{ c.estado || '?' }} ({{ c.tipo }})
          </option>
        </select>
      </label>
      <p v-if="readiness?.pronto" class="status-ok">✓ Dados completos para NF-e</p>
      <ul v-else-if="readiness?.faltando?.length" class="status-warn">
        <li v-for="(f, i) in readiness.faltando" :key="i">{{ f }}</li>
      </ul>
    </template>

    <template v-else>
      <div class="module-form-row">
        <label class="module-field">
          Tipo
          <select v-model="novo.tipo" @change="atualizarPreview">
            <option value="PF">Pessoa física</option>
            <option value="PJ">Pessoa jurídica</option>
          </select>
        </label>
        <MaskedInput
          v-model="novo.cpf_cnpj"
          :mask="novo.tipo === 'PJ' ? 'cnpj' : 'cpf'"
          :label="novo.tipo === 'PJ' ? 'CNPJ' : 'CPF'"
          required
        />
      </div>
      <label class="module-field">
        Nome / Razão social
        <input v-model="novo.nome" required />
      </label>
      <div class="module-form-row">
        <MaskedInput v-model="novo.telefone" mask="telefone" label="Telefone" />
        <label class="module-field">
          E-mail
          <input v-model="novo.email" type="email" />
        </label>
      </div>

      <CepInput v-model="novo.cep" required @endereco="onCep" />

      <label class="module-field">
        Logradouro
        <input v-model="novo.endereco" required />
      </label>
      <div class="module-form-row">
        <label class="module-field">
          Nº
          <input v-model="novo.numero" required />
        </label>
        <label class="module-field">
          Bairro
          <input v-model="novo.bairro" required />
        </label>
      </div>
      <div class="module-form-row">
        <label class="module-field">
          Cidade
          <input v-model="novo.cidade" required @input="atualizarPreview" />
        </label>
        <MaskedInput v-model="novo.estado" mask="uf" label="UF" required />
      </div>
      <MaskedInput
        v-model="novo.codigo_municipio_ibge"
        mask="ibge"
        label="Cód. IBGE município (7 dígitos)"
        required
        placeholder="Ex.: 5208707"
      />
      <div class="module-form-row">
        <MaskedInput
          v-model="novo.inscricao_estadual"
          mask="ie"
          label="Inscrição estadual"
          hint="Somente números"
        />
        <label class="module-field">
          Indicador IE
          <select v-model="novo.indicador_ie">
            <option value="9">9 — Não contribuinte</option>
            <option value="1">1 — Contribuinte</option>
            <option value="2">2 — Isento</option>
          </select>
        </label>
      </div>
    </template>

    <aside v-if="preview" class="preview-regra" :class="{ 'preview-regra--erro': !preview.encontrada }">
      <strong>Fiscal (prévia)</strong>
      <p>{{ preview.mensagem }}</p>
      <p v-if="preview.encontrada" class="preview-detalhe">
        {{ preview.operacao }} · CFOP {{ preview.cfop_resolvido }} · CSOSN {{ preview.regra?.csosn }}
      </p>
      <p v-if="preview.tributacao_resumo" class="preview-trib">
        {{ preview.tributacao_resumo }}
      </p>
      <p v-if="preview.difal_aplicavel" class="preview-difal">
        DIFAL: {{ preview.aliquota_icms_inter }}% interestadual → {{ preview.aliquota_icms_intra }}% intra destino
      </p>
      <p v-if="preview.importacao_aplicavel" class="preview-imp">
        Importação SN · orig {{ preview.icms_origem }}
        <span v-if="preview.aliquota_icms_importacao"> · ref. {{ preview.aliquota_icms_importacao }}%</span>
      </p>
    </aside>
  </section>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import CepInput from '@/components/form/CepInput.vue'
import MaskedInput from '@/components/form/MaskedInput.vue'
import { compradorVazio, normalizarCompradorCampos } from '@/constants/compradorForm'
import { listCompradores, createComprador, getCompradorNfeReadiness } from '@/services/compradores'
import { previewRegraFiscal } from '@/services/fiscal'
import { aplicarEnderecoCep } from '@/utils/cepAutofill'
import { onlyDigits } from '@/utils/inputMasks'

const props = defineProps({
  idComprador: { type: Number, default: null },
  tipoOperacaoFiscal: { type: String, default: 'domestica' },
})

const emit = defineEmits(['update:idComprador'])

const modo = ref('cadastrado')
const compradores = ref([])
const idLocal = ref(props.idComprador)
const readiness = ref(null)
const preview = ref(null)
const novo = ref(compradorVazio())

watch(idLocal, (v) => emit('update:idComprador', v || null))
watch(
  () => props.idComprador,
  (v) => {
    idLocal.value = v
  }
)

watch(
  () => novo.value.estado,
  () => atualizarPreview()
)

watch(
  () => novo.value.tipo,
  (tipo) => {
    const d = onlyDigits(novo.value.cpf_cnpj)
    novo.value.cpf_cnpj = tipo === 'PJ' ? d.slice(0, 14) : d.slice(0, 11)
    atualizarPreview()
  }
)

function onCep(end) {
  aplicarEnderecoCep(novo.value, end)
  atualizarPreview()
}

async function carregarCompradores() {
  compradores.value = await listCompradores({ ativo: true, limit: 300 })
}

watch(
  () => props.tipoOperacaoFiscal,
  () => {
    if (modo.value === 'cadastrado' && idLocal.value) onCompradorChange()
    else if (modo.value === 'novo') atualizarPreview()
  }
)

async function fetchPreview(uf, tipoCliente) {
  return previewRegraFiscal({
    uf_destino: uf,
    tipo_cliente: tipoCliente,
    tipo_operacao: props.tipoOperacaoFiscal || 'domestica',
  })
}

async function onCompradorChange() {
  readiness.value = null
  preview.value = null
  if (!idLocal.value) return
  const c = compradores.value.find((x) => x.id === idLocal.value)
  readiness.value = await getCompradorNfeReadiness(idLocal.value)
  if (c?.estado) {
    preview.value = await fetchPreview(c.estado, c.tipo || 'PF')
  }
}

async function atualizarPreview() {
  const uf = (novo.value.estado || '').trim()
  if (uf.length !== 2) {
    preview.value = null
    return
  }
  preview.value = await fetchPreview(uf, novo.value.tipo)
}

/** Cria comprador se modo novo; retorna id ou null. */
async function garantirCompradorId() {
  if (modo.value === 'cadastrado') {
    if (!idLocal.value) throw new Error('Selecione o comprador.')
    return idLocal.value
  }
  const payload = normalizarCompradorCampos({ ...novo.value })
  const criado = await createComprador(payload)
  idLocal.value = criado.id
  emit('update:idComprador', criado.id)
  await carregarCompradores()
  return criado.id
}

onMounted(async () => {
  await carregarCompradores()
  if (idLocal.value) await onCompradorChange()
})

defineExpose({ garantirCompradorId, recarregarCompradores: carregarCompradores })
</script>

<style scoped>
.comprador-nfe {
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  background: var(--color-surface-muted);
}
.comprador-modo {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  font-size: 0.875rem;
}
.modo-opt {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
}
.status-ok {
  color: var(--color-success);
  font-size: 0.8125rem;
  margin: 0 0 var(--spacing-sm);
}
.status-warn {
  margin: 0 0 var(--spacing-sm);
  padding-left: 1.1rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}
.preview-regra {
  margin-top: var(--spacing-sm);
  padding: 0.5rem 0.65rem;
  border-radius: var(--radius-sm);
  background: var(--color-info-bg);
  border: 1px solid var(--color-info);
  font-size: 0.8125rem;
  color: var(--color-info-dark);
}
.preview-regra--erro {
  background: var(--color-attention-bg);
  border-color: var(--color-attention);
  color: var(--color-text-secondary);
}
.preview-regra p {
  margin: 0.25rem 0 0;
}
.preview-detalhe {
  font-weight: 600;
}
.preview-trib {
  margin: 0.25rem 0 0;
  font-size: 0.8125rem;
}
.preview-difal {
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-info-dark);
}
.preview-imp {
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}
</style>
