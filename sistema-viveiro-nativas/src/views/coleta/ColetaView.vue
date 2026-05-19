<template>
    <div class="coleta-view">
        <div class="content-wrapper">
            <!-- Mapa ocupando toda a largura horizontal -->
            <div class="secao-mapa">
                <MapaColeta />
            </div>

            <!-- Gráficos alinhados horizontalmente abaixo do mapa -->
            <div class="secao-graficos">
                <GraficosColeta />
            </div>

            <!-- Tabela abaixo dos gráficos -->
            <div class="secao-tabela">
                <TabelaColeta />
            </div>
        </div>
    </div>
</template>

<script setup>
import MapaColeta from '@/components/coleta/MapaColeta.vue'
import GraficosColeta from '@/components/coleta/GraficosColeta.vue'
import TabelaColeta from '@/components/coleta/TabelaColeta.vue'
</script>

<style>
.coleta-view {
    width: 100%;
    height: 100%;
}

.content-wrapper {
    padding: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
    width: 100%;
}

.secao-mapa {
    width: 100%;
}

.secao-graficos {
    width: 100%;
    height: auto;
}

.secao-tabela {
    width: 100%;
}

@media (max-width: 768px) {
    .content-wrapper {
        padding: var(--spacing-md);
        gap: var(--spacing-md);
    }
}
</style>