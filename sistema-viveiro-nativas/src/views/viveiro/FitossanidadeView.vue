<template>
  <PageLayout full-height>
    <PageSection tabs flush-body>
      <div class="guias-container">
        <div class="guias-navegacao">
          <button class="guia" :class="{ ativa: guiaAtiva === 'monitoramento' }" @click="guiaAtiva = 'monitoramento'">
            Monitoramento
          </button>
          <button class="guia" :class="{ ativa: guiaAtiva === 'analise' }" @click="guiaAtiva = 'analise'">
            Análise de recorrência
          </button>
        </div>
        <div class="guia-conteudo">
          <Fitossanidade v-if="guiaAtiva === 'monitoramento'" />
          <AnaliseRecorrencia v-else />
        </div>
      </div>
    </PageSection>
  </PageLayout>
</template>

<script setup>
import { usePageTab } from '@/composables/usePageTab'
import PageLayout from '@/components/layout/PageLayout.vue'
import PageSection from '@/components/layout/PageSection.vue'
import Fitossanidade from '@/components/viveiro/Fitossanidade.vue'
import AnaliseRecorrencia from '@/components/viveiro/AnaliseRecorrencia.vue'

const guiaAtiva = usePageTab('fitossanidade', 'monitoramento', { valid: ['monitoramento', 'analise'] })
</script>

<style scoped>
.guias-container {
  width: 100%;
}

.guias-navegacao {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md) var(--spacing-lg) 0;
}

.guia-conteudo {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}
</style>
