/** Máscaras de entrada — armazena valor limpo; exibe formatado. */

export function onlyDigits(value) {
  return String(value ?? '').replace(/\D/g, '')
}

export function formatCnpj(value) {
  const d = onlyDigits(value).slice(0, 14)
  if (d.length <= 2) return d
  if (d.length <= 5) return `${d.slice(0, 2)}.${d.slice(2)}`
  if (d.length <= 8) return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5)}`
  if (d.length <= 12) return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8)}`
  return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8, 12)}-${d.slice(12)}`
}

export function formatCpf(value) {
  const d = onlyDigits(value).slice(0, 11)
  if (d.length <= 3) return d
  if (d.length <= 6) return `${d.slice(0, 3)}.${d.slice(3)}`
  if (d.length <= 9) return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6)}`
  return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6, 9)}-${d.slice(9)}`
}

export function formatTelefone(value) {
  const d = onlyDigits(value).slice(0, 11)
  if (!d.length) return ''
  if (d.length <= 2) return `(${d}`
  if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`
  if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`
  return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`
}

/** IE: só dígitos (SEFAZ costuma receber sem pontuação). */
export function parseInscricaoEstadual(value) {
  return onlyDigits(value).slice(0, 14)
}

export function formatInscricaoEstadual(value) {
  return parseInscricaoEstadual(value)
}

export function formatIbge(value) {
  return onlyDigits(value).slice(0, 7)
}

export function parseUf(value) {
  return String(value ?? '')
    .replace(/[^a-zA-Z]/g, '')
    .toUpperCase()
    .slice(0, 2)
}

export function formatUf(value) {
  return parseUf(value)
}

export const MASK_CONFIG = {
  cnpj: {
    parse: (v) => onlyDigits(v).slice(0, 14),
    format: formatCnpj,
    placeholder: '00.000.000/0000-00',
    inputmode: 'numeric',
    maxlength: 18,
  },
  cpf: {
    parse: (v) => onlyDigits(v).slice(0, 11),
    format: formatCpf,
    placeholder: '000.000.000-00',
    inputmode: 'numeric',
    maxlength: 14,
  },
  telefone: {
    parse: (v) => onlyDigits(v).slice(0, 11),
    format: formatTelefone,
    placeholder: '(00) 00000-0000',
    inputmode: 'tel',
    maxlength: 15,
  },
  ie: {
    parse: parseInscricaoEstadual,
    format: formatInscricaoEstadual,
    placeholder: 'Somente números',
    inputmode: 'numeric',
    maxlength: 14,
  },
  ibge: {
    parse: (v) => onlyDigits(v).slice(0, 7),
    format: formatIbge,
    placeholder: '0000000',
    inputmode: 'numeric',
    maxlength: 7,
  },
  uf: {
    parse: parseUf,
    format: formatUf,
    placeholder: 'UF',
    inputmode: 'text',
    maxlength: 2,
  },
}

export function formatMasked(mask, value) {
  const cfg = MASK_CONFIG[mask]
  return cfg ? cfg.format(cfg.parse(value)) : value
}

export function parseMasked(mask, value) {
  const cfg = MASK_CONFIG[mask]
  return cfg ? cfg.parse(value) : value
}
