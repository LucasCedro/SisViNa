<template>
  <div class="mapa-seletor">
    <div class="mapa-seletor__toolbar">
      <p class="mapa-seletor__hint">
        Clique no mapa ou arraste o marcador. Você também pode usar o GPS do aparelho.
      </p>
      <div class="mapa-seletor__acoes">
        <button type="button" class="btn btn-secondary btn-sm" :disabled="buscandoGps" @click="usarMinhaLocalizacao">
          {{ buscandoGps ? 'Localizando…' : 'Minha localização' }}
        </button>
        <button v-if="temPonto" type="button" class="btn btn-outline btn-sm" @click="limparPonto">
          Limpar marcação
        </button>
      </div>
    </div>

    <div ref="mapEl" class="mapa-seletor__mapa" :class="{ 'mapa-seletor__mapa--inativo': !ativo }" />

    <p v-if="temPonto" class="mapa-seletor__coords">
      <strong>Selecionado:</strong>
      Lat {{ formatCoord(latitude) }}, Lng {{ formatCoord(longitude) }}
      <span v-if="utmPreview" class="mapa-seletor__utm">
        · UTM zona {{ utmPreview.zona }}: E {{ utmPreview.easting }}, N {{ utmPreview.northing }}
      </span>
    </p>
    <p v-else class="mapa-seletor__coords mapa-seletor__coords--vazio">
      Nenhum ponto marcado — clique no mapa para definir a matriz.
    </p>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useColetaStore } from '@/store/coleta'
import { criarIconeMatriz } from '@/utils/mapaMatriz'
import { latLngParaUtm } from '@/utils/coordenadas'

const props = defineProps({
  latitude: { type: Number, default: null },
  longitude: { type: Number, default: null },
  /** Modal aberto — força redraw do Leaflet */
  ativo: { type: Boolean, default: true },
  /** ID da matriz em edição (não exibir como referência) */
  excluirMatrizId: { type: Number, default: null },
  utmZona: { type: Number, default: null },
})

const emit = defineEmits(['update:latitude', 'update:longitude', 'coordenadas'])

const store = useColetaStore()
const mapEl = ref(null)
const buscandoGps = ref(false)

let map = null
let marker = null
let refLayer = null
const iconeRef = criarIconeMatriz()
const iconeSelecao = L.divIcon({
  className: 'marcador-matriz-selecao',
  html: '<div class="marcador-matriz-selecao__pin"></div>',
  iconSize: [28, 28],
  iconAnchor: [14, 28],
})

const temPonto = computed(
  () =>
    props.latitude != null &&
    props.longitude != null &&
    !Number.isNaN(props.latitude) &&
    !Number.isNaN(props.longitude)
)

const utmPreview = computed(() => {
  if (!temPonto.value) return null
  try {
    return latLngParaUtm(props.latitude, props.longitude, props.utmZona || undefined)
  } catch {
    return null
  }
})

function formatCoord(v) {
  if (v == null || Number.isNaN(v)) return '—'
  return Number(v).toFixed(6)
}

function emitirCoordenadas(lat, lng) {
  const la = +Number(lat).toFixed(7)
  const lo = +Number(lng).toFixed(7)
  emit('update:latitude', la)
  emit('update:longitude', lo)
  emit('coordenadas', { latitude: la, longitude: lo, utm: latLngParaUtm(la, lo, props.utmZona || undefined) })
}

function posicionarMarcador(lat, lng, centralizar = false) {
  if (!map) return
  const ll = [lat, lng]
  if (marker) {
    marker.setLatLng(ll)
  } else {
    marker = L.marker(ll, { icon: iconeSelecao, draggable: true }).addTo(map)
    marker.on('dragend', () => {
      const { lat: la, lng: lo } = marker.getLatLng()
      emitirCoordenadas(la, lo)
    })
  }
  if (centralizar) map.setView(ll, Math.max(map.getZoom(), 14))
}

function limparPonto() {
  if (marker && map) {
    map.removeLayer(marker)
    marker = null
  }
  emit('update:latitude', null)
  emit('update:longitude', null)
}

