<template>
  <div class="table-card">
    <table class="data-table">
      <thead>
        <tr>
          <th class="col-check">
            <input
              type="checkbox"
              :checked="todos"
              :disabled="!podeOperar || !lista.length"
              @change="toggleTodos"
            />
          </th>
          <th>Código</th>
          <th>Espécie</th>
          <th>Local</th>
          <th>Dias</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="!lista.length">
          <td colspan="5" class="empty-cell">{{ empty }}</td>
        </tr>
        <tr v-for="p in lista" :key="p.id">
          <td>
            <input
              :checked="selecionados.includes(p.id)"
              type="checkbox"
              :disabled="!podeOperar"
              @change="toggle(p.id, $event.target.checked)"
            />
          </td>
          <td><code>{{ p.codigo_rastreio }}</code></td>
          <td>{{ p.especie_nome }}</td>
          <td>{{ p.nome_canteiro }}</td>
          <td>{{ dias(p.data_germinacao || p.data_plantio) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  lista: { type: Array, default: () => [] },
  selecionados: { type: Array, default: () => [] },
  podeOperar: { type: Boolean, default: true },
  empty: { type: String, default: 'Nenhum registro.' },
})
const emit = defineEmits(['update:selecionados'])

const todos = computed(
  () => props.lista.length > 0 && props.selecionados.length === props.lista.length
)

function toggle(id, checked) {
  const set = new Set(props.selecionados)
  if (checked) set.add(id)
  else set.delete(id)
  emit('update:selecionados', [...set])
}

function toggleTodos(e) {
  emit(
    'update:selecionados',
    e.target.checked ? props.lista.map((p) => p.id) : []
  )
}

function dias(d) {
  if (!d) return '—'
  const dt = new Date(String(d).includes('T') ? d : `${d}T12:00:00`)
  const n = Math.floor((Date.now() - dt.getTime()) / 86400000)
  return n >= 0 ? `${n}d` : '—'
}
</script>

<style scoped>
@import './producao-panel-shared.css';
</style>
