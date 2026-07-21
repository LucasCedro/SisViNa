<template>
  <div class="vendas-panel">
    <header class="module-header">
      <p class="module-header__lead">
        Registro comercial — dá baixa no estoque (planta → VENDIDA) e gera receita.
        Estoque disponível vem de <router-link to="/estoques">Estoques</router-link>.
      </p>
      <div class="module-header__actions">
        <CanAccess permission="vendas.create">
          <button type="button" class="btn btn-primary" @click="abrirNovaVenda">
            + Registrar venda
          </button>
        </CanAccess>
      </div>
    </header>

    <aside v-if="nfeAmbiente?.modo_mock" class="module-banner module-banner--mock">
      <strong>NF-e em modo simulação</strong>
      <p>
        Sem <code>FOCUS_NFE_TOKEN</code> no <code>api_viveiro/.env</code> — emissões não vão à Focus/SEFAZ.
        Configure o token e rode <code>docker restart viveiro_api</code>.
      </p>
    </aside>
    <aside v-else-if="nfeAmbiente" class="module-banner module-banner--info">
      <strong>Homologação</strong> — {{ nfeAmbiente.mensagem }}
    </aside>

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

    <div v-else class="module-table-wrap">
      <table class="module-table">
        <thead>
          <tr>
            <th>Data</th>
            <th>Comprador</th>
            <th>Itens</th>
            <th>Valor total</th>
            <th>Pagamento</th>
            <th>Status</th>
            <th>NF-e</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!historico.length">
            <td colspan="8" class="empty-cell">Nenhuma venda registrada.</td>
          </tr>
          <tr v-for="v in historico" :key="v.id">
            <td>{{ formatarData(v.data_venda) }}</td>
            <td>{{ v.comprador_nome || '—' }}</td>
            <td>{{ v.total_itens }} muda(s)</td>
            <td><strong>R$ {{ Number(v.valor_total).toFixed(2) }}</strong></td>
            <td>
              <span class="tag tag--forma">{{ v.forma_pagamento || '—' }}</span>
            </td>
            <td>
              <span class="tag" :class="'tag--' + (v.status || '').toLowerCase()">{{ labelStatus(v.status) }}</span>
            </td>
            <td class="nfe-cell">
              <span
                v-for="n in notasPorVenda[v.id] || []"
                :key="n.id"
                class="tag tag--nfe"
                :class="'tag--nfe-' + (n.status || '').toLowerCase()"
                :title="n.xmotivo || n.status"
              >
                {{ labelNfe(n) }}
              </span>
              <button
                v-if="podeEmitirNfe && v.status !== 'CANCELADO' && podeEmitirNfeVenda(v.id)"
                type="button"
                class="btn-nfe"
                :disabled="emitindoNfe === v.id"
                @click="emitirNfeVenda(v)"
              >
                {{ emitindoNfe === v.id ? '…' : labelBotaoNfe(v.id) }}
              </button>
              <span v-else-if="v.status === 'CANCELADO'" class="muted">—</span>
            </td>
            <td>
              <button type="button" class="btn-link" @click="verDetalhe(v)">Detalhes</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal nova venda -->
    <AppModalOverlay
      :aberto="vendaDialogAberto"
      :handlers="overlayVenda"
      panel-class="app-modal-panel--xl"
      aria-labelledby="venda-modal-titulo"
    >
      <form class="dialog-panel" @submit.prevent="salvarVenda">
        <header class="app-modal-header">
          <div>
            <h3 id="venda-modal-titulo">Registrar venda</h3>
            <p class="app-modal-sub">Pedido comercial — cliente, itens, pagamento e entrega.</p>
          </div>
          <button type="button" class="app-modal-fechar" aria-label="Fechar" @click="fecharVenda">×</button>
        </header>

        <div class="dialog-panel__body venda-form-body">
          <div v-if="!estoqueItems.length" class="modal-aviso">
            <p>Não há mudas <strong>aptas p/ venda</strong> no estoque comercial.</p>
            <p>Libere mudas em Produção antes de vender.</p>
            <router-link to="/producao" class="btn-link" @click="fecharVenda">Ir para Produção</router-link>
          </div>

          <template v-else>
            <VendaCompradorNfe
              ref="compradorNfeRef"
              v-model:id-comprador="formVenda.idComprador"
              :tipo-operacao-fiscal="formVenda.tipoOperacaoFiscal"
            />

            <label class="module-field chk-field venda-importacao">
              <input v-model="formVenda.origemImportada" type="checkbox" @change="onToggleImportacao" />
              Mudas de origem estrangeira (importação SN)
              <span class="field-hint">Marque se o estoque veio de importação — NF-e usará regra de importação e icms_origem ≠ 0.</span>
            </label>

            <VendaFormItens
              ref="itensRef"
              v-model="linhasVenda"
              :estoque-items="estoqueItems"
            />

            <section class="venda-sec">
              <h4 class="venda-sec__titulo">Pagamento</h4>
              <div class="module-form-row">
                <label class="module-field">
                  Situação do pagamento
                  <select v-model="formVenda.statusPagamento" required disabled>
                    <option value="PENDENTE">Pendente — aguardando aprovação financeira</option>
                  </select>
                  <span class="field-hint field-hint--info">
                    Toda venda nasce <strong>pendente</strong>. O financeiro confirma o pagamento em Detalhes da venda.
                  </span>
                </label>
                <label class="module-field">
                  Forma de pagamento
                  <select v-model="formVenda.formaPagamento" required>
                    <option value="PIX">PIX</option>
                    <option value="Transferência">Transferência</option>
                    <option value="Boleto">Boleto</option>
                    <option value="Dinheiro">Dinheiro</option>
                    <option value="Cartão">Cartão</option>
                    <option value="A combinar">A combinar</option>
                  </select>
                </label>
              </div>
            </section>

            <section class="venda-sec">
              <h4 class="venda-sec__titulo">Datas e entrega</h4>
              <div class="module-form-row">
                <label class="module-field">
                  Data da venda
                  <input v-model="formVenda.data" type="date" required />
                </label>
                <label class="module-field">
                  Previsão de entrega / retirada
                  <input v-model="formVenda.dataEntrega" type="date" />
                </label>
              </div>
            </section>

            <label class="module-field">
              Observações do pedido
              <textarea v-model="formVenda.observacoes" rows="2" placeholder="Local de entrega, referência de pagamento, pedido do cliente…" />
            </label>
          </template>
        </div>

        <footer class="app-modal-footer dialog-panel__footer--venda">
          <div v-if="linhasVenda.length" class="footer-resumo">
            <strong>{{ resumoPedido.totalMudas }}</strong> muda(s) ·
            <strong>R$ {{ resumoPedido.total.toFixed(2) }}</strong>
            · Pendente
          </div>
          <div class="footer-acoes">
            <button type="button" class="btn btn-secondary" @click="fecharVenda">Cancelar</button>
            <button
              v-if="estoqueItems.length"
              type="submit"
              class="btn btn-primary"
              :disabled="salvando || !linhasVenda.length"
            >
              {{ salvando ? 'Registrando…' : 'Confirmar venda' }}
            </button>
          </div>
        </footer>
      </form>
    </AppModalOverlay>

    <ConfirmSaidaModal
      :aberto="confirmAberto"
      @confirmar="confirmarSaida"
      @cancelar="cancelarSaida"
    />

    <!-- Detalhe venda -->
    <AppModalOverlay
      :aberto="detalheAberto"
      :handlers="overlayDetalhe"
      panel-class="app-modal-panel--wide"
      aria-labelledby="venda-detalhe-titulo"
    >
      <div v-if="vendaDetalhe" class="dialog-panel">
        <header class="app-modal-header">
          <div>
            <h3 id="venda-detalhe-titulo">Venda #{{ vendaDetalhe.id }}</h3>
            <p class="app-modal-sub">
              {{ vendaDetalhe.comprador_nome }} · {{ formatarData(vendaDetalhe.data_venda) }} ·
              <span class="tag" :class="'tag--' + (vendaDetalhe.status || '').toLowerCase()">
                {{ labelStatus(vendaDetalhe.status) }}
              </span>
            </p>
          </div>
          <button type="button" class="app-modal-fechar" aria-label="Fechar" @click="fecharDetalhe">×</button>
        </header>
        <div class="dialog-panel__body">
          <p class="detalhe-meta">
            <strong>Forma:</strong> {{ vendaDetalhe.forma_pagamento || '—' }} ·
            <strong>Total:</strong> R$ {{ Number(vendaDetalhe.valor_total).toFixed(2) }} ·
            <strong>Vendedor:</strong> {{ vendaDetalhe.funcionario_nome || '—' }}
          </p>
          <table class="module-table detalhe-itens">
            <thead>
              <tr>
                <th>Planta</th>
                <th>Espécie</th>
                <th>Qtd</th>
                <th>Unit.</th>
                <th>Desc.</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="it in vendaDetalhe.itens" :key="it.id">
                <td><code>{{ it.codigo_planta }}</code></td>
                <td>{{ it.nome_especie }}</td>
                <td>{{ it.quantidade }}</td>
                <td>R$ {{ Number(it.valor_unitario).toFixed(2) }}</td>
                <td>R$ {{ Number(it.desconto || 0).toFixed(2) }}</td>
                <td><strong>R$ {{ Number(it.valor_total).toFixed(2) }}</strong></td>
              </tr>
            </tbody>
          </table>
          <p v-if="vendaDetalhe.observacoes" class="detalhe-obs">
            <strong>Obs.:</strong> {{ vendaDetalhe.observacoes }}
          </p>
        </div>
        <footer class="app-modal-footer">
          <button
            v-if="podeAprovar && vendaDetalhe.status === 'PENDENTE'"
            type="button"
            class="btn btn-primary"
            :disabled="aprovandoVenda"
            @click="aprovarVendaAtual"
          >
            {{ aprovandoVenda ? 'Aprovando…' : 'Confirmar pagamento' }}
          </button>
          <button type="button" class="btn btn-secondary" @click="fecharDetalhe">Fechar</button>
        </footer>
      </div>
    </AppModalOverlay>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import CanAccess from '@/components/shared/CanAccess.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { useSimpleModalClose } from '@/composables/useSimpleModalClose'