function atualizarReferencias() {
  if (!refLayer) return
  refLayer.clearLayers()
  const bounds = []

  store.arvoresMatriz.forEach((a) => {
    if (props.excluirMatrizId && a.id === props.excluirMatrizId) return
    const lat = Number(a.latitude)
    const lng = Number(a.longitude)
    if (Number.isNaN(lat) || Number.isNaN(lng)) return
    const m = L.marker([lat, lng], {
      icon: iconeRef,
      opacity: 0.55,
      interactive: false,
    })
    refLayer.addLayer(m)
    bounds.push([lat, lng])
  })

  if (temPonto.value) bounds.push([props.latitude, props.longitude])
  if (bounds.length === 1 && map) map.setView(bounds[0], 12)
  else if (bounds.length > 1 && map) map.fitBounds(bounds, { padding: [24, 24], maxZoom: 14 })
}

function usarMinhaLocalizacao() {
  if (!navigator.geolocation) {
    alert('Geolocalização não disponível neste navegador.')
    return
  }
  buscandoGps.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      buscandoGps.value = false
      emitirCoordenadas(pos.coords.latitude, pos.coords.longitude)
      posicionarMarcador(pos.coords.latitude, pos.coords.longitude, true)
    },
    () => {
      buscandoGps.value = false
      alert('Não foi possível obter sua localização. Verifique permissões do navegador.')
    },
    { enableHighAccuracy: true, timeout: 15000 }
  )
}

function initMap() {
  if (!mapEl.value || map) return

  const centro =
    temPonto.value ? [props.latitude, props.longitude] : [-15.78, -47.93]
  const zoom = temPonto.value ? 14 : 5

  map = L.map(mapEl.value, { center: centro, zoom, zoomControl: false })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap',
  }).addTo(map)

  L.control.zoom({ position: 'topright' }).addTo(map)
  refLayer = L.layerGroup().addTo(map)

  map.on('click', (e) => {
    emitirCoordenadas(e.latlng.lat, e.latlng.lng)
    posicionarMarcador(e.latlng.lat, e.latlng.lng)
  })

  if (temPonto.value) posicionarMarcador(props.latitude, props.longitude)
  atualizarReferencias()
}

function invalidate() {
  nextTick(() => {
    map?.invalidateSize()
    atualizarReferencias()
  })
}

watch(
  () => [props.latitude, props.longitude],
  ([lat, lng]) => {
    if (!map) return
    if (lat != null && lng != null && !Number.isNaN(lat) && !Number.isNaN(lng)) {
      posicionarMarcador(lat, lng)
    } else if (marker) {
      map.removeLayer(marker)
      marker = null
    }
  }
)

watch(
  () => props.ativo,
  (on) => {
    if (on) {
      if (!map) initMap()
      else invalidate()
    }
  }
)

watch(
  () => store.arvoresMatriz.length,
  () => atualizarReferencias()
)

onMounted(() => {
  if (props.ativo) initMap()
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
    marker = null
    refLayer = null
  }
})

defineExpose({ invalidate })
</script>

<style scoped>
.mapa-seletor {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mapa-seletor__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.mapa-seletor__hint {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  flex: 1 1 12rem;
  line-height: 1.4;
}

.mapa-seletor__acoes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.mapa-seletor__mapa {
  height: 280px;
  width: 100%;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
  background: var(--color-surface-muted);
}

.mapa-seletor__mapa--inativo {
  opacity: 0.6;
  pointer-events: none;
}

.mapa-seletor__coords {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  line-height: 1.45;
}

.mapa-seletor__coords--vazio {
  color: var(--color-text-muted);
  font-style: italic;
}

.mapa-seletor__utm {
  color: var(--color-text-muted);
}

:deep(.marcador-matriz-selecao) {
  background: transparent;
  border: none;
}

:deep(.marcador-matriz-selecao__pin) {
  width: 28px;
  height: 28px;
  background: var(--color-primary);
  border: 3px solid #fff;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}

:deep(.marcador-matriz-selecao__pin)::after {
  content: '';
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(45deg);
}
</style>
