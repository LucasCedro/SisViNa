<template>
  <div ref="rootEl" class="seletor-especie">
    <button
      type="button"
      class="seletor-especie__trigger"
      :class="{ 'seletor-especie__trigger--aberto': aberto }"
      :disabled="disabled"
      :aria-expanded="aberto"
      aria-haspopup="listbox"
      @click="toggle"
    >
      <span class="seletor-especie__valor" :class="{ 'seletor-especie__valor--placeholder': !modelValue }">
        {{ textoSelecionado }}
      </span>
      <span class="seletor-especie__chevron" aria-hidden="true">▾</span>
    </button>

    <div v-show="aberto" class="seletor-especie__panel" role="listbox">
      <div class="seletor-especie__busca-wrap">
        <label class="seletor-especie__busca">
          <svg
            class="seletor-especie__lupa"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="7" />
            <path d="M20 20l-3.5-3.5" stroke-linecap="round" />
          </svg>
          <input
            ref="buscaRef"
            v-model="busca"
            type="text"
            class="seletor-especie__busca-input"
            placeholder="Buscar..."
            autocomplete="off"
            @keydown.escape.prevent="fechar"
            @keydown.stop
          />
        </label>
      </div>

      <ul class="seletor-especie__lista">
        <li
          v-for="e in especiesFiltradas"
          :key="e.id"
          role="option"
          class="seletor-especie__item"
          :class="{ 'seletor-especie__item--ativa': Number(modelValue) === e.id }"
          :aria-selected="Number(modelValue) === e.id"
          @click="selecionar(e)"
        >
          <span class="seletor-especie__item-label">{{ labelEspecie(e) }}</span>
        </li>
        <li v-if="!especiesFiltradas.length" class="seletor-especie__vazio">
          Nenhuma espécie encontrada
        </li>
      </ul>

      <p v-if="especies.length" class="seletor-especie__hint">
        {{ especiesFiltradas.length }} de {{ especies.length }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: { type: [Number, String], default: '' },
  especies: { type: Array, default: () => [] },
  disabled: { type: Boolean, default: false },
  placeholder: { type: String, default: 'Selecione uma espécie...' },
})

const emit = defineEmits(['update:modelValue'])

const rootEl = ref(null)
const buscaRef = ref(null)
const aberto = ref(false)
const busca = ref('')

function labelEspecie(e) {
  if (e.nome_popular) return `${e.nome_popular} (${e.nome_cientifico})`
  return e.nome_cientifico
}

const especiesOrdenadas = computed(() =>
  [...props.especies].sort((a, b) => {
    const cmp = (a.nome_popular || a.nome_cientifico || '').localeCompare(
      b.nome_popular || b.nome_cientifico || '',
      'pt-BR',
      { sensitivity: 'base' }
    )
    if (cmp !== 0) return cmp
    return (a.nome_cientifico || '').localeCompare(b.nome_cientifico || '', 'pt-BR', {
      sensitivity: 'base',
    })
  })
)

const especiesFiltradas = computed(() => {
  const q = busca.value.trim().toLowerCase()
  let lista = especiesOrdenadas.value
  if (q) {
    lista = lista.filter((e) => {
      const pop = (e.nome_popular || '').toLowerCase()
      const cient = (e.nome_cientifico || '').toLowerCase()
      return pop.includes(q) || cient.includes(q)
    })
  }
  const selId = Number(props.modelValue)
  if (selId && !lista.some((e) => e.id === selId)) {
    const selecionada = especiesOrdenadas.value.find((e) => e.id === selId)
    if (selecionada) lista = [selecionada, ...lista]
  }
  return lista
})

const textoSelecionado = computed(() => {
  const id = Number(props.modelValue)
  if (!id) return props.placeholder
  const e = props.especies.find((item) => item.id === id)
  return e ? labelEspecie(e) : props.placeholder
})

function fechar() {
  aberto.value = false
  busca.value = ''
}

async function abrir() {
  if (props.disabled) return
  aberto.value = true
  await nextTick()
  buscaRef.value?.focus()
}

function toggle() {
  if (aberto.value) fechar()
  else abrir()
}

function selecionar(e) {
  emit('update:modelValue', e.id)
  fechar()
}

function onClickFora(ev) {
  if (!aberto.value) return
  if (rootEl.value && !rootEl.value.contains(ev.target)) fechar()
}

watch(aberto, (open) => {
  if (open) document.addEventListener('pointerdown', onClickFora)
  else document.removeEventListener('pointerdown', onClickFora)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', onClickFora)
})

defineExpose({ fechar })
</script>

<style scoped>
.seletor-especie {
  position: relative;
}

.seletor-especie__trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  font-size: 0.875rem;
  font-weight: 400;
  text-align: left;
  cursor: pointer;
  color: var(--color-text-primary);
}

.seletor-especie__trigger:hover:not(:disabled) {
  border-color: var(--color-primary-200, var(--color-border));
}

.seletor-especie__trigger--aberto,
.seletor-especie__trigger:focus-visible {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 20%, transparent);
}

.seletor-especie__trigger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.seletor-especie__valor {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.seletor-especie__valor--placeholder {
  color: var(--color-text-muted);
}

.seletor-especie__chevron {
  flex-shrink: 0;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.seletor-especie__panel {
  position: absolute;
  z-index: 20;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.seletor-especie__busca-wrap {
  padding: 0.35rem 0.65rem 0.45rem;
  border-bottom: 1px solid color-mix(in srgb, var(--color-border) 65%, transparent);
}

.seletor-especie__busca {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: text;
}

.seletor-especie__lupa {
  flex-shrink: 0;
  width: 0.875rem;
  height: 0.875rem;
  color: var(--color-text-muted);
  opacity: 0.55;
}

.seletor-especie__busca-input {
  flex: 1;
  min-width: 0;
  padding: 0.2rem 0;
  border: none;
  background: transparent;
  font-size: 0.8125rem;
  font-weight: 400;
  color: var(--color-text-primary);
}

.seletor-especie__busca-input::placeholder {
  color: var(--color-text-muted);
  opacity: 0.7;
}

.seletor-especie__busca-input:focus {
  outline: none;
}

.seletor-especie__busca:focus-within .seletor-especie__lupa {
  opacity: 0.85;
  color: var(--color-text-secondary);
}

.seletor-especie__lista {
  list-style: none;
  margin: 0;
  padding: 0.25rem 0;
  max-height: 14rem;
  overflow-y: auto;
}

.seletor-especie__item {
  padding: 0.45rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 400;
  cursor: pointer;
  color: var(--color-text-primary);
}

.seletor-especie__item:hover {
  background: var(--color-surface-muted);
}

.seletor-especie__item--ativa {
  background: color-mix(in srgb, var(--color-primary) 12%, transparent);
  color: var(--color-primary-700, var(--color-primary));
  font-weight: 500;
}

.seletor-especie__item-label {
  display: block;
  line-height: 1.35;
}

.seletor-especie__vazio {
  padding: 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  text-align: center;
}

.seletor-especie__hint {
  margin: 0;
  padding: 0.35rem 0.75rem 0.5rem;
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  border-top: 1px solid color-mix(in srgb, var(--color-border) 65%, transparent);
}
</style>
