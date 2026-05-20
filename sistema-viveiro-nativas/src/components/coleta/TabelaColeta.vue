<template>
  <div class="card">
    <h3 class="card-title">
      <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
      Árvores matrizes
    </h3>
    <div class="tabela-container">
      <table class="tabela">
        <thead>
          <tr>
            <th>Espécie</th>
            <th>Nome</th>
            <th>Cidade / UF</th>
            <th>Coordenadas</th>
            <th>Sementes</th>
            <th>Germinação</th>
            <th>Última coleta</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="arvore in store.matrizesFiltradas"
            :key="arvore.id"
            class="linha-clicavel"
            :class="{ selecionada: store.matrizSelecionada?.id === arvore.id }"
            @click="store.selecionar(arvore)"
          >
            <td>{{ arvore.especie_nome || '—' }}</td>
            <td>{{ arvore.nome }}</td>
            <td>{{ local(arvore) }}</td>
            <td class="coord">{{ arvore.latitude }}, {{ arvore.longitude }}</td>
            <td>{{ arvore.sementes_coletadas ?? 0 }}</td>
            <td>{{ arvore.taxa_germinacao != null ? `${arvore.taxa_germinacao}%` : '—' }}</td>
            <td>{{ formatarData(arvore.data_ultima_coleta) }}</td>
            <td class="acoes">
              <button type="button" class="btn-coletar" title="Registrar coleta" @click.stop="emit('coletar', arvore)">
                Coleta
              </button>
              <button type="button" class="btn-editar" title="Editar" @click.stop="emit('editar', arvore)">
                Editar
              </button>
              <button type="button" class="btn-excluir" title="Excluir" @click.stop="excluir(arvore)">×</button>
            </td>
          </tr>
          <tr v-if="!store.carregando && store.matrizesFiltradas.length === 0">
            <td colspan="8" class="vazio">
              <template v-if="store.temFiltroAtivo">
                Nenhuma matriz com os filtros atuais.
              </template>
              <template v-else>
                Nenhuma matriz cadastrada. Use «Cadastrar matriz».
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

const emit = defineEmits(['editar', 'coletar'])
const store = useColetaStore()

function formatarData(data) {
  if (!data) return '—'
  return new Date(data).toLocaleDateString('pt-BR')
}

function local(arvore) {
  const p = [arvore.cidade, arvore.estado].filter(Boolean)
  return p.length ? p.join(' / ') : '—'
}

async function excluir(arvore) {
  if (!confirm(`Excluir matriz "${arvore.nome}"?`)) return
  try {
    await store.remover(arvore.id)
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir')
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

.card-title {
  display: flex;
  align-items: center;
  font-size: 1.125rem;
  font-weight: 600;
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
  border-bottom: 1px solid var(--color-border);
}

.coord {
  font-family: ui-monospace, monospace;
  font-size: 0.75rem;
}

.linha-clicavel {
  cursor: pointer;
}

.linha-clicavel:hover,
.linha-clicavel.selecionada {
  background-color: var(--color-background);
}

.acoes {
  display: flex;
  gap: 0.35rem;
  align-items: center;
}

.btn-coletar,
.btn-editar {
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-coletar {
  background: #fff3e0;
  color: #e65100;
}

.btn-editar {
  background: #e8f5e9;
  color: #2e7d32;
}

.btn-excluir {
  border: none;
  background: #fee2e2;
  color: #b91c1c;
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
