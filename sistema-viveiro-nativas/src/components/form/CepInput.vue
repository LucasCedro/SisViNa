<template>
  <label class="module-field">
    <span>{{ label }}</span>
    <input
      :value="display"
      type="text"
      inputmode="numeric"
      maxlength="9"
      placeholder="00000-000"
      :required="required"
      @input="onInput"
      @blur="onBlur"
    />
    <span v-if="buscando" class="cep-msg cep-msg--load">Buscando endereço…</span>
    <span v-else-if="msg" class="cep-msg" :class="msgOk ? 'cep-msg--ok' : 'cep-msg--err'">{{ msg }}</span>
  </label>
</template>

<script setup>
import { ref, computed } from 'vue'
import { buscarCep, formatarCep } from '@/services/viacep'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: 'CEP' },
  required: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'endereco'])

const buscando = ref(false)
const msg = ref('')
const msgOk = ref(false)
let timer = null

const display = computed(() => formatarCep(props.modelValue))

function onInput(e) {
  const raw = e.target.value.replace(/\D/g, '').slice(0, 8)
  emit('update:modelValue', raw)
  msg.value = ''
  clearTimeout(timer)
  if (raw.length === 8) {
    timer = setTimeout(() => consultar(raw), 350)
  }
}

function onBlur(e) {
  e.target.value = formatarCep(props.modelValue)
}

async function consultar(digits) {
  buscando.value = true
  msg.value = ''
  try {
    const end = await buscarCep(digits)
    emit('endereco', end)
    msgOk.value = true
    msg.value = 'Endereço preenchido automaticamente'
  } catch (err) {
    msgOk.value = false
    msg.value = err.message || 'CEP inválido'
  } finally {
    buscando.value = false
  }
}
</script>

<style scoped>
.cep-msg {
  font-size: 0.75rem;
  font-weight: 500;
}
.cep-msg--load {
  color: var(--color-text-muted);
}
.cep-msg--ok {
  color: var(--color-success);
}
.cep-msg--err {
  color: var(--color-error);
}
</style>
