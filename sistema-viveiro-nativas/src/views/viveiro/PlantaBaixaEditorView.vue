<template>
  <PageLayout>
    <PageSection>
      <template #header>
        <h2 class="secao-titulo">
          <svg xmlns="http://www.w3.org/2000/svg" class="secao-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Ferramenta de edição
        </h2>
      </template>
      <div class="editor-container">
        <ViveiroDesigner @voltar="voltarParaViveiro" />
      </div>
    </PageSection>
  </PageLayout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import PageLayout from '@/components/layout/PageLayout.vue'
import PageSection from '@/components/layout/PageSection.vue'
import ViveiroDesigner from '@/components/viveiro/ViveiroDesigner.vue'

const router = useRouter()
const voltarParaViveiro = () => router.push('/viveiro')
</script>

<style scoped>
.editor-container {
  min-height: 600px;
  height: calc(100vh - 220px);
}

@media (max-width: 768px) {
  .editor-container {
    height: calc(100vh - 180px);
  }
}
</style>
