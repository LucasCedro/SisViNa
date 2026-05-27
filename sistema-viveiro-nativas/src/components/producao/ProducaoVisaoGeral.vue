<template>
  <div class="visao-panel">
    <section class="fase">
      <header class="fase-header">
        <h2 class="fase-titulo">Armazém</h2>
        <p class="fase-desc">Sementes aguardando semeadura</p>
      </header>
      <div class="fase-cards fase-cards--armazem">
        <article class="metric-card">
          <strong class="metric-card__valor">{{ resumo?.sementes_armazem ?? 0 }}</strong>
          <span class="metric-card__label">Sementes disponíveis</span>
          <span class="metric-card__meta">{{ resumo?.lotes_com_estoque ?? 0 }} lote(s)</span>
        </article>
        <article class="metric-card metric-card--idade">
          <strong class="metric-card__valor">{{ formatDias(resumo?.dias_medios_armazem) }}</strong>
          <span class="metric-card__label">Permanência em média (dias)</span>
          <span class="metric-card__meta">Sementes no armazém (dias)</span>
        </article>
      </div>
    </section>

    <section class="fase">
      <header class="fase-header">
        <h2 class="fase-titulo">Sementeira</h2>
        <p class="fase-desc">{{ resumo?.na_sementeira ?? 0 }} plântulas</p>
      </header>
      <div class="fase-cards">
        <article class="metric-card metric-card--desenvolvimento">
          <strong class="metric-card__valor">{{ resumo?.em_desenvolvimento_sementeira ?? 0 }}</strong>
          <span class="metric-card__label">Em desenvolvimento</span>
          <ul v-if="resumo?.por_especie_desenvolvimento?.length" class="especies-mini">
            <li v-for="e in resumo.por_especie_desenvolvimento.slice(0, 4)" :key="'d-' + e.id_especie">
              <span>{{ e.especie }}</span><strong>{{ e.quantidade }}</strong>
            </li>
          </ul>
        </article>
        <article class="metric-card metric-card--acao">
          <strong class="metric-card__valor">{{ resumo?.aptas_transferencia ?? 0 }}</strong>
          <span class="metric-card__label">Aptas p/ canteiro</span>
          <ul v-if="resumo?.por_especie_aptas_transferencia?.length" class="especies-mini">
            <li v-for="e in resumo.por_especie_aptas_transferencia.slice(0, 4)" :key="'t-' + e.id_especie">
              <span>{{ e.especie }}</span><strong>{{ e.quantidade }}</strong>
            </li>
          </ul>
        </article>
        <article class="metric-card metric-card--idade">
          <strong class="metric-card__valor">{{ formatDias(resumo?.dias_medios_sementeira) }}</strong>
          <span class="metric-card__label">Permanência em média (dias)</span>
          <span class="metric-card__meta">Plântulas na sementeira (dias)</span>
        </article>
      </div>
    </section>

    <section class="fase">
      <header class="fase-header">
        <h2 class="fase-titulo">Canteiro</h2>
        <p class="fase-desc">{{ resumo?.nos_canteiros ?? 0 }} mudas</p>
      </header>
      <div class="fase-cards">
        <article class="metric-card metric-card--crescimento">
          <strong class="metric-card__valor">{{ resumo?.em_crescimento_canteiro ?? 0 }}</strong>
          <span class="metric-card__label">Em crescimento</span>
          <ul v-if="resumo?.por_especie_em_crescimento?.length" class="especies-mini">
            <li v-for="e in resumo.por_especie_em_crescimento.slice(0, 4)" :key="'c-' + e.id_especie">
              <span>{{ e.especie }}</span><strong>{{ e.quantidade }}</strong>
            </li>
          </ul>
        </article>
        <article class="metric-card metric-card--rustificacao">
          <strong class="metric-card__valor">{{ resumo?.aptas_rustificacao_canteiro ?? 0 }}</strong>
          <span class="metric-card__label">Aptas p/ rustificação</span>
          <span class="metric-card__meta">Marcadas para entrar no fluxo de rustificação</span>
          <ul v-if="resumo?.por_especie_aptas_rustificacao?.length" class="especies-mini">
            <li v-for="e in resumo.por_especie_aptas_rustificacao.slice(0, 4)" :key="'ar-' + e.id_especie">
              <span>{{ e.especie }}</span><strong>{{ e.quantidade }}</strong>
            </li>
          </ul>
        </article>
        <article class="metric-card metric-card--idade">
          <strong class="metric-card__valor">{{ formatDias(resumo?.dias_medios_canteiro) }}</strong>
          <span class="metric-card__label">Permanência em média (dias)</span>
          <span class="metric-card__meta">Mudas no canteiro (dias)</span>
        </article>
      </div>
    </section>

    <section class="fase">
      <header class="fase-header">
        <h2 class="fase-titulo">Área de rustificação</h2>
        <p class="fase-desc">{{ resumo?.na_rustificacao ?? 0 }} mudas na área</p>
      </header>
      <div class="fase-cards">
        <article class="metric-card metric-card--rust">
          <strong class="metric-card__valor">{{ resumo?.em_rustificacao ?? 0 }}</strong>
          <span class="metric-card__label">Em rustificação</span>
          <span class="metric-card__meta">Adaptação ao sol (mín. 30 dias)</span>
          <ul v-if="resumo?.por_especie_rustificacao?.length" class="especies-mini">
            <li v-for="e in resumo.por_especie_rustificacao.slice(0, 4)" :key="'r-' + e.id_especie">
              <span>{{ e.especie }}</span><strong>{{ e.quantidade }}</strong>
            </li>
          </ul>
        </article>
        <article class="metric-card metric-card--venda">
          <strong class="metric-card__valor">{{ resumo?.prontas_venda_rustificacao ?? 0 }}</strong>
          <span class="metric-card__label">Aptas p/ venda</span>
          <span class="metric-card__meta">Após rustificação — estoque em <router-link to="/estoques">Estoques</router-link></span>
        </article>
        <article class="metric-card metric-card--idade">
          <strong class="metric-card__valor">{{ formatDias(resumo?.dias_medios_rustificacao) }}</strong>
          <span class="metric-card__label">Permanência em média (dias)</span>
          <span class="metric-card__meta">Mudas na rustificação (dias)</span>
        </article>
      </div>
    </section>

    <section class="fase fase--inline">
      <article class="metric-card">
        <strong class="metric-card__valor">{{ resumo?.prontas_venda ?? 0 }}</strong>
        <span class="metric-card__label">Total aptas p/ venda (estoque comercial)</span>
      </article>
      <article class="metric-card">
        <strong class="metric-card__valor">{{ resumo?.vendidas ?? 0 }}</strong>
        <span class="metric-card__label">Mudas vendidas (acumulado)</span>
      </article>
    </section>

    <section class="card-block">
      <header class="block-header">
        <h3 class="block-title">Últimas vendas (somente físico)</h3>
        <router-link to="/vendas" class="btn btn-outline btn-sm">Abrir vendas</router-link>
      </header>
      <table v-if="resumo?.vendas_recentes?.length" class="data-table">
        <thead>
          <tr>
            <th>Data</th>
            <th>Comprador</th>
            <th>Mudas</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in resumo.vendas_recentes" :key="v.id">
            <td>{{ formatarData(v.data_venda) }}</td>
            <td>{{ v.comprador_nome || '—' }}</td>
            <td>{{ v.total_itens }}</td>
            <td><span class="tag">{{ v.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-hint">Nenhuma venda registrada.</p>
      <p class="block-foot">Valores e receita ficam no módulo Financeiro.</p>
    </section>
  </div>
</template>

<script setup>
defineProps({
  resumo: { type: Object, default: null },
})

function formatarData(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR')
}

function formatDias(v) {
  if (v === null || v === undefined) return '—'
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return String(Math.round(n))
}
</script>

<style scoped>
.visao-panel { display: flex; flex-direction: column; gap: var(--spacing-xl); }
.fase-header { margin-bottom: var(--spacing-md); }
.fase-titulo { margin: 0; font-size: 1.125rem; font-weight: 700; }
.fase-desc { margin: 0.2rem 0 0; font-size: 0.9375rem; color: var(--color-text-secondary); }
.fase-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
  gap: var(--spacing-md);
}
.fase-cards--armazem { max-width: 36rem; }
.fase--inline { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.metric-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.metric-card--desenvolvimento { border-left: 5px solid var(--color-text-muted); }
.metric-card--idade { border-left: 5px solid var(--color-info, #5b8def); background: var(--color-surface-muted, #f4f6f8); }
.metric-card--acao { border-left: 5px solid var(--color-attention); background: var(--color-attention-bg); }
.metric-card--crescimento { border-left: 5px solid var(--color-primary); }
.metric-card--rust { border-left: 5px solid #c4a574; background: #faf6f0; }
.metric-card--venda { border-left: 5px solid var(--color-success); background: var(--color-success-bg); }
.metric-card--rustificacao { border-left: 5px solid #c4a574; background: #faf6f0; }
.metric-card__valor { font-size: 2.25rem; font-weight: 700; line-height: 1; color: var(--color-primary-700); }
.metric-card__label { font-size: 1rem; font-weight: 600; }
.metric-card__meta { font-size: 0.875rem; color: var(--color-text-secondary); }
.metric-card__meta a { color: var(--color-primary); font-weight: 600; }
.especies-mini { list-style: none; margin: 0.5rem 0 0; padding: 0.5rem 0 0; border-top: 1px solid var(--color-border-subtle); }
.especies-mini li { display: flex; justify-content: space-between; font-size: 0.875rem; padding: 0.2rem 0; }
.card-block { background: var(--color-surface); border: 1px solid var(--color-border-subtle); border-radius: var(--radius-lg); padding: var(--spacing-lg); }
.block-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-md); }
.block-title { margin: 0; font-size: 1rem; font-weight: 600; }
.block-foot { margin-top: var(--spacing-md); font-size: 0.8125rem; color: var(--color-text-muted); }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.9375rem; }
.data-table th, .data-table td { padding: 0.65rem 0.75rem; border-bottom: 1px solid var(--color-border-subtle); text-align: left; }
.data-table th { font-size: 0.8125rem; color: var(--color-text-secondary); font-weight: 600; }
.tag { font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: var(--radius-full); background: var(--color-surface-muted); font-weight: 600; }
.empty-hint { margin: 0; color: var(--color-text-muted); }

@media (max-width: 768px) {
  .fase-cards, .fase--inline { grid-template-columns: 1fr; }
}
</style>
