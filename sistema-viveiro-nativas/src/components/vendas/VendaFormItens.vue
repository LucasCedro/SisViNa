<template>
  <section class="venda-itens">
    <header class="venda-itens__head">
      <div>
        <h4>Itens do pedido</h4>
        <p class="venda-itens__hint">Várias espécies na mesma venda. Escolha o lote de origem ou deixe automático (FIFO).</p>
      </div>
      <button type="button" class="btn btn-outline btn-sm" :disabled="!estoqueItems.length" @click="adicionarLinha">
        + Adicionar espécie
      </button>
    </header>

    <p v-if="!linhas.length" class="venda-itens__empty">Nenhum item — clique em “Adicionar espécie”.</p>

    <div v-for="(linha, idx) in linhas" :key="linha.uid" class="venda-linha">
      <div class="venda-linha__top">
        <span class="venda-linha__num">#{{ idx + 1 }}</span>
        <button
          v-if="linhas.length > 1"
          type="button"
          class="btn-link btn-link--danger"
          title="Remover linha"
          @click="removerLinha(idx)"
        >
          Remover
        </button>
      </div>

      <label class="module-field">
        Espécie
        <select v-model.number="linha.id_especie" required @change="onEspecieChange(linha)">
          <option :value="''">Selecione</option>
          <option v-for="e in estoqueItems" :key="e.id_especie" :value="e.id_especie">
            {{ labelEspecie(e) }} — {{ e.quantidade }} disp. · R$ {{ e.valorUnitario.toFixed(2) }}
          </option>
        </select>
      </label>

      <div class="module-form-row">
        <label class="module-field">
          Quantidade
          <input
            v-model.number="linha.quantidade"
            type="number"
            min="1"
            :max="maxQuantidade(linha)"
            required
            @input="emitUpdate"
          />
          <span v-if="linha.id_especie" class="field-hint">Máx. {{ maxQuantidade(linha) }} disp.</span>
        </label>
        <label class="module-field">
          Preço unit. (R$)
          <input
            v-model.number="linha.valorUnitario"
            type="number"
            step="0.01"
            min="0"
            required
            @input="emitUpdate"
          />
        </label>
        <label class="module-field">
          Desconto linha (R$)
          <input
            v-model.number="linha.desconto"
            type="number"
            step="0.01"
            min="0"
            @input="emitUpdate"
          />
        </label>
      </div>

      <label class="module-field">
        Origem das mudas
        <select v-model="linha.origem" @change="onOrigemChange(linha)">
          <option value="auto">Automático — sistema escolhe (FIFO)</option>
          <option value="lote">Escolher lote de sementes</option>
        </select>
      </label>

      <label v-if="linha.origem === 'lote'" class="module-field">
        Lote
        <select
          v-model="linha.loteKey"
          :disabled="!linha.id_especie || carregandoLote[linha.uid]"
          @change="onLoteChange(linha)"
        >
          <option v-if="carregandoLote[linha.uid]" value="" disabled>Carregando lotes…</option>
          <option v-else-if="!(lotesPorLinha[linha.uid] || []).length" value="" disabled>
            Nenhum lote disponível
          </option>
          <option v-for="l in lotesPorLinha[linha.uid] || []" :key="l.key" :value="l.key">
            {{ l.codigo_lote }} — {{ l.quantidade }} un.
            <template v-if="l.dias_min != null"> · {{ l.dias_min }}d rust.</template>
            <template v-if="!l.rustificacao_ok"> ⚠</template>
          </option>
        </select>
        <span v-if="carregandoLote[linha.uid]" class="field-hint">Consultando estoque por lote…</span>
        <span v-else-if="linha.loteKey && !loteTemEstoque(linha)" class="field-hint field-hint--warn">
          Quantidade acima do disponível neste lote.
        </span>
      </label>

      <div class="venda-linha__sub">
        Subtotal linha: <strong>R$ {{ subtotalLinha(linha).toFixed(2) }}</strong>
      </div>
    </div>

    <aside v-if="linhas.length" class="venda-resumo">
      <div class="venda-resumo__grid">
        <div>
          <span class="venda-resumo__label">Espécies</span>
          <strong>{{ resumo.linhas }}</strong>
        </div>
        <div>
          <span class="venda-resumo__label">Total mudas</span>
          <strong>{{ resumo.totalMudas }}</strong>
        </div>
        <div>
          <span class="venda-resumo__label">Descontos</span>
          <strong>R$ {{ resumo.descontos.toFixed(2) }}</strong>
        </div>
        <div class="venda-resumo__total">
          <span class="venda-resumo__label">Total pedido</span>
          <strong>R$ {{ resumo.total.toFixed(2) }}</strong>
        </div>
      </div>
    </aside>
  </section>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import { listPlantasDisponiveisVendaDetalhado } from '@/services/plantas'
import {
  criarLinhaVenda,
  labelEspecie,
  agruparLotes,
  subtotalLinha,
  resumoCarrinho,
} from '@/utils/vendaItens'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  estoqueItems: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const linhas = ref([])
const lotesPorLinha = reactive({})
const plantasPorEspecie = reactive({})
const carregandoLote = reactive({})

