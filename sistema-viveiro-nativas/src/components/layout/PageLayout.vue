<template>
  <div class="page-layout" :class="{ 'page-layout--full': fullHeight }">
    <slot />
  </div>
</template>

<script setup>
defineProps({
  /** Preenche altura útil abaixo do header (telas com abas internas). */
  fullHeight: { type: Boolean, default: false },
})
</script>

<style scoped>
.page-layout {
  width: 100%;
  min-height: 100%;
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.page-layout--full {
  height: 100%;
  overflow: auto;
}

@media (max-width: 768px) {
  .page-layout {
    padding: var(--spacing-md);
    gap: var(--spacing-md);
  }
}
</style>
