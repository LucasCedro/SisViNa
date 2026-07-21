<template>
  <Teleport to="body">
    <Transition name="app-loading-fade">
      <div
        v-if="visible"
        class="app-loading-overlay"
        role="alertdialog"
        aria-modal="true"
        aria-busy="true"
        :aria-label="message"
      >
        <div class="app-loading-card">
          <div class="app-loading-spinner" aria-hidden="true" />
          <p class="app-loading-msg">{{ message }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useGlobalLoading } from '@/composables/useGlobalLoading'

const { visible, message } = useGlobalLoading()
</script>

<style scoped>
.app-loading-overlay {
  position: fixed;
  inset: 0;
  z-index: 1700;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(34, 42, 28, 0.38);
  backdrop-filter: blur(2px);
  pointer-events: all;
}

.app-loading-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: var(--color-surface, #fff);
  border-radius: var(--radius-lg, 12px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
  min-width: 220px;
  max-width: min(90vw, 360px);
}

.app-loading-spinner {
  width: 2.25rem;
  height: 2.25rem;
  border: 3px solid var(--color-primary-100, #cbd3c3);
  border-top-color: var(--color-primary, #596247);
  border-radius: 50%;
  animation: app-loading-spin 0.75s linear infinite;
}

.app-loading-msg {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-text-primary, #222);
  text-align: center;
  line-height: 1.4;
}

@keyframes app-loading-spin {
  to {
    transform: rotate(360deg);
  }
}

.app-loading-fade-enter-active,
.app-loading-fade-leave-active {
  transition: opacity 0.2s ease;
}

.app-loading-fade-enter-from,
.app-loading-fade-leave-to {
  opacity: 0;
}
</style>
