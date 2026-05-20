<template>
    <div class="planta-editor-view">
        <div class="content-wrapper">
            <h1 class="titulo-pagina">Editor de Planta Baixa</h1>

            <div class="secao">
                <div class="secao-header">
                    <h2 class="secao-titulo">
                        <svg xmlns="http://www.w3.org/2000/svg" class="secao-icon" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        Ferramenta de Edição
                    </h2>
                </div>

                <div class="editor-container">
                    <ViveiroDesigner @voltar="voltarParaViveiro" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import ViveiroDesigner from '@/components/viveiro/ViveiroDesigner.vue'

const router = useRouter()
const voltarParaViveiro = () => router.push('/viveiro')
</script>

<style>
.planta-editor-view {
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

.editor-container {
    padding: var(--spacing-lg);
    height: calc(100vh - 200px);
    min-height: 600px;
}

@media (max-width: 768px) {
    .content-wrapper {
        padding: var(--spacing-md);
    }

    .editor-container {
        height: calc(100vh - 150px);
    }
}
</style>