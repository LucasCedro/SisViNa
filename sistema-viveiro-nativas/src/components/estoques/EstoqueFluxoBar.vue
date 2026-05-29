<template>
  <div class="fluxo-estoque" role="navigation" aria-label="Resumo do estoque">
    <div class="fluxo-estoque__track">
      <button
        v-for="col in colunas"
        :key="col.id"
        type="button"
        class="fluxo-col"
        :class="{ 'fluxo-col--ativo': guiaAtiva === col.guia }"
        @click="$emit('ir-guia', col.guia)"
      >
        <span class="fluxo-col__step">{{ col.step }}</span>
        <span class="fluxo-col__titulo">{{ col.titulo }}</span>
        <strong class="fluxo-col__valor">{{ col.valor }}</strong>
        <span class="fluxo-col__hint">{{ col.hint }}</span>
      </button>
    </div>
    <p class="fluxo-estoque__nota">
      Baixa de mudas em <router-link to="/vendas">Vendas</router-link>
      · produção em <router-link to="/producao">Produção</router-link>
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  resumo: { type: Object, required: true },
  guiaAtiva: { type: String, default: 'mudas' },
})

defineEmits(['ir-guia'])

function fmtMoeda(v) {
  return Number(v || 0).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  })
}

const colunas = computed(() => {
  const p = props.resumo?.mudas_pipeline || {}
  return [
    {
      id: 'sementes',
      guia: 'sementes',
      step: '1',
      titulo: 'Sementes',
      valor: props.resumo?.total_sementes_disponiveis ?? 0,
      hint: `${props.resumo?.total_lotes_sementes_ativos ?? 0} lote(s)`,
    },
    {
      id: 'dev',
      guia: 'mudas',
      step: '2',
      titulo: 'Em desenvolvimento',
      valor: p.em_desenvolvimento_total ?? 0,
      hint: `${p.em_desenvolvimento_sementeira ?? 0} sem. · ${p.em_desenvolvimento_canteiro ?? 0} cant.`,
    },
    {
      id: 'rust',
      guia: 'mudas',
      step: '3',
      titulo: 'Rustificação',
      valor: p.em_rustificacao ?? 0,
      hint: `${p.aptas_venda_aguardando_tempo ?? 0} abaixo prazo recom.`,
    },
    {
      id: 'venda',
      guia: 'mudas',
      step: '4',
      titulo: 'Prontas p/ venda',
      valor: props.resumo?.total_mudas_aptas_venda ?? 0,
      hint: `prazo recom. ${p.dias_minimos_rustificacao ?? 30} dias`,
    },
    {
      id: 'insumos',
      guia: 'insumos',
      step: '₿',
      titulo: 'Insumos (CMV)',
      valor: fmtMoeda(props.resumo?.valor_total_insumos),
      hint: `${props.resumo?.total_insumos ?? 0} item(ns)`,
    },
  ]
})
</script>

<style scoped>
.fluxo-estoque {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.fluxo-estoque__track {
  display: flex;
  gap: 0;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}

.fluxo-col {
  flex: 1 1 0;
  min-width: 9.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.15rem;
  padding: 0.65rem 1rem;
  border: none;
  border-right: 1px solid var(--color-border-subtle);
  background: transparent;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: background 0.15s;
}

.fluxo-col:last-child {
  border-right: none;
}

.fluxo-col:hover {
  background: var(--color-primary-subtle);
}

.fluxo-col--ativo {
  background: var(--color-primary-subtle);
  box-shadow: inset 0 -3px 0 var(--color-primary);
}

.fluxo-col__step {
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.fluxo-col__titulo {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.fluxo-col__valor {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-primary-700);
  line-height: 1.1;
}

.fluxo-col__hint {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  line-height: 1.3;
}

.fluxo-estoque__nota {
  margin: var(--spacing-md) 0 0;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-subtle);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.fluxo-estoque__nota a {
  color: var(--color-primary-700);
  font-weight: 600;
}
</style>
