import L from 'leaflet'

/** Ícone do marcador: coloque SVG/PNG em public/icons/ → URL /icons/nome-arquivo */
export const ICONE_MATRIZ_URL = '/icons/tree-marker.svg'

export function criarIconeMatriz() {
  return L.icon({
    iconUrl: ICONE_MATRIZ_URL,
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -32]
  })
}
