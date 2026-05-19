<template>
  <div class="card mapa-card">
    <h3 class="card-title">
      <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      Mapa de Coleta
    </h3>
    <div class="mapa-container">
      <div id="map" ref="mapContainer" class="mapa-content"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useColetaStore } from '../../store/coleta'

const store = useColetaStore()
const mapContainer = ref(null)
let map = null
const markers = []

onMounted(() => {
  if (mapContainer.value) {
    // Inicializar o mapa
    map = L.map(mapContainer.value, {
      center: [-15.7801, -47.9292], // Brasil central
      zoom: 4,
      zoomControl: false
    })

    // Adicionar o layer de tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map)

    // Adicionar controles de zoom
    L.control.zoom({
      position: 'topright'
    }).addTo(map)

    // Adicionar marcadores de árvores
    store.arvoresMatriz.forEach(arvore => {
      if (arvore.latitude && arvore.longitude) {
        const marker = L.marker([arvore.latitude, arvore.longitude]).addTo(map)

        // Adicionar popup
        const popupContent = `
          <div class="popup-content">
            <h3>${arvore.especie}</h3>
            <p><strong>Nome:</strong> ${arvore.nome}</p>
            <p><strong>Latitude:</strong> ${arvore.latitude}</p>
            <p><strong>Longitude:</strong> ${arvore.longitude}</p>
            <p><strong>Sementes Coletadas:</strong> ${arvore.sementes_coletadas}</p>
            <p><strong>Taxa de Germinação:</strong> ${arvore.taxa_germinacao}%</p>
          </div>
        `
        marker.bindPopup(popupContent)
        markers.push(marker)
      }
    })

    // Ajustar o zoom para mostrar todos os marcadores
    if (markers.length > 0) {
      const group = new L.featureGroup(markers)
      map.fitBounds(group.getBounds().pad(0.1))
    }
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style>
.card {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: var(--spacing-lg);
  width: 100%;
}

.mapa-card {
  position: relative;
  height: 600px !important;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
}

.mapa-container {
  position: relative;
  height: calc(100% - 3rem);
  border-radius: 0.375rem;
  overflow: hidden;
}

.mapa-content {
  width: 100%;
  height: 100%;
}

/* Estilos do Leaflet */
:deep(.leaflet-control-zoom) {
  margin-top: 10px;
  margin-right: 10px;
  border: none;
}

:deep(.leaflet-control-zoom a) {
  background-color: white;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

:deep(.leaflet-control-zoom a:hover) {
  background-color: var(--color-background);
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: var(--radius-md);
}

:deep(.leaflet-popup-content) {
  margin: 0;
  padding: 1rem;
  min-width: 200px;
}

:deep(.leaflet-popup-tip) {
  background-color: white;
}

:deep(.popup-content h3) {
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

:deep(.popup-content p) {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}
</style>