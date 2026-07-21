<template>
  <div v-if="visivel" class="admin-viveiro">
    <label v-if="podeSelecionar" class="admin-viveiro__select-wrap">
      <span class="sr-only">Unidade viveiro</span>
      <select
        class="admin-viveiro__select"
        :value="viveiro.ativo?.id"
        :disabled="trocando"
        @change="onChange"
      >
        <option v-for="v in opcoes" :key="v.id" :value="v.id">
          {{ v.nome }} · {{ v.modo_label }}
        </option>
      </select>
    </label>
    <span v-else class="admin-viveiro__badge" :title="viveiro.ativo?.nome">
      {{ viveiro.modoLabel }}
    </span>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useViveiroContextStore } from '@/store/viveiroContext'

const auth = useAuthStore()
const viveiro = useViveiroContextStore()
const trocando = ref(false)

const isAdmin = computed(() => auth.user?.perfis?.includes('admin'))
const podeSelecionar = computed(() => Boolean(viveiro.podeSelecionar))
const visivel = computed(() => isAdmin.value && viveiro.ativo)
const opcoes = computed(() => (viveiro.lista.length ? viveiro.lista : viveiro.ativo ? [viveiro.ativo] : []))

async function onChange(ev) {
  const id = Number(ev.target.value)
  if (!id || id === viveiro.ativo?.id) return
  trocando.value = true
  try {
    await viveiro.selectViveiro(id)
    window.location.href = '/'
  } finally {
    trocando.value = false
  }
}
</script>

<style scoped>
.admin-viveiro {
  display: flex;
  align-items: center;
}

.admin-viveiro__select {
  font-size: 0.8125rem;
  padding: 0.35rem 0.6rem;
  border-radius: var(--radius-md, 8px);
  border: 1px solid var(--color-border);
  background: var(--color-background);
  color: var(--color-text-primary);
  max-width: 16rem;
}

.admin-viveiro__badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: var(--radius-full);
  background: var(--color-primary-muted, #e8f0e4);
  color: var(--color-primary, #596247);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>
