<template>
  <div class="layout-editor">
    <header class="editor-header">
      <div class="editor-header__brand">
        <button type="button" class="btn-back" @click="emit('voltar')">
          <span aria-hidden="true">←</span> Voltar
        </button>
        <div class="editor-header__titles">
          <h1 class="editor-header__title">Editor da planta</h1>
          <p class="editor-header__sub">Arraste áreas · marque várias na lista · snap ao soltar</p>
        </div>
      </div>
      <div class="editor-header__actions">
        <button type="button" class="btn-add" @click="wizardAberto = true">+ Adicionar área</button>
        <div class="viveiro-toolbar__group" role="group" aria-label="Zoom">
          <button type="button" class="viveiro-toolbar__btn" @click="ajustarZoom(-0.15)">−</button>
          <span class="viveiro-toolbar__label">{{ Math.round(zoom * 100) }}%</span>
          <button type="button" class="viveiro-toolbar__btn" @click="ajustarZoom(0.15)">+</button>
          <button type="button" class="viveiro-toolbar__btn viveiro-toolbar__btn--text" @click="enquadrarTudo">Enquadrar</button>
          <button type="button" class="viveiro-toolbar__btn viveiro-toolbar__btn--text" @click="zoomUmParaUm">100%</button>
        </div>
        <button type="button" class="btn-save" :disabled="salvando" @click="salvarEVoltar">
          {{ salvando ? 'Salvando…' : 'Salvar' }}
        </button>
      </div>
    </header>

    <p v-if="erroSalvar" class="erro-bar" role="alert">{{ erroSalvar }}</p>

    <div class="editor-main">
      <div
        ref="canvasEl"
        class="canvas viveiro-map-canvas-bg"
        :class="{ 'canvas--panning': panning, 'canvas--dragging': !!dragCampo, 'canvas--space-pan': spacePan }"
        @wheel.prevent="onWheel"
        @pointerdown="onViewportPointerDown"
        @dblclick="onViewportDblClick"
      >
        <div class="canvas-stage">
          <div class="canvas-inner" :style="canvasInnerStyle">
            <svg
              ref="svgEl"
              class="mapa-svg"
              :width="svgFrame.w"
              :height="svgFrame.h"
              :viewBox="svgViewBoxAttr"
            >
              <defs>
                <pattern id="editor-grid-minor" width="24" height="24" patternUnits="userSpaceOnUse">
                  <path d="M 24 0 L 0 0 0 24" fill="none" :stroke="VIVEIRO_MAP_GRID.fine" stroke-width="0.5" />
                </pattern>
                <pattern id="editor-grid-major" width="96" height="96" patternUnits="userSpaceOnUse">
                  <rect width="96" height="96" fill="url(#editor-grid-minor)" />
                  <path d="M 96 0 L 0 0 0 96" fill="none" :stroke="VIVEIRO_MAP_GRID.marker" stroke-width="1" />
                </pattern>
              </defs>
              <rect
                x="0"
                y="0"
                :width="svgFrame.w"
                :height="svgFrame.h"
                fill="url(#editor-grid-major)"
                class="mapa-fundo"
                @pointerdown.stop.prevent="iniciarPan"
              />

            <g class="areas-layer">
            <g
              v-for="campo in planta.campos"
              :key="campo.id"
              class="area-grupo"
              :class="{
                'area-grupo--sel': estaSelecionado(campo),
                'area-grupo--prim': selecionado?.id === campo.id,
              }"
              @pointerdown.stop="iniciarDrag($event, campo)"
            >
              <rect
                :x="campo.x"
                :y="campo.y"
                :width="campo.largura"
                :height="campo.altura"
                :fill="corArea(campo)"
                :stroke="estaSelecionado(campo) ? VIVEIRO_MAP_TIPO.canteiro : 'rgba(0,0,0,0.15)'"
                :stroke-width="estaSelecionado(campo) ? (selecionado?.id === campo.id ? 3 : 2) : 1"
                rx="6"
              />
              <template v-if="guiasFaixa(campo).length">
                <line
                  v-for="(g, gi) in guiasFaixa(campo)"
                  :key="`${campo.id}-guia-${gi}`"
                  :x1="g.x1"
                  :y1="g.y1"
                  :x2="g.x2"
                  :y2="g.y2"
                  stroke="rgba(255,255,255,0.35)"
                  stroke-width="1"
                  stroke-dasharray="4 3"
                  pointer-events="none"
                />
              </template>
              <rect
                v-if="barraOcupacao(campo) > 0"
                :x="campo.x + 4"
                :y="campo.y + campo.altura - 10"
                :width="Math.max(4, (campo.largura - 8) * barraOcupacao(campo))"
                height="6"
                rx="3"
                fill="rgba(45, 80, 22, 0.55)"
              />
              <clipPath :id="`clip-area-${campo.id}`">
                <rect
                  :x="campo.x"
                  :y="campo.y"
                  :width="campo.largura"
                  :height="campo.altura"
                  rx="6"
                />
              </clipPath>
              <g class="area-rotulos" :clip-path="`url(#clip-area-${campo.id})`">
                <text
                  v-for="(linha, idx) in rotulosArea(campo).lines"
                  :key="`${campo.id}-lbl-${idx}`"
                  :x="linha.x"
                  :y="linha.y"
                  :class="linha.class"
                  :text-anchor="linha.anchor || 'start'"
                  :font-size="linha.fontSize"
                  :transform="linha.transform"
                >{{ linha.text }}</text>
              </g>
            </g>
            </g>
          </svg>
        </div>

        <p v-if="!planta.campos.length" class="canvas-empty">
          Nenhuma área ainda. Use <strong>+ Adicionar área</strong> para começar o croqui.
        </p>
        <p class="canvas-hint" aria-hidden="true">
          Espaço + arraste = mover · Scroll = zoom · Ctrl/Shift + clique = multiseleção
        </p>
        </div>
      </div>

      <aside class="inspector" aria-label="Painel do editor">
        <section class="inspector-areas" aria-label="Lista de áreas">
          <header class="inspector-areas__head">
            <div class="inspector-areas__titulos">
              <h2 class="inspector-areas__title">Áreas do viveiro</h2>
              <p class="inspector-areas__sub">{{ planta.campos.length }} cadastrada(s)</p>
            </div>
            <span v-if="selecionados.length" class="inspector-areas__sel">{{ selecionados.length }} sel.</span>
            <button
              v-if="selecionados.length"
              type="button"
              class="btn-limpar-sel"
              @click="limparSelecao"
            >
              Limpar
            </button>
          </header>

          <p v-if="!planta.campos.length" class="inspector-areas__empty">
            Nenhuma área. Clique em <strong>+ Adicionar área</strong> para começar.
          </p>

          <ul v-else class="lista-areas">
            <li v-for="c in planta.campos" :key="c.id">
              <div
                class="lista-item"
                :class="{
                  'lista-item--sel': estaSelecionado(c),
                  'lista-item--prim': selecionado?.id === c.id,
                }"
                role="button"
                tabindex="0"
                @click="focarCampo(c)"
                @keydown.enter="focarCampo(c)"
              >
                <input
                  type="checkbox"
                  class="lista-check"
                  :checked="estaSelecionado(c)"
                  :aria-label="`Marcar ${c.nome}`"
                  @click.stop
                  @change="toggleCheckboxLista(c, $event.target.checked)"
                />
                <span class="lista-cor" :style="{ background: corArea(c) }" aria-hidden="true" />
                <span class="lista-texto">
                  <strong>{{ c.nome }}</strong>
                  <small>{{ rotuloTipo(c.tipo) }}{{ textoBadge(c) ? ` · ${textoBadge(c)}` : '' }}</small>
                </span>
              </div>
            </li>
          </ul>
        </section>

        <div class="inspector-detalhes">
        <template v-if="selecionado">
          <header class="inspector-top">
            <span class="inspector-tipo">
              {{ selecionados.length > 1 ? `${selecionados.length} áreas selecionadas` : rotuloTipo(selecionado.tipo) }}
            </span>
            <h2 class="inspector-nome">{{ selecionado.nome }}</h2>
            <p v-if="selecionados.length > 1" class="inspector-multi-hint">
              Ajuste posição no mapa ou use alinhar abaixo.
            </p>
          </header>

          <section
            v-if="selecionados.length >= 2"
            class="inspector-secao inspector-secao--alinhar"
            aria-labelledby="sec-alinhar"
          >
            <h3 id="sec-alinhar" class="inspector-secao-titulo">Alinhar seleção</h3>
            <div class="alinhar-grid">
              <button type="button" class="btn-alinhar" title="Alinhar borda esquerda" @click="alinhar('esquerda')">Esq.</button>
              <button type="button" class="btn-alinhar" title="Centralizar horizontalmente" @click="alinhar('centro-h')">Centro H</button>
              <button type="button" class="btn-alinhar" title="Alinhar borda direita" @click="alinhar('direita')">Dir.</button>
              <button type="button" class="btn-alinhar" title="Alinhar topo" @click="alinhar('topo')">Topo</button>
              <button type="button" class="btn-alinhar" title="Centralizar verticalmente" @click="alinhar('centro-v')">Centro V</button>
              <button type="button" class="btn-alinhar" title="Alinhar base" @click="alinhar('base')">Base</button>
            </div>
            <div class="alinhar-grid alinhar-grid--2">
              <button type="button" class="btn-alinhar btn-alinhar--wide" @click="distribuir('horizontal')">
                Distribuir H
              </button>
              <button type="button" class="btn-alinhar btn-alinhar--wide" @click="distribuir('vertical')">
                Distribuir V
              </button>
            </div>
          </section>

          <div class="inspector-body">
            <div v-if="textoBadge(selecionado)" class="ocupacao-card">
              <span class="ocupacao-num">{{ textoBadge(selecionado) }}</span>
              <span class="ocupacao-leg">plantas ativas / capacidade</span>
            </div>

            <section v-if="selecionados.length === 1" class="inspector-secao" aria-labelledby="sec-dimensoes">
              <h3 id="sec-dimensoes" class="inspector-secao-titulo">Dimensões reais</h3>
              <PresetDimensoes :ativo-id="presetDimAtivo" @aplicar="aplicarPresetDimensao" />
              <div class="field-row">
                <label class="field">
                  Largura (m)
                  <input
                    v-model.number="metrosEdit.largura"
                    type="number"
                    min="0.5"
                    step="0.1"
                    @change="aplicarMetros"
                    @input="presetDimAtivo = null"
                  />
                </label>
                <label class="field">
                  Comprimento (m)
                  <input
                    v-model.number="metrosEdit.altura"
                    type="number"
                    min="0.5"
                    step="0.1"
                    @change="aplicarMetros"
                    @input="presetDimAtivo = null"
                  />
                </label>
              </div>
              <button type="button" class="btn-inverter" @click="inverterOrientacao">
                ↻ Inverter orientação
              </button>
            </section>

            <section v-if="selecionados.length === 1" class="inspector-secao" aria-labelledby="sec-identidade">
              <h3 id="sec-identidade" class="inspector-secao-titulo">Identificação</h3>
              <label class="field">
                Nome
                <input v-model="selecionado.nome" type="text" maxlength="50" @change="marcarDirty" />
              </label>

              <template v-if="selecionado.tipo === 'canteiro'">
                <div class="field-row">
                  <label class="field">
                    Linhas
                    <input
                      v-model.number="selecionado.config.linhas"
                      type="number"
                      min="1"
                      max="30"
                      @change="atualizarCapacidadeCanteiro"
                    />
                  </label>
                  <label class="field">
                    Colunas
                    <input
                      v-model.number="selecionado.config.colunas"
                      type="number"
                      min="1"
                      max="30"
                      @change="atualizarCapacidadeCanteiro"
                    />
                  </label>
                </div>
                <p class="hint">Capacidade: <strong>{{ capacidadeCanteiro }}</strong> tubetes</p>
              </template>

              <label v-else-if="isProdutivo(selecionado.tipo)" class="field field--last">
                Capacidade (mudas)
                <input
                  v-model.number="selecionado.config.capacidade"
                  type="number"
                  min="1"
                  @change="marcarDirty"
                />
              </label>
            </section>

            <p v-if="!podeExcluir" class="aviso aviso--block">
              Há plantas neste local. Transfira ou retire as mudas na produção antes de excluir.
            </p>
          </div>
        </template>
        <div v-else class="inspector-detalhes__vazio">
          <p class="inspector-detalhes__vazio-titulo">Nenhuma área selecionada</p>
          <p class="inspector-detalhes__vazio-texto">
            Clique em uma área no mapa ou na lista acima para editar nome, dimensões e capacidade.
          </p>
        </div>
        </div>

        <footer v-if="selecionado" class="inspector-footer">
          <button type="button" class="btn-duplicate" @click="duplicarSelecionado">
            Duplicar área
          </button>
          <button type="button" class="btn-danger" :disabled="!podeExcluir || excluindo" @click="pedirExclusao">
            {{ excluindo ? 'Excluindo…' : 'Excluir área' }}
          </button>
        </footer>
      </aside>
    </div>

    <ViveiroComponentWizard
      :aberto="wizardAberto"
      @fechar="wizardAberto = false"
      @confirmar="onWizardConfirmar"
    />

    <div
      v-if="dialogExcluir"
      class="dialog-overlay"
      @pointerdown.self="onOverlayExcluirDown"
      @pointerup.self="onOverlayExcluirUp"
      @pointercancel.self="cancelarOverlayExcluir"
    >
      <div class="dialog" role="alertdialog" @pointerdown="onDialogExcluirDown">
        <h3>Excluir «{{ selecionado?.nome }}»?</h3>
        <p v-if="dialogErro" class="dialog-erro">{{ dialogErro }}</p>
        <p v-else class="dialog-text">
          {{ selecionado?.apiId ? 'O local será removido do sistema e do mapa.' : 'Será removido apenas do croqui.' }}
        </p>
        <div class="dialog-acoes">
          <button type="button" class="btn-ghost" @click="fecharDialogExcluir">Cancelar</button>
          <button type="button" class="btn-danger" :disabled="excluindo" @click="confirmarExclusao">Excluir</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import ViveiroComponentWizard from './ViveiroComponentWizard.vue'
