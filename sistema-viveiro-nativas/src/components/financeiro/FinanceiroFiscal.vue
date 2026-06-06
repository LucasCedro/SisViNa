<template>
  <div class="fiscal-cockpit">
    <aside class="fiscal-aviso">
      <strong>Parâmetros fiscais — responsabilidade do contador</strong>
      <p>
        O SisViNa parametriza a <strong>NF-e de venda de mudas</strong> (CFOP, CSOSN, origem, DIFAL, textos legais).
        <strong>Não substitui</strong> SPED Fiscal, EFD Contribuições, DAS, guias de ICMS importação nem escrituração contábil —
        você continua usando seus sistemas habituais para obrigações acessórias.
      </p>
      <p class="fiscal-sn">
        <strong>Simples Nacional:</strong> ICMS das vendas domésticas recolhe via CSOSN + DAS unificado.
        Exceções que o contador parametriza aqui: <em>DIFAL</em> (interestadual + consumidor final) e
        <em>ICMS de importação</em> (mudas de origem estrangeira — guia/DAS específico).
      </p>
      <p class="fiscal-links">
        <a href="https://doc.focusnfe.com.br/reference/cfop" target="_blank" rel="noopener">Tabela CFOP (Focus)</a>
        ·
        <a href="https://campos.focusnfe.com.br/nfe/NotaFiscalXML.html" target="_blank" rel="noopener">Campos NF-e 4.00</a>
      </p>
    </aside>

    <section v-if="!carregando" class="fiscal-card fiscal-simulador">
      <h3>Simulador — qual regra vai na NF-e?</h3>
      <p class="hint">
        Teste antes de ativar regras. Usa o emitente cadastrado + matriz ativa. Não calcula imposto a recolher — só mostra parametrização.
      </p>
      <div class="field-row sim-row">
        <label class="field">
          UF destino
          <input v-model="sim.uf_destino" maxlength="2" placeholder="SP" @input="sim.uf_destino = sim.uf_destino.toUpperCase()" />
        </label>
        <label class="field">
          Tipo cliente
          <select v-model="sim.tipo_cliente">
            <option value="PF">PF</option>
            <option value="PJ">PJ</option>
          </select>
        </label>
        <label class="field">
          Tipo operação
          <select v-model="sim.tipo_operacao">
            <option value="domestica">Doméstica (nacional)</option>
            <option value="importacao">Importação SN</option>
            <option value="exterior">Exterior</option>
          </select>
        </label>
        <button type="button" class="btn btn-secondary" :disabled="simulando" @click="rodarSimulador">
          {{ simulando ? '…' : 'Simular' }}
        </button>
      </div>
      <aside v-if="simResultado" class="sim-result" :class="{ 'sim-result--erro': !simResultado.encontrada }">
        <p><strong>{{ simResultado.operacao }}</strong> · tipo {{ labelTipoOp(simResultado.tipo_operacao) }}</p>
        <p>{{ simResultado.mensagem }}</p>
        <p v-if="simResultado.encontrada">
          CFOP {{ simResultado.cfop_resolvido }} · CSOSN {{ simResultado.regra?.csosn }}
          <span v-if="simResultado.icms_origem"> · orig {{ simResultado.icms_origem }}</span>
        </p>
        <p v-if="simResultado.tributacao_resumo" class="sim-trib">{{ simResultado.tributacao_resumo }}</p>
      </aside>
    </section>

    <p v-if="erro" class="alert-erro">{{ erro }}</p>
    <p v-if="carregando" class="status-msg">Carregando…</p>

    <section v-else class="fiscal-grid">
      <div class="fiscal-card">
        <h3>Regras fiscais (matriz)</h3>
        <p class="hint">NCM + UF + tipo cliente + tipo operação → uma regra. Ordem menor = prioridade.</p>

        <table class="tabela" v-if="regras.length">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Operação</th>
              <th>NCM</th>
              <th>UF</th>
              <th>CFOP</th>
              <th>CSOSN</th>
              <th>Tributação</th>
              <th>Ativo</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in regras" :key="r.id" :class="{ 'linha-inativa': !r.ativo }">
              <td>
                <strong>{{ labelRegra(r) }}</strong>
                <span v-if="!r.nome" class="tag-legado" title="Regra seed sem nome — edite e salve">legado</span>
              </td>
              <td><span class="tag-op" :class="'tag-op--' + (r.tipo_operacao || 'domestica')">{{ labelTipoOp(r.tipo_operacao) }}</span></td>
              <td>{{ r.ncm }}</td>
              <td>{{ r.uf_origem }}→{{ r.uf_destino }}</td>
              <td>{{ r.cfop_base }}{{ r.ajustar_cfop_por_uf ? '*' : '' }}</td>
              <td>{{ r.csosn }}</td>
              <td class="col-trib">{{ resumoTrib(r) }}</td>
              <td>
                <span class="tag-ativo" :class="r.ativo ? 'tag-ativo--sim' : 'tag-ativo--nao'">
                  {{ r.ativo ? 'Sim' : 'Não' }}
                </span>
              </td>
              <td>
                <button type="button" class="btn-link" @click="editar(r)">Editar</button>
                <button
                  v-if="podeEditar"
                  type="button"
                  class="btn-link btn-link--danger"
                  @click="excluir(r)"
                >
                  Excluir
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty">Nenhuma regra cadastrada. Sem regra ativa, a NF-e não emite.</p>

        <button v-if="podeEditar" type="button" class="btn btn-primary fiscal-card__cta" @click="novaRegra">+ Nova regra</button>
      </div>

      <div v-if="formAberto" class="fiscal-card fiscal-form">
        <h3>{{ form.id ? 'Editar regra' : 'Nova regra' }}</h3>
        <div v-if="podeEditar" class="fiscal-templates">
          <span class="templates-label">Modelos rápidos:</span>
          <button type="button" class="btn btn-secondary btn-sm" @click="aplicarTemplate('domestica')">Doméstica</button>
          <button type="button" class="btn btn-secondary btn-sm" @click="aplicarTemplate('difal')">DIFAL interest.</button>
          <button type="button" class="btn btn-secondary btn-sm" @click="aplicarTemplate('importacao')">Importação SN</button>
        </div>
        <form @submit.prevent="salvar">
          <label class="field">
            <span class="field-label">
              Nome (rótulo)
              <FieldHelp rotulo="Nome" :texto="ajuda.nome" />
            </span>
            <input v-model="form.nome" placeholder="Ex.: GO interno — muda" />
          </label>
          <div class="field-row">
            <label class="field">
              <span class="field-label">
                Descrição produto (NF-e)
                <FieldHelp rotulo="Descrição" :texto="ajuda.descricao_produto" />
              </span>
              <input v-model="form.descricao_produto" placeholder="Muda de planta" />
            </label>
            <label class="field">
              <span class="field-label">
                Natureza operação
                <FieldHelp rotulo="Natureza" :texto="ajuda.natureza_operacao" />
              </span>
              <input v-model="form.natureza_operacao" placeholder="Venda de mudas" />
            </label>
          </div>
          <div class="field-row">
            <label class="field">
              <span class="field-label">
                NCM
                <FieldHelp rotulo="NCM" :texto="ajuda.ncm" />
              </span>
              <input v-model="form.ncm" required maxlength="8" />
            </label>
            <label class="field">
              <span class="field-label">
                UF origem
                <FieldHelp rotulo="UF origem" :texto="ajuda.uf_origem" />
              </span>
              <input v-model="form.uf_origem" maxlength="2" required />
            </label>
            <label class="field">
              <span class="field-label">
                UF destino
                <FieldHelp rotulo="UF destino" :texto="ajuda.uf_destino" />
              </span>
              <input v-model="form.uf_destino" maxlength="80" required placeholder="INTERESTADUAL, *, SP ou SP,MG" />
            </label>
          </div>
          <div class="field-row">
            <label class="field">
              <span class="field-label">
                Tipo operação
                <FieldHelp rotulo="Tipo operação" :texto="ajuda.tipo_operacao" />
              </span>
              <select v-model="form.tipo_operacao">
                <option value="domestica">Doméstica (nacional)</option>
                <option value="importacao">Importação SN (origem estrangeira)</option>
                <option value="exterior">Exterior (exportação)</option>
              </select>
            </label>
            <label class="field">
              <span class="field-label">
                ICMS origem (tag orig)
                <FieldHelp rotulo="ICMS origem" :texto="ajuda.icms_origem" />
              </span>
              <select v-model.number="form.icms_origem" :disabled="form.tipo_operacao === 'domestica'">
                <option :value="0">0 — Nacional</option>
                <option :value="1">1 — Importação direta</option>
                <option :value="2">2 — Adquirida mercado interno</option>
                <option :value="3">3 — Nacional conteúdo import. &gt; 40%</option>
                <option :value="4">4 — Nacional processos produtivos básicos</option>
                <option :value="5">5 — Nacional conteúdo import. ≤ 40%</option>
                <option :value="6">6 — Estrangeira importação direta s/ similar</option>
                <option :value="7">7 — Estrangeira mercado interno s/ similar</option>
                <option :value="8">8 — Nacional conteúdo import. &gt; 70%</option>
              </select>
            </label>
            <label v-if="form.tipo_operacao === 'importacao'" class="field">
              <span class="field-label">
                Alíq. ICMS importação ref. (%)
                <FieldHelp rotulo="ICMS importação" :texto="ajuda.aliquota_icms_importacao" />
              </span>
              <input
                v-model.number="form.aliquota_icms_importacao"
                type="number"
                min="0"
                max="100"
                step="0.01"
                placeholder="Ex.: 4.00"
              />
            </label>
          </div>
          <p v-if="form.tipo_operacao === 'importacao'" class="hint hint--inline">
            ICMS de importação no Simples é recolhido fora do DAS unificado — informe fundamento legal e alíquota de referência.
            Na venda, marque «origem importada» para usar esta regra.
          </p>
          <div class="field-row">
            <label class="field">
              <span class="field-label">
                Tipo cliente
                <FieldHelp rotulo="Tipo cliente" :texto="ajuda.tipo_cliente" />
              </span>
              <select v-model="form.tipo_cliente">
                <option value="ANY">Qualquer</option>
                <option value="PF">PF</option>
                <option value="PJ">PJ</option>
              </select>
            </label>
            <label class="field">
              <span class="field-label">
                CFOP (contador)
                <FieldHelp rotulo="CFOP" :texto="ajuda.cfop_base" />
              </span>
              <input v-model="form.cfop_base" required maxlength="4" placeholder="5101" />
            </label>
            <label class="field chk">
              <input v-model="form.ajustar_cfop_por_uf" type="checkbox" />
              <span class="field-label">
                Ajustar 5↔6 por UF
                <FieldHelp rotulo="Ajustar CFOP" :texto="ajuda.ajustar_cfop_por_uf" />
              </span>
            </label>
          </div>
          <div class="field-row">
            <label class="field">
              <span class="field-label">
                CSOSN
                <FieldHelp rotulo="CSOSN" :texto="ajuda.csosn" />
              </span>
              <input v-model="form.csosn" maxlength="3" required />
            </label>
            <label class="field">
              <span class="field-label">
                Ordem
                <FieldHelp rotulo="Ordem" :texto="ajuda.ordem" />
              </span>
              <input v-model.number="form.ordem" type="number" />
            </label>
            <label class="field chk">
              <input v-model="form.ativo" type="checkbox" />
              <span class="field-label">
                Regra ativa
                <FieldHelp rotulo="Ativo" :texto="ajuda.ativo" />
              </span>
            </label>
          </div>
          <label class="field chk">
            <input v-model="form.isento_icms" type="checkbox" />
            <span class="field-label">
              Isento ICMS
              <FieldHelp rotulo="Isento ICMS" :texto="ajuda.isento_icms" />
            </span>
          </label>
          <label class="field">
            <span class="field-label">
              Redução BC ICMS (%)
              <FieldHelp rotulo="Redução BC" :texto="ajuda.reducao_bc" />
            </span>
            <input
              v-model.number="form.reducao_bc_icms_percent"
              type="number"
              min="0"
              max="100"
              step="0.01"
              placeholder="Ex.: 60 (Conv. 100/97)"
            />
          </label>
          <label class="field" :class="{ 'field--required': form.isento_icms || reducaoAtiva }">
            <span class="field-label">
              Fundamento legal
              <FieldHelp rotulo="Fundamento legal" :texto="ajuda.fundamento_legal" />
            </span>
            <textarea
              v-model="form.fundamento_legal"
              rows="2"
              :placeholder="placeholderFundamento"
            />
          </label>
          <label class="field">
            <span class="field-label">
              Informações complementares (NF-e)
              <FieldHelp rotulo="Inf. complementares" :texto="ajuda.informacoes_complementares" />
            </span>
            <textarea v-model="form.informacoes_complementares" rows="2" />
          </label>
          <div class="field-row">
            <label class="field">
              <span class="field-label">
                PIS (sit. trib.)
                <FieldHelp rotulo="PIS" :texto="ajuda.pis" />
              </span>
              <input v-model="form.pis_situacao_tributaria" maxlength="3" />
            </label>
            <label class="field">
              <span class="field-label">
                COFINS
                <FieldHelp rotulo="COFINS" :texto="ajuda.cofins" />
              </span>
              <input v-model="form.cofins_situacao_tributaria" maxlength="3" />
            </label>
            <label class="field">
              <span class="field-label">
                Local destino
                <FieldHelp rotulo="Local destino" :texto="ajuda.local_destino" />
              </span>
              <select v-model.number="form.local_destino">
                <option :value="null">Automático (UF)</option>
                <option :value="1">1 — Interna</option>
                <option :value="2">2 — Interestadual</option>
                <option :value="3">3 — Exterior</option>
              </select>
            </label>
          </div>
          <label class="field chk">
            <input v-model="form.aplicar_difal" type="checkbox" />
            <span class="field-label">
              Aplicar DIFAL
              <FieldHelp rotulo="DIFAL" :texto="ajuda.difal" />
            </span>
          </label>
          <p class="hint hint--inline">
            <strong>Alíquotas %:</strong> só na NF-e quando <em>DIFAL</em> (interestadual + consumidor final) ou
            <em>importação SN</em> (referência). Vendas domésticas usam CSOSN — ICMS via DAS unificado.
          </p>
          <div v-if="form.aplicar_difal" class="field-row">
            <label class="field">
              <span class="field-label">
                Alíq. inter %
                <FieldHelp rotulo="Alíquota inter" :texto="ajuda.aliq_inter" />
              </span>
              <input v-model.number="form.aliquota_icms_inter" type="number" step="0.01" />
            </label>
            <label class="field">
              <span class="field-label">
                Alíq. intra destino %
                <FieldHelp rotulo="Alíquota intra" :texto="ajuda.aliq_intra" />
              </span>
              <input v-model.number="form.aliquota_icms_intra" type="number" step="0.01" />
            </label>
          </div>
          <label class="field">
            <span class="field-label">
              Observação interna (contador)
              <FieldHelp rotulo="Observação" :texto="ajuda.observacao" />
            </span>
            <textarea v-model="form.observacao" rows="2" placeholder="Notas do contador — não vai na NF-e" />
          </label>
          <div class="fiscal-form__actions">
            <button type="button" class="btn btn-secondary" @click="fecharForm">Cancelar</button>
            <button v-if="podeEditar" type="submit" class="btn btn-primary">Salvar regra</button>
          </div>
        </form>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import FieldHelp from '@/components/contabilidade/FieldHelp.vue'
