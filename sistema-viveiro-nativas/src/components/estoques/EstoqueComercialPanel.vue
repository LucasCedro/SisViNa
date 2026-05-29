<template>
  <div class="comercial-panel">
    <div class="pipeline-mudas" aria-label="Estágios das mudas">
      <article
        v-for="etapa in etapas"
        :key="etapa.id"
        class="pipeline-etapa"
        :class="'pipeline-etapa--' + etapa.tom"
      >
        <span class="pipeline-etapa__label">{{ etapa.label }}</span>
        <strong class="pipeline-etapa__valor">{{ etapa.valor }}</strong>
        <span v-if="etapa.meta" class="pipeline-etapa__meta">{{ etapa.meta }}</span>
      </article>
      <div class="pipeline-seta" aria-hidden="true">→</div>
      <article class="pipeline-etapa pipeline-etapa--venda">
        <span class="pipeline-etapa__label">Prontas para venda</span>
        <strong class="pipeline-etapa__valor">{{ totalUnidades }}</strong>
        <span class="pipeline-etapa__meta">recomendado ≥ {{ diasRust }} dias</span>
      </article>
    </div>

    <p class="estoque-info-box">
      Mudas <strong>aptas para venda</strong> na rustificação. O prazo de {{ diasRust }} dias é
      <strong>recomendado</strong>, não obrigatório — mudas abaixo desse prazo aparecem com aviso.
      Preços editáveis por espécie; a baixa ocorre em
      <router-link to="/vendas">Vendas</router-link>.
    </p>

    <div v-if="!items.length" class="estoque-empty">
      <p class="estoque-empty__titulo">Nenhuma muda pronta para venda</p>
      <p class="estoque-empty__texto">
        Libere o estágio em Produção (Liberar p/ venda). Mudas abaixo do prazo recomendado de
        {{ diasRust }} dias na rustificação ainda podem ser vendidas, com aviso ao gerente.
      </p>
      <div class="estoque-empty__acoes">
        <router-link to="/producao" class="btn btn-primary">Ir para Produção</router-link>
        <router-link to="/vendas" class="btn btn-outline">Registrar venda</router-link>
      </div>
      <p v-if="pipeline?.aptas_venda_aguardando_tempo" class="alert alert-warning" style="margin-top: 1rem">
        {{ pipeline.aptas_venda_aguardando_tempo }} muda(s) aptas com menos de {{ diasRust }} dias na rustificação (venda permitida, não recomendada).
      </p>
    </div>

    <div v-else class="estoque-table-card">
      <table class="estoque-table">
        <thead>
          <tr>
            <th>Espécie</th>
            <th class="col-num">Quantidade</th>
            <th class="col-num">Preço unit.</th>
            <th>Local</th>
            <th>Status</th>
            <th class="col-acoes"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.id_especie"
            :class="{ 'estoque-linha--alerta': item.quantidade < 5 }"
          >
            <td>
              <span class="estoque-especie">{{ item.nomePopular || item.nomeCientifico }}</span>
              <span v-if="item.nomePopular" class="estoque-especie-cient">{{ item.nomeCientifico }}</span>
            </td>
            <td class="col-num">
              <span class="estoque-qtd-destaque">{{ item.quantidade }}</span>
            </td>
            <td class="col-num">R$ {{ item.valorUnitario.toFixed(2) }}</td>
            <td>{{ item.localizacao }}</td>
            <td><span class="estoque-tag estoque-tag--ok">{{ item.tamanho }}</span></td>
            <td class="col-acoes">
              <button type="button" class="btn btn-outline btn-sm" @click="editarPreco(item)">
                Editar preço
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <dialog ref="dialogPreco" class="estoque-dialog">
      <form method="dialog" class="estoque-dialog__inner" @submit.prevent="salvarPreco">
        <header class="estoque-modal__header">
          <h3>Preço de venda</h3>
          <p>{{ formPreco.nomePopular || formPreco.nomeCientifico }} — {{ formPreco.quantidade }} un.</p>
        </header>
        <div class="estoque-modal__body">
          <label class="form-label">
            Preço unitário (R$)
            <input
              v-model.number="formPreco.valorUnitario"
              class="form-input"
              type="number"
              step="0.01"
              min="0.01"
              required
            />
          </label>
        </div>
        <footer class="estoque-modal__footer">
          <button type="button" class="btn btn-secondary" @click="fecharDialog">Cancelar</button>
          <button type="submit" class="btn btn-primary">Salvar</button>
        </footer>
      </form>
    </dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { atualizarPrecoEspecie } from '@/services/plantas'