import PresetDimensoes from './PresetDimensoes.vue'
import { criarComponenteNoMapa, duplicarCampoNoMapa, nomeDuplicado } from '@/utils/viveiroLayout'
import { sanitizarCamposLayout } from '@/utils/viveiroLayoutSanitize'
import { elementosParaCamposEditor } from '@/utils/viveiroApiMapper'
import { getViveiroLayout, saveViveiroLayout } from '@/services/viveiroLayout'
import {
  sincronizarCamposComCanteiros,
  plantaParaLayoutPersistido,
  removerCanteirosAusentesDoLayout,
  excluirCampoProdutivo,
  isComponenteProdutivo,
} from '@/utils/viveiroLayoutSync'
import { useViveiroStore } from '@/store/viveiro'
import { listCanteirosComOcupacao } from '@/services/canteiros'
import {
  mapOcupacaoPorApiId,
  textoBadgeOcupacao,
  podeExcluirArea,
} from '@/utils/viveiroOcupacao'
import { CATALOGO_PRODUTIVO, CATALOGO_VISUAL } from '@/constants/viveiroComponentes'
import { CHART_NEUTRAL } from '@/constants/chartColors'
import { VIVEIRO_MAP_GRID, VIVEIRO_MAP_TIPO } from '@/constants/viveiroMapColors'
import { layoutRotulosArea } from '@/utils/viveiroAreaRotulos'
import {
  PX_POR_METRO,
  aplicarMetrosAoCampo,
  inverterOrientacaoCampo,
  orientacaoFaixa,
} from '@/constants/viveiroDimensoes'
import {
  snapVarios,
  alinharCampos,
  distribuirCampos,
} from '@/utils/viveiroLayoutSnap'
const emit = defineEmits(['voltar'])

