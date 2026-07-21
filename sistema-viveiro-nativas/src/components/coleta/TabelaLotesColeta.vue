<template>
  <div class="card">
    <header class="card-header">
      <h3 class="card-title">Teste de germinação</h3>
      <span class="card-count">{{ store.lotesFiltrados.length }} lote(s)</span>
    </header>

    <p class="card-hint">Registre o resultado quando o laboratório liberar.</p>

    <div class="tabela-container">
      <table class="tabela">
        <thead>
          <tr>
            <th>Código lote</th>
            <th>Espécie</th>
            <th>Matriz</th>
            <th>Lote (estoque)</th>
            <th>Reserva teste</th>
            <th>Germinação</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lote in lotesOrdenados" :key="lote.id">
            <td>
              <code class="codigo">{{ lote.codigo_lote }}</code>
            </td>
            <td>{{ nomeEspecie(lote) }}</td>
            <td>{{ lote.matriz_nome || '—' }}</td>
            <td>{{ lote.quantidade_disponivel ?? '—' }}</td>
            <td>{{ reservaTeste(lote) }}</td>
            <td>
              <span v-if="germinacaoLote(lote) != null" class="tag tag--ok">
                {{ germinacaoLote(lote) }}%
              </span>
              <span v-else class="tag tag--pendente">Pendente</span>
            </td>
            <td>{{ labelStatus(lote.status) }}</td>
            <td class="acoes">
              <button
                v-if="podeCriar"
                type="button"
                class="btn-teste"
                title="Registrar teste de germinação"
                @click="emit('registrar-teste', lote)"
              >
                {{ germinacaoLote(lote) != null ? 'Novo teste' : 'Teste germ.' }}
              </button>
              <span v-else class="acoes-muted">—</span>
            </td>
          </tr>
          <tr v-if="!store.carregando && store.lotesFiltrados.length === 0">
            <td colspan="8" class="vazio">
              Nenhum lote no filtro atual. Registre uma coleta com «Gerar lote».
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useColetaStore } from '@/store/coleta'
import { usePermissions } from '@/composables/usePermissions'
import { STATUS_LOTE } from '@/constants/coletaDominio'
import { germinacaoLote as taxaGermLote } from '@/utils/coletaKpi'
import { nomePopularExibicao } from '@/utils/especiesDisplay'

const emit = defineEmits(['registrar-teste'])
const store = useColetaStore()
const { can } = usePermissions()
const podeCriar = computed(() => can('coleta.create'))

const lotesOrdenados = computed(() =>
  [...store.lotesFiltrados].sort((a, b) =>
    (b.codigo_lote || '').localeCompare(a.codigo_lote || '')
  )
)

function labelStatus(v) {
  return STATUS_LOTE.find((s) => s.value === v)?.label || v || '—'
}

function nomeEspecie(lote) {
  if (lote.especie_nome) return nomePopularExibicao(lote.especie_nome)
  const m = store.arvoresMatriz.find((a) => a.id === lote.id_arvore_matriz)
  return nomePopularExibicao(m?.especie_nome) || '—'
}

function reservaTeste(lote) {
  const coleta = store.coletas.find((c) => c.id === lote.id_coleta_sementes)
  const n = coleta?.sementes_reservadas_teste
  if (n == null) return '—'
  return Number(n).toLocaleString('pt-BR')
}

function germinacaoLote(lote) {
  return taxaGermLote(lote, store.testes)
}
</script>

<style scoped>
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: var(--spacing-lg);
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.card-count {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.card-hint {
  margin: 0 0 var(--spacing-md);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  line-height: 1.45;
}

.tabela-container {
  overflow-x: auto;
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
}

.tabela {
  width: 100%;
  border-collapse: collapse;
}

.tabela th {
  background: var(--color-background);
  padding: var(--spacing-md);
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.tabela td {
  padding: var(--spacing-md);
  font-size: 0.875rem;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.codigo {
  font-family: var(--font-mono, monospace);
  font-size: 0.8125rem;
  background: var(--color-primary-subtle);
  padding: 0.15rem 0.4rem;
  border-radius: var(--radius-sm);
}

.tag {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
}

.tag--ok {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.tag--pendente {
  background: var(--color-attention-bg);
  color: var(--color-analog-2);
}

.acoes {
  white-space: nowrap;
}

.btn-teste {
  border: none;
  padding: 0.35rem 0.65rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-teste:hover {
  background: var(--color-primary-dark);
}

.vazio {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 2rem !important;
}
</style>
