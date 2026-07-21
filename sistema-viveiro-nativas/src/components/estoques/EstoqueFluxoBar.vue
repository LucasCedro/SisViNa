<template>
  <div class="fluxo-estoque" role="navigation" aria-label="Resumo do estoque">
    <header class="fluxo-estoque__header">
      <h2 class="fluxo-estoque__titulo">Pipeline de estoque</h2>
      <p class="fluxo-estoque__sub">
        Ocupação vs capacidade do
        <router-link to="/viveiro">mapa do viveiro</router-link>
      </p>
    </header>

    <div class="fluxo-estoque__track">
      <button
        v-for="(col, idx) in colunas"
        :key="col.id"
        type="button"
        class="fluxo-col"
        :class="[
          `fluxo-col--${col.tom}`,
          {
            'fluxo-col--ativo': guiaAtiva === col.guia,
            'fluxo-col--alerta': col.ocupacao?.alerta,
            'fluxo-col--cheio': col.ocupacao?.cheio,
          },
        ]"
        :aria-label="col.ariaLabel"
        @click="$emit('ir-guia', col.guia)"
      >
        <div class="fluxo-col__top">
          <span class="fluxo-col__step">{{ col.step }}</span>
          <span
            v-if="col.ocupacao?.pct != null"
            class="fluxo-col__pct"
            :class="{
              'fluxo-col__pct--alerta': col.ocupacao.alerta,
              'fluxo-col__pct--cheio': col.ocupacao.cheio,
            }"
          >
            {{ col.ocupacao.pct }}%
          </span>
        </div>

        <span class="fluxo-col__titulo">{{ col.titulo }}</span>

        <div v-if="col.ocupacao?.capacidade" class="fluxo-col__ocupacao">
          <div class="fluxo-col__numeros" aria-hidden="true">
            <span class="fluxo-col__atual">{{ fmtNum(col.ocupacao.atual) }}</span>
            <span class="fluxo-col__sep">/</span>
            <span class="fluxo-col__cap">{{ fmtNum(col.ocupacao.capacidade) }}</span>
          </div>
          <div
            class="fluxo-col__bar"
            role="progressbar"
            :aria-valuenow="col.ocupacao.atual"
            :aria-valuemin="0"
            :aria-valuemax="col.ocupacao.capacidade"
            :aria-label="`Ocupação ${col.ocupacao.pct}%`"
          >
            <div
              class="fluxo-col__bar-fill"
              :style="{ width: `${col.ocupacao.pctBar}%` }"
            />
          </div>
        </div>

        <div v-else class="fluxo-col__valor-solo-wrap">
          <strong class="fluxo-col__valor-solo">{{ col.valorDisplay }}</strong>
          <span v-if="col.unidade" class="fluxo-col__unidade">{{ col.unidade }}</span>
        </div>

        <span class="fluxo-col__hint">{{ col.hint }}</span>

        <span v-if="idx < colunas.length - 1" class="fluxo-col__seta" aria-hidden="true">→</span>
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

function fmtNum(v) {
  return Number(v ?? 0).toLocaleString('pt-BR')
}

function fmtMoeda(v) {
  return Number(v || 0).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  })
}

function ocupacao(atual, capacidade) {
  const n = Number(atual ?? 0)
  const cap = Number(capacidade ?? 0)
  if (cap <= 0) return null
  const pct = Math.round((n / cap) * 100)
  return {
    atual: n,
    capacidade: cap,
    pct,
    pctBar: Math.min(100, pct),
    alerta: pct >= 85 && pct < 100,
    cheio: pct >= 100,
  }
}

function ariaOcupacao(titulo, occ) {
  if (!occ) return titulo
  return `${titulo}: ${fmtNum(occ.atual)} de ${fmtNum(occ.capacidade)} (${occ.pct}% da capacidade)`
}