const resumo = computed(() => resumoCarrinho(linhas.value))

watch(
  () => props.modelValue,
  (v) => {
    if (v !== linhas.value) linhas.value = v?.length ? [...v] : []
  },
  { immediate: true, deep: true }
)

function emitUpdate() {
  emit('update:modelValue', linhas.value)
}

function adicionarLinha() {
  const primeira = props.estoqueItems[0]
  linhas.value.push(criarLinhaVenda(primeira))
  emitUpdate()
}

function removerLinha(idx) {
  const uid = linhas.value[idx]?.uid
  linhas.value.splice(idx, 1)
  if (uid) {
    delete lotesPorLinha[uid]
    delete carregandoLote[uid]
  }
  emitUpdate()
}

function maxQuantidade(linha) {
  if (!linha.id_especie) return 1
  const esp = props.estoqueItems.find((e) => e.id_especie === Number(linha.id_especie))
  let max = esp?.quantidade || 1

  if (linha.origem === 'lote' && linha.loteKey) {
    const lote = (lotesPorLinha[linha.uid] || []).find((l) => l.key === linha.loteKey)
    if (lote) max = Math.min(max, lote.quantidade)
  }

  const usadoOutras = linhas.value
    .filter((l) => l.uid !== linha.uid && l.id_especie === linha.id_especie)
    .reduce((s, l) => s + (Number(l.quantidade) || 0), 0)
  return Math.max(1, max - usadoOutras)
}

async function carregarPlantas(idEspecie) {
  const id = Number(idEspecie)
  if (plantasPorEspecie[id]) return plantasPorEspecie[id]
  const lista = await listPlantasDisponiveisVendaDetalhado(id)
  plantasPorEspecie[id] = lista
  return lista
}

async function onEspecieChange(linha) {
  const esp = props.estoqueItems.find((e) => e.id_especie === Number(linha.id_especie))
  linha.quantidade = 1
  linha.valorUnitario = esp?.valorUnitario ?? 0
  linha.desconto = 0
  linha.origem = 'auto'
  linha.id_lote_sementes = null
  linha.loteKey = null
  delete lotesPorLinha[linha.uid]
  if (linha.id_especie) await carregarPlantas(linha.id_especie)
  emitUpdate()
}

async function onOrigemChange(linha) {
  if (linha.origem === 'auto') {
    linha.id_lote_sementes = null
    linha.loteKey = null
  } else {
    await carregarLotesLinha(linha)
  }
  emitUpdate()
}

async function carregarLotesLinha(linha) {
  if (!linha.id_especie) return
  carregandoLote[linha.uid] = true
  try {
    const plantas = await carregarPlantas(linha.id_especie)
    lotesPorLinha[linha.uid] = agruparLotes(plantas)
    if (lotesPorLinha[linha.uid].length && !linha.loteKey) {
      linha.loteKey = lotesPorLinha[linha.uid][0].key
      onLoteChange(linha)
    }
  } finally {
    carregandoLote[linha.uid] = false
  }
}

function onLoteChange(linha) {
  const lote = (lotesPorLinha[linha.uid] || []).find((l) => l.key === linha.loteKey)
  linha.id_lote_sementes = lote?.id_lote_sementes ?? null
  if (lote && linha.quantidade > lote.quantidade) {
    linha.quantidade = lote.quantidade
  }
  emitUpdate()
}

function loteTemEstoque(linha) {
  if (linha.origem !== 'lote' || !linha.loteKey) return true
  const lote = (lotesPorLinha[linha.uid] || []).find((l) => l.key === linha.loteKey)
  return lote ? linha.quantidade <= lote.quantidade : false
}

/** Inicializa com uma linha se vazio. */
function init(linhasIniciais) {
  linhas.value = linhasIniciais?.length ? linhasIniciais : [criarLinhaVenda(props.estoqueItems[0])]
  emitUpdate()
}

defineExpose({ init, resumo, loteTemEstoque })
</script>

<style scoped>
.venda-itens {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}
.venda-itens__head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-sm);
}
.venda-itens__head h4 {
  margin: 0 0 0.2rem;
  font-size: 1rem;
}
.venda-itens__hint {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}
.venda-itens__empty {
  margin: 0;
  padding: var(--spacing-md);
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-text-muted);
}
.venda-linha {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  background: var(--color-surface-muted);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
.venda-linha__top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.venda-linha__num {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text-muted);
}
.btn-link--danger {
  color: var(--color-error);
}
.venda-linha__sub {
  font-size: 0.875rem;
  text-align: right;
  color: var(--color-text-secondary);
}
.field-hint--warn {
  color: var(--color-text-secondary);
}
.venda-resumo {
  padding: var(--spacing-md);
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-lg);
  background: var(--color-primary-subtle);
}
.venda-resumo__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: var(--spacing-md);
  align-items: end;
}
.venda-resumo__label {
  display: block;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text-muted);
  margin-bottom: 0.15rem;
}
.venda-resumo__total strong {
  font-size: 1.25rem;
  color: var(--color-primary-700);
}
</style>
