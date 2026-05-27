<template>
  <section class="page-section" :class="{ 'page-section--tabs': tabs, 'page-section--flush': flush }">
    <header v-if="$slots.header" class="page-section__header">
      <slot name="header" />
    </header>
    <div class="page-section__body" :class="{ 'page-section__body--flush': flushBody }">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  tabs: { type: Boolean, default: false },
  flush: { type: Boolean, default: false },
  flushBody: { type: Boolean, default: false },
})
</script>

<style scoped>
.page-section {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.page-section--tabs {
  overflow: visible;
  min-height: 0;
}

.page-section--flush {
  box-shadow: none;
  background: transparent;
}

.page-section__header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-subtle);
}

.page-section__body {
  padding: var(--spacing-lg);
}

.page-section__body--flush {
  padding: 0;
}

.page-section--tabs .page-section__body {
  padding: var(--spacing-lg);
  overflow: visible;
}
</style>
