/**
 * Cores do mapa do viveiro (SVG / canvas / atributos dinâmicos).
 * Hex literal — atributos SVG não resolvem var(--color-*).
 * Espelhadas em `src/assets/viveiro-map-shell.css` (--viveiro-*).
 */
import {
  CHART_PRIMARY,
  CHART_PRIMARY_DARK,
  CHART_PRIMARY_LIGHT,
  CHART_SUCCESS,
  CHART_WARNING,
  CHART_INFO,
  CHART_INFO_DARK,
  CHART_NEUTRAL,
  CHART_COMPLEMENT_DARK,
} from './chartColors'

/** Cor de texto / grade no export PNG */
export const VIVEIRO_MAP_TEXT = '#2C2D2A'
export const VIVEIRO_MAP_SURFACE = '#FFFFFF'

export const VIVEIRO_MAP_GRID = {
  fine: '#EEF0EA',
  marker: CHART_NEUTRAL,
}

/** Cor padrão por tipo de área (legenda + novos elementos) */
export const VIVEIRO_MAP_TIPO = {
  canteiro: CHART_PRIMARY,
  sementeira: CHART_WARNING,
  rustificacao: CHART_PRIMARY_LIGHT,
  'area-trabalho': CHART_PRIMARY_LIGHT,
  estoque: CHART_NEUTRAL,
  armazenamento: CHART_NEUTRAL,
  sede: CHART_INFO,
  lago: CHART_INFO_DARK,
  garagem: CHART_NEUTRAL,
  campo: CHART_PRIMARY_LIGHT,
  espaco: CHART_WARNING,
}

/** Paletas do seletor de cor no editor (5 tons harmônicos) */
export const VIVEIRO_PALETTES = {
  campo: [CHART_PRIMARY_LIGHT, CHART_PRIMARY, CHART_SUCCESS, CHART_PRIMARY_DARK, CHART_COMPLEMENT_DARK],
  canteiro: [CHART_PRIMARY, CHART_PRIMARY_DARK, CHART_SUCCESS, '#625947', CHART_PRIMARY_LIGHT],
  espaco: [CHART_WARNING, '#B8963F', CHART_PRIMARY_LIGHT, CHART_NEUTRAL, CHART_COMPLEMENT_DARK],
  sementeira: [CHART_WARNING, '#B8963F', '#D4BA6A', '#E8D49A', '#FBF6E8'],
  rustificacao: [CHART_PRIMARY_LIGHT, '#CBD3C3', CHART_NEUTRAL, CHART_WARNING, '#EEF0EA'],
  'area-trabalho': [CHART_PRIMARY_LIGHT, '#CBD3C3', CHART_NEUTRAL, CHART_WARNING, '#EEF0EA'],
  estoque: [CHART_NEUTRAL, '#CBD3C3', CHART_PRIMARY_LIGHT, '#EEF0EA', CHART_COMPLEMENT_DARK],
}

/** Legenda da planta baixa (somente tipos exibidos no mapa) */
export const VIVEIRO_LEGENDA = [
  { cor: VIVEIRO_MAP_TIPO.sementeira, label: 'Sementeira', tipos: ['sementeira'] },
  { cor: VIVEIRO_MAP_TIPO.canteiro, label: 'Canteiro', tipos: ['canteiro'] },
  { cor: VIVEIRO_MAP_TIPO.rustificacao, label: 'Rustificação', tipos: ['rustificacao'] },
  { cor: VIVEIRO_MAP_TIPO.sede, label: 'Sede', tipos: ['sede'] },
  { cor: VIVEIRO_MAP_TIPO.lago, label: 'Água', tipos: ['lago'] },
  { cor: VIVEIRO_MAP_TIPO.garagem, label: 'Garagem', tipos: ['garagem', 'armazenamento'] },
  { cor: VIVEIRO_MAP_TIPO['area-trabalho'], label: 'Trabalho', tipos: ['area-trabalho'] },
]

export function corPadraoTipo(tipo) {
  return VIVEIRO_MAP_TIPO[tipo] || CHART_NEUTRAL
}

export function paletaTipo(tipo) {
  return VIVEIRO_PALETTES[tipo] || []
}
