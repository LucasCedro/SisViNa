<template>
  <div class="card">
    <header class="card-header">
      <h3 class="card-title">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 7V3m8 4V3m-9 8h10m2 10H5a2 2 0 01-2-2V7a2 2 0 012-2h14a2 2 0 012 2v12a2 2 0 01-2 2z"
          />
        </svg>
        Histórico de coletas
      </h3>
      <span class="card-count">{{ store.coletasFiltradas.length }} registro(s)</span>
    </header>

    <div class="tabela-container">
      <table class="tabela">
        <thead>
          <tr>
            <th>Data</th>
            <th>Matriz</th>
            <th>Espécie</th>
            <th>Sementes</th>
            <th>Lotes</th>
            <th>Funcionário</th>
            <th>Observações</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="coleta in store.coletasFiltradas" :key="coleta.id">
            <td>{{ formatarData(coleta.data_coleta) }}</td>
            <td>{{ coleta.matriz_nome || '—' }}</td>
            <td>{{ coleta.especie_nome || '—' }}</td>
            <td>{{ coleta.quantidade_sementes ?? 0 }}</td>
            <td>{{ coleta.lotes?.length ?? 0 }}</td>
            <td>{{ coleta.funcionario_nome || '—' }}</td>
            <td class="obs-cell">{{ coleta.observacoes || '—' }}</td>
            <td class="acoes">
              <button type="button" class="btn-editar" title="Editar coleta" @click="emit('editar-coleta', coleta)">
                Editar
              </button>
              <button type="button" class="btn-excluir" title="Excluir coleta" @click="excluir(coleta)">×</button>
            </td>
          </tr>
          <tr v-if="!store.carregando && store.coletasFiltradas.length === 0">
            <td colspan="8" class="vazio">
              <template v-if="store.temFiltroAtivo">
                Nenhuma coleta com os filtros atuais.
              </template>
              <template v-else>
                Nenhuma coleta registrada. Use «Cadastrar coleta».
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { useColetaStore } from '@/store/coleta'

const emit = defineEmits(['editar-coleta'])
const store = useColetaStore()

function formatarData(data) {
  if (!data) return '—'
  return new Date(data + (String(data).includes('T') ? '' : 'T12:00:00')).toLocaleDateString('pt-BR')
}

async function excluir(coleta) {
  if (!confirm(`Excluir coleta de ${formatarData(coleta.data_coleta)}? Lotes vinculados serão removidos.`)) return
  try {
    await store.removerColeta(coleta.id)
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir coleta')
  }
}
</script>

<style scoped>
.card {
  background-color: var(--color-surface);
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
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: var(--spacing-sm);
}

.card-count {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
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
  background-color: var(--color-background);
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
  vertical-align: top;
}

.obs-cell {
  max-width: 22rem;
  color: var(--color-text-secondary);
}

.acoes {
  display: flex;
  gap: 0.35rem;
  align-items: center;
}

.btn-editar {
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-success-bg);
  color: var(--color-success);
}

.btn-excluir {
  border: none;
  background: var(--color-error-bg);
  color: var(--color-error);
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.125rem;
  line-height: 1;
}

.vazio {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 2rem !important;
}
</style>
