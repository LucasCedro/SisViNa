<template>
  <div class="layout-editor">
    <header class="editor-header">
      <div class="header-left">
        <button type="button" class="btn-ghost" @click="emit('voltar')">← Voltar ao viveiro</button>
      </div>
      <div class="header-actions">
        <button type="button" class="btn-primary" @click="wizardAberto = true">+ Adicionar área</button>
        <div class="zoom-bar" role="group" aria-label="Zoom">
          <button type="button" class="btn-icon" @click="ajustarZoom(-0.15)">−</button>
          <span>{{ Math.round(zoom * 100) }}%</span>
          <button type="button" class="btn-icon" @click="ajustarZoom(0.15)">+</button>
          <button type="button" class="btn-ghost-sm" @click="enquadrarTudo">Enquadrar</button>
          <button type="button" class="btn-ghost-sm" title="Zoom 100%" @click="zoomUmParaUm">100%</button>
        </div>
        <button type="button" class="btn-save" :disabled="salvando" @click="salvarEVoltar">
          {{ salvando ? 'Salvando…' : 'Salvar layout' }}
        </button>
      </div>
    </header>

    <p v-if="erroSalvar" class="erro-bar" role="alert">{{ erroSalvar }}</p>

    <div class="editor-main">
      <div
        ref="canvasEl"
        class="canvas"
        :class="{ 'canvas--panning': panning, 'canvas--dragging': !!dragCampo, 'canvas--space-pan': spacePan }"
        @wheel.prevent="onWheel"
        @pointerdown="onViewportPointerDown"
        @dblclick="onViewportDblClick"
      >
        <div class="canvas-inner" :style="canvasInnerStyle">
          <svg
            ref="svgEl"
            class="mapa-svg"
            :width="viewBox.w"
            :height="viewBox.h"
            :viewBox="`0 0 ${viewBox.w} ${viewBox.h}`"
          >
            <defs>
              <pattern id="editor-grid" width="32" height="32" patternUnits="userSpaceOnUse">
                <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#cccbc6" stroke-width="0.75" />
              </pattern>
            </defs>
            <rect
              :width="viewBox.w"
              :height="viewBox.h"
              fill="url(#editor-grid)"
              class="mapa-fundo"
              @pointerdown.stop.prevent="iniciarPan"
            />

            <g class="areas-layer">
            <g
              v-for="campo in planta.campos"
              :key="campo.id"
              class="area-grupo"
              :class="{ 'area-grupo--sel': selecionado?.id === campo.id }"
              @pointerdown.stop="iniciarDrag($event, campo)"
              @click.stop="selecionar(campo)"
            >
              <rect
                :x="campo.x"
                :y="campo.y"
                :width="campo.largura"
                :height="campo.altura"
                :fill="corArea(campo)"
                :stroke="selecionado?.id === campo.id ? '#2d5016' : 'rgba(0,0,0,0.15)'"
                :stroke-width="selecionado?.id === campo.id ? 3 : 1"
                rx="6"
              />
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
          Arraste o grid (fundo) para mover · Espaço + arraste em qualquer lugar · Scroll = zoom
        </p>
      </div>

      <aside class="inspector" aria-label="Propriedades da área">
        <template v-if="selecionado">
          <header class="inspector-top">
            <span class="inspector-tipo">{{ rotuloTipo(selecionado.tipo) }}</span>
            <h2 class="inspector-nome">{{ selecionado.nome }}</h2>
          </header>

          <div class="inspector-body">
            <div v-if="textoBadge(selecionado)" class="ocupacao-card">
              <span class="ocupacao-num">{{ textoBadge(selecionado) }}</span>
              <span class="ocupacao-leg">plantas ativas / capacidade</span>
            </div>

            <section class="inspector-secao" aria-labelledby="sec-dimensoes">
              <h3 id="sec-dimensoes" class="inspector-secao-titulo">Dimensões</h3>
              <div class="field-row">
                <label class="field">
                  Largura (m)
                  <input
                    v-model.number="metrosEdit.largura"
                    type="number"
                    min="0.5"
                    step="0.1"
                    @change="aplicarMetros"
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
                  />
                </label>
              </div>
            </section>

            <section class="inspector-secao" aria-labelledby="sec-identidade">
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

          <footer class="inspector-footer">
            <button type="button" class="btn-danger" :disabled="!podeExcluir || excluindo" @click="pedirExclusao">
              {{ excluindo ? 'Excluindo…' : 'Excluir área' }}
            </button>
          </footer>
        </template>

        <template v-else>
          <header class="inspector-top inspector-top--lista">
            <h2 class="inspector-title">Áreas do viveiro</h2>
            <p class="inspector-hint">Clique no mapa ou escolha abaixo.</p>
          </header>
          <ul class="inspector-body lista-areas">
            <li v-for="c in planta.campos" :key="c.id">
              <button type="button" class="lista-btn" @click="selecionar(c)">
                <span class="lista-cor" :style="{ background: corArea(c) }" />
                <span class="lista-texto">
                  <strong>{{ c.nome }}</strong>
                  <small>{{ rotuloTipo(c.tipo) }}{{ textoBadge(c) ? ` · ${textoBadge(c)}` : '' }}</small>
                </span>
              </button>
            </li>
            <li v-if="!planta.campos.length" class="lista-vazia">Nenhuma área cadastrada.</li>
          </ul>
        </template>
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
import { criarComponenteNoMapa } from '@/utils/viveiroLayout'
import { sanitizarCamposLayout } from '@/utils/viveiroLayoutSanitize'
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
import { layoutRotulosArea } from '@/utils/viveiroAreaRotulos'