const colunas = computed(() => {
  const p = props.resumo?.mudas_pipeline || {}
  const cap = props.resumo?.capacidades_viveiro || {}

  const sementesOcc = ocupacao(props.resumo?.total_sementes_disponiveis, cap.armazem)
  const devOcc = ocupacao(p.em_desenvolvimento_total, cap.desenvolvimento)
  const rustOcc = ocupacao(p.em_rustificacao, cap.rustificacao)
  const vendaOcc = ocupacao(props.resumo?.total_mudas_aptas_venda, cap.rustificacao)

  return [
    {
      id: 'sementes',
      guia: 'sementes',
      step: '1',
      tom: 'sementes',
      titulo: 'Sementes',
      ocupacao: sementesOcc,
      valorDisplay: fmtNum(props.resumo?.total_sementes_disponiveis),
      hint: `${fmtMoeda(props.resumo?.valor_total_sementes)} · ${props.resumo?.total_lotes_sementes_ativos ?? 0} lote(s)`,
      ariaLabel: ariaOcupacao('Sementes no armazém', sementesOcc),
    },
    {
      id: 'dev',
      guia: 'mudas',
      step: '2',
      tom: 'dev',
      titulo: 'Em desenvolvimento',
      ocupacao: devOcc,
      valorDisplay: fmtNum(p.em_desenvolvimento_total),
      hint: `${p.em_desenvolvimento_sementeira ?? 0} na sementeira · ${p.em_desenvolvimento_canteiro ?? 0} no canteiro`,
      ariaLabel: ariaOcupacao('Mudas em desenvolvimento', devOcc),
    },
    {
      id: 'rust',
      guia: 'mudas',
      step: '3',
      tom: 'rust',
      titulo: 'Rustificação',
      ocupacao: rustOcc,
      valorDisplay: fmtNum(p.em_rustificacao),
      hint: `${p.aptas_venda_aguardando_tempo ?? 0} abaixo do prazo recomendado`,
      ariaLabel: ariaOcupacao('Mudas em rustificação', rustOcc),
    },
    {
      id: 'venda',
      guia: 'mudas',
      step: '4',
      tom: 'venda',
      titulo: 'Prontas p/ venda',
      ocupacao: vendaOcc,
      valorDisplay: fmtNum(props.resumo?.total_mudas_aptas_venda),
      hint: `Prazo recomendado: ${p.dias_minimos_rustificacao ?? 30} dias na área`,
      ariaLabel: ariaOcupacao('Mudas prontas para venda', vendaOcc),
    },
    {
      id: 'insumos',
      guia: 'insumos',
      step: '₿',
      tom: 'insumos',
      titulo: 'Insumos',
      ocupacao: null,
      valorDisplay: fmtMoeda(props.resumo?.valor_total_insumos),
      unidade: 'valor em estoque',
      hint: `${props.resumo?.total_insumos ?? 0} item(ns) cadastrado(s)`,
      ariaLabel: `Insumos: ${fmtMoeda(props.resumo?.valor_total_insumos)} em estoque`,
    },
  ]
})
</script>

<style scoped>
.fluxo-estoque {
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, var(--color-surface) 55%);
  border: 1px solid var(--color-primary-100);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.fluxo-estoque__header {
  margin-bottom: var(--spacing-md);
}

.fluxo-estoque__titulo {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: 0.01em;
}

.fluxo-estoque__sub {
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.fluxo-estoque__sub a {
  color: var(--color-primary-700);
  font-weight: 600;
  text-decoration: none;
}

.fluxo-estoque__sub a:hover {
  text-decoration: underline;
}

.fluxo-estoque__track {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.35rem;
  scroll-snap-type: x proximity;
}

.fluxo-col {
  position: relative;
  flex: 1 1 0;
  min-width: 10.5rem;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.35rem;
  padding: 0.85rem 1rem 0.8rem;
  border: 1px solid var(--color-border-subtle);
  border-bottom: 3px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: background 0.2s ease, border-color 0.2s ease;
  scroll-snap-align: start;
  box-shadow: var(--shadow-sm);
}

.fluxo-col:hover {
  border-color: var(--color-primary-100);
  border-bottom-color: var(--color-primary-200);
  background: var(--color-surface);
}

.fluxo-col--ativo {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary-100);
  border-bottom-color: var(--color-primary);
}

