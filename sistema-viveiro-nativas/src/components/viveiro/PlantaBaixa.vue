<template>
  <div class="planta-baixa-wrap">
    <div class="mapa-toolbar viveiro-toolbar" role="toolbar" aria-label="Controles do mapa">
      <div class="mapa-toolbar__controls">
        <div class="viveiro-toolbar__group">
          <button type="button" class="viveiro-toolbar__btn" title="Diminuir zoom" @click="ajustarZoom(-0.2)">−</button>
          <span class="viveiro-toolbar__label">{{ Math.round(zoomUsuario * 100) }}%</span>
          <button type="button" class="viveiro-toolbar__btn" title="Aumentar zoom" @click="ajustarZoom(0.2)">+</button>
        </div>
        <button type="button" class="viveiro-toolbar__btn viveiro-toolbar__btn--text" @click="enquadrar">Enquadrar</button>
        <button type="button" class="viveiro-toolbar__btn viveiro-toolbar__btn--text" @click="zoomUsuario = 1">100%</button>
        <span v-if="escalaMetros" class="mapa-escala" :title="`Escala: ${PX_POR_METRO} px por metro`">
          <span class="mapa-escala__bar" :style="{ width: `${escalaMetros}px` }" />
          {{ metrosBarra }} m
        </span>
      </div>
      <div v-if="legendaFiltrada.length" class="mapa-legenda-row" role="list" aria-label="Legenda">
        <span v-for="item in legendaFiltrada" :key="item.label" class="mapa-legenda-item" role="listitem">
          <span class="mapa-legenda-swatch" :style="{ backgroundColor: item.cor }" />
          {{ item.label }}
        </span>
      </div>
    </div>

    <div
      ref="viewportRef"
      class="planta-viewport viveiro-map-canvas-bg"
      :class="{ 'planta-viewport--panning': panning }"
      @wheel.prevent="onWheel"
      @pointerdown="onPanStart"
    >
      <div
        class="planta-stage"
        :style="stageStyle"
      >
        <div
          class="planta-baixa viveiro-map-surface"
          :style="{
            width: `${Math.floor(mapW * escalaTotal)}px`,
            height: `${Math.floor(mapH * escalaTotal)}px`,
          }"
        >
          <div
            v-for="elemento in layout.elementos"
            :key="elemento.id"
            :class="[
              'elemento',
              elemento.tipo,
              `elemento--layout-${rotulosElemento(elemento).layout}`,
              { selecionado: elementoSelecionado?.id === elemento.id },
            ]"
            :style="estiloElemento(elemento)"
            :title="tituloElemento(elemento)"
            @click.stop="selecionarElemento(elemento.id)"
          >
            <span
              v-if="elemento.apiId && elemento.badgeOcupacao != null"
              class="ocupacao-badge"
              :class="{ 'ocupacao-badge--cheio': ocupacaoCheia(elemento) }"
            >
              {{ elemento.badgeOcupacao }}
            </span>
            <div
              v-if="pendenciasElemento(elemento).length"
              class="pendencias-mapa"
              role="list"
              :aria-label="`Pendências em ${elemento.nome}`"
            >
              <button
                v-for="p in pendenciasElemento(elemento)"
                :key="p.tipo"
                type="button"
                role="listitem"
                class="pendencia-icone"
                :class="`pendencia-icone--${p.nivel}`"
                :title="`${p.titulo} (${p.count})`"
                @click.stop="irPendencia(p)"
              >
                <span class="pendencia-icone-sym" aria-hidden="true">{{ p.icone }}</span>
                <span class="pendencia-icone-qtd">{{ p.count }}</span>
              </button>
            </div>
            <div class="elemento-rotulos">
              <span v-if="rotulosElemento(elemento).showTipo" class="elemento-tipo">
                {{ rotuloTipo(elemento.tipo) }}
              </span>
              <span v-if="rotulosElemento(elemento).metrosExib" class="elemento-metros">
                {{ rotulosElemento(elemento).metrosExib }}
              </span>
              <span class="elemento-nome">{{ rotulosElemento(elemento).nomeExib }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useViveiroStore } from '@/store/viveiro'
import { rotulosMapaElemento } from '@/utils/viveiroAreaRotulos'
import { PX_POR_METRO } from '@/constants/viveiroDimensoes'
import { pendenciasDoCanteiro } from '@/utils/viveiroPendenciasMapa'
import { VIVEIRO_LEGENDA } from '@/constants/viveiroMapColors'

const PAD = 24
const store = useViveiroStore()
const router = useRouter()
const viewportRef = ref(null)
const viewportSize = ref({ w: 800, h: 480 })
const zoomUsuario = ref(1)
const pan = ref({ x: 0, y: 0 })
const panning = ref(false)
let panStart = null