import { AJUDA_REGRA_FISCAL, LABEL_TIPO_OPERACAO, labelRegraFiscal, resumoTributacaoRegra } from '@/constants/fiscalHelp'
import {
  listRegrasFiscais,
  createRegraFiscal,
  updateRegraFiscal,
  deleteRegraFiscal,
  previewRegraFiscal,
} from '@/services/fiscal'

defineProps({
  podeEditar: { type: Boolean, default: false },
})

const ajuda = AJUDA_REGRA_FISCAL
const labelRegra = labelRegraFiscal
const resumoTrib = resumoTributacaoRegra
const labelTipoOp = (t) => LABEL_TIPO_OPERACAO[t] || t || 'Doméstica'

const carregando = ref(true)
const simulando = ref(false)
const sim = ref({ uf_destino: 'SP', tipo_cliente: 'PF', tipo_operacao: 'domestica' })
const simResultado = ref(null)
const erro = ref(null)
const regras = ref([])
const formAberto = ref(false)
const form = ref(regraVazia())

const reducaoAtiva = computed(
  () => form.value.reducao_bc_icms_percent != null && Number(form.value.reducao_bc_icms_percent) > 0
)

const placeholderFundamento = computed(() => {
  if (form.value.isento_icms) {
    return 'Obrigatório — ex.: RCTE-GO An. IX art. 7º h) — isenção de ICMS'
  }
  if (reducaoAtiva.value) {
    return 'Obrigatório — ex.: Conv. ICMS 100/97 — redução 60% BC interestadual'
  }
  return 'Dispositivo legal quando houver isenção ou redução de BC'
})

