<template>
  <section class="coleta-panel filtros-card">
    <header class="filtros-header">
      <h2 class="filtros-titulo">Filtros</h2>
      <span class="filtro-resumo">
        Exibindo <strong>{{ store.matrizesFiltradas.length }}</strong>
        de {{ store.arvoresMatriz.length }} matrizes
      </span>
    </header>

    <div class="filtros-grid">
      <label class="filtro">
        <span>Buscar</span>
        <input
          v-model="store.filtros.busca"
          type="search"
          placeholder="Nome, cidade ou espécie..."
        />
      </label>

      <label class="filtro">
        <span>Espécie</span>
        <select v-model="store.filtros.id_especie">
          <option value="">Todas</option>
          <option v-for="e in store.especiesParaFiltro" :key="e.id" :value="e.id">
            {{ e.nome }}
          </option>
        </select>
      </label>

      <label class="filtro">
        <span>UF</span>
        <select v-model="store.filtros.estado">
          <option value="">Todas</option>
          <option v-for="uf in store.estadosParaFiltro" :key="uf" :value="uf">
            {{ uf }}
          </option>
        </select>
      </label>

      <div class="filtro-acoes">
        <button
          v-if="store.temFiltroAtivo"
          type="button"
          class="btn-limpar"
          @click="store.limparFiltros()"
        >
          Limpar filtros
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useColetaStore } from '@/store/coleta'

const store = useColetaStore()
</script>

<style scoped>
.coleta-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.filtros-card {
  padding: 1rem 1.375rem 1.125rem;
}

.filtros-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.875rem;
  flex-wrap: wrap;
}

.filtros-titulo {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-secondary);
}

.filtro-resumo {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.filtro-resumo strong {
  color: var(--color-text-primary);
}

.filtros-grid {
  display: grid;
  grid-template-columns: minmax(180px, 2fr) minmax(140px, 1fr) minmax(80px, 0.5fr) auto;
  gap: 1rem;
  align-items: end;
}

.filtro {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.filtro input,
.filtro select {
  font-weight: 400;
  text-transform: none;
  letter-spacing: normal;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 0.875rem;
  background: #fff;
  color: var(--color-text-primary);
}

.filtro input:focus,
.filtro select:focus {
  outline: none;
  border-color: #6ca234;
  box-shadow: 0 0 0 2px rgba(108, 162, 52, 0.15);
}

.filtro-acoes {
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  min-height: 2.25rem;
}

.btn-limpar {
  padding: 0.5rem 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: #fff;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.btn-limpar:hover {
  background: var(--color-background);
  color: var(--color-text-primary);
}

@media (max-width: 900px) {
  .filtros-grid {
    grid-template-columns: 1fr 1fr;
  }

  .filtro-acoes {
    grid-column: 1 / -1;
    justify-content: flex-start;
  }
}

@media (max-width: 520px) {
  .filtros-grid {
    grid-template-columns: 1fr;
  }
}
</style>
