<template>
  <div
    v-if="aberto"
    class="wizard-overlay"
    @pointerdown.self="onOverlayPointerDown"
    @pointerup.self="onOverlayPointerUp"
    @pointercancel.self="cancelarFechamentoOverlay"
  >
    <div class="wizard-card" role="dialog" aria-labelledby="wizard-titulo" @pointerdown="onModalPointerDown">
      <header class="wizard-header">
        <h2 id="wizard-titulo">{{ tituloEtapa }}</h2>
        <button type="button" class="btn-fechar" @click="fechar" aria-label="Fechar">×</button>
      </header>

      <div v-if="etapa === 'tipo'" class="wizard-body">
        <p class="wizard-hint">
          Áreas de <strong>produção</strong> entram no fluxo (semeadura, transferência).
          Demais itens aparecem só no croqui.
        </p>
        <h3 class="wizard-sub">Produção</h3>
        <div class="tipo-grid">
          <button
            v-for="item in CATALOGO_PRODUTIVO"
            :key="item.tipo"
            type="button"
            class="tipo-card"
            @click="escolherTipo(item.tipo)"
          >
            <span class="tipo-cor" :style="{ backgroundColor: item.corPadrao }" />
            <strong>{{ item.titulo }}</strong>
            <span class="tipo-desc">{{ item.descricao }}</span>
          </button>
        </div>
        <h3 class="wizard-sub">Infraestrutura</h3>
        <div class="tipo-grid">
          <button
            v-for="item in CATALOGO_VISUAL"
            :key="item.tipo"
            type="button"
            class="tipo-card"
            @click="escolherTipo(item.tipo)"
          >
            <span class="tipo-cor" :style="{ backgroundColor: item.corPadrao }" />
            <strong>{{ item.titulo }}</strong>
            <span class="tipo-desc">{{ item.descricao }}</span>
          </button>
        </div>
        <footer class="wizard-footer">
          <button type="button" class="btn-sec" @click="fechar">Cancelar</button>
        </footer>
      </div>

      <div v-else-if="etapa === 'canteiro'" class="wizard-body">
        <label class="field">
          Nome do canteiro
          <input v-model="form.nome" type="text" placeholder="Ex.: Canteiro A" />
        </label>
        <div class="field-row">
          <label class="field">
            Linhas
            <input v-model.number="form.linhas" type="number" min="1" max="20" />
          </label>
          <label class="field">
            Colunas
            <input v-model.number="form.colunas" type="number" min="1" max="20" />
          </label>
        </div>
        <p class="wizard-hint">Capacidade: <strong>{{ form.linhas * form.colunas }}</strong> mudas</p>
        <label class="field">
          Espécie (opcional)
          <select v-model="form.especieId" :disabled="carregandoEspecies">
            <option :value="null">— Sem espécie definida —</option>
            <option v-for="e in especies" :key="e.id" :value="e.id">
              {{ e.nome_popular || e.nome_cientifico }}
            </option>
          </select>
        </label>
        <PresetDimensoes :ativo-id="presetAtivo" @aplicar="aplicarPreset" />
        <div class="field-row">
          <label class="field">
            Largura real (m)
            <input v-model.number="form.metrosLargura" type="number" min="0.5" max="200" step="0.1" @input="presetAtivo = null" />
          </label>
          <label class="field">
            Comprimento real (m)
            <input v-model.number="form.metrosAltura" type="number" min="0.5" max="200" step="0.1" @input="presetAtivo = null" />
          </label>
        </div>
        <footer class="wizard-footer">
          <button type="button" class="btn-sec" @click="voltarTipo">Voltar</button>
          <button type="button" class="btn-prim" @click="confirmar">Adicionar ao mapa</button>
        </footer>
      </div>

      <div v-else-if="etapa === 'sementeira'" class="wizard-body">
        <label class="field">
          Nome da sementeira
          <input v-model="form.nome" type="text" placeholder="Ex.: Sementeira 1" />
        </label>
        <label class="field">
          Capacidade aproximada (mudas)
          <input v-model.number="form.capacidade" type="number" min="1" max="9999" />
        </label>
        <PresetDimensoes :ativo-id="presetAtivo" @aplicar="aplicarPreset" />
        <div class="field-row">
          <label class="field">
            Largura real (m)
            <input v-model.number="form.metrosLargura" type="number" min="0.5" max="200" step="0.1" @input="presetAtivo = null" />
          </label>
          <label class="field">
            Comprimento real (m)
            <input v-model.number="form.metrosAltura" type="number" min="0.5" max="200" step="0.1" @input="presetAtivo = null" />
          </label>
        </div>
        <footer class="wizard-footer">
          <button type="button" class="btn-sec" @click="voltarTipo">Voltar</button>
          <button type="button" class="btn-prim" @click="confirmar">Adicionar ao mapa</button>
        </footer>
      </div>

      <div v-else-if="etapa === 'rustificacao'" class="wizard-body">
        <label class="field">
          Nome da área
          <input v-model="form.nome" type="text" placeholder="Ex.: Rustificação norte" />
        </label>
        <label class="field">
          Capacidade aproximada (mudas)
          <input v-model.number="form.capacidade" type="number" min="1" max="9999" />
        </label>
        <PresetDimensoes
          :ativo-id="presetAtivo"
          hint="Rustificação costuma ser mais larga que longa."
          :presets="presetsRustificacao"
          @aplicar="aplicarPreset"
        />
        <div class="field-row">
          <label class="field">
            Largura real (m)
            <input v-model.number="form.metrosLargura" type="number" min="0.5" max="200" step="0.1" @input="presetAtivo = null" />
          </label>
          <label class="field">
            Comprimento real (m)
            <input v-model.number="form.metrosAltura" type="number" min="0.5" max="200" step="0.1" @input="presetAtivo = null" />
          </label>
        </div>
        <footer class="wizard-footer">
          <button type="button" class="btn-sec" @click="voltarTipo">Voltar</button>
          <button type="button" class="btn-prim" @click="confirmar">Adicionar ao mapa</button>
        </footer>
      </div>

      <div v-else-if="etapa === 'visual'" class="wizard-body">
        <label class="field">
          Nome da área
          <input v-model="form.nome" type="text" :placeholder="placeholderVisual" />
        </label>
        <div class="field-row">
          <label class="field">
            Largura real (m)
            <input v-model.number="form.metrosLargura" type="number" min="0.5" max="200" step="0.1" />
          </label>
          <label class="field">
            Comprimento real (m)
            <input v-model.number="form.metrosAltura" type="number" min="0.5" max="200" step="0.1" />
          </label>
        </div>
        <footer class="wizard-footer">
          <button type="button" class="btn-sec" @click="voltarTipo">Voltar</button>
          <button type="button" class="btn-prim" @click="confirmar">Adicionar ao mapa</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  CATALOGO_PRODUTIVO,
  CATALOGO_VISUAL,
  TIPOS_COMPONENTE,
} from '@/constants/viveiroComponentes'
import { listEspecies } from '@/services/especies'
import { useModalOverlayClose } from '@/composables/useModalOverlayClose'
import PresetDimensoes from './PresetDimensoes.vue'
import { METROS_PADRAO_PRODUTIVO, PRESETS_DIMENSAO } from '@/constants/viveiroDimensoes'

