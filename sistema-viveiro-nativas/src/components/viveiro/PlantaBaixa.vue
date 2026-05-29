<template>
  <div class="planta-baixa-wrap">
    <div ref="viewportRef" class="planta-viewport">
      <div class="planta-viewport-inner">
        <div
          class="planta-scaler"
          :style="{
            width: `${dimensoesEscaladas.w}px`,
            height: `${dimensoesEscaladas.h}px`,
          }"
        >
          <div
            class="planta-baixa"
            :style="{
              width: `${mapW}px`,
              height: `${mapH}px`,
              transform: `scale(${escala})`,
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
              @click="selecionarElemento(elemento.id)"
            >
              <span
                v-if="elemento.apiId && elemento.badgeOcupacao != null"
                class="ocupacao-badge"
                :class="{ 'ocupacao-badge--cheio': ocupacaoCheia(elemento) }"
              >
                {{ elemento.badgeOcupacao }}
              </span>
              <span v-if="temAlerta(elemento)" class="alerta-indicador" title="Alerta">!</span>
              <div class="elemento-rotulos">
                <span v-if="rotulosElemento(elemento).showTipo" class="elemento-tipo">
                  {{ rotuloTipo(elemento.tipo) }}
                </span>
                <span class="elemento-nome">{{ rotulosElemento(elemento).nomeExib }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <p class="mapa-dica">Clique em uma área para ver detalhes no painel à direita.</p>

    <div class="legenda" role="list" aria-label="Legenda">
      <span v-for="item in legenda" :key="item.label" class="legenda-item" role="listitem">
        <span class="cor-amostra" :style="{ backgroundColor: item.cor }" />
        {{ item.label }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useViveiroStore } from '@/store/viveiro'
import { rotulosMapaElemento } from '@/utils/viveiroAreaRotulos'

const PAD = 32
const store = useViveiroStore()
const viewportRef = ref(null)
const viewportSize = ref({ w: 800, h: 480 })

const layout = computed(() => store.layout)
const elementoSelecionado = computed(() => store.elementoSelecionado)
const alertas = computed(() => store.alertasAtivos)

const legenda = [
  { cor: '#C8A84B', label: 'Sementeira' },
  { cor: '#596247', label: 'Canteiro' },
  { cor: '#ffe135', label: 'Rustificação' },
  { cor: '#6b8cae', label: 'Sede' },
  { cor: '#4a9fd4', label: 'Água' },
  { cor: '#8E9089', label: 'Garagem' },
  { cor: '#A4B39A', label: 'Trabalho' },
]

const mapW = computed(() => Math.max(320, layout.value.dimensoes?.largura || 1000))
const mapH = computed(() => Math.max(240, layout.value.dimensoes?.altura || 400))

/** Escala para caber no viewport — arredondada para evitar loop de subpixel. */
const escala = computed(() => {
  const vw = viewportSize.value.w - PAD
  const vh = viewportSize.value.h - PAD
  if (vw <= 0 || vh <= 0) return 1
  const raw = Math.min(vw / mapW.value, vh / mapH.value, 1)
  return Math.floor(raw * 1000) / 1000
})

const dimensoesEscaladas = computed(() => ({
  w: Math.floor(mapW.value * escala.value),
  h: Math.floor(mapH.value * escala.value),
}))

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
})

onUnmounted(() => {
  ro?.disconnect()
})

const rotulosPorId = computed(() => {
  const map = {}
  for (const el of layout.value.elementos) {
    map[el.id] = rotulosMapaElemento({
      largura: el.dimensoes?.largura ?? 100,
      altura: el.dimensoes?.altura ?? 80,
      nome: el.nome,
      temBadge: el.apiId != null && el.badgeOcupacao != null,
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
  })

const estiloElemento = (elemento) => {
  const r = rotulosElemento(elemento)
  return {
    left: `${elemento.posicao.x}px`,
    top: `${elemento.posicao.y}px`,
    width: `${elemento.dimensoes?.largura ?? 100}px`,
    height: `${elemento.dimensoes?.altura ?? 80}px`,
    backgroundColor: elemento.cor,
    '--fs-tipo': r.fsTipo ? `${r.fsTipo}px` : '0',
    '--fs-nome': `${r.fsNome}px`,
    '--fs-badge': `${r.fsBadge}px`,
    '--el-pad': `${r.pad}px`,
  }
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
  if (el.badgeOcupacao != null && el.apiId) parts.push(`Ocupação: ${el.badgeOcupacao}`)
  return parts.join(' · ')
}

const temAlerta = (elemento) =>
  elemento.tipo === 'canteiro' && alertas.value.some((a) => a.canteiro === elemento.nome)

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
}

.planta-viewport {
  flex: 1;
  min-height: 0;
  height: clamp(360px, 56vh, 600px);
  overflow: hidden;
  background: repeating-conic-gradient(#e8e8e4 0% 25%, #f0f0ec 0% 50%) 50% / 16px 16px;
  contain: layout paint;
}

.planta-viewport-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  box-sizing: border-box;
}

.planta-scaler {
  position: relative;
  flex-shrink: 0;
  contain: layout size;
}

.planta-baixa {
  position: relative;
  transform-origin: top left;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow);
  backface-visibility: hidden;
}

.elemento {
  position: absolute;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  padding: var(--el-pad, 5px);
  overflow: hidden;
  transition: box-shadow 0.15s ease, outline 0.15s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}

.elemento-rotulos {
  margin-top: auto;
  width: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
  pointer-events: none;
}

.elemento:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 5;
}

.elemento.selecionado {
  outline: 3px solid var(--color-primary);
  outline-offset: 2px;
  z-index: 10;
}

.elemento-tipo {
  font-size: var(--fs-tipo, 9px);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  line-height: 1.15;
  color: rgba(0, 0, 0, 0.5);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.elemento-nome {
  font-size: var(--fs-nome, 11px);
  font-weight: 600;
  line-height: 1.2;
  color: rgba(0, 0, 0, 0.78);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-shadow:
    0 0 6px rgba(255, 255, 255, 0.9),
    0 1px 1px rgba(255, 255, 255, 0.7);
}

.elemento--layout-padrao {
  justify-content: flex-end;
}

.elemento--layout-padrao .ocupacao-badge {
  position: absolute;
  top: var(--el-pad, 5px);
  right: var(--el-pad, 5px);
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

.elemento--layout-minimal .elemento-tipo {
  display: none;
}

.elemento--layout-minimal:has(.ocupacao-badge) .elemento-nome {
  display: none;
}

.elemento--layout-minimal .ocupacao-badge {
  position: static;
}

.ocupacao-badge {
  flex-shrink: 0;
  padding: 1px 5px;
  font-size: var(--fs-badge, 10px);
  font-weight: 700;
  line-height: 1.25;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.9);
  color: rgba(0, 0, 0, 0.75);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  pointer-events: none;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ocupacao-badge--cheio {
  background: #fef3c7;
  color: #92400e;
}

.alerta-indicador {
  position: absolute;
  top: var(--el-pad, 5px);
  left: var(--el-pad, 5px);
  width: 14px;
  height: 14px;
  background: var(--color-error);
  color: #fff;
  border-radius: 50%;
  font-size: 9px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.mapa-dica {
  flex-shrink: 0;
  margin: 0;
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  background: var(--color-surface);
  border-top: 1px solid var(--color-border-subtle);
}

.legenda {
  flex-shrink: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm) var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-lg) var(--spacing-md);
  background: var(--color-surface);
}

.legenda-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.cor-amostra {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}
</style>
