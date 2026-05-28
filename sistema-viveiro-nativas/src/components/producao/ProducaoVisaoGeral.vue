<template>
  <div class="visao-panel">
    <div class="fases-pipeline">
      <section class="fase">
        <header class="fase-header">
          <span class="fase-step" aria-hidden="true">1</span>
          <div>
            <h2 class="fase-titulo">Armazém</h2>
            <p class="fase-desc">Estoque de Sementes</p>
          </div>
        </header>
        <div class="fase-cards fase-cards--compact">
          <article class="metric-card">
            <strong class="metric-card__valor">{{ resumo?.sementes_armazem ?? 0 }}</strong>
            <span class="metric-card__label">Sementes disponíveis</span>
            <span class="metric-card__meta">{{ resumo?.lotes_com_estoque ?? 0 }} lote(s)</span>
          </article>
          <article class="metric-card metric-card--idade">
            <strong class="metric-card__valor">{{ formatDias(resumo?.dias_medios_armazem) }}</strong>
            <span class="metric-card__label">Permanência em média (dias)</span>
          </article>
        </div>
      </section>

      <section class="fase">
        <header class="fase-header">
          <span class="fase-step" aria-hidden="true">2</span>
          <div>
            <h2 class="fase-titulo">Sementeira</h2>
            <p class="fase-desc">{{ resumo?.na_sementeira ?? 0 }} plântulas</p>
          </div>
        </header>
        <div class="fase-cards">
          <article class="metric-card metric-card--desenvolvimento">
            <strong class="metric-card__valor">{{ resumo?.em_desenvolvimento_sementeira ?? 0 }}</strong>
            <span class="metric-card__label">Em desenvolvimento</span>
            <ul v-if="resumo?.por_especie_desenvolvimento?.length" class="especies-mini">
              <li v-for="e in resumo.por_especie_desenvolvimento.slice(0, 4)" :key="'d-' + e.id_especie">
                <span>{{ e.especie }}</span>
                <strong>{{ e.quantidade }}</strong>
              </li>
            </ul>
          </article>
          <article class="metric-card metric-card--acao">
            <strong class="metric-card__valor">{{ resumo?.aptas_transferencia ?? 0 }}</strong>
            <span class="metric-card__label">Aptas p/ canteiro</span>
            <ul v-if="resumo?.por_especie_aptas_transferencia?.length" class="especies-mini">
              <li v-for="e in resumo.por_especie_aptas_transferencia.slice(0, 4)" :key="'t-' + e.id_especie">
                <span>{{ e.especie }}</span>
                <strong>{{ e.quantidade }}</strong>
              </li>
            </ul>
          </article>
          <article class="metric-card metric-card--idade">
            <strong class="metric-card__valor">{{ formatDias(resumo?.dias_medios_sementeira) }}</strong>
            <span class="metric-card__label">Permanência em média (dias)</span>
          </article>
        </div>
      </section>

      <section class="fase">
        <header class="fase-header">
          <span class="fase-step" aria-hidden="true">3</span>
          <div>
            <h2 class="fase-titulo">Canteiro</h2>
            <p class="fase-desc">{{ resumo?.nos_canteiros ?? 0 }} mudas</p>
          </div>
        </header>
        <div class="fase-cards">
          <article class="metric-card metric-card--crescimento">
            <strong class="metric-card__valor">{{ resumo?.em_crescimento_canteiro ?? 0 }}</strong>
            <span class="metric-card__label">Em crescimento</span>
            <ul v-if="resumo?.por_especie_em_crescimento?.length" class="especies-mini">
              <li v-for="e in resumo.por_especie_em_crescimento.slice(0, 4)" :key="'c-' + e.id_especie">
                <span>{{ e.especie }}</span>
                <strong>{{ e.quantidade }}</strong>
              </li>
            </ul>
          </article>
          <article class="metric-card metric-card--rustificacao">
            <strong class="metric-card__valor">{{ resumo?.aptas_rustificacao_canteiro ?? 0 }}</strong>
            <span class="metric-card__label">Aptas p/ rustificação</span>
            <ul v-if="resumo?.por_especie_aptas_rustificacao?.length" class="especies-mini">
              <li v-for="e in resumo.por_especie_aptas_rustificacao.slice(0, 4)" :key="'ar-' + e.id_especie">
                <span>{{ e.especie }}</span>
                <strong>{{ e.quantidade }}</strong>
              </li>
            </ul>
          </article>
          <article class="metric-card metric-card--idade">
            <strong class="metric-card__valor">{{ formatDias(resumo?.dias_medios_canteiro) }}</strong>
            <span class="metric-card__label">Permanência em média (dias)</span>
          </article>
        </div>
      </section>

      <section class="fase fase--last">
        <header class="fase-header">
          <span class="fase-step" aria-hidden="true">4</span>
          <div>
            <h2 class="fase-titulo">Área de rustificação</h2>
            <p class="fase-desc">{{ resumo?.na_rustificacao ?? 0 }} mudas na área</p>
          </div>
        </header>
        <div class="fase-cards fase-cards--compact">
          <article class="metric-card metric-card--rust">
            <strong class="metric-card__valor">{{ resumo?.em_rustificacao ?? 0 }}</strong>
            <span class="metric-card__label">Em rustificação</span>
            <span class="metric-card__meta">(mín. 30 dias)</span>
            <ul v-if="resumo?.por_especie_rustificacao?.length" class="especies-mini">
              <li v-for="e in resumo.por_especie_rustificacao.slice(0, 4)" :key="'r-' + e.id_especie">
                <span>{{ e.especie }}</span>
                <strong>{{ e.quantidade }}</strong>
              </li>
            </ul>
          </article>
          <article class="metric-card metric-card--idade">
            <strong class="metric-card__valor">{{ formatDias(resumo?.dias_medios_rustificacao) }}</strong>
            <span class="metric-card__label">Permanência em média (dias)</span>
          </article>
        </div>
        <p v-if="(resumo?.prontas_venda_rustificacao ?? 0) > 0" class="fase-nota">
          {{ resumo.prontas_venda_rustificacao }} muda(s) já liberada(s) para venda nesta área —
          veja o estoque em <router-link to="/estoques">Estoques</router-link>.
        </p>
      </section>
    </div>

    <section class="resumo-comercial" aria-labelledby="resumo-comercial-titulo">
      <header class="resumo-comercial__header">
        <div>
          <h2 id="resumo-comercial-titulo" class="resumo-comercial__titulo">Resultado comercial</h2>
          <p class="resumo-comercial__desc">Estoque apto e desempenho de vendas no período</p>
        </div>
        <nav class="resumo-comercial__nav" aria-label="Atalhos comerciais">
          <router-link to="/estoques" class="resumo-comercial__link">Estoques</router-link>
          <router-link to="/vendas" class="resumo-comercial__link">Vendas</router-link>
        </nav>
      </header>

      <div class="kpi-grid">
        <article class="kpi kpi--estoque">
          <span class="kpi__badge">Estoque</span>
          <strong class="kpi__valor">{{ resumo?.prontas_venda ?? 0 }}</strong>
          <span class="kpi__label">Mudas aptas à venda</span>
          <span class="kpi__hint">Disponíveis para pedido</span>
        </article>
        <article class="kpi kpi--mtd">
          <span class="kpi__badge">MTD</span>
          <strong class="kpi__valor">{{ resumo?.vendidas_mtd ?? 0 }}</strong>
          <span class="kpi__label">Mudas vendidas no mês</span>
          <span class="kpi__hint">{{ rotuloMesAtual }}</span>
        </article>
        <article class="kpi kpi--ytd">
          <span class="kpi__badge">YTD</span>
          <strong class="kpi__valor">{{ resumo?.vendidas_ytd ?? 0 }}</strong>
          <span class="kpi__label">Mudas vendidas no ano</span>
          <span class="kpi__hint">Acumulado em {{ anoAtual }}</span>
        </article>
      </div>

      <div class="vendas-recentes">
        <header class="vendas-recentes__header">
          <h3 class="vendas-recentes__titulo">Últimas vendas</h3>
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
        <p v-else class="empty-hint">Nenhuma venda registrada no período.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

