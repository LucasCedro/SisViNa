<template>
    <div class="prescricao-view">
        <div class="content-wrapper">
            <h1 class="titulo-pagina">Prescrição Técnica</h1>

            <div class="secao">
                <div class="secao-content">
                    <PrescricaoTecnica />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import PrescricaoTecnica from '@/components/prescricao/PrescricaoTecnica.vue';
</script>

<style>
.prescricao-view {
    width: 100%;
    height: 100%;
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

.secao-content {
    padding: var(--spacing-lg);
}

@media (max-width: 768px) {
    .content-wrapper {
        padding: var(--spacing-md);
        gap: var(--spacing-md);
    }
}
</style>