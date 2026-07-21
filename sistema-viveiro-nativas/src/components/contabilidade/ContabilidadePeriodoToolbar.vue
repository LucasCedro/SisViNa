<template>
  <div class="contab-dem">
    <header class="contab-dem__toolbar">
      <div class="contab-dem__periodo">
        <label class="field-inline">
          <span>Mês</span>
          <select v-model.number="mes" @change="emitPeriodo">
            <option :value="0">Todos</option>
            <option v-for="(nome, idx) in meses" :key="idx" :value="idx + 1">{{ nome }}</option>
          </select>
        </label>
        <label class="field-inline">
          <span>Ano</span>
          <select v-model.number="ano" @change="emitPeriodo">
            <option v-for="a in anosDisponiveis" :key="a" :value="a">{{ a }}</option>
          </select>
        </label>
      </div>
      <button type="button" class="btn btn-secondary btn-sm" :disabled="carregando" @click="$emit('atualizar')">
        {{ carregando ? 'Atualizando…' : 'Atualizar' }}
      </button>
    </header>
    <slot />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  mes: { type: Number, required: true },
  ano: { type: Number, required: true },
  carregando: { type: Boolean, default: false },
})

const emit = defineEmits(['periodo', 'atualizar'])

const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
const mes = ref(props.mes)
const ano = ref(props.ano)

watch(() => [props.mes, props.ano], ([m, a]) => {
  mes.value = m
  ano.value = a
})

const anosDisponiveis = computed(() => {
  const y = new Date().getFullYear()
  return [y - 1, y, y + 1]
})

function emitPeriodo() {
  emit('periodo', { mes: mes.value, ano: ano.value })
}
</script>

<style scoped>
.contab-dem__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}
.contab-dem__periodo {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}
.field-inline {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8125rem;
}
.field-inline select {
  min-width: 5.5rem;
}
</style>
