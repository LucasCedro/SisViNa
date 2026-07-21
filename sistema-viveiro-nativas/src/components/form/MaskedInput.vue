<template>
  <label v-if="!bare" class="module-field">
    <span v-if="label">{{ label }}</span>
    <input
      :value="display"
      type="text"
      :inputmode="cfg.inputmode"
      :maxlength="cfg.maxlength"
      :placeholder="placeholder || cfg.placeholder"
      :required="required"
      :disabled="disabled"
      :autocomplete="autocomplete"
      @input="onInput"
      @blur="onBlur"
    />
    <span v-if="hint" class="field-hint">{{ hint }}</span>
  </label>
  <input
    v-else
    :value="display"
    type="text"
    :inputmode="cfg.inputmode"
    :maxlength="cfg.maxlength"
    :placeholder="placeholder || cfg.placeholder"
    :required="required"
    :disabled="disabled"
    :autocomplete="autocomplete"
    @input="onInput"
    @blur="onBlur"
  />
</template>

<script setup>
import { computed } from 'vue'
import { MASK_CONFIG } from '@/utils/inputMasks'

const props = defineProps({
  modelValue: { type: String, default: '' },
  mask: {
    type: String,
    required: true,
    validator: (v) => Object.keys(MASK_CONFIG).includes(v),
  },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  hint: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  autocomplete: { type: String, default: 'off' },
  /** Sem wrapper label — use dentro de label customizado (God Mode, Configurações). */
  bare: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const cfg = computed(() => MASK_CONFIG[props.mask])

const display = computed(() => cfg.value.format(props.modelValue))

function onInput(e) {
  emit('update:modelValue', cfg.value.parse(e.target.value))
}

function onBlur(e) {
  e.target.value = cfg.value.format(props.modelValue)
}
</script>

<style scoped>
.field-hint {
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--color-text-muted);
}
</style>
