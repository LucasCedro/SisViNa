<template>
  <div class="contab-bp module-sec">
    <p v-if="carregando && !dados" class="status-msg">Carregando balanço…</p>
    <p v-else-if="erro" class="alert-erro">{{ erro }}</p>
    <template v-else-if="dados">
      <p class="contab-lead">
        Balanço patrimonial — referência <strong>{{ fmtData(dados.data_referencia) }}</strong>
        ({{ dados.periodo?.label }}). Estrutura Lei 6.404 / CPC; posição patrimonial na data.
      </p>

      <div class="bp-consolidado">
        <section class="bp-coluna">
          <header class="bp-coluna-titulo">Ativo</header>

          <div v-for="bloco in blocosAtivo" :key="bloco.id" class="bp-grupo">
            <h4 class="bp-grupo-titulo">{{ bloco.titulo }}</h4>
            <dl class="bp-dl">
              <div
                v-for="linha in bloco.linhas"
                :key="linha.id"
                :class="classesLinha(linha)"
              >
                <dt>
                  <button
                    v-if="linha.clicavel"
                    type="button"
                    class="bp-linha-btn"
                    @click="abrir(linha)"
                  >
                    {{ linha.label }}
                    <span class="bp-linha-hint">ver cálculo</span>
                  </button>
                  <template v-else>
                    <span>{{ linha.label }}</span>
                    <span v-if="linha.naoEscriturado" class="bp-tag">não escriturado</span>
                  </template>
                </dt>
                <dd>{{ fmtValor(linha) }}</dd>
              </div>
            </dl>
          </div>

          <div class="bp-total-geral">
            <span>Total do ativo</span>
            <button type="button" class="bp-total-btn" @click="abrir(linhaAtivoTotal)">
              R$ {{ fmt(dados.ativo?.total) }}
              <span class="bp-linha-hint">ver cálculo</span>
            </button>
          </div>
        </section>

        <section class="bp-coluna">
          <header class="bp-coluna-titulo">Passivo e patrimônio líquido</header>

          <div v-for="bloco in blocosPassivoPl" :key="bloco.id" class="bp-grupo">
            <h4 class="bp-grupo-titulo">{{ bloco.titulo }}</h4>
            <dl class="bp-dl">
              <div
                v-for="linha in bloco.linhas"
                :key="linha.id"
                :class="classesLinha(linha)"
              >
                <dt>
                  <button
                    v-if="linha.clicavel"
                    type="button"
                    class="bp-linha-btn"
                    @click="abrir(linha)"
                  >
                    {{ linha.label }}
                    <span class="bp-linha-hint">ver cálculo</span>
                  </button>
                  <template v-else>
                    <span>{{ linha.label }}</span>
                    <span v-if="linha.naoEscriturado" class="bp-tag">não escriturado</span>
                  </template>
                </dt>
                <dd>{{ fmtValor(linha) }}</dd>
              </div>
            </dl>
          </div>

          <div class="bp-total-geral">
            <span>Total passivo + PL</span>
            <strong>R$ {{ fmt(dados.passivo_mais_pl ?? dados.patrimonio_liquido) }}</strong>
          </div>
        </section>
      </div>

      <p
        v-if="equacaoOk"
        class="bp-equacao bp-equacao--ok"
      >
        Ativo (R$ {{ fmt(dados.ativo?.total) }}) = Passivo + PL (R$ {{ fmt(dados.passivo_mais_pl) }})
      </p>

      <aside v-if="dados.observacoes?.length" class="module-banner module-banner--info">
        <strong>Notas do balanço</strong>
        <ul>
          <li v-for="(o, i) in dados.observacoes" :key="i">{{ o }}</li>
        </ul>
      </aside>

      <ContabilidadeDetalheModal
        :aberto="!!modal"
        :titulo="modal?.label || ''"
        :valor="modal?.valor"
        :tipo="modal?.tipo || 'resultado'"
        :bloco="modal?.bloco"
        :estoque="modal?.estoque"
        :estoque-foco="modal?.estoqueFoco"
        @fechar="modal = null"
      />
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import ContabilidadeDetalheModal from './ContabilidadeDetalheModal.vue'

const props = defineProps({
  dados: { type: Object, default: null },
  carregando: { type: Boolean, default: false },
  erro: { type: String, default: null },
})

const modal = ref(null)

const det = computed(() => props.dados?.detalhes)

const equacaoOk = computed(() => {
  const ativo = Number(props.dados?.ativo?.total || 0)
  const passivoPl = Number(props.dados?.passivo_mais_pl || 0)
  return Math.abs(ativo - passivoPl) < 0.01
})

