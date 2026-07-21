<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Header from './components/layout/Header.vue';
import Sidebar from './components/layout/Sidebar.vue';
import MobileNav from './components/layout/MobileNav.vue';
import AppLoadingOverlay from './components/shared/AppLoadingOverlay.vue';
import { useViewport } from './composables/useViewport';

const route = useRoute();
const { isMobile } = useViewport();

const isBlankLayout = computed(() => route.meta.layout === 'blank')

const currentPageTitle = computed(() => {
  const routePath = route.path;
  if (routePath === '/') return 'Início';
  if (routePath.includes('/producao')) return 'Produção';
  if (routePath.includes('/estoques')) return 'Compras e Estoques';
  if (routePath.includes('/viveiro')) return 'Viveiro';
  if (routePath.includes('/fitossanidade')) return 'Fitossanidade';
  if (routePath.includes('/fertilizacao')) return 'Fertilização';
  if (routePath.includes('/vendas')) return 'Vendas';
  if (routePath.includes('/prescricao')) return 'Prescrição Técnica';
  if (routePath.includes('/coleta')) return 'Coleta de Sementes';
  if (routePath.includes('/biblioteca')) return 'Biblioteca';
  if (routePath.includes('/financeiro')) return 'Financeiro';
  if (routePath.includes('/configuracoes')) return 'Configurações';
  if (routePath.includes('/admin/god-mode')) return 'God Mode';
  return 'Viveiro Nativas';
});
</script>

<template>
  <AppLoadingOverlay />
  <router-view v-if="isBlankLayout" />
  <div v-else class="app-container" :class="{ 'app-container--mobile': isMobile }">
    <Sidebar v-if="!isMobile" />
    <main class="main-content">
      <Header
        v-if="route.meta.hideHeader !== true"
        :title="currentPageTitle"
        :hide-title="route.meta.hidePageTitle === true"
      />
      <div
        class="page-content"
        :class="{
          'page-content--fill': route.meta.contentFill === true,
          'page-content--with-mobile-nav': isMobile,
        }"
      >
        <router-view />
      </div>
    </main>
    <MobileNav v-if="isMobile" />
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

.app-container--mobile {
  max-width: 100vw;
  overflow-x: hidden;
}

.main-content {
  flex: 1;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.page-content {
  flex: 1;
  overflow: auto;
  padding: 0;
  margin: 0;
  min-height: 0;
}

.page-content--fill {
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.page-content--fill > * {
  flex: 1;
  min-height: 0;
  min-width: 0;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

@media (max-width: 767px) {
  .page-content {
    padding: 0;
  }
}
</style>
