/** Paleta para Chart.js / SVG — hex literal (canvas não resolve CSS vars). */

// Série principal (produção / coleta)
export const CHART_PRIMARY = '#596247';      // primary-500
export const CHART_PRIMARY_DARK = '#47503A'; // primary-600
export const CHART_PRIMARY_LIGHT = '#A4B39A';

// Série informativa (linhas / tendências)
export const CHART_INFO = '#47607B';
export const CHART_INFO_DARK = '#3A5066';

// Semânticas em gráficos
export const CHART_SUCCESS = '#3E6247';
export const CHART_WARNING = '#C8A84B';
export const CHART_DANGER = '#8E3B2B';
export const CHART_NEUTRAL = '#8E9089';
export const CHART_COMPLEMENT_DARK = '#624E47';

/** DFC — evolução do caixa (barras CSS; mesmos hex que main.css) */
export const CHART_DFC = {
  entrada: CHART_SUCCESS,
  saida: CHART_COMPLEMENT_DARK,
  saldoPos: CHART_PRIMARY,
  saldoNeg: CHART_DANGER,
  saidaOpacity: 0.88,
};

/** DRE — evolução faturamento × CMV (Contabilidade / FinanceiroPainel) */
export const CHART_DRE = {
  faturamento: CHART_SUCCESS,
  cmv: CHART_WARNING,
  cmvOpacity: 0.85,
};

/** Timeline de estoque — cor do local (badges / borda da barra) */
export const CHART_ESTOQUE_ETAPA = {
  armazem: CHART_COMPLEMENT_DARK,
  sementeira: CHART_WARNING,
  canteiro: CHART_SUCCESS,
  rustificacao: CHART_PRIMARY_LIGHT,
};

/** Timeline estoque — intensidade do verde por dias (escala primary do design system) */
export const CHART_TIMELINE_DIAS = {
  min: '#EEF0EA',   // primary-50
  soft: '#CBD3C3',  // primary-100
  mid: '#A4B39A',   // primary-200
  base: '#596247',  // primary-500
  dark: '#353D2B',  // primary-700
  max: '#222A1C',   // primary-900
}

function _hexToRgb(hex) {
  const m = /^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/.exec(hex)
  if (!m) return null
  return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)]
}

function _mixHex(a, b, t) {
  const ra = _hexToRgb(a)
  const rb = _hexToRgb(b)
  if (!ra || !rb) return a
  const mix = (i) => Math.round(ra[i] + (rb[i] - ra[i]) * t)
  const h = (n) => n.toString(16).padStart(2, '0')
  return `#${h(mix(0))}${h(mix(1))}${h(mix(2))}`
}

/** Estilo da barra: verde mais escuro = mais dias (relativo ao máximo da visão). */
export function estoqueTimelineBarStyle(dias, maxDias) {
  const d = Number(dias) || 0
  if (d <= 0) {
    return {
      background: CHART_TIMELINE_DIAS.min,
      color: CHART_TIMELINE_DIAS.dark,
      opacity: 0.4,
    }
  }
  const ratio = maxDias > 0 ? Math.min(1, d / maxDias) : 1
  const top = ratio >= 0.85
    ? CHART_TIMELINE_DIAS.base
    : _mixHex(CHART_TIMELINE_DIAS.soft, CHART_TIMELINE_DIAS.mid, ratio * 1.1)
  const bottom = ratio >= 0.85
    ? CHART_TIMELINE_DIAS.max
    : _mixHex(CHART_TIMELINE_DIAS.mid, CHART_TIMELINE_DIAS.dark, ratio * 1.15)
  return {
    background: `linear-gradient(180deg, ${top}, ${bottom})`,
    color: ratio >= 0.42 ? '#fff' : CHART_TIMELINE_DIAS.dark,
    opacity: 1,
  }
}

// Paleta categórica para múltiplas séries
export const CHART_PALETTE = [
  CHART_PRIMARY,
  CHART_SUCCESS,
  '#625947',   // analog-2
  CHART_COMPLEMENT_DARK,
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