function regraVazia() {
  return {
    id: null,
    nome: '',
    ncm: '06029090',
    uf_origem: 'GO',
    uf_destino: 'INTERESTADUAL',
    tipo_cliente: 'ANY',
    cfop_base: '5101',
    ajustar_cfop_por_uf: true,
    csosn: '400',
    descricao_produto: 'Muda de planta',
    natureza_operacao: 'Venda de mudas',
    isento_icms: false,
    reducao_bc_icms_percent: null,
    fundamento_legal: '',
    informacoes_complementares: '',
    pis_situacao_tributaria: '',
    cofins_situacao_tributaria: '',
    local_destino: null,
    aplicar_difal: false,
    aliquota_icms_inter: 12,
    aliquota_icms_intra: 18,
    tipo_operacao: 'domestica',
    icms_origem: 0,
    aliquota_icms_importacao: null,
    observacao: '',
    ativo: true,
    ordem: 0,
  }
}

async function carregar() {
  carregando.value = true
  erro.value = null
  try {
    regras.value = await listRegrasFiscais()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha ao carregar regras fiscais.'
  } finally {
    carregando.value = false
  }
}

function novaRegra() {
  form.value = regraVazia()
  formAberto.value = true
}

function regraParaForm(r) {
  const base = regraVazia()
  return {
    ...base,
    ...r,
    id: r.id,
    nome: r.nome?.trim() || labelRegraFiscal(r),
    descricao_produto: r.descricao_produto ?? base.descricao_produto,
    natureza_operacao: r.natureza_operacao ?? base.natureza_operacao,
    ajustar_cfop_por_uf: r.ajustar_cfop_por_uf ?? true,
    isento_icms: r.isento_icms ?? false,
    aplicar_difal: r.aplicar_difal ?? false,
    ativo: r.ativo ?? false,
    ordem: r.ordem ?? 0,
    reducao_bc_icms_percent: r.reducao_bc_icms_percent ?? null,
    aliquota_icms_inter: r.aliquota_icms_inter ?? (r.aplicar_difal ? 12 : null),
    aliquota_icms_intra: r.aliquota_icms_intra ?? (r.aplicar_difal ? 18 : null),
    fundamento_legal: r.fundamento_legal ?? '',
    informacoes_complementares: r.informacoes_complementares ?? '',
    pis_situacao_tributaria: r.pis_situacao_tributaria ?? '',
    cofins_situacao_tributaria: r.cofins_situacao_tributaria ?? '',
    observacao: r.observacao ?? '',
    local_destino: r.local_destino ?? null,
    tipo_operacao: r.tipo_operacao ?? 'domestica',
    icms_origem: r.icms_origem ?? (r.tipo_operacao === 'importacao' ? 1 : 0),
    aliquota_icms_importacao: r.aliquota_icms_importacao ?? null,
  }
}