.fluxo-col--ativo:hover {
  background: var(--color-primary-subtle);
  border-bottom-color: var(--color-primary);
}

.fluxo-col--sementes {
  border-top: 3px solid var(--color-complement-dark);
}

.fluxo-col--dev {
  border-top: 3px solid var(--color-primary);
}

.fluxo-col--rust {
  border-top: 3px solid var(--color-primary-200);
}

.fluxo-col--venda {
  border-top: 3px solid var(--color-success);
}

.fluxo-col--insumos {
  border-top: 3px solid var(--color-info);
}

.fluxo-col--alerta.fluxo-col--ativo {
  border-bottom-color: var(--color-attention);
}

.fluxo-col--cheio.fluxo-col--ativo {
  border-bottom-color: var(--color-danger);
}

.fluxo-col--ativo .fluxo-col__titulo {
  color: var(--color-primary-700);
}

.fluxo-col__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.35rem;
}

.fluxo-col__step {
  font-size: 0.625rem;
  font-weight: 800;
  color: var(--color-primary-700);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.12rem 0.45rem;
  border-radius: var(--radius-full);
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary-100);
}

.fluxo-col--ativo .fluxo-col__step {
  border-color: var(--color-primary-200);
}

.fluxo-col__pct {
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--color-primary-700);
  font-variant-numeric: tabular-nums;
  padding: 0.1rem 0.4rem;
  border-radius: var(--radius-full);
  background: var(--color-primary-subtle);
}

.fluxo-col__pct--alerta {
  color: var(--color-attention);
  background: var(--color-attention-bg);
}

.fluxo-col__pct--cheio {
  color: var(--color-danger);
  background: var(--color-danger-bg);
}

.fluxo-col__titulo {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  line-height: 1.25;
}

.fluxo-col__ocupacao {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-top: 0.1rem;
}

.fluxo-col__numeros {
  display: flex;
  align-items: baseline;
  gap: 0.15rem;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.fluxo-col__atual {
  font-size: 1.625rem;
  font-weight: 800;
  color: var(--color-primary-700);
  letter-spacing: -0.02em;
}

.fluxo-col__sep {
  font-size: 1rem;
  font-weight: 500;
  color: var(--color-text-muted);
  margin: 0 0.05rem;
}

.fluxo-col__cap {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.fluxo-col__bar {
  height: 0.35rem;
  border-radius: var(--radius-full);
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary-100);
  overflow: hidden;
}

.fluxo-col__bar-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--color-primary-200), var(--color-primary));
  transition: width 0.45s ease;
}

.fluxo-col--alerta .fluxo-col__bar-fill {
  background: linear-gradient(90deg, var(--color-attention), #a67c00);
}

.fluxo-col--cheio .fluxo-col__bar-fill {
  background: linear-gradient(90deg, var(--color-danger), #6b2a20);
}

.fluxo-col__valor-solo-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  margin-top: 0.15rem;
}

.fluxo-col__valor-solo {
  font-size: 1.375rem;
  font-weight: 800;
  color: var(--color-primary-700);
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.fluxo-col__unidade {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
}

.fluxo-col__hint {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  line-height: 1.35;
  margin-top: auto;
  padding-top: 0.15rem;
}

.fluxo-col__seta {
  display: none;
}

.fluxo-estoque__nota {
  margin: var(--spacing-md) 0 0;
  padding-top: var(--spacing-md);
  border-top: 1px dashed var(--color-border-subtle);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.fluxo-estoque__nota a {
  color: var(--color-primary-700);
  font-weight: 600;
}

@media (min-width: 900px) {
  .fluxo-col__seta {
    display: block;
    position: absolute;
    right: -0.65rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.875rem;
    color: var(--color-text-muted);
    z-index: 1;
    pointer-events: none;
  }

  .fluxo-col:last-child .fluxo-col__seta {
    display: none;
  }
}

@media (max-width: 640px) {
  .fluxo-col {
    min-width: 9rem;
    padding: 0.75rem 0.85rem;
  }

  .fluxo-col__atual {
    font-size: 1.375rem;
  }
}
</style>
