<template>
  <div class="estoques-view">
    <div class="content-wrapper">
      <h1 class="titulo-pagina">Gestão de Estoques</h1>
      <p class="subtitulo">
        Sementes em armazém (lotes), plantas na sementeira/canteiro e insumos (substrato, etc.) para controle operacional e contábil.
      </p>

      <div class="cards">
        <div class="card">
          <span class="card-label">Lotes ativos</span>
          <strong>{{ resumo?.total_lotes_sementes_ativos ?? '—' }}</strong>
        </div>
        <div class="card">
          <span class="card-label">Sementes disponíveis</span>
          <strong>{{ resumo?.total_sementes_disponiveis ?? '—' }}</strong>
        </div>
        <div class="card">
          <span class="card-label">Plantas na sementeira</span>
          <strong>{{ resumo?.total_plantas_sementeira ?? '—' }}</strong>
        </div>
        <div class="card">
          <span class="card-label">Mudas nos canteiros</span>
          <strong>{{ resumo?.total_plantas_canteiro ?? '—' }}</strong>
        </div>
        <div class="card">
          <span class="card-label">Tipos de insumo</span>
          <strong>{{ resumo?.total_insumos ?? '—' }}</strong>
        </div>
      </div>

      <div class="secao-header">
        <h2>Estoque de sementes (lotes)</h2>
        <button type="button" class="btn-prim" @click="modalEntrada = true">Entrada no armazém</button>
      </div>
      <div class="tabela-wrap">
        <table class="tabela">
          <thead>
            <tr>
              <th>Código</th>
              <th>Origem</th>
              <th>Espécie</th>
              <th>Matriz</th>
              <th>Disponível</th>
              <th>Armazenamento</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in resumo?.lotes_sementes || []" :key="l.id">
              <td>{{ l.codigo_lote }}</td>
              <td><span class="tag">{{ l.origem_lote }}</span></td>
              <td>{{ l.especie_nome }}</td>
              <td>{{ l.matriz_nome || '—' }}</td>
              <td>{{ l.quantidade_disponivel }} / {{ l.quantidade_inicial }}</td>
              <td>{{ l.condicoes_armazenamento || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2 class="secao-titulo">Locais do viveiro</h2>
      <p class="hint">Defina se cada área é sementeira, canteiro de mudas ou armazém.</p>
      <div class="tabela-wrap">
        <table class="tabela">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Tipo</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in locais" :key="c.id">
              <td>{{ c.nome }}</td>
              <td>
                <select v-model="c.tipo_local" class="select-inline">
                  <option value="sementeira">Sementeira</option>
                  <option value="canteiro">Canteiro</option>
                  <option value="armazem">Armazém</option>
                </select>
              </td>
              <td>
                <button type="button" class="btn-sec" @click="salvarLocal(c)">Salvar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2 class="secao-titulo">Insumos e substratos</h2>
      <div class="tabela-wrap">
        <table class="tabela">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Tipo</th>
              <th>Estoque</th>
              <th>Unidade</th>
              <th>Fornecedor</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="i in resumo?.insumos || []" :key="i.id">
              <td>{{ i.nome }}</td>
              <td>{{ i.tipo }}</td>
              <td>{{ i.quantidade_estoque }}</td>
              <td>{{ i.unidade_medida || '—' }}</td>
              <td>{{ i.fornecedor || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="modalEntrada" class="modal-overlay" @click.self="modalEntrada = false">
      <div class="modal-card">
        <h3>Entrada de sementes no armazém</h3>
        <p class="hint">Compra ou estoque guardado — sem vínculo obrigatório com coleta.</p>
        <form @submit.prevent="salvarEntrada">
          <label class="field">
            Espécie
            <select v-model.number="formEntrada.id_especie" required>
              <option v-for="e in especies" :key="e.id" :value="e.id">
                {{ e.nome_popular || e.nome_cientifico }}
              </option>
            </select>
          </label>
          <label class="field">
            Quantidade
            <input v-model.number="formEntrada.quantidade" type="number" min="1" required />
          </label>
          <label class="field">
            Origem
            <select v-model="formEntrada.origem_lote">
              <option value="armazem">Armazém</option>
              <option value="compra">Compra</option>
              <option value="ajuste">Ajuste / inventário</option>
            </select>
          </label>
          <label class="field">
            Condições de armazenamento
            <input v-model="formEntrada.condicoes_armazenamento" type="text" />
          </label>
          <label class="field">
            Observações
            <textarea v-model="formEntrada.observacoes" rows="2" />
          </label>
          <p v-if="erro" class="erro">{{ erro }}</p>
          <div class="modal-footer">
            <button type="button" class="btn-sec" @click="modalEntrada = false">Cancelar</button>
            <button type="submit" class="btn-prim" :disabled="salvando">Registrar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getResumoEstoques, entradaSementesArmazem } from '@/services/estoques'
import { listEspecies } from '@/services/especies'
import { listCanteiros, updateCanteiro } from '@/services/canteiros'

const resumo = ref(null)
const locais = ref([])
const especies = ref([])
const modalEntrada = ref(false)
const salvando = ref(false)
const erro = ref('')
const formEntrada = ref({
  id_especie: null,
  quantidade: 100,
  origem_lote: 'armazem',
  condicoes_armazenamento: '',
  observacoes: ''
})

async function carregar() {
  resumo.value = await getResumoEstoques()
}

onMounted(async () => {
  especies.value = await listEspecies()
  if (especies.value.length) formEntrada.value.id_especie = especies.value[0].id
  locais.value = await listCanteiros({ ativo: true, limit: 200 })
  await carregar()
})

async function salvarLocal(c) {
  await updateCanteiro(c.id, { tipo_local: c.tipo_local })
  await carregar()
}

async function salvarEntrada() {
  erro.value = ''
  salvando.value = true
  try {
    await entradaSementesArmazem(formEntrada.value)
    modalEntrada.value = false
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao registrar entrada.'
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.estoques-view {
  width: 100%;
}
.content-wrapper {
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}
.titulo-pagina {
  font-size: 1.75rem;
  font-weight: 700;
}
.subtitulo {
  color: var(--color-text-secondary);
  margin-top: -0.5rem;
}
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
}
.card {
  background: var(--color-surface);
  padding: 1rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.card-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
.secao-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.secao-titulo {
  font-size: 1.25rem;
  margin-top: 0.5rem;
}
.tabela-wrap {
  overflow-x: auto;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}
.tabela {
  width: 100%;
  border-collapse: collapse;
}
.tabela th,
.tabela td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
}
.tag {
  font-size: 0.75rem;
  padding: 0.15rem 0.4rem;
  background: #e8f4fc;
  border-radius: 4px;
}
.btn-prim {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-card {
  background: white;
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 420px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}
.field input,
.field select,
.field textarea {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}
.hint {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
}
.modal-footer {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
.btn-sec {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  background: white;
  border-radius: var(--radius-sm);
}
.erro {
  color: #c0392b;
}
.select-inline {
  padding: 0.35rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}
</style>
