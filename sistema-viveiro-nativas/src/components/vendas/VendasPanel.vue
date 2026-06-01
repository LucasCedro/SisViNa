<template>
  <div class="vendas-panel">
    <header class="sec-header">
      <div>
        <p class="sec-lead">
          Registro comercial — dá baixa no estoque (planta → VENDIDA) e gera receita.
          Estoque disponível vem de <router-link to="/estoques">Estoques</router-link>.
        </p>
      </div>
      <button type="button" class="btn-prim" @click="abrirNovaVenda">
        + Registrar venda
      </button>
    </header>

    <aside v-if="estoqueResumo.total === 0" class="aviso-estoque">
      <strong>Sem estoque comercial para vender</strong>
      <p>
        Espécies cadastradas só aparecem na venda depois de liberar mudas em
        <router-link to="/producao">Produção → Liberar estágios → Aptas p/ venda</router-link>.
      </p>
      <ul v-if="pipeline" class="aviso-lista">
        <li><strong>{{ pipeline.em_crescimento_canteiro }}</strong> mudas em crescimento (canteiro)</li>
        <li><strong>{{ pipeline.prontas_venda }}</strong> aptas p/ venda agora</li>
        <li><strong>{{ pipeline.em_desenvolvimento_sementeira }}</strong> plântulas na sementeira</li>
      </ul>
    </aside>

    <aside v-else class="estoque-resumo-bar">
      <span><strong>{{ estoqueResumo.total }}</strong> mudas expedíveis</span>
      <span>{{ estoqueResumo.especies }} espécie(s) com estoque</span>
      <router-link to="/estoques">Ver estoque comercial →</router-link>
    </aside>

    <p v-if="erro" class="alert-erro">{{ erro }}</p>
    <aside v-if="avisoVenda.length" class="aviso-estoque aviso-estoque--warn">
      <strong>Venda registrada — avisos de manejo</strong>
      <ul class="aviso-lista">
        <li v-for="(a, i) in avisoVenda" :key="i">{{ a }}</li>
      </ul>
    </aside>
    <p v-if="carregando" class="status-msg">Carregando…</p>

    <div v-else class="tabela-wrap">
      <table class="tabela">
        <thead>
          <tr>
            <th>Data</th>
            <th>Comprador</th>
            <th>Itens</th>
            <th>Valor total</th>
            <th>Pagamento</th>
            <th>Status</th>
            <th>Obs.</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!historico.length">
            <td colspan="7" class="empty-cell">Nenhuma venda registrada.</td>
          </tr>
          <tr v-for="v in historico" :key="v.id">
            <td>{{ formatarData(v.data_venda) }}</td>
            <td>{{ v.comprador_nome || '—' }}</td>
            <td>{{ v.total_itens }}</td>
            <td><strong>R$ {{ Number(v.valor_total).toFixed(2) }}</strong></td>
            <td>{{ v.forma_pagamento || v.formaPagamento || '—' }}</td>
            <td><span class="tag" :class="'tag--' + (v.status || '').toLowerCase()">{{ v.status }}</span></td>
            <td>{{ v.observacoes || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal venda -->
    <dialog ref="dialogVenda" class="dialog-venda">
      <form method="dialog" class="dialog-box" @submit.prevent="salvarVenda">
        <h3>Registrar venda</h3>

        <div v-if="!estoqueItems.length" class="modal-aviso">
          <p>Não há mudas <strong>aptas p/ venda</strong> no estoque comercial.</p>
          <p>Libere mudas em Produção antes de vender.</p>
          <router-link to="/producao" class="btn-link" @click="fecharDialog">Ir para Produção</router-link>
        </div>

        <template v-else>
          <label class="field">
            Espécie (estoque comercial)
            <select v-model="formVenda.especieId" required @change="atualizarDadosEspecie">
              <option value="">Selecione</option>
              <option v-for="item in estoqueItems" :key="item.id_especie" :value="item.id_especie">
                {{ item.nomePopular || item.nomeCientifico }} — {{ item.quantidade }} disp. · R$ {{ item.valorUnitario.toFixed(2) }}
              </option>
            </select>
          </label>

          <div class="field-row">
            <label class="field">
              Quantidade
              <input
                v-model.number="formVenda.quantidade"
                type="number"
                min="1"
                :max="especieSelecionada?.quantidade || 1"
                required
                @input="calcularValorTotal"
              />
              <span v-if="especieSelecionada" class="field-hint">
                Máximo: {{ especieSelecionada.quantidade }}
              </span>
            </label>
            <label class="field">
              Valor total (R$)
              <input v-model.number="formVenda.valorTotal" type="number" step="0.01" min="0" required />
            </label>
          </div>

          <div class="field-row">
            <label class="field">
              Comprador
              <select v-model.number="formVenda.idComprador" required>
                <option value="">Selecione</option>
                <option v-for="c in compradores" :key="c.id" :value="c.id">{{ c.nome }}</option>
              </select>
            </label>
            <label class="field">
              Forma de pagamento
              <select v-model="formVenda.formaPagamento" required>
                <option value="PIX">PIX</option>
                <option value="Transferência">Transferência</option>
                <option value="Boleto">Boleto</option>
                <option value="Dinheiro">Dinheiro</option>
                <option value="Cartão">Cartão</option>
              </select>
            </label>
          </div>

          <label class="field">
            Data da venda
            <input v-model="formVenda.data" type="date" required />
          </label>

          <label class="field">
            Observações
            <textarea v-model="formVenda.observacoes" rows="2" />
          </label>

          <p class="field-hint field-hint--info">
            Recomendação de pelo menos 30 dias na rustificação.
          </p>
        </template>

        <div class="dialog-actions">
          <button type="button" class="btn-sec" @click="fecharDialog">Cancelar</button>
          <button
            v-if="estoqueItems.length"
            type="submit"
            class="btn-prim"
            :disabled="salvando || !formVenda.especieId"
          >
            Confirmar venda
          </button>
        </div>
      </form>
    </dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { getEstoqueResumo } from '@/services/plantas'
import { getProducaoResumo } from '@/services/producao'
import { listVendas, createVenda } from '@/services/vendas'
import { listCompradores } from '@/services/compradores'

const auth = useAuthStore()
const carregando = ref(true)
const salvando = ref(false)
const erro = ref(null)
const estoqueItems = ref([])
const historico = ref([])
const compradores = ref([])
const pipeline = ref(null)
const dialogVenda = ref(null)
const avisoVenda = ref([])

const formVenda = ref({
  data: new Date().toISOString().split('T')[0],
  especieId: '',
  quantidade: 1,
  valorTotal: 0,
  idComprador: '',
  formaPagamento: 'PIX',
  observacoes: '',
})

const estoqueResumo = computed(() => ({
  total: estoqueItems.value.reduce((s, i) => s + i.quantidade, 0),
  especies: estoqueItems.value.filter((i) => i.quantidade > 0).length,
}))

const especieSelecionada = computed(() => {
  if (!formVenda.value.especieId) return null
  return estoqueItems.value.find((i) => i.id_especie === Number(formVenda.value.especieId))
})

async function carregarEstoque() {
  const estoque = await getEstoqueResumo()
  estoqueItems.value = estoque
    .filter((e) => e.quantidade > 0)
    .map((e) => ({
      id_especie: e.id_especie,
      nomePopular: e.nome_popular,
      nomeCientifico: e.nome_cientifico,
      quantidade: e.quantidade,
      valorUnitario: Number(e.valor_unitario) || 0,
    }))
}

async function carregar() {
  carregando.value = true
  erro.value = null
  try {
    const [vendas, comps, resumo] = await Promise.all([
      listVendas({ limit: 200 }),
      listCompradores({ ativo: true, limit: 200 }),
      getProducaoResumo().catch(() => null),
    ])
    historico.value = vendas
    compradores.value = comps
    pipeline.value = resumo
    await carregarEstoque()
  } catch (e) {
    erro.value = 'Falha ao carregar vendas.'
    console.error(e)
  } finally {
    carregando.value = false
  }
}

onMounted(carregar)
defineExpose({ carregar })

async function abrirNovaVenda() {
  await carregarEstoque()
  formVenda.value = {
    data: new Date().toISOString().split('T')[0],
    especieId: estoqueItems.value[0]?.id_especie || '',
    quantidade: 1,
    valorTotal: 0,
    idComprador: compradores.value[0]?.id || '',
    formaPagamento: 'PIX',
    observacoes: '',
  }
  if (especieSelecionada.value) calcularValorTotal()
  dialogVenda.value?.showModal()
}

function fecharDialog() {
  dialogVenda.value?.close()
}

function atualizarDadosEspecie() {
  formVenda.value.quantidade = 1
  calcularValorTotal()
}

function calcularValorTotal() {
  if (especieSelecionada.value && formVenda.value.quantidade) {
    formVenda.value.valorTotal =
      especieSelecionada.value.valorUnitario * formVenda.value.quantidade
  }
}

async function salvarVenda() {
  if (!especieSelecionada.value) return
  if (formVenda.value.quantidade > especieSelecionada.value.quantidade) {
    alert('Quantidade acima do estoque comercial.')
    return
  }
  if (!formVenda.value.idComprador || !auth.user?.id) {
    alert('Selecione comprador e faça login.')
    return
  }
  salvando.value = true
  try {
    const valorUnit = especieSelecionada.value.valorUnitario
    const res = await createVenda({
      id_comprador: Number(formVenda.value.idComprador),
      id_funcionario: auth.user.id,
      data_venda: `${formVenda.value.data}T12:00:00`,
      forma_pagamento: formVenda.value.formaPagamento,
      status: 'PAGO',
      observacoes: formVenda.value.observacoes,
      itens_por_especie: [
        {
          id_especie: especieSelecionada.value.id_especie,
          quantidade: formVenda.value.quantidade,
          valor_unitario: valorUnit,
          desconto: 0,
        },
      ],
    })
    avisoVenda.value = res.avisos?.length ? res.avisos : []
    fecharDialog()
    await carregar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao registrar venda.')
  } finally {
    salvando.value = false
  }
}

function formatarData(d) {
  return new Date(d).toLocaleDateString('pt-BR')
}
</script>

<style scoped>
.vendas-panel {
  width: 100%;
}

.sec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
}

.sec-lead {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  max-width: 32rem;
  line-height: 1.45;
}

.sec-lead a {
  color: var(--color-primary);
  font-weight: 600;
}

.btn-prim,
.btn-sec {
  padding: 0.55rem 1.125rem;
  border-radius: var(--radius-lg);
  font-family: inherit;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-prim {
  border: none;
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-sec {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.aviso-estoque {
  padding: var(--spacing-lg);
  background: var(--color-attention-bg);
  border: 1px solid var(--color-attention);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
}

.aviso-estoque strong {
  display: block;
  font-size: 1rem;
  margin-bottom: 0.35rem;
}

.aviso-estoque p {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
}

.aviso-estoque a {
  color: var(--color-primary);
  font-weight: 600;
}

.aviso-estoque--warn {
  background: #fff8e6;
  border-color: #e6a817;
}

.aviso-lista {
  margin: var(--spacing-md) 0 0;
  padding-left: 1.25rem;
  font-size: 0.9375rem;
}

.estoque-resumo-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-success-bg);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
  font-size: 0.9375rem;
}

.estoque-resumo-bar strong {
  font-size: 1.125rem;
  color: var(--color-primary-700);
}

.estoque-resumo-bar a {
  margin-left: auto;
  color: var(--color-primary);
  font-weight: 600;
}

.alert-erro {
  padding: 0.75rem 1rem;
  background: var(--color-error-bg);
  color: var(--color-error);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-md);
}

.tabela-wrap {
  overflow-x: auto;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-subtle);
  box-shadow: var(--shadow-sm);
}

