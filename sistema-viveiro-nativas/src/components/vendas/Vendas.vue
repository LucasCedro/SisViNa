<template>
  <div class="module-root">
    <nav class="module-tabs" aria-label="Seções de vendas">
      <button
        v-for="t in abas"
        :key="t.id"
        type="button"
        class="module-tab"
        :class="{ ativo: aba === t.id }"
        @click="aba = t.id"
      >
        {{ t.label }}
      </button>
    </nav>

    <VendasPanel v-show="aba === 'vendas'" ref="vendasPanelRef" />
    <VendasClientesPanel v-show="aba === 'clientes'" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { usePageTab } from '@/composables/usePageTab'
import VendasPanel from './VendasPanel.vue'
import VendasClientesPanel from './VendasClientesPanel.vue'

const aba = usePageTab('vendas', 'vendas', { valid: ['vendas', 'clientes'] })
const vendasPanelRef = ref(null)

const abas = [
  { id: 'vendas', label: 'Vendas' },
  { id: 'clientes', label: 'Clientes' },
]

watch(aba, (id) => {
  if (id === 'vendas') vendasPanelRef.value?.recarregarCompradores?.()
})
</script>
