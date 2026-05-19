<template>
  <div class="card">
    <h3 class="card-title">
      <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
      Dados de Coleta
    </h3>
    <div class="tabela-container">
      <table class="tabela">
        <thead>
          <tr>
            <th>Espécie</th>
            <th>Nome da Árvore</th>
            <th>Sementes Coletadas</th>
            <th>Taxa de Germinação</th>
            <th>Tempo de Armazenamento</th>
            <th>Data da Coleta</th>
            <th>Observações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="arvore in store.arvoresMatriz" :key="arvore.id">
            <td>{{ arvore.especie }}</td>
            <td>{{ arvore.nome }}</td>
            <td>{{ arvore.sementes_coletadas }}</td>
            <td>{{ arvore.taxa_germinacao }}%</td>
            <td>{{ calcularTempoArmazenamento(arvore.data_coleta) }}</td>
            <td>{{ formatarData(arvore.data_coleta) }}</td>
            <td>{{ arvore.observacoes || '-' }}</td>
          </tr>
          <tr v-if="store.arvoresMatriz.length === 0">
            <td colspan="7" class="text-center py-4 text-gray-500">
              Nenhum dado de coleta disponível
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { useColetaStore } from '../../store/coleta'

const store = useColetaStore()

const formatarData = (data) => {
  if (!data) return '-'
  return new Date(data).toLocaleDateString('pt-BR')
}

const calcularTempoArmazenamento = (dataColeta) => {
  if (!dataColeta) return '-'

  const hoje = new Date()
  const coleta = new Date(dataColeta)
  const diff = Math.floor((hoje - coleta) / (1000 * 60 * 60 * 24))

  if (diff < 30) return `${diff} dias`
  if (diff < 365) return `${Math.floor(diff / 30)} meses`
  return `${Math.floor(diff / 365)} anos`
}
</script>

<style>
.card {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: var(--spacing-lg);
  width: 100%;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: var(--spacing-sm);
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
}

.tabela td {
  padding: var(--spacing-md);
  font-size: 0.875rem;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
}

.tabela tbody tr:last-child td {
  border-bottom: none;
}

.tabela tbody tr:hover {
  background-color: var(--color-background);
}

@media (max-width: 768px) {

  .tabela th,
  .tabela td {
    padding: var(--spacing-sm);
    font-size: 0.75rem;
  }
}
</style>