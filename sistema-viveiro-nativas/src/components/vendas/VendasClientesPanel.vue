<template>
  <div class="clientes-root">
    <nav class="clientes-subnav" aria-label="Visões de clientes">
      <button
        v-for="t in abas"
        :key="t.id"
        type="button"
        class="clientes-subtab"
        :class="{ 'clientes-subtab--ativa': aba === t.id }"
        @click="aba = t.id"
      >
        {{ t.label }}
      </button>
    </nav>

    <ClientesAnaliticoPanel
      v-show="aba === 'inteligencia'"
      ref="analiticoRef"
      @novo="irCadastroNovo"
      @editar="irCadastroEditar"
    />
    <ClientesCadastroPanel
      v-show="aba === 'cadastro'"
      ref="cadastroRef"
      @salvou="onSalvou"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { usePageTab } from '@/composables/usePageTab'
import ClientesAnaliticoPanel from './ClientesAnaliticoPanel.vue'
import ClientesCadastroPanel from './ClientesCadastroPanel.vue'

const aba = usePageTab('vendas', 'inteligencia', {
  subKey: 'clientes',
  valid: ['inteligencia', 'cadastro'],
})
const analiticoRef = ref(null)
const cadastroRef = ref(null)

const abas = [
  { id: 'inteligencia', label: 'Inteligência' },
  { id: 'cadastro', label: 'Cadastro' },
]

function irCadastroNovo() {
  aba.value = 'cadastro'
  cadastroRef.value?.abrirNovo()
}

async function irCadastroEditar(id) {
  aba.value = 'cadastro'
  await cadastroRef.value?.editarPorId(id)
}

function onSalvou() {
  analiticoRef.value?.carregar()
}
</script>

<style scoped>
.clientes-subnav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: var(--spacing-lg);
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.clientes-subtab {
  border: none;
  background: transparent;
  padding: 0.45rem 0.85rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -0.55rem;
  font-family: inherit;
}

.clientes-subtab--ativa {
  color: var(--color-primary-700);
  border-bottom-color: var(--color-primary);
}
</style>
