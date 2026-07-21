<template>
  <Teleport to="body">
    <div
      v-if="aberto"
      ref="root"
      class="confirm-saida-overlay"
      role="presentation"
      tabindex="-1"
      @keydown.esc.prevent.stop="$emit('cancelar')"
      @pointerdown.self="$emit('cancelar')"
    >
      <div
        class="confirm-saida-card"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-saida-titulo"
        aria-describedby="confirm-saida-texto"
        @pointerdown.stop
      >
        <header class="confirm-saida-card__header">
          <h3 id="confirm-saida-titulo">Deseja realmente sair?</h3>
          <p id="confirm-saida-texto">
            Há informações preenchidas que ainda não foram salvas.
          </p>
        </header>
        <footer class="confirm-saida-card__footer">
          <button type="button" class="btn btn-secondary" @click="$emit('cancelar')">
            Cancelar
          </button>
          <button type="button" class="btn btn-primary confirm-saida-card__sair" @click="$emit('confirmar')">
            Sair
          </button>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  aberto: { type: Boolean, default: false },
})

defineEmits(['confirmar', 'cancelar'])

const root = ref(null)

watch(
  () => props.aberto,
  async (open) => {
    if (!open) return
    await nextTick()
    root.value?.focus()
  },
)
</script>

<style scoped>
.confirm-saida-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal-confirm, 1600);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(34, 42, 28, 0.42);
  backdrop-filter: blur(3px);
}

.confirm-saida-card {
  width: min(400px, calc(100vw - 2rem));
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.confirm-saida-card__header {
  padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-md);
  border-bottom: 1px solid var(--color-border-subtle);
}

.confirm-saida-card__header h3 {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.confirm-saida-card__header p {
  margin: 0.45rem 0 0;
  font-size: 0.875rem;
  line-height: 1.45;
  color: var(--color-text-secondary);
}

.confirm-saida-card__footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-surface-muted);
}

.confirm-saida-card__sair {
  min-width: 5.5rem;
}
</style>