defineProps({
  resumo: { type: Object, default: null },
})

const agora = new Date()
const anoAtual = agora.getFullYear()
const rotuloMesAtual = computed(() =>
  agora.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
)

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
.visao-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.visao-lead {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  max-width: 42rem;
}

/* Pipeline produtivo (fases 1–4) */
.fases-pipeline {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.fase {
  padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-md);
  border-bottom: 1px solid var(--color-border-subtle);
}

.fase--last {
  border-bottom: none;
}

.fase-header {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.fase-step {
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--color-primary-700);
  background: var(--color-primary-subtle);
  border-radius: var(--radius-full);
}

.fase-titulo {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.fase-desc {
  margin: 0.15rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.fase-nota {
  margin: var(--spacing-md) 0 0;
  padding: 0.65rem 0.85rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-success);
}

.fase-nota a {
  color: var(--color-primary);
  font-weight: 600;
}

.fase-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(11.5rem, 1fr));
  gap: var(--spacing-md);
}

.fase-cards--compact {
  max-width: 40rem;
}

.metric-card {
  background: var(--color-background);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.metric-card--desenvolvimento {
  border-left: 4px solid var(--color-text-muted);
}

.metric-card--idade {
  border-left: 4px solid var(--color-info, #47607b);
  background: var(--color-surface-muted);
}

.metric-card--acao {
  border-left: 4px solid var(--color-attention);
  background: var(--color-attention-bg);
}

.metric-card--crescimento {
  border-left: 4px solid var(--color-primary);
}

.metric-card--rust,
.metric-card--rustificacao {
  border-left: 4px solid #c4a574;
  background: #faf6f0;
}

.metric-card__valor {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.1;
  color: var(--color-primary-700);
}

.metric-card__label {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.metric-card__meta {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.especies-mini {
  list-style: none;
  margin: 0.35rem 0 0;
  padding: 0.35rem 0 0;
  border-top: 1px solid var(--color-border-subtle);
}

.especies-mini li {
  display: flex;
  justify-content: space-between;
  font-size: 0.8125rem;
  padding: 0.15rem 0;
}

/* Bloco comercial */
.resumo-comercial {
  background: linear-gradient(
    165deg,
    var(--color-primary-50) 0%,
    var(--color-surface) 45%,
    var(--color-surface) 100%
  );
  border: 2px solid var(--color-primary-100);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg) var(--spacing-xl);
  box-shadow: var(--shadow-md, 0 4px 14px rgba(44, 45, 42, 0.08));
}

.resumo-comercial__header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-primary-100);
}

.resumo-comercial__titulo {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-primary-900);
  letter-spacing: -0.02em;
}

