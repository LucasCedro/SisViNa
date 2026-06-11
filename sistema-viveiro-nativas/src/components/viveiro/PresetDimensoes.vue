<template>
  <div class="preset-dims">
    <p v-if="hint" class="preset-hint">{{ hint }}</p>
    <div class="preset-chips" role="list" :aria-label="ariaLabel">
      <button
        v-for="p in presets"
        :key="p.id"
        type="button"
        role="listitem"
        class="preset-chip"
        :class="{ 'preset-chip--ativo': ativoId === p.id }"
        :title="p.descricao"
        @click="emit('aplicar', p)"
      >
        <span class="preset-chip-preview" :class="`preset-chip-preview--${previewClass(p)}`" aria-hidden="true" />
        <span class="preset-chip-label">{{ p.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { PRESETS_DIMENSAO } from '@/constants/viveiroDimensoes'

defineProps({
  hint: { type: String, default: 'Medidas reais do chão — canteiros costumam ser faixas estreitas.' },
  ariaLabel: { type: String, default: 'Presets de dimensão' },
  ativoId: { type: String, default: null },
  presets: { type: Array, default: () => PRESETS_DIMENSAO },
})

const emit = defineEmits(['aplicar'])

function previewClass(p) {
  const ratio = p.largura / p.altura
  if (ratio > 1.4) return 'h'
  if (ratio < 0.7) return 'v'
  return 'q'
}
</script>

<style scoped>
.preset-hint {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  color: #6b7280;
  line-height: 1.4;
}

.preset-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.preset-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.55rem;
  border: 1px solid #d1d5db;
  border-radius: 999px;
  background: #fff;
  font-size: 0.75rem;
  font-family: inherit;
  color: #374151;
  cursor: pointer;
  transition: border-color 0.12s, background 0.12s;
}

.preset-chip:hover {
  border-color: var(--color-primary, #4a7c2a);
  background: #f9fafb;
}

.preset-chip--ativo {
  border-color: var(--color-primary, #4a7c2a);
  background: #eef4e8;
  color: #2d5016;
  font-weight: 600;
}

.preset-chip-preview {
  display: block;
  border-radius: 2px;
  background: var(--color-primary, #6ca234);
  opacity: 0.75;
  flex-shrink: 0;
}

.preset-chip-preview--v {
  width: 6px;
  height: 14px;
}

.preset-chip-preview--h {
  width: 14px;
  height: 6px;
}

.preset-chip-preview--q {
  width: 10px;
  height: 10px;
}

.preset-chip-label {
  white-space: nowrap;
}
</style>
