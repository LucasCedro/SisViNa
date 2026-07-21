<template>
  <Teleport to="body">
    <div
      v-if="aberto"
      class="app-modal-overlay"
      @pointerdown.self="handlers.onOverlayPointerDown"
      @pointerup.self="handlers.onOverlayPointerUp"
      @pointercancel.self="handlers.cancelarFechamentoOverlay"
    >
      <div
        class="app-modal-panel"
        :class="panelClass"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="ariaLabelledby"
        :aria-label="ariaLabel"
        @pointerdown="handlers.onModalPointerDown"
      >
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  aberto: { type: Boolean, default: false },
  handlers: { type: Object, required: true },
  panelClass: { type: [String, Array, Object], default: 'app-modal-panel--md' },
  ariaLabelledby: { type: String, default: undefined },
  ariaLabel: { type: String, default: undefined },
})
</script>