function aplicarTemplate(kind) {
  const base = regraVazia()
  if (kind === 'domestica') {
    form.value = {
      ...base,
      nome: 'Venda interna — muda nacional',
      uf_destino: 'INTERNA',
      tipo_operacao: 'domestica',
      icms_origem: 0,
      cfop_base: '5101',
      csosn: '400',
    }
  } else if (kind === 'difal') {
    form.value = {
      ...base,
      nome: 'Interestadual — DIFAL consumidor final',
      uf_destino: 'INTERESTADUAL',
      tipo_operacao: 'domestica',
      cfop_base: '6101',
      aplicar_difal: true,
      aliquota_icms_inter: 12,
      aliquota_icms_intra: 18,
    }
  } else if (kind === 'importacao') {
    form.value = {
      ...base,
      nome: 'Mudas origem importada — SN',
      uf_destino: 'INTERNA',
      tipo_operacao: 'importacao',
      icms_origem: 1,
      aliquota_icms_importacao: 4,
      cfop_base: '5101',
      csosn: '400',
      descricao_produto: 'Muda de planta — origem estrangeira',
      fundamento_legal:
        'ICMS importação — Simples Nacional: recolhimento conforme orientação contábil (validar vigência).',
      informacoes_complementares: 'Origem mercadoria estrangeira (icms_origem=1).',
      ativo: false,
    }
  }
}

