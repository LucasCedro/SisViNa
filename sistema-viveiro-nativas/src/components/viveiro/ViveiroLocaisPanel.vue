<template>
  <section class="locais-panel">
    <p class="page-desc">
      Classifique cada área do viveiro. O tipo define o fluxo: sementeira → canteiro → rustificação.
      Áreas criadas no layout aparecem aqui.
    </p>

    <div v-if="!locais.length" class="empty-state">
      <p class="empty-title">Nenhum local cadastrado</p>
      <p class="empty-text">Use <strong>Editar layout</strong> no mapa para desenhar sementeiras e canteiros.</p>
    </div>

    <div v-else class="estoque-table-card">
      <table class="estoque-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Tipo do local</th>
            <th class="col-acoes"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in locais" :key="c.id">
            <td class="estoque-especie">{{ c.nome }}</td>
            <td>
              <select v-model="c.tipo_local" class="estoque-select-inline">
                <option value="sementeira">Sementeira</option>
                <option value="canteiro">Canteiro de mudas</option>
                <option value="rustificacao">Rustificação</option>
                <option value="armazem">Armazém de sementes</option>
              </select>
            </td>
            <td class="col-acoes">
              <button type="button" class="btn btn-outline btn-sm" @click="salvar(c)">Salvar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listCanteiros, updateCanteiro } from '@/services/canteiros'
import '@/components/estoques/estoques-shared.css'

const locais = ref([])

async function carregar() {
  locais.value = await listCanteiros({ ativo: true, limit: 200 })
}

async function salvar(c) {
  await updateCanteiro(c.id, { tipo_local: c.tipo_local })
  await carregar()
}

onMounted(carregar)

defineExpose({ carregar })
</script>

<style scoped>
.locais-panel {
  padding: 0 var(--spacing-lg) var(--spacing-xl);
}

.page-desc {
  margin: 0 0 var(--spacing-lg);
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  max-width: 42rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
}

.empty-title {
  margin: 0 0 0.5rem;
  font-weight: 600;
}

.empty-text {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.9375rem;
}
</style>