const layout = computed(() => store.layout)
const elementoSelecionado = computed(() => store.elementoSelecionado)
const LEGENDA_TODOS = VIVEIRO_LEGENDA

const legendaFiltrada = computed(() => {
  const tipos = new Set((layout.value.elementos || []).map((e) => e.tipo))
  return LEGENDA_TODOS.filter((l) => l.tipos.some((t) => tipos.has(t)))
})

const mapW = computed(() => Math.max(320, layout.value.dimensoes?.largura || 1000))
const mapH = computed(() => Math.max(240, layout.value.dimensoes?.altura || 400))

const escalaBase = computed(() => {
  const vw = viewportSize.value.w - PAD * 2
  const vh = viewportSize.value.h - PAD * 2
  if (vw <= 0 || vh <= 0) return 1
  const fit = Math.min(vw / mapW.value, vh / mapH.value)
  // Não encolhe demais: legível mesmo em plantas grandes
  return Math.max(fit, 0.55)
})

const escalaTotal = computed(() => escalaBase.value * zoomUsuario.value)

const stageStyle = computed(() => ({
  width: `${Math.floor(mapW.value * escalaTotal.value)}px`,
  height: `${Math.floor(mapH.value * escalaTotal.value)}px`,
  transform: `translate(${pan.value.x}px, ${pan.value.y}px)`,
}))

const escalaMetros = computed(() => Math.round(PX_POR_METRO * escalaTotal.value))
const metrosBarra = computed(() => {
  const px = escalaMetros.value
  if (px >= PX_POR_METRO * 0.85) return 1
  if (px >= PX_POR_METRO * 0.4) return 2
  return 5
})

function medirViewport() {
  const el = viewportRef.value
  if (!el) return
  const w = el.clientWidth
  const h = el.clientHeight
  if (Math.abs(w - viewportSize.value.w) <= 2 && Math.abs(h - viewportSize.value.h) <= 2) return
  viewportSize.value = { w, h }
}

let ro
onMounted(() => {
  medirViewport()
  ro = new ResizeObserver(() => medirViewport())
  if (viewportRef.value) ro.observe(viewportRef.value)
  requestAnimationFrame(() => {
    medirViewport()
    enquadrar()
  })
})

onUnmounted(() => {
  ro?.disconnect()
  window.removeEventListener('pointermove', onPanMove)
  window.removeEventListener('pointerup', onPanEnd)
  window.removeEventListener('pointercancel', onPanEnd)
})

const rotulosPorId = computed(() => {
  const map = {}
  for (const el of layout.value.elementos) {
    map[el.id] = rotulosMapaElemento({
      largura: el.dimensoes?.largura ?? 100,
      altura: el.dimensoes?.altura ?? 80,
      nome: el.nome,
      temBadge: el.apiId != null && el.badgeOcupacao != null,
      metros: el.metros,
    })
  }
  return map
})

const rotulosElemento = (elemento) =>
  rotulosPorId.value[elemento.id] ||
  rotulosMapaElemento({
    largura: elemento.dimensoes?.largura ?? 100,
    altura: elemento.dimensoes?.altura ?? 80,
    nome: elemento.nome,
    temBadge: elemento.apiId != null && elemento.badgeOcupacao != null,
    metros: elemento.metros,
  })

const estiloElemento = (elemento) => {
  const r = rotulosElemento(elemento)
  const s = escalaTotal.value
  return {
    left: `${elemento.posicao.x * s}px`,
    top: `${elemento.posicao.y * s}px`,
    width: `${(elemento.dimensoes?.largura ?? 100) * s}px`,
    height: `${(elemento.dimensoes?.altura ?? 80) * s}px`,
    backgroundColor: elemento.cor,
    '--fs-tipo': r.fsTipo ? `${r.fsTipo * s}px` : '0',
    '--fs-nome': `${r.fsNome * s}px`,
    '--fs-badge': `${r.fsBadge * s}px`,
    '--fs-metros': `${Math.max(7, (r.fsTipo || 9) * s * 0.9)}px`,
    '--el-pad': `${r.pad * s}px`,
  }
}

function pendenciasElemento(elemento) {
  return pendenciasDoCanteiro(store.pendenciasPorCanteiro, elemento.apiId)
}

function irPendencia(p) {
  if (p?.rota) router.push(p.rota)
}

function ajustarZoom(delta) {
  zoomUsuario.value = Math.min(4, Math.max(0.25, +(zoomUsuario.value + delta).toFixed(2)))
}

