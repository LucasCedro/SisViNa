/** Paleta para Chart.js / SVG — hex literal (canvas não resolve CSS vars). */

// Série principal (produção / coleta)
export const CHART_PRIMARY = '#596247';      // primary-500
export const CHART_PRIMARY_DARK = '#47503A'; // primary-600
export const CHART_PRIMARY_LIGHT = '#A4B39A';

// Série informativa (linhas / tendências)
export const CHART_INFO = '#47607B';

// Semânticas em gráficos
export const CHART_SUCCESS = '#3E6247';
export const CHART_WARNING = '#C8A84B';
export const CHART_DANGER = '#8E3B2B';
export const CHART_NEUTRAL = '#8E9089';

// Paleta categórica para múltiplas séries
export const CHART_PALETTE = [
  CHART_PRIMARY,
  CHART_SUCCESS,
  '#625947',   // analog-2
  '#624E47',   // complement-dark
  CHART_INFO,
  CHART_PRIMARY_LIGHT,
  CHART_WARNING,
  CHART_PRIMARY_DARK,
  CHART_NEUTRAL,
  '#353D2B',   // primary-700
];

// Utilitário simples para gerar preenchimento translúcido a partir de uma cor base (hex 6 dígitos)
export function withAlpha(hex, alpha = 0.15) {
  // Espera '#RRGGBB'
  const m = /^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/.exec(hex);
  if (!m) return hex;
  const r = parseInt(m[1], 16);
  const g = parseInt(m[2], 16);
  const b = parseInt(m[3], 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