.tabela {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9375rem;
}

.tabela th,
.tabela td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border-subtle);
  text-align: left;
}

.tabela th {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-surface-muted);
}

.empty-cell {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-muted);
}

.tag {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-full);
  font-weight: 600;
  background: var(--color-surface-muted);
}

.tag--pago {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.dialog-venda {
  border: none;
  border-radius: var(--radius-lg);
  padding: 0;
  max-width: 520px;
  width: 92%;
  box-shadow: var(--shadow-lg);
}

.dialog-box {
  padding: var(--spacing-lg);
}

.dialog-box h3 {
  margin: 0 0 var(--spacing-md);
}

.modal-aviso {
  padding: var(--spacing-md);
  background: var(--color-attention-bg);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-md);
  font-size: 0.9375rem;
}

.modal-aviso p {
  margin: 0 0 0.35rem;
}

.btn-link {
  display: inline-block;
  margin-top: 0.5rem;
  color: var(--color-primary);
  font-weight: 600;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

.field input,
.field select,
.field textarea {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: inherit;
  font-size: 0.9375rem;
  font-weight: 400;
}

.field-hint {
  font-size: 0.8125rem;
  font-weight: 400;
  color: var(--color-text-muted);
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: var(--spacing-md);
}

@media (max-width: 600px) {
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
