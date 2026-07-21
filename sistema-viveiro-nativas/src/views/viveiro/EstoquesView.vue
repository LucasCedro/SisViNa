<template>
  <PageLayout>
    <header class="estoque-page-header">
      <div>
        <p class="page-lead">
          Sementes, insumos (média móvel), mudas por custo acumulado — do desenvolvimento à comercialização.
        </p>
        <ul v-if="resumo" class="estoque-kpis-linha" aria-label="Totais de estoque">
          <li>
            <span class="estoque-kpis-linha__lbl">CMV vivas</span>
            <strong>R$ {{ formatMoeda(resumo.valor_total_mudas) }}</strong>
          </li>
          <li>
            <span class="estoque-kpis-linha__lbl">Comercial</span>
            <strong>R$ {{ formatMoeda(resumo.valor_mudas_comercial) }}</strong>
          </li>
          <li>
            <span class="estoque-kpis-linha__lbl">Sementes</span>
            <strong>R$ {{ formatMoeda(resumo.valor_total_sementes) }}</strong>
          </li>
        </ul>
      </div>
      <div class="estoque-page-header__acoes">
        <button
          type="button"
          class="btn btn-secondary"
          :disabled="carregando"
          @click="carregar"
        >
          {{ carregando ? 'Atualizando…' : 'Atualizar' }}
        </button>
      </div>
    </header>

    <p v-if="carregando && !resumo" class="alert alert-info">Carregando resumo de estoques…</p>
    <p v-else-if="erroPagina" class="alert alert-error">
      {{ erroPagina }}
      <button type="button" class="btn btn-outline btn-sm" style="margin-left: 0.5rem" @click="carregar">
        Tentar novamente
      </button>
    </p>

    <template v-else-if="resumo">
      <EstoqueFluxoBar :resumo="resumo" :guia-ativa="guiaAtiva" @ir-guia="guiaAtiva = $event" />

      <nav class="guias-navegacao estoque-guias" aria-label="Seções de estoque">
        <button
          v-for="g in guias"
          :key="g.id"
          type="button"
          class="guia"
          :class="{ ativa: guiaAtiva === g.id }"
          @click="guiaAtiva = g.id"
        >
          {{ g.label }}
          <span v-if="g.badge != null" class="guia-badge">{{ g.badge }}</span>
        </button>
      </nav>

      <!-- Mudas -->
      <PageSection v-show="guiaAtiva === 'mudas'">
        <template #header>
          <div class="secao-titulo-wrap">
            <h2 class="secao-titulo">Mudas — estoque comercial</h2>
            <p class="secao-sub">Aptas para venda na área de rustificação</p>
          </div>
        </template>
        <EstoqueComercialPanel
          :items="resumo.estoque_comercial"
          :pipeline="resumo.mudas_pipeline"
          @atualizado="carregar"
        />
        <EstoqueTimelinePanel :timeline-inicial="resumo.timeline_especies" />
        <EstoqueAnaliticoPanel
          :analitico-viveiro="resumo.analitico_mudas"
          :analitico-rustificacao="resumo.analitico_mudas_rustificacao"
        />
      </PageSection>

      <!-- Sementes -->
      <PageSection v-show="guiaAtiva === 'sementes'">
        <template #header>
          <div class="secao-header-flex">
            <div>
              <h2 class="secao-titulo">Sementes no armazém</h2>
              <p class="secao-sub">
                {{ resumo.total_lotes_sementes_ativos }} lote(s) ·
                {{ resumo.total_sementes_disponiveis }} sementes ·
                valor CMV: <strong>R$ {{ formatMoeda(resumo.valor_total_sementes) }}</strong>
              </p>
            </div>
            <button v-if="podeEditar" type="button" class="btn btn-primary" @click="abrirEntradaSementes">
              + Entrada no armazém
            </button>
          </div>
        </template>

        <div v-if="!resumo.lotes_sementes?.length" class="estoque-empty">
          <p class="estoque-empty__titulo">Nenhum lote com saldo</p>
          <p class="estoque-empty__texto">
            Registre entrada de sementes (compra, armazém ou ajuste) ou forme lotes a partir da coleta.
          </p>
          <div class="estoque-empty__acoes">
            <button v-if="podeEditar" type="button" class="btn btn-primary" @click="abrirEntradaSementes">
              Registrar entrada
            </button>
            <router-link to="/coleta" class="btn btn-outline">Módulo Coleta</router-link>
          </div>
        </div>
        <div v-else class="estoque-table-card">
          <table class="estoque-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Origem</th>
                <th>Espécie</th>
                <th>Matriz</th>
                <th class="col-num">Disponível</th>
                <th class="col-num">Consumido</th>
                <th class="col-num">Dias armaz.</th>
                <th class="col-num">Valor lote</th>
                <th class="col-num">Custo/un.</th>
                <th class="col-num">Germ. %</th>
                <th>Formação / coleta</th>
                <th>Armazenamento</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="l in resumo.lotes_sementes" :key="l.id">
                <td><code>{{ l.codigo_lote }}</code></td>
                <td><span class="estoque-tag estoque-tag--info">{{ l.origem_lote }}</span></td>
                <td>{{ l.especie_nome || '—' }}</td>
                <td>{{ l.matriz_nome || '—' }}</td>
                <td class="col-num">
                  <strong>{{ l.quantidade_disponivel }}</strong>
                  <span class="text-muted"> / {{ l.quantidade_inicial }}</span>
                </td>
                <td class="col-num">
                  {{ l.percentual_consumido != null ? l.percentual_consumido + '%' : '—' }}
                </td>
                <td class="col-num">{{ l.dias_armazenamento ?? '—' }}</td>
                <td class="col-num">{{ l.valor_total != null ? 'R$ ' + formatMoeda(l.valor_total) : '—' }}</td>
                <td class="col-num">{{ l.custo_unitario != null ? 'R$ ' + Number(l.custo_unitario).toFixed(4) : '—' }}</td>
                <td class="col-num">
                  {{ l.ultimo_teste_germinacao != null ? l.ultimo_teste_germinacao + '%' : '—' }}
                </td>
                <td>
                  <span class="text-muted">{{ l.data_formacao_lote || '—' }}</span>
                  <span v-if="l.data_coleta" class="text-muted"> · coleta {{ l.data_coleta }}</span>
                </td>
                <td>{{ l.condicoes_armazenamento || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </PageSection>

      <!-- Insumos -->
      <PageSection v-show="guiaAtiva === 'insumos'">
        <template #header>
          <div class="secao-header-flex">
            <div>
              <h2 class="secao-titulo">Insumos e substratos</h2>
              <p class="secao-sub">
                Valor total: <strong>R$ {{ formatMoeda(resumo.valor_total_insumos) }}</strong>
                — registre compras com quantidade e valor pago (preço médio automático)
              </p>
            </div>
            <button v-if="podeEditar" type="button" class="btn btn-primary" @click="abrirCadastroInsumo">
              + Cadastrar insumo
            </button>
          </div>
        </template>

        <p class="estoque-info-box">
          <strong>Entradas:</strong> registre compras com quantidade e <strong>valor total da NF</strong>
          — o preço médio alimenta o CMV no Financeiro.
          <strong>Sementeira:</strong> saídas de substrato são <strong>manuais</strong> (botão Saída).
          <strong>Canteiro:</strong> na transferência sementeira→canteiro o sistema baixa substrato
          automaticamente conforme a premissa em
          <router-link to="/financeiro">Financeiro</router-link>.
        </p>

        <div v-if="!resumo.insumos?.length" class="estoque-empty">
          <p class="estoque-empty__titulo">Nenhum insumo cadastrado</p>
          <p class="estoque-empty__texto">
            Cadastre substrato, NPK, embalagens etc. Depois use <strong>Entrada</strong> para registrar compras.
          </p>
          <button v-if="podeEditar" type="button" class="btn btn-primary" @click="abrirCadastroInsumo">
            Cadastrar primeiro insumo
          </button>
        </div>
        <div v-else class="estoque-table-card">
          <table class="estoque-table">
            <thead>
              <tr>
                <th>Insumo</th>
                <th>Tipo</th>
                <th class="col-num">Estoque</th>
                <th class="col-num">Preço médio</th>
                <th class="col-num">Valor CMV</th>
                <th>Fornecedor</th>
                <th>Última mov.</th>
                <th>Situação</th>
                <th class="col-acoes">Movimentação</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="i in resumo.insumos"
                :key="i.id"
                :class="{
                  'estoque-linha--alerta': i.alerta_estoque === 'abaixo_minimo',
                  'estoque-linha--max': i.alerta_estoque === 'acima_maximo',
                }"
              >
                <td>
                  <span class="estoque-especie">{{ i.nome }}</span>
                  <span class="estoque-especie-cient">{{ i.unidade_medida || 'unidade' }}</span>
                  <span v-if="i.descricao" class="text-muted insumo-desc">{{ i.descricao }}</span>
                  <div
                    v-if="i.estoque_maximo && i.estoque_maximo > 0"
                    class="estoque-saldo-bar"
                    :title="`Mín: ${i.estoque_minimo} · Máx: ${i.estoque_maximo}`"
                  >
                    <div
                      class="estoque-saldo-bar__fill"
                      :class="barraClasse(i)"
                      :style="{ width: barraPct(i) + '%' }"
                    />
                  </div>
                </td>
                <td>{{ i.tipo }}</td>
                <td class="col-num">
                  <span class="estoque-qtd-destaque">{{ i.quantidade_estoque }}</span>
                </td>
                <td class="col-num">
                  {{
                    i.preco_unitario != null
                      ? `R$ ${Number(i.preco_unitario).toFixed(2)}`
                      : '—'
                  }}
                </td>
                <td class="col-num">R$ {{ formatMoeda(i.valor_estoque) }}</td>
                <td>{{ i.fornecedor || '—' }}</td>
                <td>
                  <span v-if="i.ultima_movimentacao">{{ i.ultima_movimentacao }}</span>
                  <span v-else class="text-muted">—</span>
                  <span v-if="i.qtd_movimentacoes" class="text-muted"> ({{ i.qtd_movimentacoes }} mov.)</span>
                </td>
                <td>
                  <span v-if="i.alerta_estoque === 'abaixo_minimo'" class="estoque-tag estoque-tag--warn">
                    Abaixo do mínimo
                  </span>
                  <span v-else-if="i.alerta_estoque === 'acima_maximo'" class="estoque-tag estoque-tag--max">
                    Acima do máximo
                  </span>
                  <span v-else class="estoque-tag estoque-tag--ok">Normal</span>
                </td>
                <td v-if="podeEditar" class="col-acoes">
                  <div class="estoque-acoes-grupo">
                    <button type="button" class="btn btn-outline btn-sm" title="Editar cadastro" @click="abrirEditarInsumo(i)">
                      Editar
                    </button>
                    <button type="button" class="btn btn-primary btn-sm" @click="abrirMov(i, 'entrada')">
                      Entrada
                    </button>
                    <button
                      type="button"
                      class="btn btn-secondary btn-sm"
                      :disabled="!i.quantidade_estoque"
                      @click="abrirMov(i, 'saida')"
                    >
                      Saída
                    </button>
                  </div>
                </td>
                <td v-else class="col-acoes text-muted">—</td>
              </tr>
            </tbody>
          </table>
        </div>
      </PageSection>
    </template>

    <!-- Modal cadastro / edição insumo -->
    <AppModalOverlay
      :aberto="modalInsumoForm"
      :handlers="overlayInsumo"
      panel-class="app-modal-panel--wide"
    >
        <header class="estoque-modal__header">
          <h3>{{ modoInsumoForm === 'editar' ? 'Editar insumo' : 'Cadastrar insumo' }}</h3>
          <p>{{ metaInsumoForm.dicaUnidade }}</p>
        </header>
        <form class="estoque-modal__body estoque-form-grid" @submit.prevent="salvarInsumoForm">
          <label class="form-label form-label--full">
            Nome
            <input v-model="formInsumo.nome" class="form-input" required type="text" maxlength="100" />
          </label>
          <label class="form-label">
            Tipo
            <select v-model="formInsumo.tipo" class="form-input" :disabled="modoInsumoForm === 'editar'">
              <option v-for="t in TIPOS_INSUMO" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </label>
          <label class="form-label">
            Unidade de estoque
            <select v-model="formInsumo.unidade_medida" class="form-input" required>
              <option v-for="u in metaInsumoForm.unidades" :key="u.value" :value="u.value">{{ u.label }}</option>
            </select>
            <span class="field-hint">{{ metaInsumoForm.dicaUnidade }}</span>
          </label>
          <label class="form-label form-label--full">
            Descrição (opcional)
            <input
              v-model="formInsumo.descricao"
              class="form-input"
              type="text"
              placeholder="Ex.: casca de pinus + vermiculita 70/30"
            />
          </label>
          <label class="form-label">
            Fornecedor (opcional)
            <input v-model="formInsumo.fornecedor" class="form-input" type="text" maxlength="100" />
          </label>
          <label class="form-label">
            Estoque mínimo
            <input v-model.number="formInsumo.estoque_minimo" class="form-input" type="number" min="0" step="0.01" />
            <span class="field-hint">Opcional</span>
          </label>
          <label class="form-label">
            Estoque máximo
            <input v-model.number="formInsumo.estoque_maximo" class="form-input" type="number" min="0" step="0.01" />
            <span class="field-hint">Opcional</span>
          </label>
          <template v-if="modoInsumoForm === 'cadastro'">
            <label class="form-label">
              Entrada inicial — quantidade
              <input
                v-model.number="formInsumo.quantidade_inicial"
                class="form-input"
                type="number"
                min="0"
                step="0.01"
              />
              <span class="field-hint">Opcional — pode registrar depois em Entrada</span>
            </label>
            <label class="form-label">
              Valor total da NF (R$)
              <input
                v-model.number="formInsumo.valor_compra"
                class="form-input"
                type="number"
                min="0"
                step="0.01"
                :required="formInsumo.quantidade_inicial > 0"
              />
              <span class="field-hint">{{ metaInsumoForm.dicaEntrada }}</span>
            </label>
            <label v-if="formInsumo.quantidade_inicial > 0" class="form-label">
              Pagamento
              <select v-model="formInsumo.status_pagamento" class="form-input">
                <option value="PAGO">À vista (pago)</option>
                <option value="PENDENTE">A prazo (pendente)</option>
              </select>
            </label>
            <p v-if="previewCadastroPu" class="form-label form-label--full insumo-preview-pu">
              Preço médio estimado: <strong>{{ fmtPrecoUnitario(previewCadastroPu) }}</strong>
              / {{ formInsumo.unidade_medida }}
            </p>
          </template>
          <p v-if="erroModal" class="alert alert-error form-label--full">{{ erroModal }}</p>
        </form>
        <footer class="estoque-modal__footer">
          <button type="button" class="btn btn-secondary" @click="fecharInsumoForm">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="salvando" @click="salvarInsumoForm">
            {{ salvando ? 'Salvando…' : modoInsumoForm === 'editar' ? 'Salvar alterações' : 'Cadastrar' }}
          </button>
        </footer>
    </AppModalOverlay>
    <ConfirmSaidaModal
      :aberto="confirmAbertoInsumo"
      @confirmar="confirmarSaidaInsumo"
      @cancelar="cancelarSaidaInsumo"
    />

    <!-- Modal sementes -->
    <AppModalOverlay
      :aberto="modalEntrada"
      :handlers="overlayEntrada"
      panel-class="app-modal-panel--wide"
      aria-labelledby="modal-sementes-titulo"
    >
        <header class="estoque-modal__header">
          <h3 id="modal-sementes-titulo">Entrada de sementes</h3>
          <p>Compra ou estoque guardado</p>
        </header>
        <form class="estoque-modal__body estoque-form-grid" @submit.prevent="salvarEntrada">
          <label class="form-label">
            Espécie
            <select v-model.number="formEntrada.id_especie" class="form-input" required>
              <option v-for="e in especies" :key="e.id" :value="e.id">
                {{ e.nome_popular || e.nome_cientifico }}
              </option>
            </select>
          </label>
          <label class="form-label">
            Quantidade
            <input v-model.number="formEntrada.quantidade" class="form-input" type="number" min="1" required />
          </label>
          <label class="form-label">
            Origem do lote
            <select v-model="formEntrada.origem_lote" class="form-input">
              <option value="armazem">Armazém</option>
              <option value="compra">Compra</option>
              <option value="ajuste">Ajuste / inventário</option>
            </select>
          </label>
          <label class="form-label">
            Valor total pago (R$) — compra do lote
            <input v-model.number="formEntrada.valor_total" class="form-input" type="number" min="0" step="0.01" />
          </label>
          <label class="form-label">
            Condições de armazenamento
            <input v-model="formEntrada.condicoes_armazenamento" class="form-input" type="text" />
          </label>
          <label class="form-label">
            Observações
            <textarea v-model="formEntrada.observacoes" class="form-input" rows="2" />
          </label>
          <p v-if="erroModal" class="alert alert-error">{{ erroModal }}</p>
        </form>
        <footer class="estoque-modal__footer">
          <button type="button" class="btn btn-secondary" @click="fecharEntrada">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="salvando" @click="salvarEntrada">
            {{ salvando ? 'Salvando…' : 'Registrar entrada' }}
          </button>
        </footer>
    </AppModalOverlay>
    <ConfirmSaidaModal
      :aberto="confirmAbertoEntrada"
      @confirmar="confirmarSaidaEntrada"
      @cancelar="cancelarSaidaEntrada"
    />

    <!-- Modal insumo -->
    <AppModalOverlay
      :aberto="modalMov"
      :handlers="overlayMov"
      panel-class="app-modal-panel--wide"
    >
        <header class="estoque-modal__header">
          <h3>{{ formMov.tipo === 'entrada' ? 'Entrada de insumo' : 'Saída de insumo' }}</h3>
          <p>{{ insumoSelecionado?.nome }} · saldo atual {{ insumoSelecionado?.quantidade_estoque }} {{ insumoSelecionado?.unidade_medida || 'un.' }}</p>
        </header>
        <form class="estoque-modal__body estoque-form-grid" @submit.prevent="salvarMov">
          <label class="form-label">
            Quantidade ({{ insumoSelecionado?.unidade_medida || 'un.' }})
            <input
              v-model.number="formMov.quantidade"
              class="form-input"
              type="number"
              min="0.01"
              step="0.01"
              required
            />
          </label>
          <label v-if="formMov.tipo === 'entrada'" class="form-label">
            Valor total da NF (R$)
            <input
              v-model.number="formMov.valor_total"
              class="form-input"
              type="number"
              min="0.01"
              step="0.01"
              placeholder="Ex.: 1000,00"
              :required="entradaExigeValor"
            />
            <span class="field-hint">
              {{ entradaExigeValor ? 'Obrigatório na primeira entrada (preço médio = CMV)' : 'Atualiza o preço médio do estoque' }}
            </span>
          </label>
          <p
            v-if="formMov.tipo === 'entrada' && previewMovPu"
            class="form-label form-label--full insumo-preview-pu"
          >
            Preço unitário desta entrada: <strong>{{ fmtPrecoUnitario(previewMovPu) }}</strong>
            / {{ insumoSelecionado?.unidade_medida }}
          </p>
          <label v-if="formMov.tipo === 'entrada'" class="form-label">
            Pagamento
            <select v-model="formMov.status_pagamento" class="form-input">
              <option value="PAGO">À vista (pago)</option>
              <option value="PENDENTE">A prazo (pendente)</option>
            </select>
            <span class="field-hint">À vista entra no caixa; a prazo só na DRE até quitar</span>
          </label>
          <label v-if="formMov.tipo === 'saida'" class="form-label">
            Motivo
            <select v-model="formMov.motivo" class="form-input">
              <option v-for="m in MOTIVOS_SAIDA" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </label>
          <label class="form-label">
            Data da movimentação
            <input v-model="formMov.data_movimento" class="form-input" type="date" required />
          </label>
          <label class="form-label form-label--full">
            Observação
            <input
              v-model="formMov.observacao_extra"
              class="form-input"
              type="text"
              :placeholder="formMov.tipo === 'saida' ? 'Detalhe opcional' : 'NF, lote, fornecedor…'"
            />
          </label>
          <p v-if="erroModal" class="alert alert-error form-label--full">{{ erroModal }}</p>
        </form>
        <footer class="estoque-modal__footer">
          <button type="button" class="btn btn-secondary" @click="fecharMov">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="salvando" @click="salvarMov">
            {{ salvando ? 'Salvando…' : 'Confirmar' }}
          </button>
        </footer>
    </AppModalOverlay>
    <ConfirmSaidaModal
      :aberto="confirmAbertoMov"
      @confirmar="confirmarSaidaMov"
      @cancelar="cancelarSaidaMov"
    />
  </PageLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import AppModalOverlay from '@/components/shared/AppModalOverlay.vue'
import ConfirmSaidaModal from '@/components/shared/ConfirmSaidaModal.vue'
import { useModalFormClose } from '@/composables/useModalFormClose'
import { useFormDirty } from '@/utils/formDirty'
import { usePermissions } from '@/composables/usePermissions'
import { usePageTab } from '@/composables/usePageTab'
import { useGlobalLoading } from '@/composables/useGlobalLoading'
import PageLayout from '@/components/layout/PageLayout.vue'
import PageSection from '@/components/layout/PageSection.vue'
import EstoqueComercialPanel from '@/components/estoques/EstoqueComercialPanel.vue'
import EstoqueTimelinePanel from '@/components/estoques/EstoqueTimelinePanel.vue'
import EstoqueAnaliticoPanel from '@/components/estoques/EstoqueAnaliticoPanel.vue'
import EstoqueFluxoBar from '@/components/estoques/EstoqueFluxoBar.vue'
import { getResumoEstoques, entradaSementesArmazem, registrarMovimentacaoInsumo } from '@/services/estoques'
import { createInsumo, updateInsumo } from '@/services/insumos'
import { listEspecies } from '@/services/especies'
import {
  TIPOS_INSUMO,
  MOTIVOS_SAIDA,
  metaTipoInsumo,
  unidadeDefaultTipo,
  previewPrecoUnitario,
  fmtPrecoUnitario,
} from '@/constants/insumosUi'
import '@/components/estoques/estoques-shared.css'

const GUIAS_ESTOQUE = ['mudas', 'sementes', 'insumos']
const resumo = ref(null)
const { can } = usePermissions()
const { runWithLoading } = useGlobalLoading()
const podeEditar = computed(() => can('estoques.edit'))
const guiaAtiva = usePageTab('estoques', 'mudas', { valid: GUIAS_ESTOQUE })
const especies = ref([])
const carregando = ref(true)
const erroPagina = ref('')
const modalEntrada = ref(false)
const modalMov = ref(false)
const modalInsumoForm = ref(false)
const modoInsumoForm = ref('cadastro')
const insumoEditandoId = ref(null)
const salvando = ref(false)
const erroModal = ref('')
const insumoSelecionado = ref(null)

function formInsumoVazio() {
  return {
    nome: '',
    tipo: 'Substrato',
    unidade_medida: 'kg',
    descricao: '',
    fornecedor: '',
    estoque_minimo: 0,
    estoque_maximo: null,
    quantidade_inicial: null,
    valor_compra: null,
    status_pagamento: 'PAGO',
  }
}

const formInsumo = ref(formInsumoVazio())

const formEntrada = ref({
  id_especie: null,
  quantidade: 100,
  valor_total: null,
  origem_lote: 'armazem',
  condicoes_armazenamento: '',
  observacoes: '',
})

const formMov = ref({
  tipo: 'entrada',
  quantidade: 1,
  valor_total: null,
  status_pagamento: 'PAGO',
  data_movimento: new Date().toISOString().slice(0, 10),
  motivo: 'uso_sementeira',
  observacao_extra: '',
})

const { isDirty: isDirtyInsumo, rebase: rebaseInsumo } = useFormDirty(
  formInsumo,
  () => modalInsumoForm.value
)
const { isDirty: isDirtyEntrada, rebase: rebaseEntrada } = useFormDirty(
  formEntrada,
  () => modalEntrada.value
)
const { isDirty: isDirtyMov, rebase: rebaseMov } = useFormDirty(formMov, () => modalMov.value)

function fecharInsumoFormInterno() {
  modalInsumoForm.value = false
  insumoEditandoId.value = null
}

function fecharEntradaInterno() {
  modalEntrada.value = false
}

function fecharMovInterno() {
  modalMov.value = false
  insumoSelecionado.value = null
}

const overlayInsumo = useModalFormClose(fecharInsumoFormInterno, () => isDirtyInsumo.value, () => modalInsumoForm.value)
const overlayEntrada = useModalFormClose(fecharEntradaInterno, () => isDirtyEntrada.value, () => modalEntrada.value)
const overlayMov = useModalFormClose(fecharMovInterno, () => isDirtyMov.value, () => modalMov.value)

const {
  confirmAberto: confirmAbertoInsumo,
  confirmarSaida: confirmarSaidaInsumo,
  cancelarSaida: cancelarSaidaInsumo,
  requestClose: requestCloseInsumo,
  sairSemConfirmar: sairSemConfirmarInsumo,
} = overlayInsumo

const {
  confirmAberto: confirmAbertoEntrada,
  confirmarSaida: confirmarSaidaEntrada,
  cancelarSaida: cancelarSaidaEntrada,
  requestClose: requestCloseEntrada,
  sairSemConfirmar: sairSemConfirmarEntrada,
} = overlayEntrada

const {
  confirmAberto: confirmAbertoMov,
  confirmarSaida: confirmarSaidaMov,
  cancelarSaida: cancelarSaidaMov,
  requestClose: requestCloseMov,
  sairSemConfirmar: sairSemConfirmarMov,
} = overlayMov

const metaInsumoForm = computed(() => metaTipoInsumo(formInsumo.value.tipo))

const previewCadastroPu = computed(() =>
  previewPrecoUnitario(formInsumo.value.quantidade_inicial, formInsumo.value.valor_compra)
)

const previewMovPu = computed(() =>
  previewPrecoUnitario(formMov.value.quantidade, formMov.value.valor_total)
)

const entradaExigeValor = computed(() => {
  const i = insumoSelecionado.value
  if (!i || formMov.value.tipo !== 'entrada') return false
  const semEstoque = !i.quantidade_estoque || Number(i.quantidade_estoque) <= 0
  const semPreco = i.preco_unitario == null || Number(i.preco_unitario) <= 0
  return semEstoque && semPreco
})

watch(
  () => formInsumo.value.tipo,
  (tipo, prev) => {
    if (modoInsumoForm.value !== 'cadastro' || tipo === prev) return
    const unidades = metaTipoInsumo(tipo).unidades.map((u) => u.value)
    if (!unidades.includes(formInsumo.value.unidade_medida)) {
      formInsumo.value.unidade_medida = unidadeDefaultTipo(tipo)
    }
  }
)

watch(modalEntrada, (aberto) => {
  if (aberto) nextTick().then(rebaseEntrada)
})

const guias = computed(() => {
  const r = resumo.value
  const alertas = (r?.insumos || []).filter((i) => i.alerta_estoque).length
  return [
    { id: 'mudas', label: 'Mudas', badge: r?.total_mudas_aptas_venda || null },
    { id: 'sementes', label: 'Sementes', badge: r?.total_lotes_sementes_ativos || null },
    { id: 'insumos', label: 'Insumos', badge: alertas > 0 ? alertas : r?.total_insumos || null },
  ]
})

function formatMoeda(v) {
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function barraPct(i) {
  const max = Number(i.estoque_maximo) || 0
  if (max <= 0) return 0
  return Math.min(100, (Number(i.quantidade_estoque) / max) * 100)
}

function barraClasse(i) {
  if (i.alerta_estoque === 'abaixo_minimo') return 'estoque-saldo-bar__fill--danger'
  if (i.alerta_estoque === 'acima_maximo') return 'estoque-saldo-bar__fill--warn'
  const pct = barraPct(i)
  if (pct < 30) return 'estoque-saldo-bar__fill--warn'
  return ''
}

async function carregar() {
  carregando.value = true
  erroPagina.value = ''
  try {
    resumo.value = await getResumoEstoques()
  } catch (e) {
    erroPagina.value =
      e.response?.data?.detail || 'Não foi possível carregar o resumo de estoques.'
    resumo.value = null
  } finally {
    carregando.value = false
  }
}

onMounted(async () => {
  try {
    especies.value = await listEspecies()
    if (especies.value.length) formEntrada.value.id_especie = especies.value[0].id
  } catch {
    /* secundário */
  }
  await carregar()
})

function abrirEntradaSementes() {
  if (!podeEditar.value) return
  modalEntrada.value = true
}

function abrirCadastroInsumo() {
  if (!podeEditar.value) return
  modoInsumoForm.value = 'cadastro'
  insumoEditandoId.value = null
  formInsumo.value = formInsumoVazio()
  erroModal.value = ''
  modalInsumoForm.value = true
  nextTick().then(rebaseInsumo)
}

function abrirEditarInsumo(insumo) {
  if (!podeEditar.value) return
  modoInsumoForm.value = 'editar'
  insumoEditandoId.value = insumo.id
  formInsumo.value = {
    nome: insumo.nome,
    tipo: insumo.tipo,
    unidade_medida: insumo.unidade_medida || unidadeDefaultTipo(insumo.tipo),
    descricao: insumo.descricao || '',
    fornecedor: insumo.fornecedor || '',
    estoque_minimo: insumo.estoque_minimo ?? 0,
    estoque_maximo: insumo.estoque_maximo ?? null,
    quantidade_inicial: null,
    valor_compra: null,
  }
  erroModal.value = ''
  modalInsumoForm.value = true
  nextTick().then(rebaseInsumo)
}

function fecharInsumoForm() {
  overlayInsumo.resetOverlayPress()
  requestCloseInsumo()
}

function fecharEntrada() {
  overlayEntrada.resetOverlayPress()
  requestCloseEntrada()
}

async function salvarInsumoForm() {
  erroModal.value = ''
  if (modoInsumoForm.value === 'cadastro' && formInsumo.value.quantidade_inicial > 0) {
    if (!formInsumo.value.valor_compra || formInsumo.value.valor_compra <= 0) {
      erroModal.value = 'Informe o valor total da NF na entrada inicial.'
      return
    }
  }
  salvando.value = true
  try {
    await runWithLoading(async () => {
      if (modoInsumoForm.value === 'editar') {
        await updateInsumo(insumoEditandoId.value, {
          nome: formInsumo.value.nome.trim(),
          descricao: formInsumo.value.descricao?.trim() || null,
          unidade_medida: formInsumo.value.unidade_medida,
          fornecedor: formInsumo.value.fornecedor?.trim() || null,
          estoque_minimo: formInsumo.value.estoque_minimo ?? 0,
          estoque_maximo: formInsumo.value.estoque_maximo || null,
        })
      } else {
        const ins = await createInsumo({
          nome: formInsumo.value.nome.trim(),
          tipo: formInsumo.value.tipo,
          descricao: formInsumo.value.descricao?.trim() || null,
          unidade_medida: formInsumo.value.unidade_medida,
          fornecedor: formInsumo.value.fornecedor?.trim() || null,
          estoque_minimo: formInsumo.value.estoque_minimo ?? 0,
          estoque_maximo: formInsumo.value.estoque_maximo || null,
          quantidade_estoque: 0,
        })
        if (formInsumo.value.quantidade_inicial > 0) {
          await registrarMovimentacaoInsumo(ins.id, {
            tipo: 'entrada',
            quantidade: formInsumo.value.quantidade_inicial,
            valor_total: formInsumo.value.valor_compra,
            data_movimento: new Date().toISOString().slice(0, 10),
            status_pagamento: formInsumo.value.status_pagamento || 'PAGO',
            observacao: 'Entrada inicial',
          })
        }
      }
      sairSemConfirmarInsumo()
      guiaAtiva.value = 'insumos'
      await carregar()
    }, 'Salvando insumo…')
  } catch (e) {
    erroModal.value = e.response?.data?.detail || 'Erro ao salvar insumo.'
  } finally {
    salvando.value = false
  }
}

async function salvarEntrada() {
  erroModal.value = ''
  salvando.value = true
  try {
    await runWithLoading(async () => {
      await entradaSementesArmazem(formEntrada.value)
      sairSemConfirmarEntrada()
      guiaAtiva.value = 'sementes'
      await carregar()
    }, 'Registrando entrada…')
  } catch (e) {
    erroModal.value = e.response?.data?.detail || 'Erro ao registrar entrada.'
  } finally {
    salvando.value = false
  }
}

function abrirMov(insumo, tipo) {
  if (!podeEditar.value) return
  insumoSelecionado.value = insumo
  formMov.value = {
    tipo,
    quantidade: 1,
    valor_total: null,
    data_movimento: new Date().toISOString().slice(0, 10),
    motivo: tipo === 'saida' ? 'uso_sementeira' : 'uso_sementeira',
    observacao_extra: '',
  }
  erroModal.value = ''
  modalMov.value = true
  nextTick().then(rebaseMov)
}

function montarObservacaoMov() {
  const partes = []
  if (formMov.value.tipo === 'saida') {
    const m = MOTIVOS_SAIDA.find((x) => x.value === formMov.value.motivo)
    if (m) partes.push(m.label)
  }
  if (formMov.value.observacao_extra?.trim()) {
    partes.push(formMov.value.observacao_extra.trim())
  }
  return partes.length ? partes.join(' — ') : undefined
}

function fecharMov() {
  overlayMov.resetOverlayPress()
  requestCloseMov()
}

async function salvarMov() {
  erroModal.value = ''
  if (formMov.value.tipo === 'entrada' && entradaExigeValor.value) {
    if (!formMov.value.valor_total || formMov.value.valor_total <= 0) {
      erroModal.value = 'Informe o valor total da NF — necessário para o preço médio (CMV).'
      return
    }
  }
  salvando.value = true
  try {
    await runWithLoading(async () => {
      const payload = {
        tipo: formMov.value.tipo,
        quantidade: formMov.value.quantidade,
        data_movimento: formMov.value.data_movimento,
        observacao: montarObservacaoMov(),
      }
      if (formMov.value.tipo === 'entrada' && formMov.value.valor_total != null) {
        payload.valor_total = formMov.value.valor_total
        payload.status_pagamento = formMov.value.status_pagamento || 'PAGO'
      }
      await registrarMovimentacaoInsumo(insumoSelecionado.value.id, payload)
      sairSemConfirmarMov()
      await carregar()
    }, 'Registrando movimentação…')
  } catch (e) {
    const d = e.response?.data?.detail
    erroModal.value = typeof d === 'string' ? d : 'Erro na movimentação.'
  } finally {
    salvando.value = false
  }
}
</script>

<style scoped>
.secao-titulo-wrap,
.secao-header-flex {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
  width: 100%;
}

.secao-titulo {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.secao-sub {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.guia-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.25rem;
  height: 1.25rem;
  padding: 0 0.35rem;
  margin-left: 0.35rem;
  font-size: 0.6875rem;
  font-weight: 700;
  background: var(--color-primary-subtle);
  color: var(--color-primary-700);
  border-radius: var(--radius-full);
}

.guia.ativa .guia-badge {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.text-muted {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  font-weight: 400;
}

.field-hint {
  font-size: 0.8125rem;
  font-weight: 400;
  color: var(--color-text-muted);
}

.insumo-desc {
  display: block;
  font-size: 0.75rem;
  margin-top: 0.15rem;
}

code {
  font-size: 0.8125rem;
  color: var(--color-primary-700);
  background: var(--color-primary-subtle);
  padding: 0.15rem 0.4rem;
  border-radius: var(--radius-sm);
}

.estoque-modal--wide {
  max-width: 36rem;
}

.form-label--full {
  grid-column: 1 / -1;
}

.insumo-preview-pu {
  margin: 0;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.insumo-preview-pu strong {
  color: var(--color-primary-700);
}
</style>
