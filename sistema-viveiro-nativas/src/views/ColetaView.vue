<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-800 mb-8">
      Gestão de Coleta de Sementes
    </h1>

    <div class="grid grid-cols-1 gap-8">
      <!-- Mapa -->
      <MapaColeta />

      <!-- Gráficos -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <GraficosColeta />
      </div>

      <!-- Tabela -->
      <TabelaColeta />
    </div>
  </div>
</template>

<script setup>
import MapaColeta from '../components/coleta/MapaColeta.vue'
import GraficosColeta from '../components/coleta/GraficosColeta.vue'
import TabelaColeta from '../components/coleta/TabelaColeta.vue'
</script>

<style scoped>
.container {
  max-width: 1400px;
}
</style> 