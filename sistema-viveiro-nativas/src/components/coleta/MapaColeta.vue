<template>
  <div class="card mapa-card">
    <div class="mapa-header">
      <h3 class="card-title">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        Mapa de matrizes
      </h3>
      <!-- Contador: edite o texto aqui (linha ~12) -->
      <!-- <span class="contador">{{ store.matrizesFiltradas.length }} no mapa</span> -->
    </div>

    <div class="mapa-layout">
      <div class="mapa-container">
        <div ref="mapContainer" class="mapa-content"></div>
      </div>

      <MatrizPainelDetalhe
        @editar="emit('editar', $event)"
        @coletar="emit('coletar', $event)"
        @editar-coleta="emit('editar-coleta', $event)"
        @teste="emit('teste', $event)"
        @semeadura="emit('semeadura', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useColetaStore } from '@/store/coleta'
import { criarIconeMatriz } from '@/utils/mapaMatriz'
import MatrizPainelDetalhe from '@/components/coleta/MatrizPainelDetalhe.vue'

const emit = defineEmits(['editar', 'coletar', 'editar-coleta', 'teste', 'semeadura'])

const store = useColetaStore()
const mapContainer = ref(null)
let map = null
let markersLayer = null
const iconeArvore = criarIconeMatriz()

function formatarData(data) {
  if (!data) return '—'
  return new Date(data).toLocaleDateString('pt-BR')
}

function localizacao(arvore) {
  const partes = [arvore.cidade, arvore.estado].filter(Boolean)
  return partes.length ? partes.join(' / ') : '—'
}

function popupHtml(arvore) {
  return `
    <div class="popup-content">
      <h3>${arvore.especie_nome || 'Matriz'}</h3>
      <p><strong>Nome:</strong> ${arvore.nome}</p>
      <p><strong>Local:</strong> ${localizacao(arvore)}</p>
      <p><strong>Lat/Lng:</strong> ${arvore.latitude}, ${arvore.longitude}</p>
      <p><em>Clique para ver detalhes e editar</em></p>
    </div>
  `
}

function atualizarMarcadores() {
  if (!map || !markersLayer) return
  markersLayer.clearLayers()
  const bounds = []

  store.matrizesFiltradas.forEach((arvore) => {
    const lat = Number(arvore.latitude)
    const lng = Number(arvore.longitude)
    if (Number.isNaN(lat) || Number.isNaN(lng)) return

    const marker = L.marker([lat, lng], { icon: iconeArvore })
    marker.bindPopup(popupHtml(arvore))
    marker.on('click', () => store.selecionar(arvore))
    markersLayer.addLayer(marker)
    bounds.push([lat, lng])
  })

  if (bounds.length === 1) {
    map.setView(bounds[0], 12)
  } else if (bounds.length > 1) {
    map.fitBounds(bounds, { padding: [40, 40] })
  }
}

onMounted(() => {
  if (!mapContainer.value) return

  map = L.map(mapContainer.value, {
    center: [-15.7801, -47.9292],
    zoom: 4,
    zoomControl: false
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  }).addTo(map)

  L.control.zoom({ position: 'topright' }).addTo(map)
  markersLayer = L.layerGroup().addTo(map)
  atualizarMarcadores()
})

watch(() => store.matrizesFiltradas, atualizarMarcadores, { deep: true })

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style scoped>
.card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: var(--spacing-lg);
  width: 100%;
}

.mapa-card {
  position: relative;
  min-height: 600px;
}

.mapa-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
}

.contador {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.mapa-layout {
  display: flex;
  gap: 1rem;
  height: calc(600px - 3rem);
}

.mapa-container {
  flex: 1;
  border-radius: 0.375rem;
  overflow: hidden;
  min-height: 0;
}

.mapa-content {
  width: 100%;
  height: 100%;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: var(--radius-md);
}

:deep(.popup-content h3) {
  font-weight: 700;
  font-size: 0.9375rem;
  margin-bottom: 0.35rem;
}

:deep(.popup-content p) {
  font-size: 0.8125rem;
  margin: 0.15rem 0;
}

@media (max-width: 900px) {
  .mapa-layout {
    flex-direction: column;
    height: auto;
  }

  .mapa-container {
    height: 420px;
  }

}
</style>