function linha(id, label, valor, opts = {}) {
  return {
    id,
    label,
    valor: Number(valor || 0),
    indent: opts.indent || 0,
    total: !!opts.total,
    subtotal: !!opts.subtotal,
    clicavel: !!opts.clicavel,
    naoEscriturado: !!opts.naoEscriturado,
    tipo: opts.tipo || 'resultado',
    bloco: opts.bloco ?? null,
    estoque: opts.estoque ?? null,
    estoqueFoco: opts.estoqueFoco ?? null,
  }
}

const blocosAtivo = computed(() => {
  const c = props.dados?.ativo?.circulante
  const nc = props.dados?.ativo?.nao_circulante
  const d = det.value
  if (!c) return []

  return [
    {
      id: 'circulante',
      titulo: 'Ativo circulante',
      linhas: [
        linha('caixa', 'Caixa e equivalentes de caixa', c.caixa_equivalentes, {
          clicavel: true,
          bloco: d?.caixa_equivalentes,
        }),
        linha('cr', 'Contas a receber de clientes', c.contas_receber, {
          clicavel: true,
          tipo: 'a_receber',
          bloco: d?.contas_receber,
        }),
        linha('est_total', 'Estoques', c.estoques?.total, {
          subtotal: true,
          clicavel: true,
          bloco: d?.estoques,
        }),
        linha('est_mudas', 'Mudas', c.estoques?.mudas, {
          indent: 1,
          clicavel: true,
          bloco: d?.estoque_mudas,
        }),
        linha('est_insumos', 'Insumos', c.estoques?.insumos, {
          indent: 1,
          clicavel: true,
          tipo: 'estoque',
          estoque: d?.estoque_insumos
            ? { insumos: d.estoque_insumos, insumos_itens: d.estoque_insumos.itens }
            : null,
          estoqueFoco: 'insumos',
        }),
        linha('est_sementes', 'Sementes', c.estoques?.sementes, {
          indent: 1,
          clicavel: true,
          tipo: 'estoque',
          estoque: d?.estoque_sementes
            ? { sementes: d.estoque_sementes, sementes_itens: d.estoque_sementes.itens }
            : null,
          estoqueFoco: 'sementes',
        }),
        linha('desp_ant', 'Despesas antecipadas', c.despesas_antecipadas, { naoEscriturado: true }),
        linha('tot_circ', 'Total do ativo circulante', c.total, {
          total: true,
          clicavel: true,
          bloco: d?.ativo_circulante,
        }),
      ],
    },
    {
      id: 'nao_circulante',
      titulo: 'Ativo não circulante',
      linhas: [
        linha('rlz_lp', 'Realizável a longo prazo', nc?.realizavel_longo_prazo, { naoEscriturado: true }),
        linha('invest', 'Investimentos', nc?.investimentos, { naoEscriturado: true }),
        linha('imob', 'Imobilizado', nc?.imobilizado, {
          clicavel: Number(nc?.imobilizado) > 0,
          bloco: d?.imobilizado,
        }),
        linha('intang', 'Intangível', nc?.intangivel, { naoEscriturado: true }),
        linha('tot_nc', 'Total do ativo não circulante', nc?.total, { total: true }),
      ],
    },
  ]
})

const blocosPassivoPl = computed(() => {
  const pc = props.dados?.passivo?.circulante
  const pnc = props.dados?.passivo?.nao_circulante
  const pl = props.dados?.patrimonio_liquido_grupo
  const d = det.value
  if (!pc) return []

  const blocos = [
    {
      id: 'pass_circ',
      titulo: 'Passivo circulante',
      linhas: [
        linha('forn', 'Fornecedores', pc.fornecedores, {
          clicavel: true,
          tipo: 'compras_insumos',
          bloco: d?.fornecedores,
        }),
        linha('emp', 'Empréstimos e financiamentos', pc.emprestimos_financiamentos, { naoEscriturado: true }),
        linha('fisc', 'Obrigações fiscais', pc.obrigacoes_fiscais, { naoEscriturado: true }),
        linha('outras', 'Outras obrigações', pc.outras_obrigacoes, { naoEscriturado: true }),
        linha('tot_pc', 'Total do passivo circulante', pc.total, { total: true }),
      ],
    },
    {
      id: 'pass_nc',
      titulo: 'Passivo não circulante',
      linhas: [
        linha('emp_lp', 'Empréstimos', pnc?.emprestimos, { naoEscriturado: true }),
        linha('outras_lp', 'Outras obrigações', pnc?.outras_obrigacoes, { naoEscriturado: true }),
        linha('tot_pnc', 'Total do passivo não circulante', pnc?.total, { total: true }),
      ],
    },
    {
      id: 'pl',
      titulo: 'Patrimônio líquido',
      linhas: [
        linha('capital', 'Capital social', pl?.capital_social, { naoEscriturado: true }),
        linha('reservas', 'Reservas de lucros', pl?.reservas, { naoEscriturado: true }),
        linha('acum', 'Lucros/prejuízos acumulados', pl?.lucros_acumulados, {
          clicavel: true,
          bloco: d?.lucros_acumulados,
        }),
        linha('resultado', 'Resultado do exercício', pl?.resultado_exercicio, {
          clicavel: true,
          bloco: d?.resultado_exercicio,
        }),
        linha('tot_pl', 'Total do patrimônio líquido', pl?.total ?? props.dados?.patrimonio_liquido, {
          total: true,
          clicavel: true,
          bloco: d?.patrimonio_liquido,
        }),
      ],
    },
  ]

  return blocos
})

