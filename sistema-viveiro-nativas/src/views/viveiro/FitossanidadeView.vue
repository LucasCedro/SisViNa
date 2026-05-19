<template>
    <div class="fitossanidade-view">
        <div class="content-wrapper">
            <h1 class="titulo-pagina">Fitossanidade</h1>

            <div class="secao">
                <div class="guias-container">
                    <div class="guias-navegacao">
                        <button 
                            class="guia" 
                            :class="{ 'ativa': guiaAtiva === 'monitoramento' }" 
                            @click="guiaAtiva = 'monitoramento'"
                        >
                            Monitoramento
                        </button>
                        <button 
                            class="guia" 
                            :class="{ 'ativa': guiaAtiva === 'analise' }" 
                            @click="guiaAtiva = 'analise'"
                        >
                            Análise de Recorrência
                        </button>
                    </div>
                    
                    <div class="guia-conteudo">
                        <div v-if="guiaAtiva === 'monitoramento'" class="painel-container">
                            <Fitossanidade />
                        </div>
                        <div v-else-if="guiaAtiva === 'analise'" class="painel-container">
                            <AnaliseRecorrencia />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import Fitossanidade from '@/components/viveiro/Fitossanidade.vue';
import AnaliseRecorrencia from '@/components/viveiro/AnaliseRecorrencia.vue';

const guiaAtiva = ref('monitoramento');
</script>

<style>
.fitossanidade-view {
    width: 100%;
    height: auto;
    min-height: 100%;
    overflow: auto;
}

.content-wrapper {
    padding: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
    width: 100%;
    height: auto;
}

.titulo-pagina {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-lg);
}

.secao {
    background-color: var(--color-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: visible;
    height: auto;
    min-height: 600px;
    width: 100%;
}

/* Estilos para as guias */
.guias-container {
    padding: var(--spacing-lg);
    width: 100%;
    height: auto;
}

.guias-navegacao {
    display: flex;
    border-bottom: 1px solid var(--color-border);
    margin-bottom: var(--spacing-lg);
}

.guia {
    padding: var(--spacing-md) var(--spacing-lg);
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 1rem;
    font-weight: 500;
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;
}

.guia:hover {
    color: var(--color-primary);
}

.guia.ativa {
    color: var(--color-primary);
    border-bottom: 3px solid var(--color-primary);
    font-weight: 600;
}

.guia-conteudo {
    height: auto;
    min-height: 500px;
    overflow: visible;
}

.painel-container {
    width: 100%;
    height: auto;
    overflow: visible;
}

/* Responsividade para as guias */
@media (max-width: 768px) {
    .content-wrapper {
        padding: var(--spacing-md);
        gap: var(--spacing-md);
    }
    
    .guias-navegacao {
        flex-direction: column;
    }
    
    .guia {
        width: 100%;
        text-align: left;
        border-left: 3px solid transparent;
        border-bottom: none;
    }
    
    .guia.ativa {
        border-left: 3px solid var(--color-primary);
        border-bottom: none;
    }
}
</style> 