import { usePermissions } from '@/composables/usePermissions'
import { useGlobalLoading } from '@/composables/useGlobalLoading'
import { useFormDirty } from '@/utils/formDirty'
import { useAuthStore } from '@/store/auth'
import { getEstoqueResumo, listPlantasDisponiveisVendaDetalhado } from '@/services/plantas'
import { getProducaoResumo } from '@/services/producao'
import { listVendas, createVenda, getVenda, aprovarVenda } from '@/services/vendas'
import { emitirNfe, listNotasVenda, getNfeAmbiente } from '@/services/nfe'
import VendaCompradorNfe from '@/components/vendas/VendaCompradorNfe.vue'
import VendaFormItens from '@/components/vendas/VendaFormItens.vue'
import { criarLinhaVenda, resumoCarrinho, resolverItensVenda } from '@/utils/vendaItens'

const auth = useAuthStore()
const { can } = usePermissions()
const { runWithLoading } = useGlobalLoading()
const podeEmitirNfe = computed(() => can('fiscal.emit'))
const podeAprovar = computed(() => can('vendas.approve'))
const carregando = ref(true)
const salvando = ref(false)
const erro = ref(null)
const estoqueItems = ref([])
const historico = ref([])
const pipeline = ref(null)
const detalheAberto = ref(false)
const compradorNfeRef = ref(null)
const itensRef = ref(null)
const avisoVenda = ref([])
const emitindoNfe = ref(null)
const aprovandoVenda = ref(false)
const notasPorVenda = ref({})
const nfeAmbiente = ref(null)
const linhasVenda = ref([])
const vendaDetalhe = ref(null)

