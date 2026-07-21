<template>
  <div class="modo-nav-wrap">
    <nav class="modo-nav" aria-label="Modo de operação">
      <button
        type="button"
        class="modo-btn"
        :class="{ 'modo-btn--ativo': modelo === PRODUCAO_MODO.MASSA }"
        @click="modelo = PRODUCAO_MODO.MASSA"
      >
        {{ PRODUCAO_MODO_LABEL[PRODUCAO_MODO.MASSA] }}
      </button>
      <button
        type="button"
        class="modo-btn"
        :class="{ 'modo-btn--ativo': modelo === PRODUCAO_MODO.INDIVIDUAL }"
        @click="modelo = PRODUCAO_MODO.INDIVIDUAL"
      >
        {{ PRODUCAO_MODO_LABEL[PRODUCAO_MODO.INDIVIDUAL] }}
      </button>
    </nav>
    <p class="modo-ajuda">{{ PRODUCAO_MODO_AJUDA }}</p>
    <slot :modo="modelo" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  PRODUCAO_MODO,
  PRODUCAO_MODO_LABEL,
  PRODUCAO_MODO_AJUDA,
} from '@/constants/producaoUi'

const props = defineProps({
  modo: { type: String, default: PRODUCAO_MODO.MASSA },
})

const emit = defineEmits(['update:modo'])

const modelo = computed({
  get: () => props.modo,
  set: (v) => emit('update:modo', v),
})
</script>

<style scoped>
.modo-nav {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.modo-ajuda {
  margin: 0 0 var(--spacing-md);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  line-height: 1.45;
}

.modo-btn {
  padding: 0.45rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
}

.modo-btn--ativo {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-text-inverse);
}
</style>
