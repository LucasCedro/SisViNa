<template>
  <div v-if="visivel" class="admin-empresa">
    <label v-if="podeSelecionar" class="admin-empresa__select-wrap">
      <span class="sr-only">Empresa</span>
      <select
        class="admin-empresa__select"
        :value="empresaAtivaId"
        :disabled="trocando"
        @change="onChange"
      >
        <option v-for="e in opcoes" :key="e.id" :value="e.id">
          {{ e.nome_fantasia }}
        </option>
      </select>
    </label>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useViveiroContextStore } from '@/store/viveiroContext'

const STORAGE_KEY = 'brotare_admin_empresa_id'

const auth = useAuthStore()
const viveiro = useViveiroContextStore()
const trocando = ref(false)

const podeSelecionar = computed(() => Boolean(auth.user?.pode_selecionar_empresa))
const visivel = computed(() => podeSelecionar.value && opcoes.value.length > 0)
const opcoes = computed(() => auth.user?.empresas || [])

const empresaAtivaId = computed(() => {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    const id = Number(stored)
    if (opcoes.value.some((e) => e.id === id)) return id
  }
  return auth.user?.empresa_ativa?.id ?? opcoes.value[0]?.id ?? null
})

async function onChange(ev) {
  const id = Number(ev.target.value)
  if (!id || id === empresaAtivaId.value) return
  trocando.value = true
  try {
    localStorage.setItem(STORAGE_KEY, String(id))
    viveiro.clearAdminSelection()
    await auth.loadUser()
    window.location.href = '/'
  } finally {
    trocando.value = false
  }
}
</script>

<style scoped>
.admin-empresa {
  display: flex;
  align-items: center;
}

.admin-empresa__select {
  font-size: 0.8125rem;
  padding: 0.35rem 0.6rem;
  border-radius: var(--radius-md, 8px);
  border: 1px solid var(--color-border);
  background: var(--color-background);
  color: var(--color-text-primary);
  max-width: 14rem;
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