const linhaAtivoTotal = computed(() =>
  linha('ativo_total', 'Total do ativo', props.dados?.ativo?.total, {
    clicavel: true,
    bloco: det.value?.ativo_total,
  }),
)

function classesLinha(linha) {
  return {
    'bp-dl--indent': linha.indent > 0,
    'bp-dl--subtotal': linha.subtotal,
    'bp-dl--total': linha.total,
    'bp-dl--destaque': linha.id === 'cr' || linha.id === 'forn',
    'bp-dl--zerado': linha.naoEscriturado && !linha.valor,
  }
}

function abrir(linha) {
  modal.value = linha
}

function fmt(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function fmtValor(linha) {
  if (linha.naoEscriturado && !linha.valor) return '—'
  return `R$ ${fmt(linha.valor)}`
}

function fmtData(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR')
}
</script>

<style scoped>
@import '@/components/financeiro/financeiro-shared.css';

.contab-lead {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin: 0 0 var(--spacing-md);
}

.bp-consolidado {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  align-items: start;
}

@media (max-width: 768px) {
  .bp-consolidado {
    grid-template-columns: 1fr;
  }
}

.bp-coluna {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}

.bp-coluna-titulo {
  margin: 0 0 var(--spacing-sm);
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-primary);
  border-bottom: 2px solid var(--color-primary);
  padding-bottom: 0.35rem;
}

.bp-grupo + .bp-grupo {
  margin-top: var(--spacing-md);
}

.bp-grupo-titulo {
  margin: 0 0 0.25rem;
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text-muted);
}

.bp-dl {
  margin: 0;
}

.bp-dl > div {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.3rem 0;
  border-bottom: 1px solid var(--color-border-subtle);
  font-size: 0.875rem;
}

.bp-dl--indent dt {
  padding-left: 1rem;
  font-size: 0.8125rem;
}

.bp-dl dt {
  color: var(--color-text-muted);
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem;
}

.bp-dl dd {
  margin: 0;
  font-weight: 600;
  white-space: nowrap;
}

.bp-tag {
  font-size: 0.625rem;
  color: var(--color-text-muted);
  font-style: italic;
}

.bp-linha-btn,
.bp-total-btn {
  border: none;
  background: none;
  padding: 0;
  font: inherit;
  color: inherit;
  text-align: left;
  cursor: pointer;
  display: inline-flex;
  flex-direction: column;
  gap: 0.1rem;
}

.bp-total-btn {
  font-weight: 700;
  color: var(--color-text-primary);
}

.bp-linha-btn:hover .bp-linha-hint,
.bp-total-btn:hover .bp-linha-hint {
  color: var(--color-primary);
}

.bp-linha-hint {
  font-size: 0.625rem;
  color: var(--color-text-muted);
  font-weight: 400;
}

.bp-dl--subtotal {
  font-weight: 600;
}

.bp-dl--total {
  font-weight: 700;
  border-bottom: none;
  padding-top: 0.4rem;
  margin-top: 0.15rem;
  border-top: 1px solid var(--color-border-subtle);
}

.bp-dl--destaque dd {
  color: var(--color-attention);
}

.bp-dl--zerado dd {
  color: var(--color-text-muted);
  font-weight: 400;
}

.bp-total-geral {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-sm);
  border-top: 2px solid var(--color-primary);
  font-weight: 700;
  font-size: 0.9375rem;
}

.bp-equacao {
  margin: var(--spacing-sm) 0 0;
  font-size: 0.8125rem;
  text-align: center;
}

.bp-equacao--ok {
  color: var(--color-success, var(--color-text-muted));
}

.module-banner ul {
  margin: 0.35rem 0 0;
  padding-left: 1.1rem;
  font-size: 0.8125rem;
}
</style>
