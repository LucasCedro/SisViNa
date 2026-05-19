<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Header from './components/layout/Header.vue';
import Sidebar from './components/layout/Sidebar.vue';

const route = useRoute();

const isBlankLayout = computed(() => route.meta.layout === 'blank')

const currentPageTitle = computed(() => {
  const routePath = route.path;
  if (routePath === '/') return 'Página Inicial';
  if (routePath.includes('/viveiro')) return 'Viveiro';
  if (routePath.includes('/fitossanidade')) return 'Fitossanidade';
  if (routePath.includes('/fertilizacao')) return 'Fertilização';
  if (routePath.includes('/vendas-estoque')) return 'Vendas e Estoque';
  if (routePath.includes('/prescricao')) return 'Prescrição Técnica';
  if (routePath.includes('/coleta')) return 'Coleta de Sementes';
  if (routePath.includes('/biblioteca')) return 'Biblioteca';
  if (routePath.includes('/financeiro')) return 'Financeiro';
  return 'Viveiro Nativas';
});
</script>

<template>
  <router-view v-if="isBlankLayout" />
  <div v-else class="app-container">
    <Sidebar />
    <main class="main-content">
      <Header :title="currentPageTitle" />
      <div class="page-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style>
.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: var(--color-background);
}

.main-content {
  flex: 1;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  overflow: auto;
  padding: 0;
  margin: 0;
}

/* Estilos globais */
:root {
  --color-primary: #3498db;
  --color-primary-dark: #2980b9;
  --color-surface: #ffffff;
  --color-background: #f5f7fa;
  --color-border: #e1e5eb;
  --color-text-primary: #2c3e50;
  --color-text-secondary: #6c7a89;

  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 0.75rem;
  --spacing-lg: 1rem;
  --spacing-xl: 1.5rem;

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-full: 9999px;

  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  color: var(--color-text-primary);
  font-size: 16px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .page-content {
    padding: 0;
  }
}
</style>
