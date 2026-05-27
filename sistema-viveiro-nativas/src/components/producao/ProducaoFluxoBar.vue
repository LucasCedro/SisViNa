<template>
  <div class="pipeline" role="navigation" aria-label="Fluxo de produção">
    <div class="pipeline-track">
      <section
        v-for="(bloco, i) in blocos"
        :key="bloco.id"
        class="pipeline-col"
        :class="{ 'pipeline-col--ativo': colunaAtiva(bloco.id) }"
      >
        <button type="button" class="pipeline-col__head" @click="$emit('ir-etapa', bloco.id)">
          <span class="pipeline-col__step">{{ i + 1 }}</span>
          <span class="pipeline-col__titulo">{{ bloco.titulo }}</span>
        </button>

        <div class="pipeline-col__body">
          <article
            v-for="card in cardsDoBloco(bloco)"
            :key="card.id"
            class="pipeline-card"
            :class="'pipeline-card--' + (card.tom || 'neutro')"
            @click="$emit('ir-etapa', card.irPara || bloco.id)"
          >
            <span class="pipeline-card__valor">
              {{ card.valor }}
              <span v-if="card.sufixo" class="pipeline-card__sufixo">{{ card.sufixo }}</span>
            </span>
            <span class="pipeline-card__label">{{ card.label }}</span>
          </article>
        </div>
      </section>
    </div>

    <p class="pipeline-nota">
      Vendas em <router-link to="/vendas">Vendas</router-link>
      · estoque em <router-link to="/estoques">Estoques</router-link>
    </p>
  </div>
</template>

<script setup>
const props = defineProps({
  blocos: { type: Array, required: true },
  blocoAtivo: { type: String, default: 'visao' },
})
defineEmits(['ir-etapa'])

function cardsDoBloco(bloco) {
  if (bloco.cards?.length) return bloco.cards
  return [
    {
      id: 'solo',
      valor: bloco.valorTotal,
      sufixo: bloco.valorSufixo,
      label: bloco.subtitulo || 'Total',
      tom: 'neutro',
    },
  ]
}

function colunaAtiva(id) {
  const map = {
    semeadura: ['semeadura'],
    sementeira: ['liberar_canteiro', 'transferencia'],
    canteiro: ['rustificacao', 'liberar_venda'],
    rustificacao: ['rustificacao', 'liberar_venda'],
    vendidas: ['visao'],
  }
  return (map[id] || [id]).includes(props.blocoAtivo)
}
</script>

<style scoped>
.pipeline {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--spacing-lg);
}

.pipeline-track {
  display: flex;
  gap: 0;
  align-items: stretch;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}

.pipeline-col {
  flex: 1 1 0;
  min-width: 11rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0 0.5rem;
  border-right: 1px solid var(--color-border-subtle);
}

.pipeline-col:last-child {
  border-right: none;
}

.pipeline-col--ativo .pipeline-col__titulo {
  color: var(--color-primary-700);
}

.pipeline-col__head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: none;
  background: none;
  padding: 0;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  width: 100%;
}

.pipeline-col__step {
  flex-shrink: 0;
  width: 1.625rem;
  height: 1.625rem;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-size: 0.8125rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.pipeline-col__titulo {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.pipeline-col__body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.pipeline-card {
  flex: 1;
  min-height: 4.5rem;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-subtle);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.2rem;
  transition: box-shadow 0.15s, border-color 0.15s;
}

.pipeline-card:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--color-primary-100);
}

.pipeline-card--desenvolvimento {
  background: var(--color-surface-muted);
  border-left: 4px solid var(--color-text-muted);
}

.pipeline-card--acao {
  background: var(--color-attention-bg);
  border-left: 4px solid var(--color-attention);
}

.pipeline-card--crescimento {
  background: var(--color-primary-subtle);
  border-left: 4px solid var(--color-primary);
}

.pipeline-card--rustificacao {
  background: #f5f0e8;
  border-left: 4px solid #c4a574;
}

.pipeline-card--venda {
  background: var(--color-success-bg);
  border-left: 4px solid var(--color-success);
}

.pipeline-card--neutro {
  background: var(--color-background);
}

.pipeline-card__valor {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
  color: var(--color-primary-700);
}

.pipeline-card__sufixo {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.pipeline-card__label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  line-height: 1.3;
}

.pipeline-nota {
  margin: var(--spacing-md) 0 0;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-subtle);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.pipeline-nota a {
  color: var(--color-primary);
  font-weight: 600;
}

@media (max-width: 900px) {
  .pipeline-track {
    flex-direction: column;
  }
  .pipeline-col {
    border-right: none;
    border-bottom: 1px solid var(--color-border-subtle);
    padding-bottom: var(--spacing-md);
    min-width: 100%;
  }
  .pipeline-col:last-child {
    border-bottom: none;
  }
  .pipeline-col__body {
    flex-direction: row;
  }
  .pipeline-card {
    flex: 1;
    min-height: 4rem;
  }
}
</style>