.resumo-comercial__desc {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.resumo-comercial__nav {
  display: flex;
  gap: var(--spacing-sm);
}

.resumo-comercial__link {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-md);
  color: var(--color-primary-700);
  background: var(--color-surface);
  border: 1px solid var(--color-primary-100);
  text-decoration: none;
  transition: background 0.15s ease;
}

.resumo-comercial__link:hover {
  background: var(--color-primary-subtle);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.kpi {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  min-height: 7.5rem;
}

.kpi__badge {
  align-self: flex-start;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm, 4px);
}

.kpi__valor {
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1;
  margin-top: 0.15rem;
}

.kpi__label {
  font-size: 0.9375rem;
  font-weight: 600;
}

.kpi__hint {
  font-size: 0.8125rem;
  opacity: 0.85;
  margin-top: auto;
}

.kpi--estoque {
  background: var(--color-surface);
  border: 1px dashed var(--color-primary-200);
  color: var(--color-text-primary);
}

.kpi--estoque .kpi__badge {
  background: var(--color-primary-subtle);
  color: var(--color-primary-700);
}

.kpi--estoque .kpi__valor {
  color: var(--color-primary-700);
}

.kpi--mtd {
  background: var(--color-primary-500);
  color: var(--color-text-inverse);
  box-shadow: 0 2px 8px rgba(89, 98, 71, 0.35);
}

.kpi--mtd .kpi__badge {
  background: rgba(255, 255, 255, 0.2);
  color: var(--color-text-inverse);
}

.kpi--mtd .kpi__valor {
  color: var(--color-text-inverse);
}

.kpi--ytd {
  background: var(--color-complement-dark, #624e47);
  color: var(--color-text-inverse);
}

.kpi--ytd .kpi__badge {
  background: rgba(255, 255, 255, 0.15);
  color: var(--color-text-inverse);
}

.kpi--ytd .kpi__valor {
  color: var(--color-text-inverse);
}

.vendas-recentes {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-primary-100);
}

.vendas-recentes__titulo {
  margin: 0 0 var(--spacing-md);
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9375rem;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.data-table th,
.data-table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid var(--color-border-subtle);
  text-align: left;
}

.data-table th {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  font-weight: 600;
  background: var(--color-surface-muted);
}

.tag {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-full);
  background: var(--color-surface-muted);
  font-weight: 600;
}

.empty-hint {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

@media (max-width: 900px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .kpi__valor {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .fase-cards {
    grid-template-columns: 1fr;
  }

  .resumo-comercial {
    padding: var(--spacing-md);
  }
}
</style>