const formVenda = ref({
  data: new Date().toISOString().split('T')[0],
  dataEntrega: '',
  idComprador: null,
  formaPagamento: 'PIX',
  statusPagamento: 'PENDENTE',
  observacoes: '',
  origemImportada: false,
  tipoOperacaoFiscal: 'domestica',
})

const vendaDialogAberto = ref(false)

const vendaFormSnapshot = computed(() => ({
  ...formVenda.value,
  linhas: linhasVenda.value,
}))

const { isDirty, rebase } = useFormDirty(vendaFormSnapshot, () => vendaDialogAberto.value)

function fecharVendaInterno() {
  vendaDialogAberto.value = false
}

const overlayVenda = useModalFormClose(
  fecharVendaInterno,
  () => isDirty.value,
  () => vendaDialogAberto.value
)

const {
  confirmAberto,
  confirmarSaida,
  cancelarSaida,
  sairSemConfirmar,
} = overlayVenda

function fecharVenda() {
  overlayVenda.resetOverlayPress()
  overlayVenda.requestClose()
}

function fecharDetalheInterno() {
  detalheAberto.value = false
  vendaDetalhe.value = null
}

const overlayDetalhe = useSimpleModalClose(fecharDetalheInterno, () => detalheAberto.value)

const estoqueResumo = computed(() => ({
  total: estoqueItems.value.reduce((s, i) => s + i.quantidade, 0),
  especies: estoqueItems.value.filter((i) => i.quantidade > 0).length,
}))