function onWheel(e) {
  const delta = e.deltaY > 0 ? -0.12 : 0.12
  ajustarZoom(delta)
}

function enquadrar() {
  zoomUsuario.value = 1
  pan.value = { x: 0, y: 0 }
}

function onPanStart(e) {
  if (e.button !== 0) return
  if (e.target.closest('.elemento')) return
  panning.value = true
  panStart = { x: e.clientX - pan.value.x, y: e.clientY - pan.value.y, id: e.pointerId }
  e.currentTarget.setPointerCapture?.(e.pointerId)
  window.addEventListener('pointermove', onPanMove)
  window.addEventListener('pointerup', onPanEnd)
  window.addEventListener('pointercancel', onPanEnd)
}

function onPanMove(e) {
  if (!panning.value || !panStart) return
  pan.value = { x: e.clientX - panStart.x, y: e.clientY - panStart.y }
}

function onPanEnd() {
  panning.value = false
  panStart = null
  window.removeEventListener('pointermove', onPanMove)
  window.removeEventListener('pointerup', onPanEnd)
  window.removeEventListener('pointercancel', onPanEnd)
}

const rotuloTipo = (tipo) => {
  const map = {
    canteiro: 'Canteiro',
    sementeira: 'Sementeira',
    rustificacao: 'Rustificação',
    sede: 'Sede',
    lago: 'Água',
    garagem: 'Garagem',
    'area-trabalho': 'Trabalho',
    armazenamento: 'Armazém',
  }
  return map[tipo] || tipo
}

const tituloElemento = (el) => {
  const parts = [el.nome, rotuloTipo(el.tipo)]
  if (el.metros?.largura) parts.push(`${el.metros.largura}×${el.metros.altura} m`)
  if (el.badgeOcupacao != null && el.apiId) parts.push(`Ocupação: ${el.badgeOcupacao}`)
  return parts.join(' · ')
}

const selecionarElemento = (elementoId) => store.selecionarElemento(elementoId)

const ocupacaoCheia = (elemento) => {
  if (!elemento.capacidade) return (elemento.totalPlantas || 0) > 0
  return (elemento.totalPlantas || 0) >= elemento.capacidade
}
</script>

<style scoped>
.planta-baixa-wrap {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  height: 100%;
  user-select: none;
}

.mapa-toolbar {
  flex-direction: column;
  align-items: stretch;
  gap: 0;
  padding: 1rem 1.75rem;
}

.mapa-toolbar__controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.875rem;
}

.mapa-escala {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-left: auto;
}

.mapa-legenda-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.625rem 1.25rem;
  margin-top: 0.875rem;
  padding-top: 0.875rem;
  border-top: 1px solid var(--color-border-subtle);
}

.mapa-legenda-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.mapa-escala__bar {
  display: inline-block;
  height: 3px;
  background: var(--color-neutral-medium);
  border-radius: 2px;
  border-left: 1px solid var(--color-text-primary);
  border-right: 1px solid var(--color-text-primary);
}