const viveiroStore = useViveiroStore()
const planta = reactive({ campos: [], nome: 'Planta do Viveiro', data: '' })
const layoutAoAbrir = ref(null)
const selecionado = ref(null)
const selecionadosIds = ref(new Set())
const wizardAberto = ref(false)
const salvando = ref(false)
const excluindo = ref(false)
const erroSalvar = ref(null)
const dialogExcluir = ref(false)
const dialogErro = ref(null)
const ocupacaoPorApiId = ref({})
const metrosEdit = reactive({ largura: null, altura: null })
const presetDimAtivo = ref(null)

const canvasEl = ref(null)
const svgEl = ref(null)
const zoom = ref(1)
const pan = reactive({ x: 40, y: 40 })
const viewBox = reactive({ w: 900, h: 600 })

const MARGEM_SVG = 48

const svgFrame = computed(() => {
  if (!planta.campos.length) {
    return { vbX: 0, vbY: 0, w: viewBox.w, h: viewBox.h }
  }
  const { minX, minY, maxX, maxY } = boundsConteudo(0)
  const bw = maxX - minX
  const bh = maxY - minY
  return {
    vbX: minX - MARGEM_SVG,
    vbY: minY - MARGEM_SVG,
    w: Math.max(320, bw + MARGEM_SVG * 2),
    h: Math.max(240, bh + MARGEM_SVG * 2),
  }
})

const svgViewBoxAttr = computed(() => {
  const f = svgFrame.value
  return `${f.vbX} ${f.vbY} ${f.w} ${f.h}`
})

