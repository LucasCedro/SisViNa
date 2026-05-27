<template>
  <div class="estoque-comercial">
    <header class="sec-header">
      <div>
        <h2 class="sec-titulo">Estoque comercial de mudas</h2>
        <p class="sec-lead">
          Apenas mudas marcadas como <strong>aptas p/ venda</strong> em Produção.
          A baixa ocorre automaticamente ao registrar a venda.
        </p>
      </div>
      <div class="sec-total">
        <strong>{{ totalUnidades }}</strong>
        <span>unidades vendáveis</span>
      </div>
    </header>

    <div v-if="!items.length" class="empty-box">
      <p class="empty-box__titulo">Nenhuma muda no estoque comercial</p>
      <p class="empty-box__texto">
        Espécies cadastradas só aparecem aqui depois que mudas no canteiro forem liberadas em
        <router-link to="/producao">Produção → Liberar estágios</router-link>.
      </p>
      <div v-if="pipeline" class="pipeline-resumo">
        <span><strong>{{ pipeline.em_crescimento_canteiro }}</strong> em crescimento no canteiro</span>
        <span><strong>{{ pipeline.em_desenvolvimento_sementeira }}</strong> na sementeira (desenvolv.)</span>
      </div>
    </div>

    <div v-else class="tabela-wrap">
      <table class="tabela">
        <thead>
          <tr>
            <th>Espécie</th>
            <th>Quantidade</th>
            <th>Preço unitário</th>
            <th>Localização</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id_especie" :class="{ 'linha-alerta': item.quantidade < 5 }">
            <td>
              <div class="especie-nome">{{ item.nomePopular || item.nomeCientifico }}</div>
              <div v-if="item.nomePopular" class="especie-cient">{{ item.nomeCientifico }}</div>
            </td>
            <td><strong class="qtd">{{ item.quantidade }}</strong></td>
            <td>R$ {{ item.valorUnitario.toFixed(2) }}</td>
            <td>{{ item.localizacao }}</td>
            <td>{{ item.tamanho }}</td>
            <td>
              <button type="button" class="btn-sec" @click="editarPreco(item)">Editar preço</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <dialog ref="dialogPreco" class="dialog-preco">
      <form method="dialog" class="dialog-box" @submit.prevent="salvarPreco">
        <h3>Preço de venda — {{ formPreco.nomePopular || formPreco.nomeCientifico }}</h3>
        <p class="dialog-hint">{{ formPreco.quantidade }} unidade(s) no estoque comercial</p>
        <label class="field">
          Preço unitário (R$)
          <input v-model.number="formPreco.valorUnitario" type="number" step="0.01" min="0.01" required />
        </label>
        <div class="dialog-actions">
          <button type="button" class="btn-sec" @click="fecharDialog">Cancelar</button>
          <button type="submit" class="btn-prim">Salvar</button>
        </div>
      </form>
    </dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getEstoqueResumo, atualizarPrecoEspecie } from '@/services/plantas'
import { getProducaoResumo } from '@/services/producao'

const items = ref([])
const pipeline = ref(null)
const dialogPreco = ref(null)
const formPreco = ref({
  id_especie: null,
  nomePopular: '',
  nomeCientifico: '',
  quantidade: 0,
  valorUnitario: 0,
})

const totalUnidades = computed(() =>
  items.value.reduce((s, i) => s + (i.quantidade || 0), 0)
)

async function carregar() {
  const [estoque, resumo] = await Promise.all([
    getEstoqueResumo(),
    getProducaoResumo().catch(() => null),
  ])
  pipeline.value = resumo
  items.value = estoque.map((e) => ({
    id_especie: e.id_especie,
    nomePopular: e.nome_popular,
    nomeCientifico: e.nome_cientifico,
    quantidade: e.quantidade,
    valorUnitario: Number(e.valor_unitario) || 0,
    localizacao: e.localizacao || '—',
    tamanho: e.status_predominante || '—',
  }))
}

onMounted(carregar)
defineExpose({ carregar })

function editarPreco(item) {
  formPreco.value = { ...item }
  dialogPreco.value?.showModal()
}

function fecharDialog() {
  dialogPreco.value?.close()
}

async function salvarPreco() {
  await atualizarPrecoEspecie(formPreco.value.id_especie, formPreco.value.valorUnitario)
  fecharDialog()
  await carregar()
}
</script>

<style scoped>
.sec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
}

.sec-titulo {
  margin: 0 0 0.35rem;
  font-size: 1.25rem;
  font-weight: 700;
}

.sec-lead {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  max-width: 36rem;
  line-height: 1.45;
}

.sec-total {
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.sec-total strong {
  font-size: 2rem;
  color: var(--color-primary-700);
  line-height: 1;
}

.sec-total span {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.empty-box {
  padding: var(--spacing-xl);
  background: var(--color-surface-muted);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
  text-align: center;
}

.empty-box__titulo {
  margin: 0 0 0.5rem;
  font-size: 1.0625rem;
  font-weight: 700;
}

.empty-box__texto {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
}

.empty-box__texto a {
  color: var(--color-primary);
  font-weight: 600;
}

.pipeline-resumo {
  display: flex;
  justify-content: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-md);
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
}

.tabela-wrap {
  overflow-x: auto;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-subtle);
}

.tabela {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9375rem;
}

.tabela th,
.tabela td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--color-border-subtle);
  text-align: left;
}

.tabela th {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-surface-muted);
}

.qtd {
  font-size: 1.125rem;
  color: var(--color-primary-700);
}

.linha-alerta {
  background: var(--color-attention-bg);
}

.especie-nome {
  font-weight: 600;
}

.especie-cient {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  font-style: italic;
}

.btn-sec,
.btn-prim {
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-sec {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.btn-prim {
  border: none;
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.dialog-preco {
  border: none;
  border-radius: var(--radius-lg);
  padding: 0;
  max-width: 400px;
  box-shadow: var(--shadow-lg);
}

.dialog-box {
  padding: var(--spacing-lg);
}

.dialog-hint {
  margin: 0 0 var(--spacing-md);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

.field input {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: inherit;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>
