<template>
  <section class="alertas-panel">
    <h3 class="alertas-titulo">Alertas recentes</h3>
    <p v-if="!alertas.length" class="alertas-vazio">Nenhum alerta ativo no momento.</p>
    <ul v-else class="alertas-lista">
      <li v-for="a in alertas.slice(0, 5)" :key="a.id" class="alerta-item">
        <span class="alerta-dot" aria-hidden="true" />
        <div class="alerta-texto">
          <span class="alerta-msg">{{ a.mensagem }}</span>
          <span v-if="a.canteiro" class="alerta-local">{{ a.canteiro }}</span>
        </div>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useViveiroStore } from '@/store/viveiro'

const store = useViveiroStore()
const alertas = computed(() => store.alertasAtivos || [])
</script>

<style scoped>
.alertas-panel {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-subtle);
}

.alertas-titulo {
  margin: 0 0 var(--spacing-sm);
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.alertas-vazio {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.alertas-lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.alerta-item {
  display: flex;
  gap: var(--spacing-sm);
  align-items: flex-start;
  padding: var(--spacing-sm) var(--spacing-md);
  background: #fef3f2;
  border-radius: var(--radius-md);
  font-size: 0.8125rem;
}

.alerta-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-error, #dc2626);
  margin-top: 0.35rem;
  flex-shrink: 0;
}

.alerta-texto {
  min-width: 0;
  flex: 1;
}

.alerta-msg {
  display: block;
  color: var(--color-text-primary);
  word-break: break-word;
  overflow-wrap: anywhere;
  line-height: 1.35;
}

.alerta-local {
  display: block;
  color: var(--color-text-secondary);
  margin-top: 0.15rem;
}
</style>