const resumoPedido = computed(() => resumoCarrinho(linhasVenda.value))

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
    const [vendas, resumo, amb] = await Promise.all([
      listVendas({ limit: 200 }),
      getProducaoResumo().catch(() => null),
      getNfeAmbiente().catch(() => null),
    ])
    nfeAmbiente.value = amb
    historico.value = vendas
    pipeline.value = resumo
    await carregarNotasVendas(vendas)
    await carregarEstoque()
  } catch (e) {
    erro.value = 'Falha ao carregar vendas.'
    console.error(e)
  } finally {
    carregando.value = false
  }
}

onMounted(carregar)
defineExpose({
  carregar,
  recarregarCompradores: () => compradorNfeRef.value?.recarregarCompradores?.(),
})

async function abrirNovaVenda() {
  if (!can('vendas.create')) return
  await carregarEstoque()
  formVenda.value = {
    data: new Date().toISOString().split('T')[0],
    dataEntrega: '',
    idComprador: null,
    formaPagamento: 'PIX',
    statusPagamento: 'PENDENTE',
    observacoes: '',
    origemImportada: false,
    tipoOperacaoFiscal: 'domestica',
  }
  linhasVenda.value = [criarLinhaVenda(estoqueItems.value[0])]
  vendaDialogAberto.value = true
  await nextTick()
  rebase()
}

async function verDetalhe(v) {
  try {
    vendaDetalhe.value = await getVenda(v.id)
    detalheAberto.value = true
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao carregar detalhe.')
  }
}

function fecharDetalhe() {
  overlayDetalhe.resetOverlayPress()
  fecharDetalheInterno()
}

function labelStatus(st) {
  const map = { PAGO: 'Pago', PENDENTE: 'Pendente', CANCELADO: 'Cancelado' }
  return map[st] || st
}

function onToggleImportacao() {
  formVenda.value.tipoOperacaoFiscal = formVenda.value.origemImportada ? 'importacao' : 'domestica'
}

async function salvarVenda() {
  if (!linhasVenda.value.length) return
  if (!auth.user?.id) {
    alert('Faça login.')
    return
  }

  for (const linha of linhasVenda.value) {
    if (linha.origem === 'lote' && itensRef.value && !itensRef.value.loteTemEstoque(linha)) {
      alert('Ajuste a quantidade — estoque insuficiente no lote selecionado.')
      return
    }
  }

  salvando.value = true
  try {
    await runWithLoading(async () => {
      const idComprador = await compradorNfeRef.value?.garantirCompradorId()
      if (!idComprador) {
        alert('Informe o cliente da venda.')
        return
      }

      const itens = await resolverItensVenda(linhasVenda.value, (idEsp) =>
        listPlantasDisponiveisVendaDetalhado(idEsp)
      )

      if (formVenda.value.dataEntrega) {
        for (const it of itens) {
          it.data_entrega = formVenda.value.dataEntrega
        }
      }

      let obs = formVenda.value.observacoes?.trim() || ''
      if (formVenda.value.statusPagamento === 'PENDENTE' && !obs.toLowerCase().includes('pagamento pendente')) {
        obs = obs ? `${obs}\nPagamento pendente.` : 'Pagamento pendente.'
      }

      const res = await createVenda({
        id_comprador: Number(idComprador),
        id_funcionario: auth.user.id,
        data_venda: `${formVenda.value.data}T12:00:00`,
        forma_pagamento: formVenda.value.formaPagamento,
        status: 'PENDENTE',
        observacoes: obs || null,
        tipo_operacao_fiscal: formVenda.value.tipoOperacaoFiscal,
        itens,
      })
      avisoVenda.value = res.avisos?.length ? res.avisos : []
      sairSemConfirmar()
      await carregar()
    }, 'Registrando venda…')
  } catch (e) {
    alert(e.response?.data?.detail || e.message || 'Erro ao registrar venda.')
  } finally {
    salvando.value = false
  }
}

function formatarData(d) {
  return new Date(d).toLocaleDateString('pt-BR')
}

async function carregarNotasVendas(vendas) {
  const map = {}
  await Promise.all(
    (vendas || []).slice(0, 50).map(async (v) => {
      try {
        const notas = await listNotasVenda(v.id)
        if (notas?.length) map[v.id] = notas
      } catch {
        /* sem notas */
      }
    })
  )
  notasPorVenda.value = map
}

