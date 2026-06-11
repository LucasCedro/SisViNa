<template>
  <ViveiroLayoutEditor @voltar="voltarParaViveiro" />
</template>

<script setup>
import { useRouter } from 'vue-router'
import ViveiroLayoutEditor from '@/components/viveiro/ViveiroLayoutEditor.vue'

const router = useRouter()
const voltarParaViveiro = () => router.push('/viveiro')
</script>

<style scoped>
:deep(.layout-editor) {
  height: 100%;
  min-height: 100%;
  overflow: hidden;
}
</style>