const PX_POR_METRO = 24
const emit = defineEmits(['voltar'])

const viveiroStore = useViveiroStore()
const planta = reactive({ campos: [], nome: 'Planta do Viveiro', data: '' })
const layoutAoAbrir = ref(null)
const selecionado = ref(null)
const wizardAberto = ref(false)
const salvando = ref(false)
const excluindo = ref(false)
const erroSalvar = ref(null)
const dialogExcluir = ref(false)
const dialogErro = ref(null)
const ocupacaoPorApiId = ref({})
const metrosEdit = reactive({ largura: null, altura: null })

const canvasEl = ref(null)
const svgEl = ref(null)
const zoom = ref(1)
const pan = reactive({ x: 40, y: 40 })
const viewBox = reactive({ w: 900, h: 600 })

const canvasInnerStyle = computed(() => ({
  width: `${viewBox.w}px`,
  height: `${viewBox.h}px`,
  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom.value})`,
  transformOrigin: '0 0',
}))

const dragCampo = ref(null)
let dragStart = null
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
  return campo.cor || CORES[campo.tipo] || '#9ca3af'
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
  })
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

function selecionar(campo) {
  selecionado.value = campo
  metrosEdit.largura = campo.metros?.largura ?? (campo.largura ? +(campo.largura / PX_POR_METRO).toFixed(1) : null)
  metrosEdit.altura = campo.metros?.altura ?? (campo.altura ? +(campo.altura / PX_POR_METRO).toFixed(1) : null)
  if (campo.tipo === 'canteiro' && !campo.config) {
    campo.config = { linhas: 4, colunas: 4, capacidade: 16 }
  }
}

function marcarDirty() {
  ajustarViewBox()
}

function aplicarMetros() {
  const c = selecionado.value
  if (!c) return
  const largura = Number(metrosEdit.largura)
  const altura = Number(metrosEdit.altura)
  if (largura > 0 && altura > 0) {
    c.metros = { largura, altura }
    c.largura = Math.round(largura * PX_POR_METRO)
    c.altura = Math.round(altura * PX_POR_METRO)
    ajustarViewBox()
  }
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
  const pad = 56
  const { minX, minY, maxX, maxY } = boundsConteudo()
  const bw = Math.max(80, maxX - minX)
  const bh = Math.max(60, maxY - minY)
  const cw = el.clientWidth
  const ch = el.clientHeight
  const scaleX = (cw - pad * 2) / bw
  const scaleY = (ch - pad * 2) / bh
  zoom.value = Math.min(2.5, Math.max(0.2, Math.min(scaleX, scaleY, 1.25)))
  pan.x = (cw - bw * zoom.value) / 2 - minX * zoom.value
  pan.y = (ch - bh * zoom.value) / 2 - minY * zoom.value
}

function zoomUmParaUm() {
  zoom.value = 1
  const el = canvasEl.value
  if (!el || !planta.campos.length) {
    pan.x = 40
    pan.y = 40
    return
  }
  const { minX, minY, maxX, maxY } = boundsConteudo()
  const bw = maxX - minX
  const bh = maxY - minY
  const cw = el.clientWidth
  const ch = el.clientHeight
  pan.x = (cw - bw) / 2 - minX
  pan.y = (ch - bh) / 2 - minY
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
  if (spacePan.value) {
    iniciarPan(event)
    return
  }
  selecionar(campo)
  dragCampo.value = campo
  const p = svgPoint(event)
  dragStart = { px: p.x, py: p.y, ox: campo.x, oy: campo.y }
  window.addEventListener('pointermove', onDragMove)
  window.addEventListener('pointerup', onDragEnd)
  window.addEventListener('pointercancel', onDragEnd)
}

function onDragMove(event) {
  if (!dragCampo.value || !dragStart) return
  const p = svgPoint(event)
  dragCampo.value.x = Math.max(0, dragStart.ox + (p.x - dragStart.px))
  dragCampo.value.y = Math.max(0, dragStart.oy + (p.y - dragStart.py))
  ajustarViewBox()
}

function onDragEnd() {
  dragCampo.value = null
  dragStart = null
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

function onKeyDown(event) {
  if (event.code === 'Space' && !event.repeat) {
    spacePan.value = true
    event.preventDefault()
  }
}

function onKeyUp(event) {
  if (event.code === 'Space') {
    spacePan.value = false
  }
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
  let data = {}
  try {
    data = await getViveiroLayout()
  } catch {
    /* layout vazio */
  }
  if (data?.campos?.length) {
    planta.campos = sanitizarCamposLayout(data.campos)
    planta.nome = data.nome || planta.nome
    if (data.viewBox?.width) viewBox.w = data.viewBox.width
    if (data.viewBox?.height) viewBox.h = data.viewBox.height
    layoutAoAbrir.value = data
  }
  ajustarViewBox()
  setTimeout(enquadrarTudo, 100)
}

onMounted(() => {
  carregarLayout()
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('keyup', onKeyUp)
})

onUnmounted(() => {
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
  () => ajustarViewBox()
)
</script>

<style scoped>
.layout-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: #ecece8;
}

.editor-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.65rem 1rem;
  background: #fff;
  border-bottom: 1px solid #e0e0dc;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.btn-ghost {
  border: none;
  background: none;
  color: var(--color-primary, #4a7c2a);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  padding: 0.35rem 0.5rem;
}

.btn-ghost-sm {
  border: none;
  background: none;
  font-size: 0.75rem;
  color: #666;
  cursor: pointer;
  font-family: inherit;
}

.btn-primary {
  padding: 0.45rem 0.9rem;
  border: none;
  border-radius: 8px;
  background: var(--color-primary, #4a7c2a);
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  font-family: inherit;
}

.btn-save {
  padding: 0.45rem 1rem;
  border: none;
  border-radius: 8px;
  background: #2d5016;
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  font-family: inherit;
}

.btn-save:disabled {
  opacity: 0.55;
}

.zoom-bar {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.4rem;
  background: #f4f4f2;
  border-radius: 8px;
  border: 1px solid #e0e0dc;
  font-size: 0.75rem;
  font-weight: 600;
  color: #555;
}

.btn-icon {
  width: 28px;
  height: 28px;
  border: none;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-family: inherit;
}

.erro-bar {
  margin: 0;
  padding: 0.5rem 1rem;
  background: #fef3f2;
  color: #b42318;
  font-size: 0.8125rem;
  border-bottom: 1px solid #fecaca;
}

.editor-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 340px);
  flex: 1;
  min-height: 0;
  gap: 0;
}

.canvas {
  position: relative;
  min-height: 0;
  overflow: hidden;
  cursor: grab;
  background: #d8d8d4;
  background-image: radial-gradient(circle at 1px 1px, #c4c4be 1px, transparent 0);
  background-size: 20px 20px;
}

.canvas--panning {
  cursor: grabbing;
  user-select: none;
}

.canvas--dragging {
  cursor: move;
}

.canvas-inner {
  position: absolute;
  top: 0;
  left: 0;
  will-change: transform;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
}

.mapa-svg {
  display: block;
  background: #f7f7f4;
  border: 1px solid #b8b8b2;
  border-radius: 2px;
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

.canvas-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  margin: 0;
  padding: 0.4rem 0.75rem;
  font-size: 0.6875rem;
  color: #555;
  background: rgba(255, 255, 255, 0.92);
  border-top: 1px solid #d0d0ca;
  pointer-events: none;
  z-index: 2;
}

.area-grupo--sel rect:first-child {
  filter: drop-shadow(0 2px 8px rgba(45, 80, 22, 0.35));
}

.lbl-tipo {
  font-size: 9px;
  font-weight: 700;
  fill: rgba(0, 0, 0, 0.55);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  pointer-events: none;
}

.lbl-nome {
  font-size: 12px;
  font-weight: 600;
  fill: #1a1a1a;
  pointer-events: none;
}

.lbl-badge {
  font-size: 11px;
  font-weight: 700;
  fill: #1a1a1a;
  pointer-events: none;
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
  color: #666;
  font-size: 0.9375rem;
  pointer-events: none;
}

.inspector {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  background: #fafaf9;
  border-left: 1px solid #e0e0dc;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.04);
}

.inspector-top {
  flex-shrink: 0;
  padding: 1rem 1rem 0.75rem;
  background: #fff;
  border-bottom: 1px solid #ebebe8;
}

.inspector-top--lista {
  padding-bottom: 0.5rem;
}

.inspector-body {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 0.85rem 1rem 1rem;
  -webkit-overflow-scrolling: touch;
}

.inspector-footer {
  flex-shrink: 0;
  padding: 0.75rem 1rem 1rem;
  background: #fff;
  border-top: 1px solid #ebebe8;
}

.inspector-title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1a1a1a;
}

.inspector-hint {
  margin: 0.35rem 0 0;
  font-size: 0.8125rem;
  color: #666;
  line-height: 1.4;
}

.inspector-tipo {
  display: inline-block;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #4a7c2a;
  background: #eef4e8;
  padding: 0.2rem 0.45rem;
  border-radius: 4px;
  margin-bottom: 0.4rem;
}

.inspector-nome {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 600;
  line-height: 1.35;
  word-break: break-word;
  overflow-wrap: anywhere;
  color: #1a1a1a;
}

.inspector-secao {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #fff;
  border: 1px solid #ebebe8;
  border-radius: 10px;
}

.inspector-secao-titulo {
  margin: 0 0 0.65rem;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #888;
}

.ocupacao-card {
  background: linear-gradient(180deg, #f4f7f0 0%, #eef4e8 100%);
  border: 1px solid #d4e4c8;
  border-radius: 10px;
  padding: 0.85rem 0.75rem;
  margin-bottom: 0.85rem;
  text-align: center;
}

.ocupacao-num {
  display: block;
  font-size: 1.375rem;
  font-weight: 700;
  color: #2d5016;
  line-height: 1.2;
}

.ocupacao-leg {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.6875rem;
  color: #666;
  line-height: 1.35;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #555;
  min-width: 0;
}

.field--last {
  margin-bottom: 0;
}

.field input {
  width: 100%;
  box-sizing: border-box;
  min-width: 0;
  padding: 0.5rem 0.6rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  font-family: inherit;
  background: #fff;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.field input:focus {
  outline: none;
  border-color: #4a7c2a;
  box-shadow: 0 0 0 3px rgba(74, 124, 42, 0.15);
}

.field-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 0.5rem;
}

.field-row .field {
  margin-bottom: 0;
}

.hint {
  margin: 0.5rem 0 0;
  font-size: 0.8125rem;
  color: #666;
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
  background: #fef3f2;
  color: #b42318;
  border: 1px solid #fecaca;
}

.btn-danger {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: none;
  border-radius: 8px;
  background: #dc2626;
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s ease, opacity 0.15s ease;
}

.btn-danger:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-danger:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.lista-areas {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.lista-vazia {
  padding: 1.5rem 0.5rem;
  text-align: center;
  font-size: 0.8125rem;
  color: #888;
}

.lista-btn {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 0.55rem 0.65rem;
  border: 1px solid #e8e8e4;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.lista-btn:hover {
  border-color: #4a7c2a;
  background: #f4f7f0;
}

.lista-cor {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.lista-texto {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
  flex: 1;
}

.lista-texto strong {
  font-size: 0.8125rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lista-texto small {
  font-size: 0.6875rem;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  background: #fff;
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
  color: #555;
}

.dialog-erro {
  color: #b42318;
}

.dialog-acoes {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

@media (max-width: 900px) {
  .editor-main {
    grid-template-columns: 1fr;
    grid-template-rows: minmax(0, 1fr) auto;
  }

  .inspector {
    border-left: none;
    border-top: 1px solid #e0e0dc;
    max-height: min(42vh, 360px);
    box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.06);
  }
}
</style>