const STATUS_NFE_BLOQUEIA_REEMISSAO = ['processando', 'autorizada']

function labelNfe(n) {
  if (n.status === 'simulacao') return 'Simulação'
  const sim = (n.xmotivo || '').toLowerCase().includes('simula')
  if (n.status === 'autorizada') return sim ? 'Simulação' : `NF ${n.numero || n.id}`
  if (n.status === 'processando') return 'Processando…'
  if (n.status === 'rejeitada') return 'Rejeitada'
  return n.status || 'NF-e'
}

function podeEmitirNfeVenda(vendaId) {
  const notas = notasPorVenda.value[vendaId] || []
  return !notas.some((n) =>
    STATUS_NFE_BLOQUEIA_REEMISSAO.includes((n.status || '').toLowerCase())
  )
}

function labelBotaoNfe(vendaId) {
  const notas = notasPorVenda.value[vendaId] || []
  return notas.some((n) => (n.status || '').toLowerCase() === 'rejeitada') ? 'Reemitir' : 'Emitir'
}

function detalheErroNfe(err) {
  const d = err?.response?.data?.detail
  if (typeof d === 'string' && d.trim()) return d
  if (Array.isArray(d)) return d.map((x) => x.msg || x).join('\n')
  return err?.message || 'Erro ao emitir NF-e.'
}

async function aprovarVendaAtual() {
  if (!podeAprovar.value || !vendaDetalhe.value) return
  aprovandoVenda.value = true
  try {
    await runWithLoading(async () => {
      vendaDetalhe.value = await aprovarVenda(vendaDetalhe.value.id)
      await carregar()
    }, 'Confirmando pagamento…')
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao aprovar pagamento.')
  } finally {
    aprovandoVenda.value = false
  }
}

async function emitirNfeVenda(venda) {
  if (!podeEmitirNfe.value) return
  if (nfeAmbiente.value?.modo_mock && !confirm(
    'Modo SIMULAÇÃO — a nota NÃO será enviada à Focus/SEFAZ. Continuar?'
  )) return
  emitindoNfe.value = venda.id
  try {
    await runWithLoading(async () => {
      const res = await emitirNfe(venda.id)
      alert(res.mensagem || 'NF-e emitida.')
      await carregar()
    }, 'Emitindo NF-e…')
  } catch (e) {
    alert(detalheErroNfe(e))
    await carregar()
  } finally {
    emitindoNfe.value = null
  }
}
</script>

<style scoped>
.vendas-panel {
  width: 100%;
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
  background: var(--color-attention-bg);
  border-color: var(--color-attention);
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

.tag--pendente {
  background: var(--color-attention-bg);
  color: var(--color-text-secondary);
}

.tag--cancelado {
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
}

.tag--forma {
  background: transparent;
  border: 1px solid var(--color-border-subtle);
  font-weight: 500;
}

.nfe-cell {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  white-space: nowrap;
}

.btn-nfe {
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid var(--color-primary);
  background: transparent;
  color: var(--color-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.btn-nfe:disabled {
  opacity: 0.5;
  cursor: wait;
}

.tag--nfe {
  font-size: 0.7rem;
  margin-right: 0.25rem;
}

.tag--nfe-simulacao {
  background: var(--color-attention-bg);
  color: var(--color-text-secondary);
}
.tag--nfe-autorizada {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.tag--nfe-rejeitada,
.tag--nfe-processando {
  background: var(--color-surface-muted);
}

.muted {
  color: var(--color-text-muted);
}

.venda-form-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.venda-sec__titulo {
  margin: 0 0 var(--spacing-sm);
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.dialog-panel__footer--venda {
  flex-wrap: wrap;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.footer-resumo {
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
}

.footer-acoes {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

.detalhe-meta {
  margin: 0 0 var(--spacing-md);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.detalhe-itens {
  font-size: 0.8125rem;
}

.detalhe-obs {
  margin: var(--spacing-md) 0 0;
  font-size: 0.875rem;
}

.venda-importacao {
  margin-bottom: var(--spacing-md);
  font-size: 0.875rem;
}
.venda-importacao .field-hint {
  display: block;
  font-weight: 400;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}
.chk-field {
  flex-direction: row;
  align-items: flex-start;
  gap: 0.5rem;
}

@media (max-width: 600px) {
  .footer-acoes {
    width: 100%;
    margin-left: 0;
  }
  .dialog-panel__footer--venda {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
