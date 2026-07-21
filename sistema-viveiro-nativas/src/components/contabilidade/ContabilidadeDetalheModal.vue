<template>
  <AppModalOverlay
    :aberto="aberto"
    :handlers="modalClose"
    panel-class="app-modal-panel--xl"
  >
    <header class="fin-modal-header">
      <div>
        <p class="fin-modal-eyebrow">Composição do indicador</p>
        <h2>{{ titulo }}</h2>
        <p v-if="valor != null" class="fin-modal-valor">{{ fmt(valor) }}</p>
      </div>
      <button type="button" class="fin-modal-fechar" aria-label="Fechar" @click="fechar">×</button>
    </header>
    <div class="fin-modal-body">
      <FinanceiroDetalheBloco
        :tipo="tipo"
        :bloco="bloco"
        :estoque="estoque"
        :estoque-foco="estoqueFoco"
        :embedded="false"
      />
    </div>
    <footer class="fin-modal-footer">
      <button type="button" class="btn btn-secondary btn-sm" @click="fechar">Fechar</button>
    </footer>
  </AppModalOverlay>
</template>

<script setup>
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import FinanceiroDetalheBloco from '@/components/financeiro/FinanceiroDetalheBloco.vue'
import { useSimpleModalClose } from '@/composables/useSimpleModalClose'

const props = defineProps({
  aberto: { type: Boolean, default: false },
  titulo: { type: String, default: '' },
  valor: { type: Number, default: null },
  tipo: { type: String, required: true },
  bloco: { type: Object, default: null },
  estoque: { type: Object, default: null },
  estoqueFoco: { type: String, default: null },
})

const emit = defineEmits(['fechar'])

function fecharInterno() {
  emit('fechar')
}

const modalClose = useSimpleModalClose(fecharInterno, () => props.aberto)

function fechar() {
  modalClose.resetOverlayPress()
  fecharInterno()
}

function fmt(v) {
  return Number(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}
</script>

<style scoped>
@import '@/components/financeiro/financeiro-shared.css';
</style>