const props = defineProps({
  aberto: { type: Boolean, default: false },
})

const emit = defineEmits(['fechar', 'confirmar'])

const etapa = ref('tipo')
const especies = ref([])
const carregandoEspecies = ref(false)

const form = ref(criarFormPadrao())
const presetAtivo = ref(null)

const presetsRustificacao = PRESETS_DIMENSAO.filter((p) =>
  ['quad-10x8', 'quad-6x6', 'faixa-4x20'].includes(p.id)
)

const tituloEtapa = computed(() => {
  const map = {
    tipo: 'Adicionar área',
    canteiro: 'Novo canteiro',
    sementeira: 'Nova sementeira',
    rustificacao: 'Nova área de rustificação',
    visual: 'Nova área',
  }
  return map[etapa.value] || 'Adicionar área'
})

const placeholderVisual = computed(() => {
  const map = {
    [TIPOS_COMPONENTE.SEDE]: 'Ex.: Sede administrativa',
    [TIPOS_COMPONENTE.LAGO]: 'Ex.: Caixa d\'água',
    [TIPOS_COMPONENTE.GARAGEM]: 'Ex.: Garagem',
    [TIPOS_COMPONENTE.AREA_TRABALHO]: 'Ex.: Bancada de substrato',
  }
  return map[form.value.tipo] || 'Nome da área'
})

function criarFormPadrao() {
  return {
    tipo: null,
    nome: '',
    linhas: 4,
    colunas: 4,
    largura: 180,
    altura: 130,
    capacidade: 20,
    especieId: null,
    metrosLargura: null,
    metrosAltura: null,
  }
}

function aplicarPreset(preset) {
  form.value.metrosLargura = preset.largura
  form.value.metrosAltura = preset.altura
  presetAtivo.value = preset.id
}