async function rodarSimulador() {
  const uf = (sim.value.uf_destino || '').trim()
  if (sim.value.tipo_operacao !== 'exterior' && uf.length !== 2) {
    alert('Informe UF destino com 2 letras (ou escolha Exterior).')
    return
  }
  simulando.value = true
  try {
    simResultado.value = await previewRegraFiscal({
      uf_destino: sim.value.tipo_operacao === 'exterior' ? 'EX' : uf,
      tipo_cliente: sim.value.tipo_cliente,
      tipo_operacao: sim.value.tipo_operacao,
    })
  } catch (e) {
    simResultado.value = { encontrada: false, mensagem: e.response?.data?.detail || 'Erro na simulação.' }
  } finally {
    simulando.value = false
  }
}

function editar(r) {
  form.value = regraParaForm(r)
  formAberto.value = true
}

function fecharForm() {
  formAberto.value = false
}

async function salvar() {
  const payload = { ...form.value }
  delete payload.id
  try {
    if (form.value.id) {
      await updateRegraFiscal(form.value.id, payload)
    } else {
      await createRegraFiscal(payload)
    }
    fecharForm()
    await carregar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar regra.')
  }
}

async function excluir(r) {
  if (!confirm(`Excluir regra "${r.nome || r.id}"?`)) return
  try {
    await deleteRegraFiscal(r.id)
    await carregar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir.')
  }
}