import './estoques-shared.css'

const emit = defineEmits(['atualizado'])

const props = defineProps({
  items: { type: Array, default: () => [] },
  pipeline: { type: Object, default: null },
})

const dialogPreco = ref(null)
const formPreco = ref({
  id_especie: null,
  nomePopular: '',
  nomeCientifico: '',
  quantidade: 0,
  valorUnitario: 0,
})

const diasRust = computed(() => props.pipeline?.dias_minimos_rustificacao ?? 30)

const mappedItems = computed(() =>
  props.items.map((e) => ({
    id_especie: e.id_especie,
    nomePopular: e.nome_popular,
    nomeCientifico: e.nome_cientifico,
    quantidade: e.quantidade,
    valorUnitario: Number(e.valor_unitario) || 0,
    localizacao: e.localizacao || '—',
    tamanho: e.status_predominante || 'MUDA',
  }))
)

const items = computed(() => mappedItems.value)

const totalUnidades = computed(() =>
  items.value.reduce((s, i) => s + (i.quantidade || 0), 0)
)

const etapas = computed(() => {
  const p = props.pipeline || {}
  return [
    {
      id: 'dev',
      label: 'Desenvolvimento',
      valor: p.em_desenvolvimento_total ?? 0,
      meta: `${p.em_desenvolvimento_sementeira ?? 0} sem. · ${p.em_desenvolvimento_canteiro ?? 0} cant.`,
      tom: 'dev',
    },
    {
      id: 'rust',
      label: 'Em rustificação',
      valor: p.em_rustificacao ?? 0,
      meta: null,
      tom: 'rust',
    },
    {
      id: 'wait',
      label: 'Abaixo prazo recom.',
      valor: p.aptas_venda_aguardando_tempo ?? 0,
      meta: `${diasRust.value} dias`,
      tom: 'wait',
    },
  ]
})

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
  emit('atualizado')
}
</script>

<style scoped>
.comercial-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.pipeline-mudas {
  display: flex;
  align-items: stretch;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.pipeline-etapa {
  flex: 1 1 7rem;
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-subtle);
  background: var(--color-surface-muted);
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.pipeline-etapa--dev {
  border-color: var(--color-primary-100);
  background: var(--color-primary-subtle);
}

.pipeline-etapa--rust {
  border-color: var(--color-info-bg);
  background: var(--color-info-bg);
}

.pipeline-etapa--wait {
  border-color: var(--color-attention);
  background: var(--color-attention-bg);
}

.pipeline-etapa--venda {
  border-color: var(--color-success);
  background: var(--color-success-bg);
  flex: 1.2 1 8rem;
}

.pipeline-etapa__label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.pipeline-etapa__valor {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary-700);
  line-height: 1.1;
}

.pipeline-etapa__meta {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
}

.pipeline-seta {
  align-self: center;
  color: var(--color-text-muted);
  font-size: 1.25rem;
  padding: 0 0.25rem;
}

@media (max-width: 640px) {
  .pipeline-seta {
    display: none;
  }
}

.estoque-dialog {
  border: none;
  border-radius: var(--radius-xl);
  padding: 0;
  max-width: 420px;
  box-shadow: var(--shadow-lg);
}

.estoque-dialog__inner {
  margin: 0;
}
</style>
