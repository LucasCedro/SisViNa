<template>
  <div class="contab-notas module-sec">
    <p v-if="carregando && !dados" class="status-msg">Carregando notas…</p>
    <p v-else-if="erro" class="alert-erro">{{ erro }}</p>
    <template v-else-if="dados">
      <p class="contab-lead">
        Notas explicativas — critérios contábeis e destaques de {{ dados.periodo?.label }}.
      </p>

      <div class="notas-grid">
        <article v-for="(sec, i) in dados.secoes" :key="i" class="nota-card">
          <h3>{{ sec.titulo }}</h3>
          <p>{{ sec.texto }}</p>
        </article>
      </div>

      <aside class="nota-resumo">
        <h3>Resumo numérico</h3>
        <dl>
          <div><dt>Ativo total (BP)</dt><dd>R$ {{ fmt(dados.balanco_resumo?.ativo_total) }}</dd></div>
          <div><dt>Contas a receber</dt><dd>R$ {{ fmt(dados.balanco_resumo?.contas_receber) }}</dd></div>
          <div><dt>Patrimônio líquido</dt><dd>R$ {{ fmt(dados.balanco_resumo?.patrimonio_liquido) }}</dd></div>
          <div><dt>Faturamento (DRE)</dt><dd>R$ {{ fmt(dados.dre_resumo?.faturamento) }}</dd></div>
          <div><dt>Resultado operacional</dt><dd>R$ {{ fmt(dados.dre_resumo?.resultado_operacional) }}</dd></div>
        </dl>
      </aside>
    </template>
  </div>
</template>

<script setup>
defineProps({
  dados: { type: Object, default: null },
  carregando: { type: Boolean, default: false },
  erro: { type: String, default: null },
})

function fmt(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.contab-lead {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin: 0 0 var(--spacing-md);
}
.notas-grid {
  display: grid;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}
.nota-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}
.nota-card h3 {
  margin: 0 0 0.35rem;
  font-size: 0.9375rem;
}
.nota-card p {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-secondary, inherit);
}
.nota-resumo {
  background: var(--color-surface-muted);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}
.nota-resumo h3 {
  margin: 0 0 var(--spacing-sm);
  font-size: 0.9375rem;
}
.nota-resumo dl {
  margin: 0;
}
.nota-resumo > dl > div {
  display: flex;
  justify-content: space-between;
  padding: 0.3rem 0;
  font-size: 0.875rem;
  border-bottom: 1px solid var(--color-border-subtle);
}
.nota-resumo dt {
  color: var(--color-text-muted);
}
.nota-resumo dd {
  margin: 0;
  font-weight: 600;
}
</style>
