<template>
  <div class="viveiro-kpis" role="group" aria-label="Resumo do viveiro">
    <div class="kpi">
      <span class="kpi-valor">{{ totalAreas }}</span>
      <span class="kpi-label">Áreas no mapa</span>
    </div>
    <div class="kpi">
      <span class="kpi-valor">{{ totalMudas }}</span>
      <span class="kpi-label">Mudas ativas</span>
    </div>
    <div class="kpi" :class="{ 'kpi--alerta': alertas > 0 }">
      <span class="kpi-valor">{{ alertas }}</span>
      <span class="kpi-label">Alertas</span>
    </div>
    <div class="kpi">
      <span class="kpi-valor">{{ areasProdutivas }}</span>
      <span class="kpi-label">Locais de produção</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useViveiroStore } from '@/store/viveiro'

const store = useViveiroStore()

const totalAreas = computed(() => store.layout.elementos?.length ?? 0)
const totalMudas = computed(() => store.metricas.totalMudas ?? store.mudas.length)
const alertas = computed(() => store.alertasAtivos?.length ?? 0)
const areasProdutivas = computed(() =>
  (store.layout.elementos || []).filter((e) =>
    ['canteiro', 'sementeira', 'rustificacao'].includes(e.tipo)
  ).length
)
</script>

<style scoped>
.viveiro-kpis {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.kpi {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: 1rem 1.125rem;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.kpi-valor {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.2;
}

.kpi-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  line-height: 1.35;
}

.kpi--alerta .kpi-valor {
  color: var(--color-error, #b42318);
}

@media (max-width: 900px) {
  .viveiro-kpis {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
