<template>
  <span
    class="field-help"
    @mouseenter="visivel = true"
    @mouseleave="visivel = false"
  >
    <span
      class="field-help__btn"
      tabindex="0"
      role="img"
      :aria-label="`Ajuda: ${rotulo}`"
    >
      ?
    </span>
    <span v-show="visivel" class="field-help__text" role="tooltip">{{ texto }}</span>
  </span>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  rotulo: { type: String, default: 'campo' },
  texto: { type: String, required: true },
})

const visivel = ref(false)
</script>

<style scoped>
.field-help {
  position: relative;
  display: inline-flex;
  vertical-align: middle;
  margin-left: 0.35rem;
}
.field-help__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.05rem;
  height: 1.05rem;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-primary);
  font-size: 0.625rem;
  font-weight: 700;
  line-height: 1;
  cursor: help;
  user-select: none;
}
.field-help:hover .field-help__btn,
.field-help:focus-within .field-help__btn {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}
.field-help__text {
  position: absolute;
  z-index: 20;
  left: 50%;
  top: calc(100% + 0.35rem);
  transform: translateX(-50%);
  width: max-content;
  max-width: min(300px, 85vw);
  padding: 0.5rem 0.65rem;
  font-size: 0.8125rem;
  font-weight: 400;
  line-height: 1.45;
  color: var(--color-text-primary);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  pointer-events: none;
}
.field-help__text::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-bottom-color: var(--color-border);
}
</style>