.mapa-legenda-swatch {
  width: 11px;
  height: 11px;
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.planta-viewport {
  flex: 1;
  min-height: 480px;
  overflow: hidden;
  cursor: grab;
  padding: 1.25rem 1.75rem;
  box-sizing: border-box;
}

.planta-viewport--panning {
  cursor: grabbing;
}

.planta-stage {
  position: relative;
  margin: auto;
  will-change: transform;
}

.planta-baixa {
  position: relative;
  backface-visibility: hidden;
}

.elemento {
  position: absolute;
  border-radius: 5px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  padding: var(--el-pad, 6px);
  overflow: hidden;
  transition: box-shadow 0.15s ease, outline 0.15s ease, filter 0.15s ease;
  border: 1px solid rgba(0, 0, 0, 0.12);
  box-sizing: border-box;
}

.elemento-rotulos {
  position: relative;
  z-index: 1;
  margin-top: auto;
  width: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
  pointer-events: none;
}

.elemento:hover {
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
  filter: brightness(1.03);
  z-index: 5;
}

.elemento.selecionado {
  outline: 3px solid var(--color-primary);
  outline-offset: 1px;
  z-index: 10;
  box-shadow: 0 6px 20px rgba(45, 80, 22, 0.25);
}

.elemento-tipo {
  font-size: var(--fs-tipo, 9px);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  line-height: 1.15;
  color: rgba(0, 0, 0, 0.5);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.elemento-metros {
  font-size: var(--fs-metros, 8px);
  font-weight: 600;
  color: rgba(0, 0, 0, 0.42);
  line-height: 1.1;
}

.elemento-nome {
  font-size: var(--fs-nome, 11px);
  font-weight: 600;
  line-height: 1.2;
  color: rgba(0, 0, 0, 0.82);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-shadow:
    0 0 6px rgba(255, 255, 255, 0.95),
    0 1px 2px rgba(255, 255, 255, 0.8);
}

.elemento--layout-padrao {
  justify-content: flex-end;
}

.elemento--layout-padrao .ocupacao-badge {
  position: absolute;
  top: var(--el-pad, 5px);
  right: var(--el-pad, 5px);
  z-index: 2;
}

.elemento--layout-stacked {
  justify-content: flex-start;
}

.elemento--layout-stacked .elemento-rotulos {
  margin-top: 0;
  flex: 1;
  min-height: 0;
}

.elemento--layout-stacked .ocupacao-badge {
  position: static;
  align-self: flex-start;
  margin-bottom: 2px;
  order: -1;
  z-index: 2;
}

.elemento--layout-faixa-v {
  justify-content: space-between;
  align-items: center;
  text-align: center;
}

.elemento--layout-faixa-v .elemento-rotulos {
  margin: auto 0;
  align-items: center;
  flex: 1;
  justify-content: center;
  gap: 3px;
}

.elemento--layout-faixa-v .elemento-nome {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  white-space: nowrap;
  max-height: 72%;
  text-overflow: ellipsis;
  overflow: hidden;
}

.elemento--layout-faixa-v .ocupacao-badge {
  position: absolute;
  bottom: var(--el-pad, 5px);
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
}

.elemento--layout-faixa-h {
  justify-content: center;
}

.elemento--layout-faixa-h .elemento-rotulos {
  margin: 0;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  width: 100%;
}

.elemento--layout-faixa-h .elemento-tipo {
  flex: 0 0 auto;
  max-width: 28%;
}

.elemento--layout-faixa-h .elemento-nome {
  flex: 1 1 auto;
  text-align: center;
}

.elemento--layout-faixa-h .elemento-metros {
  position: absolute;
  bottom: var(--el-pad, 4px);
  left: 50%;
  transform: translateX(-50%);
}

.elemento--layout-faixa-h .ocupacao-badge {
  position: absolute;
  top: var(--el-pad, 5px);
  right: var(--el-pad, 5px);
  z-index: 2;
}

.elemento--layout-minimal {
  justify-content: center;
  align-items: center;
}

.elemento--layout-minimal .elemento-rotulos {
  margin: 0;
  text-align: center;
  align-items: center;
}

.elemento--layout-minimal .elemento-tipo,
.elemento--layout-minimal .elemento-metros {
  display: none;
}

.elemento--layout-minimal:has(.ocupacao-badge) .elemento-nome {
  display: none;
}

.elemento--layout-minimal .ocupacao-badge {
  position: static;
  z-index: 2;
}

.ocupacao-badge {
  flex-shrink: 0;
  padding: 1px 5px;
  font-size: var(--fs-badge, 10px);
  font-weight: 700;
  line-height: 1.25;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.92);
  color: rgba(0, 0, 0, 0.75);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  pointer-events: none;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ocupacao-badge--cheio {
  background: var(--color-attention-bg);
  color: var(--color-text-secondary);
}

.pendencias-mapa {
  position: absolute;
  top: var(--el-pad, 4px);
  left: var(--el-pad, 4px);
  right: auto;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
  z-index: 4;
  pointer-events: none;
  max-width: calc(100% - var(--el-pad, 4px) * 2);
}

.elemento--layout-faixa-v .pendencias-mapa,
.elemento--layout-minimal .pendencias-mapa {
  left: auto;
  right: var(--el-pad, 4px);
  align-items: flex-end;
}

.pendencia-icone {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 1px 4px 1px 3px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 6px;
  background: var(--color-surface);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
  cursor: pointer;
  font-family: inherit;
  line-height: 1;
  pointer-events: auto;
}

.pendencia-icone:hover {
  filter: brightness(0.97);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.16);
}

.pendencia-icone--alto {
  border-color: var(--color-error-bg);
  background: var(--color-error-bg);
}

.pendencia-icone--medio {
  border-color: var(--color-attention-bg);
  background: var(--color-attention-bg);
}

.pendencia-icone-sym {
  font-size: calc(var(--fs-badge, 10px) + 1px);
  font-weight: 800;
  line-height: 1;
}

.pendencia-icone-qtd {
  font-size: calc(var(--fs-badge, 10px) - 1px);
  font-weight: 700;
  color: rgba(0, 0, 0, 0.7);
  min-width: 0.65rem;
  text-align: center;
}

@media (max-width: 720px) {
  .mapa-escala {
    margin-left: 0;
  }
}
</style>