watch(
  () => props.aberto,
  async (aberto) => {
    if (!aberto) return
    etapa.value = 'tipo'
    form.value = criarFormPadrao()
    presetAtivo.value = null
    if (especies.value.length) return
    carregandoEspecies.value = true
    try {
      especies.value = await listEspecies()
    } catch {
      especies.value = []
    } finally {
      carregandoEspecies.value = false
    }
  }
)

const NOMES_PADRAO = {
  [TIPOS_COMPONENTE.CANTEIRO]: 'Canteiro',
  [TIPOS_COMPONENTE.SEMENTEIRA]: 'Sementeira',
  [TIPOS_COMPONENTE.RUSTIFICACAO]: 'Área de rustificação',
  [TIPOS_COMPONENTE.SEDE]: 'Sede',
  [TIPOS_COMPONENTE.LAGO]: 'Lago / água',
  [TIPOS_COMPONENTE.GARAGEM]: 'Garagem',
  [TIPOS_COMPONENTE.AREA_TRABALHO]: 'Área de trabalho',
}

function escolherTipo(tipo) {
  const base = { ...criarFormPadrao(), tipo, nome: NOMES_PADRAO[tipo] || 'Área' }
  presetAtivo.value = null
  if (tipo === TIPOS_COMPONENTE.CANTEIRO) {
    form.value = {
      ...base,
      metrosLargura: METROS_PADRAO_PRODUTIVO.largura,
      metrosAltura: METROS_PADRAO_PRODUTIVO.altura,
    }
    presetAtivo.value = 'faixa-4x40'
    etapa.value = 'canteiro'
  } else if (tipo === TIPOS_COMPONENTE.SEMENTEIRA) {
    form.value = { ...base, metrosLargura: 6, metrosAltura: 24 }
    presetAtivo.value = 'faixa-6x24'
    etapa.value = 'sementeira'
  } else if (tipo === TIPOS_COMPONENTE.RUSTIFICACAO) {
    form.value = { ...base, metrosLargura: 10, metrosAltura: 8 }
    presetAtivo.value = 'quad-10x8'
    etapa.value = 'rustificacao'
  } else {
    form.value = base
    etapa.value = 'visual'
  }
}

function voltarTipo() {
  etapa.value = 'tipo'
  form.value = criarFormPadrao()
}

function fecharInterno() {
  emit('fechar')
}

const {
  onModalPointerDown,
  onOverlayPointerDown,
  onOverlayPointerUp,
  cancelarFechamentoOverlay,
  resetOverlayPress,
} = useModalOverlayClose(fecharInterno)

function fechar() {
  resetOverlayPress()
  fecharInterno()
}

function confirmar() {
  const f = form.value
  const nome = (f.nome || '').trim()
  if (!nome) {
    alert('Informe um nome para a área.')
    return
  }

  let especieNome = null
  if (f.especieId) {
    const esp = especies.value.find((e) => e.id === f.especieId)
    especieNome = esp?.nome_popular || esp?.nome_cientifico || null
  }

  emit('confirmar', {
    tipo: f.tipo,
    nome,
    linhas: f.linhas,
    colunas: f.colunas,
    largura: f.largura,
    altura: f.altura,
    metrosLargura: f.metrosLargura,
    metrosAltura: f.metrosAltura,
    capacidade: f.capacidade,
    especieId: f.especieId,
    especieNome,
  })
}
</script>

<style scoped>
.wizard-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.wizard-card {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.wizard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.wizard-header h2 {
  margin: 0;
  font-size: 1.125rem;
}

.btn-fechar {
  border: none;
  background: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: #6b7280;
}

.wizard-body {
  padding: 1rem 1.25rem;
}

.wizard-sub {
  margin: 1rem 0 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #6b7280;
}

.wizard-sub:first-of-type {
  margin-top: 0;
}

.wizard-hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 0.75rem;
}

.tipo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.tipo-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
}

.tipo-card:hover {
  border-color: var(--color-primary, #4a7c2a);
  background: #f9fafb;
}

.tipo-cor {
  width: 100%;
  height: 6px;
  border-radius: 3px;
}

.tipo-desc {
  font-size: 0.75rem;
  color: #6b7280;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.field input,
.field select {
  padding: 0.5rem 0.65rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-family: inherit;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.wizard-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-sec,
.btn-prim {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-family: inherit;
  cursor: pointer;
  border: 1px solid #d1d5db;
  background: #fff;
}

.btn-prim {
  background: var(--color-primary, #4a7c2a);
  color: #fff;
  border-color: transparent;
}
</style>
