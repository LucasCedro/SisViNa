<template>
    <div class="viveiro-view">
        <div class="content-wrapper">
            <h1 class="titulo-pagina">Gestão do Viveiro</h1>

            <!-- Guias de navegação -->
            <div class="secao">
                <div class="guias-container">
                    <div class="guias-navegacao">
                        <button class="guia" :class="{ 'ativa': guiaAtiva === 'gestao' }" @click="guiaAtiva = 'gestao'">
                            Gestão
                        </button>
                        <button class="guia" :class="{ 'ativa': guiaAtiva === 'cadastro' }"
                            @click="guiaAtiva = 'cadastro'">
                            Cadastro de Mudas
                        </button>
                    </div>

                    <div class="guia-conteudo">
                        <!-- Conteúdo da guia Gestão -->
                        <div v-if="guiaAtiva === 'gestao'" class="painel-container">
                            <!-- Seção da Planta Baixa -->
                            <div class="secao planta-baixa-secao">
                                <div class="secao-header">
                                    <h2 class="secao-titulo">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="secao-icon" fill="none"
                                            viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                        </svg>
                                        Planta Baixa do Viveiro
                                    </h2>
                                    <button @click="editarPlantaBaixa" class="btn-acao">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none"
                                            viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                        </svg>
                                        Editar Planta Baixa
                                    </button>
                                </div>

                                <div class="planta-container">
                                    <PlantaBaixa />
                                </div>
                            </div>

                            <!-- Layout de duas colunas para Detalhes e Dashboard -->
                            <div class="layout-colunas">
                                <!-- Painel de Detalhes -->
                                <div class="secao painel-detalhes-secao">
                                    <div class="secao-header">
                                        <h2 class="secao-titulo">
                                            <svg xmlns="http://www.w3.org/2000/svg" class="secao-icon" fill="none"
                                                viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                            </svg>
                                            Detalhes
                                        </h2>
                                    </div>

                                    <div class="painel-container">
                                        <PainelDetalhes />
                                    </div>
                                </div>

                                <!-- Painel de Dashboards -->
                                <div class="secao dashboard-secao">
                                    <div class="secao-header">
                                        <h2 class="secao-titulo">
                                            <svg xmlns="http://www.w3.org/2000/svg" class="secao-icon" fill="none"
                                                viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                            </svg>
                                            Dashboard
                                        </h2>
                                    </div>

                                    <div class="dashboard-container">
                                        <DashboardViveiro />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Conteúdo da guia Cadastro de Mudas -->
                        <div v-else-if="guiaAtiva === 'cadastro'" class="painel-container">
                            <CadastroMudas />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import PlantaBaixa from '@/components/viveiro/PlantaBaixa.vue';
import PainelDetalhes from '@/components/viveiro/PainelDetalhes.vue';
import DashboardViveiro from '@/components/viveiro/DashboardViveiro.vue';
import CadastroMudas from '@/components/viveiro/CadastroMudas.vue';
import { useViveiroStore } from '@/store/viveiro';

const store = useViveiroStore();
const router = useRouter();
const guiaAtiva = ref('gestao');

const editarPlantaBaixa = () => {
    router.push('/viveiro/planta-editor');
};

onMounted(() => {
    // Inicialização do store se necessário
    // Em uma aplicação real, aqui seria um bom lugar para carregar dados do backend
});
</script>

<style>
.viveiro-view {
    width: 100%;
    height: auto;
    min-height: 100%;
}

.content-wrapper {
    padding: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
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
    overflow: hidden;
}

.secao-header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.secao-titulo {
    display: flex;
    align-items: center;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
}

.secao-icon {
    width: 1.5rem;
    height: 1.5rem;
    margin-right: var(--spacing-md);
    color: var(--color-primary);
}

.planta-baixa-secao {
    margin-bottom: var(--spacing-xl);
}

.planta-container {
    padding: var(--spacing-lg);
    min-height: 600px;
}

.layout-colunas {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-xl);
}

.painel-container,
.dashboard-container {
    padding: var(--spacing-lg);
    height: auto;
    min-height: 500px;
}

/* Estilos para as guias */
.guias-container {
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

/* Responsividade */
@media (max-width: 1200px) {
    .layout-colunas {
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
    }
}

@media (max-width: 768px) {
    .content-wrapper {
        padding: var(--spacing-md);
        gap: var(--spacing-md);
    }

    .planta-container {
        min-height: 400px;
    }

    .painel-container,
    .dashboard-container {
        height: auto;
        min-height: 400px;
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

.btn-acao {
    display: flex;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
}

.btn-acao:hover {
    background-color: var(--color-primary-dark);
}

.btn-icon {
    width: 1.1rem;
    height: 1.1rem;
    margin-right: var(--spacing-sm);
}
</style>