const canvasInnerStyle = computed(() => ({
  width: `${svgFrame.value.w}px`,
  height: `${svgFrame.value.h}px`,
  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom.value})`,
  transformOrigin: '0 0',
}))

const dragCampo = ref(null)
const DRAG_THRESHOLD = 5
/** @type {{ campo: object, aditivo: boolean, px: number, py: number, moved: boolean, origens: { c: object, ox: number, oy: number }[] } | null} */
let dragSessao = null
const panning = ref(false)
const spacePan = ref(false)
let panStart = null
let panPointerId = null

const ROTULOS = {
  canteiro: 'Canteiro',
  sementeira: 'Sementeira',
  rustificacao: 'Rustificação',
  sede: 'Sede',
  lago: 'Água',
  garagem: 'Garagem',
  'area-trabalho': 'Trabalho',
  estoque: 'Estoque',
}

const CORES = Object.fromEntries(
  [...CATALOGO_PRODUTIVO, ...CATALOGO_VISUAL].map((c) => [c.tipo, c.corPadrao])
)

const selecionados = computed(() =>
  planta.campos.filter((c) => selecionadosIds.value.has(c.id))
)

const capacidadeCanteiro = computed(() => {
  const c = selecionado.value
  if (!c || c.tipo !== 'canteiro') return 0
  return (c.config?.linhas || 1) * (c.config?.colunas || 1)
})

const podeExcluir = computed(() => {
  const c = selecionado.value
  if (!c) return false
  if (!isComponenteProdutivo(c.tipo)) return true
  if (!c.apiId) return true
  return podeExcluirArea(ocupacaoPorApiId.value[c.apiId], 0)
})

function rotuloTipo(tipo) {
  return ROTULOS[tipo] || tipo
}

function corArea(campo) {
  return campo.cor || CORES[campo.tipo] || CHART_NEUTRAL
}

function isProdutivo(tipo) {
  return isComponenteProdutivo(tipo)
}

function textoBadge(campo) {
  if (!isProdutivo(campo.tipo)) return null
  const occ = campo.apiId ? ocupacaoPorApiId.value[campo.apiId] : null
  return textoBadgeOcupacao(campo, occ, 0)
}

function rotulosArea(campo) {
  return layoutRotulosArea({
    x: campo.x,
    y: campo.y,
    largura: campo.largura,
    altura: campo.altura,
    rotuloTipo: rotuloTipo(campo.tipo),
    nome: campo.nome,
    badge: textoBadge(campo),
    metros: campo.metros,
  })
}

function guiasFaixa(campo) {
  if (!['canteiro', 'sementeira', 'rustificacao'].includes(campo.tipo)) return []
  const orient = orientacaoFaixa(campo.largura, campo.altura)
  if (!orient) return []
  const linhas = []
  const pad = 8
  if (orient === 'vertical') {
    const passo = Math.max(28, Math.round(campo.altura / 8))
    for (let y = campo.y + passo; y < campo.y + campo.altura - pad; y += passo) {
      linhas.push({
        x1: campo.x + pad,
        y1: y,
        x2: campo.x + campo.largura - pad,
        y2: y,
      })
    }
  } else {
    const passo = Math.max(28, Math.round(campo.largura / 8))
    for (let x = campo.x + passo; x < campo.x + campo.largura - pad; x += passo) {
      linhas.push({
        x1: x,
        y1: campo.y + pad,
        x2: x,
        y2: campo.y + campo.altura - pad,
      })
    }
  }
  return linhas
}

function barraOcupacao(campo) {
  const badge = textoBadge(campo)
  if (!badge || !badge.includes('/')) return 0
  const [a, b] = badge.split('/').map(Number)
  if (!b) return 0
  return Math.min(1, a / b)
}

function ajustarViewBox() {
  let maxX = 400
  let maxY = 300
  for (const c of planta.campos) {
    maxX = Math.max(maxX, c.x + c.largura + 80)
    maxY = Math.max(maxY, c.y + c.altura + 80)
  }
  viewBox.w = maxX
  viewBox.h = maxY
}

function estaSelecionado(campo) {
  return selecionadosIds.value.has(campo.id)
}

function ehSelecaoAditiva(event) {
  return event.shiftKey || event.ctrlKey || event.metaKey
}

function aplicarMetrosInspector(c) {
  if (!c) return
  metrosEdit.largura = c.metros?.largura ?? (c.largura ? +(c.largura / PX_POR_METRO).toFixed(1) : null)
  metrosEdit.altura = c.metros?.altura ?? (c.altura ? +(c.altura / PX_POR_METRO).toFixed(1) : null)
  if (c.tipo === 'canteiro' && !c.config) {
    c.config = { linhas: 4, colunas: 4, capacidade: 16 }
  }
}

function selecionar(campo, { aditivo = false } = {}) {
  if (!campo) return
  if (aditivo) {
    const next = new Set(selecionadosIds.value)
    if (next.has(campo.id)) next.delete(campo.id)
    else next.add(campo.id)
    selecionadosIds.value = next
    if (!next.size) {
      selecionado.value = null
      return
    }
    selecionado.value = campo
  } else {
    selecionadosIds.value = new Set([campo.id])
    selecionado.value = campo
  }
  aplicarMetrosInspector(selecionado.value)
}

function toggleCheckboxLista(campo, marcado) {
  const next = new Set(selecionadosIds.value)
  if (marcado) next.add(campo.id)
  else next.delete(campo.id)
  selecionadosIds.value = next
  if (next.size) {
    selecionado.value = campo
    aplicarMetrosInspector(campo)
  } else {
    selecionado.value = null
  }
}

function focarCampo(campo) {
  selecionar(campo, { aditivo: false })
}

function limparSelecao() {
  selecionadosIds.value = new Set()
  selecionado.value = null
}

function grupoArrastePara(campo) {
  const inSel = selecionadosIds.value.has(campo.id)
  if (inSel && selecionadosIds.value.size > 1) {
    return planta.campos.filter((c) => selecionadosIds.value.has(c.id))
  }
  return [campo]
}

function alinhar(modo) {
  const grupo = selecionados.value
  if (grupo.length < 2) return
  alinharCampos(grupo, modo)
  snapVarios(grupo, planta.campos)
  marcarDirty()
}

function distribuir(eixo) {
  const grupo = selecionados.value
  if (grupo.length < 3) return
  distribuirCampos(grupo, eixo === 'vertical' ? 'vertical' : 'horizontal')
  snapVarios(grupo, planta.campos)
  marcarDirty()
}

function marcarDirty() {
  ajustarViewBox()
}

function duplicarSelecionado() {
  const orig = selecionado.value
  if (!orig) return
  const copia = duplicarCampoNoMapa(orig)
  if (!copia) return
  copia.nome = nomeDuplicado(orig.nome, planta.campos.map((c) => c.nome))
  planta.campos.push(copia)
  selecionar(copia, { aditivo: false })
  marcarDirty()
}

function aplicarMetros() {
  const c = selecionado.value
  if (!c) return
  if (aplicarMetrosAoCampo(c, metrosEdit.largura, metrosEdit.altura)) {
    ajustarViewBox()
  }
}

function aplicarPresetDimensao(preset) {
  metrosEdit.largura = preset.largura
  metrosEdit.altura = preset.altura
  presetDimAtivo.value = preset.id
  aplicarMetros()
}

function inverterOrientacao() {
  const c = selecionado.value
  if (!c) return
  inverterOrientacaoCampo(c)
  metrosEdit.largura = c.metros?.largura ?? metrosEdit.largura
  metrosEdit.altura = c.metros?.altura ?? metrosEdit.altura
  presetDimAtivo.value = null
  marcarDirty()
}

function atualizarCapacidadeCanteiro() {
  const c = selecionado.value
  if (!c?.config) return
  c.config.capacidade = capacidadeCanteiro.value
  marcarDirty()
}

function svgPoint(event) {
  if (!svgEl.value) return { x: 0, y: 0 }
  const pt = svgEl.value.createSVGPoint()
  pt.x = event.clientX
  pt.y = event.clientY
  const ctm = svgEl.value.getScreenCTM()
  if (!ctm) return { x: 0, y: 0 }
  return pt.matrixTransform(ctm.inverse())
}

function boundsConteudo(padding = 40) {
  if (!planta.campos.length) {
    return { minX: padding, minY: padding, maxX: viewBox.w - padding, maxY: viewBox.h - padding }
  }
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  for (const c of planta.campos) {
    minX = Math.min(minX, c.x)
    minY = Math.min(minY, c.y)
    maxX = Math.max(maxX, c.x + c.largura)
    maxY = Math.max(maxY, c.y + c.altura)
  }
  return { minX, minY, maxX, maxY }
}

/** Coloca todas as áreas visíveis e centralizadas no viewport. */
function enquadrarTudo() {
  const el = canvasEl.value
  if (!el) return
  const pad = 32
  const f = svgFrame.value
  const bw = f.w
  const bh = f.h
  const cw = el.clientWidth
  const ch = el.clientHeight
  const scaleX = (cw - pad * 2) / bw
  const scaleY = (ch - pad * 2) / bh
  zoom.value = Math.min(2.5, Math.max(0.55, Math.min(scaleX, scaleY)))
  pan.x = (cw - bw * zoom.value) / 2
  pan.y = (ch - bh * zoom.value) / 2
}

function zoomUmParaUm() {
  zoom.value = 1
  const el = canvasEl.value
  if (!el) return
  const f = svgFrame.value
  const cw = el.clientWidth
  const ch = el.clientHeight
  pan.x = (cw - f.w) / 2
  pan.y = (ch - f.h) / 2
}

let canvasRo
function observarCanvas() {
  canvasRo?.disconnect()
  if (!canvasEl.value) return
  canvasRo = new ResizeObserver(() => {
    if (!dragCampo.value && !panning.value) enquadrarTudo()
  })
  canvasRo.observe(canvasEl.value)
}

function iniciarPan(event) {
  if (dragCampo.value) return
  if (!spacePan.value && event.target?.closest?.('.area-grupo')) return
  if (event.button !== 0 && event.button !== 1) return

  event.preventDefault()
  event.stopPropagation()

  panning.value = true
  panPointerId = event.pointerId
  panStart = { mx: event.clientX, my: event.clientY, px: pan.x, py: pan.y }
  selecionado.value = null
  selecionadosIds.value = new Set()

  const cap = canvasEl.value
  if (cap?.setPointerCapture) {
    try {
      cap.setPointerCapture(event.pointerId)
    } catch {
      /* ignore */
    }
  }

  window.addEventListener('pointermove', onPanMove)
  window.addEventListener('pointerup', onPanEnd)
  window.addEventListener('pointercancel', onPanEnd)
}

function onViewportPointerDown(event) {
  if (event.target?.classList?.contains('mapa-fundo')) return
  if (event.target?.closest?.('.area-grupo')) return
  iniciarPan(event)
}

function onViewportDblClick(event) {
  if (event.target.closest?.('.area-grupo')) return
  enquadrarTudo()
}

function iniciarDrag(event, campo) {
  if (event.button !== 0) return
  event.preventDefault()
  if (spacePan.value) {
    iniciarPan(event)
    return
  }

  const p = svgPoint(event)
  const grupo = grupoArrastePara(campo)
  dragCampo.value = campo
  dragSessao = {
    campo,
    aditivo: ehSelecaoAditiva(event),
    px: p.x,
    py: p.y,
    moved: false,
    origens: grupo.map((c) => ({ c, ox: c.x, oy: c.y })),
  }
  window.addEventListener('pointermove', onDragMove)
  window.addEventListener('pointerup', onDragEnd)
  window.addEventListener('pointercancel', onDragEnd)
}

function onDragMove(event) {
  if (!dragSessao) return
  const p = svgPoint(event)
  const dx = p.x - dragSessao.px
  const dy = p.y - dragSessao.py

  if (!dragSessao.moved) {
    if (Math.abs(dx) <= DRAG_THRESHOLD && Math.abs(dy) <= DRAG_THRESHOLD) return
    dragSessao.moved = true
    if (!dragSessao.aditivo && dragSessao.origens.length === 1) {
      selecionar(dragSessao.campo)
      dragSessao.origens = [{ c: dragSessao.campo, ox: dragSessao.campo.x, oy: dragSessao.campo.y }]
    }
  }

  for (const { c, ox, oy } of dragSessao.origens) {
    c.x = Math.max(0, ox + dx)
    c.y = Math.max(0, oy + dy)
  }
  ajustarViewBox()
}

function onDragEnd() {
  if (!dragSessao) return
  if (!dragSessao.moved) {
    selecionar(dragSessao.campo, { aditivo: dragSessao.aditivo })
  } else {
    const grupo = dragSessao.origens.map((o) => o.c)
    snapVarios(grupo, planta.campos)
    marcarDirty()
  }
  dragCampo.value = null
  dragSessao = null
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', onDragEnd)
  window.removeEventListener('pointercancel', onDragEnd)
}

function onPanMove(event) {
  if (!panning.value || !panStart) return
  pan.x = panStart.px + (event.clientX - panStart.mx)
  pan.y = panStart.py + (event.clientY - panStart.my)
}

function onPanEnd(event) {
  panning.value = false
  panStart = null
  const cap = canvasEl.value
  if (cap?.releasePointerCapture && panPointerId != null) {
    try {
      cap.releasePointerCapture(panPointerId)
    } catch {
      /* ignore */
    }
  }
  panPointerId = null
  window.removeEventListener('pointermove', onPanMove)
  window.removeEventListener('pointerup', onPanEnd)
  window.removeEventListener('pointercancel', onPanEnd)
}

function focoEmCampoTexto() {
  const el = document.activeElement
  if (!el) return false
  const tag = el.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true
  return Boolean(el.isContentEditable)
}

function onKeyDown(event) {
  if (event.code !== 'Space' || event.repeat) return
  if (focoEmCampoTexto()) return
  spacePan.value = true
  event.preventDefault()
}

function onKeyUp(event) {
  if (event.code !== 'Space') return
  if (focoEmCampoTexto()) return
  spacePan.value = false
}

function onWheel(event) {
  const el = canvasEl.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const mx = event.clientX - rect.left
  const my = event.clientY - rect.top
  const wx = (mx - pan.x) / zoom.value
  const wy = (my - pan.y) / zoom.value
  const step = event.deltaY > 0 ? -0.12 : 0.12
  const next = Math.min(2.5, Math.max(0.2, zoom.value + step))
  zoom.value = next
  pan.x = mx - wx * zoom.value
  pan.y = my - wy * zoom.value
}

function ajustarZoom(delta) {
  const el = canvasEl.value
  if (!el) {
    zoom.value = Math.min(2.5, Math.max(0.2, zoom.value + delta))
    return
  }
  const rect = el.getBoundingClientRect()
  const mx = rect.width / 2
  const my = rect.height / 2
  const wx = (mx - pan.x) / zoom.value
  const wy = (my - pan.y) / zoom.value
  const next = Math.min(2.5, Math.max(0.2, zoom.value + delta))
  zoom.value = next
  pan.x = mx - wx * zoom.value
  pan.y = my - wy * zoom.value
}

async function carregarOcupacao() {
  try {
    const list = await listCanteirosComOcupacao({ ativo: true })
    ocupacaoPorApiId.value = mapOcupacaoPorApiId(list)
  } catch {
    ocupacaoPorApiId.value = {}
  }
}

function onWizardConfirmar(payload) {
  const componente = criarComponenteNoMapa(payload, planta.campos.length)
  if (!componente) return
  planta.campos.push(componente)
  wizardAberto.value = false
  ajustarViewBox()
  selecionar(componente)
  setTimeout(enquadrarTudo, 80)
}

let overlayExcluirPress = false

function onDialogExcluirDown() {
  overlayExcluirPress = false
}

function onOverlayExcluirDown() {
  overlayExcluirPress = true
}

function onOverlayExcluirUp() {
  if (overlayExcluirPress) fecharDialogExcluir()
  overlayExcluirPress = false
}

function cancelarOverlayExcluir() {
  overlayExcluirPress = false
}

function fecharDialogExcluir() {
  overlayExcluirPress = false
  dialogExcluir.value = false
  dialogErro.value = null
}

function pedirExclusao() {
  dialogErro.value = null
  dialogExcluir.value = true
}

async function confirmarExclusao() {
  const campo = selecionado.value
  if (!campo || !podeExcluir.value) return
  excluindo.value = true
  dialogErro.value = null
  try {
    if (isComponenteProdutivo(campo.tipo) && campo.apiId) {
      await excluirCampoProdutivo(campo)
      const next = { ...ocupacaoPorApiId.value }
      delete next[campo.apiId]
      ocupacaoPorApiId.value = next
    }
    const idx = planta.campos.findIndex((c) => c.id === campo.id)
    if (idx !== -1) planta.campos.splice(idx, 1)
    const layout = plantaParaLayoutPersistido(planta, viewBox)
    await saveViveiroLayout(layout)
    layoutAoAbrir.value = layout
    selecionado.value = null
    fecharDialogExcluir()
    ajustarViewBox()
  } catch (e) {
    dialogErro.value = e.response?.data?.detail || 'Não foi possível excluir.'
  } finally {
    excluindo.value = false
  }
}

async function salvarEVoltar() {
  if (salvando.value) return
  salvando.value = true
  erroSalvar.value = null
  try {
    const anterior = layoutAoAbrir.value || (await getViveiroLayout().catch(() => ({})))
    const errosRem = await removerCanteirosAusentesDoLayout(planta.campos, anterior)
    if (errosRem.length) {
      erroSalvar.value = errosRem.join(' · ')
      return
    }
    const erros = await sincronizarCamposComCanteiros(planta.campos)
    if (erros.length) {
      erroSalvar.value = erros.join(' · ')
      return
    }
    const layout = plantaParaLayoutPersistido(planta, viewBox)
    await saveViveiroLayout(layout)
    layoutAoAbrir.value = layout
    await viveiroStore.carregar(true)
    emit('voltar')
  } catch (e) {
    erroSalvar.value = e.response?.data?.detail || 'Falha ao salvar o layout.'
  } finally {
    salvando.value = false
  }
}

async function carregarLayout() {
  await carregarOcupacao()
  if (!viveiroStore.hidratado) {
    await viveiroStore.carregar()
  }

  let data = {}
  try {
    data = await getViveiroLayout()
  } catch {
    /* layout vazio na API */
  }

  if (data?.campos?.length) {
    planta.campos = sanitizarCamposLayout(data.campos)
    planta.nome = data.nome || planta.nome
    if (data.viewBox?.width) viewBox.w = data.viewBox.width
    if (data.viewBox?.height) viewBox.h = data.viewBox.height
    layoutAoAbrir.value = data
  } else if (viveiroStore.layout.elementos?.length) {
    planta.campos = elementosParaCamposEditor(viveiroStore.layout.elementos)
    planta.nome = viveiroStore.layout.nome || planta.nome
    if (viveiroStore.layout.dimensoes?.largura) viewBox.w = viveiroStore.layout.dimensoes.largura
    if (viveiroStore.layout.dimensoes?.altura) viewBox.h = viveiroStore.layout.dimensoes.altura
  }

  ajustarViewBox()
  setTimeout(enquadrarTudo, 100)
}

onMounted(() => {
  carregarLayout()
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('keyup', onKeyUp)
  requestAnimationFrame(() => {
    observarCanvas()
    enquadrarTudo()
  })
})

onUnmounted(() => {
  canvasRo?.disconnect()
  window.removeEventListener('keydown', onKeyDown)
  window.removeEventListener('keyup', onKeyUp)
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', onDragEnd)
  window.removeEventListener('pointercancel', onDragEnd)
  window.removeEventListener('pointermove', onPanMove)
  window.removeEventListener('pointerup', onPanEnd)
  window.removeEventListener('pointercancel', onPanEnd)
})

watch(
  () => planta.campos.length,
  () => {
    ajustarViewBox()
    requestAnimationFrame(() => enquadrarTudo())
  }
)
</script>

<style scoped>
.layout-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: var(--color-background);
  user-select: none;
  -webkit-user-select: none;
}

.layout-editor input,
.layout-editor textarea,
.layout-editor select {
  user-select: text;
  -webkit-user-select: text;
}

.editor-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  padding: 0.75rem 1.5rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-subtle);
  flex-shrink: 0;
  z-index: 5;
}

.editor-header__brand {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
}

.editor-header__title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}

.editor-header__sub {
  margin: 0.125rem 0 0;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  line-height: 1.45;
}

.editor-header__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  flex-shrink: 0;
}

.btn-back:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-add {
  padding: 0.5rem 0.875rem;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: var(--color-text-inverse);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  font-family: inherit;
  white-space: nowrap;
}

.btn-save {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-analog-1);
  color: var(--color-text-inverse);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  font-family: inherit;
  white-space: nowrap;
}

.btn-save:disabled {
  opacity: 0.55;
}

.erro-bar {
  margin: 0;
  padding: 0.625rem 1.5rem;
  background: var(--color-error-bg);
  color: var(--color-error);
  font-size: 0.875rem;
  border-bottom: 1px solid var(--color-error-bg);
  flex-shrink: 0;
}

.editor-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(380px, 440px);
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.canvas {
  position: relative;
  min-height: 0;
  overflow: hidden;
  cursor: grab;
  padding: 1.25rem 1.5rem;
  box-sizing: border-box;
}

.canvas-stage {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 420px;
}

.canvas-inner {
  position: absolute;
  top: 0;
  left: 0;
  will-change: transform;
}

.mapa-svg {
  display: block;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 12px 40px rgba(44, 45, 42, 0.14);
  user-select: none;
}

.mapa-svg text {
  user-select: none;
  pointer-events: none;
  font-family: var(--font-sans);
}

.area-rotulos text {
  paint-order: stroke fill;
  stroke: rgba(255, 255, 255, 0.92);
  stroke-width: 4px;
  stroke-linejoin: round;
}

.lbl-tipo {
  font-size: 10px;
  font-weight: 700;
  fill: rgba(0, 0, 0, 0.62);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.lbl-nome {
  font-size: 13px;
  font-weight: 700;
  fill: var(--color-text-primary);
}

.lbl-badge {
  font-size: 11px;
  font-weight: 700;
  fill: var(--color-text-primary);
}

.canvas-hint {
  position: absolute;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  margin: 0;
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-full);
  pointer-events: none;
  z-index: 2;
  max-width: calc(100% - 3rem);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: var(--shadow-sm);
}

.inspector {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border-subtle);
}

.inspector-areas {
  display: flex;
  flex-direction: column;
  flex: 0 1 42%;
  min-height: 240px;
  max-height: 48%;
  border-bottom: 1px solid var(--color-border-subtle);
  background: var(--color-surface-muted);
}

.inspector-areas__head {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1.125rem 1.25rem 0.875rem;
  flex-shrink: 0;
}

.inspector-areas__titulos {
  flex: 1;
  min-width: 0;
}

.inspector-areas__title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.3;
}

.inspector-areas__sub {
  margin: 0.25rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.inspector-areas__sel {
  flex-shrink: 0;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-primary);
  background: var(--color-primary-subtle);
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-full);
}

.inspector-areas__empty {
  margin: 0;
  padding: 1rem 1.25rem 1.25rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.inspector-detalhes {
  flex: 1 1 auto;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.inspector-detalhes__vazio {
  padding: 1.5rem 1.25rem;
  text-align: center;
}

.inspector-detalhes__vazio-titulo {
  margin: 0 0 0.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.inspector-detalhes__vazio-texto {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  max-width: 22rem;
  margin-inline: auto;
}

.inspector-top {
  flex-shrink: 0;
  padding: 1.125rem 1.25rem 1rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-subtle);
}

.inspector-body {
  padding: 1rem 1.25rem 1.25rem;
}

.inspector-footer {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  padding: 1rem 1.25rem 1.25rem;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border-subtle);
}

.btn-limpar-sel {
  flex-shrink: 0;
  border: 1px solid var(--color-border-subtle);
  background: var(--color-surface);
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-family: inherit;
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-md);
}

.btn-limpar-sel:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.lista-areas {
  list-style: none;
  margin: 0;
  padding: 0 1rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.lista-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 0.875rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.lista-item:hover {
  border-color: var(--color-border);
  box-shadow: var(--shadow-sm);
}

.lista-item--sel {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.lista-item--prim {
  box-shadow: 0 0 0 2px rgba(74, 124, 42, 0.25);
}

.lista-check {
  flex-shrink: 0;
  margin: 0;
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
  cursor: pointer;
}

.lista-cor {
  width: 12px;
  height: 36px;
  border-radius: 4px;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.lista-texto {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
  flex: 1;
  text-align: left;
}

.lista-texto strong {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lista-texto small {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.canvas--panning {
  cursor: grabbing;
  user-select: none;
}

.canvas--dragging {
  cursor: move;
  user-select: none;
}

.mapa-fundo {
  cursor: grab;
}

.areas-layer {
  pointer-events: auto;
}

.canvas--space-pan {
  cursor: grab;
}

.canvas--space-pan .area-grupo {
  cursor: grab;
}

.canvas--panning,
.canvas--panning .mapa-fundo,
.canvas--panning .area-grupo {
  cursor: grabbing !important;
}

.area-grupo {
  cursor: move;
}

.area-grupo--sel rect:first-child {
  filter: drop-shadow(0 1px 6px rgba(45, 80, 22, 0.28));
}

.area-grupo--prim rect:first-child {
  filter: drop-shadow(0 2px 10px rgba(45, 80, 22, 0.4));
}

.inspector-multi-hint {
  margin: 0.35rem 0 0;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  line-height: 1.35;
}

.inspector-secao--alinhar {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary-light);
}

.alinhar-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.alinhar-grid--2 {
  margin-top: 0.5rem;
  grid-template-columns: 1fr 1fr;
}

.btn-alinhar {
  padding: 0.5rem 0.375rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-family: inherit;
  text-align: center;
  min-height: 2.25rem;
}

.btn-alinhar:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
  color: var(--color-primary-dark);
}

.btn-alinhar--wide {
  font-size: 0.7rem;
}

.canvas-empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 2rem;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.9375rem;
  pointer-events: none;
}

.btn-duplicate {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-primary);
  border-radius: 8px;
  background: var(--color-surface);
  color: var(--color-primary-dark);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.btn-duplicate:hover {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary-dark);
}

.btn-inverter {
  width: 100%;
  margin-top: 0.35rem;
  padding: 0.45rem 0.65rem;
  border: 1px dashed var(--color-border);
  border-radius: 8px;
  background: var(--color-background);
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
}

.btn-inverter:hover {
  border-color: var(--color-primary);
  color: var(--color-primary-dark);
  background: var(--color-primary-subtle);
}

:deep(.lbl-metros) {
  fill: rgba(0, 0, 0, 0.5);
  font-weight: 600;
  font-size: 10px;
}

.inspector-tipo {
  display: inline-block;
  font-size: 0.8125rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-primary);
  background: var(--color-primary-subtle);
  padding: var(--v-s1) var(--v-s2);
  border-radius: var(--radius-md);
  margin-bottom: var(--v-s2);
}

.inspector-nome {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.35;
  word-break: break-word;
  overflow-wrap: anywhere;
  color: var(--color-text-primary);
}

.inspector-secao {
  margin-bottom: var(--v-s3);
  padding: var(--v-s3);
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
}

.inspector-secao-titulo {
  margin: 0 0 var(--v-s2);
  font-size: 0.8125rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.ocupacao-card {
  background: linear-gradient(180deg, var(--color-primary-subtle) 0%, var(--color-surface-muted) 100%);
  border: 1px solid var(--color-primary-light);
  border-radius: var(--radius-xl);
  padding: var(--v-s3);
  margin-bottom: var(--v-s3);
  text-align: center;
}

.ocupacao-num {
  display: block;
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-primary-dark);
  line-height: 1.15;
}

.ocupacao-leg {
  display: block;
  margin-top: var(--v-s2);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  line-height: var(--v-line);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--v-s2);
  margin-bottom: var(--v-s3);
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 0;
}

.field--last {
  margin-bottom: 0;
}

.field input {
  width: 100%;
  box-sizing: border-box;
  min-width: 0;
  padding: var(--v-s2) var(--v-s3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  font-size: 0.9375rem;
  font-family: inherit;
  background: var(--color-surface);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.field input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(74, 124, 42, 0.15);
}

.field-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: var(--v-s3);
}

.field-row .field {
  margin-bottom: 0;
}

.hint {
  margin: 0.5rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  line-height: 1.4;
}

.aviso {
  font-size: 0.8125rem;
  line-height: 1.45;
  padding: 0.6rem 0.7rem;
  border-radius: 8px;
  margin: 0;
}

.aviso--block {
  background: var(--color-error-bg);
  color: var(--color-error);
  border: 1px solid var(--color-error-bg);
}

.btn-danger {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: none;
  border-radius: 8px;
  background: var(--color-error);
  color: var(--color-text-inverse);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s ease, opacity 0.15s ease;
}

.btn-danger:hover:not(:disabled) {
  background: var(--color-error-dark);
}

.btn-danger:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.dialog {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 1.25rem;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.dialog h3 {
  margin: 0 0 0.5rem;
  font-size: 1.0625rem;
}

.dialog-text,
.dialog-erro {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.dialog-erro {
  color: var(--color-error);
}

.dialog-acoes {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

@media (max-width: 900px) {
  .editor-main {
    grid-template-columns: 1fr;
    grid-template-rows: minmax(340px, 1fr) minmax(300px, 44vh);
  }

  .inspector {
    border-left: none;
    border-top: 1px solid var(--color-border-subtle);
  }

  .editor-header__sub {
    display: none;
  }

  .canvas-hint {
    display: none;
  }
}

@media (max-width: 520px) {
  .editor-header__titles {
    display: none;
  }

  .editor-header__actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