onMounted(carregar)
defineExpose({ carregar })
</script>

<style scoped>
.fiscal-aviso {
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-attention-bg);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
  font-size: 0.9375rem;
}
.fiscal-aviso p {
  margin: 0.35rem 0 0;
}
.fiscal-links a {
  color: var(--color-primary);
  font-weight: 600;
}
.fiscal-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}
.fiscal-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}
.fiscal-card h3 {
  margin: 0 0 var(--spacing-md);
}
.hint {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin: 0 0 var(--spacing-md);
}
.tabela {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  margin-bottom: var(--spacing-md);
}
.tabela th,
.tabela td {
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border-subtle);
  text-align: left;
}
.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-weight: 600;
  margin-right: 0.5rem;
}
.btn-link--danger {
  color: var(--color-error);
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: var(--spacing-md);
  font-size: 0.875rem;
  font-weight: 600;
  position: relative;
}
.field-label {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.15rem;
  position: relative;
}
.field--required .field-label::after {
  content: ' *';
  color: var(--color-error);
}
.field input,
.field select,
.field textarea {
  font-weight: 400;
  padding: 0.45rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}
.field-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--spacing-md);
}
.field.chk {
  flex-direction: row;
  align-items: center;
  font-weight: 500;
  flex-wrap: wrap;
}
.fiscal-card__cta {
  margin-top: var(--spacing-sm);
}
.fiscal-form__actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  padding-top: var(--spacing-md);
  margin-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border-subtle);
}
.empty {
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-md);
}
.alert-erro {
  color: var(--color-error);
}
.linha-inativa {
  opacity: 0.72;
}
.tag-legado {
  display: inline-block;
  margin-left: 0.35rem;
  font-size: 0.625rem;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  background: var(--color-border-subtle);
  font-weight: 600;
  color: var(--color-text-muted);
}
.col-trib {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  max-width: 11rem;
}
.tag-ativo {
  font-size: 0.75rem;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-weight: 600;
}
.tag-ativo--sim {
  background: #d1e7dd;
  color: #0f5132;
}
.tag-ativo--nao {
  background: #e2e3e5;
  color: #41464b;
}
.hint--inline {
  margin: -0.35rem 0 var(--spacing-md);
  padding: 0.5rem 0.65rem;
  background: var(--color-surface-muted);
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
}
.fiscal-sn {
  margin-top: 0.5rem;
  font-size: 0.875rem;
}
.fiscal-simulador {
  margin-bottom: var(--spacing-lg);
}
.sim-row {
  align-items: end;
}
.sim-result {
  margin-top: var(--spacing-md);
  padding: 0.65rem 0.75rem;
  border-radius: var(--radius-sm);
  background: #cff4fc;
  border: 1px solid #0dcaf0;
  font-size: 0.875rem;
}
.sim-result--erro {
  background: #fff3cd;
  border-color: #ffc107;
}
.sim-result p {
  margin: 0.2rem 0;
}
.sim-trib {
  font-weight: 600;
}
.fiscal-templates {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
  margin-bottom: var(--spacing-md);
}
.templates-label {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  margin-right: 0.25rem;
}
.btn-sm {
  padding: 0.25rem 0.55rem;
  font-size: 0.8125rem;
}
.tag-op {
  font-size: 0.6875rem;
  padding: 0.12rem 0.4rem;
  border-radius: 4px;
  font-weight: 700;
  white-space: nowrap;
}
.tag-op--domestica {
  background: #e7f1ff;
  color: #084298;
}
.tag-op--importacao {
  background: #fff3cd;
  color: #664d03;
}
.tag-op--exterior {
  background: #d1e7dd;
  color: #0f5132;
}
</style>
