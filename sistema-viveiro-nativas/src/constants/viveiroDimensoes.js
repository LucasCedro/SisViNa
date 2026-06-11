/** Escala croqui: 1 m real = N px no mapa (proporção uniforme). */
export const PX_POR_METRO = 24

/** Presets típicos de viveiro — canteiros e sementeiras em faixa. */
export const PRESETS_DIMENSAO = [
  { id: 'faixa-4x40', label: 'Faixa 4 × 40 m', largura: 4, altura: 40, descricao: 'Canteiro longo' },
  { id: 'faixa-4x20', label: 'Faixa 4 × 20 m', largura: 4, altura: 20, descricao: 'Meia faixa' },
  { id: 'faixa-3x30', label: 'Faixa 3 × 30 m', largura: 3, altura: 30, descricao: 'Faixa estreita' },
  { id: 'faixa-6x24', label: 'Faixa 6 × 24 m', largura: 6, altura: 24, descricao: 'Sementeira longa' },
  { id: 'quad-6x6', label: 'Quadrado 6 × 6 m', largura: 6, altura: 6, descricao: 'Área compacta' },
  { id: 'quad-10x8', label: 'Retângulo 10 × 8 m', largura: 10, altura: 8, descricao: 'Rustificação / sede' },
]

export const METROS_PADRAO_PRODUTIVO = { largura: 4, altura: 40 }

export function metrosParaPx(metros) {
  return Math.round(Number(metros) * PX_POR_METRO)
}

export function pxParaMetros(px) {
  if (!px) return null
  return +(Number(px) / PX_POR_METRO).toFixed(1)
}

export function aplicarMetrosAoCampo(campo, larguraM, alturaM) {
  const largura = Number(larguraM)
  const altura = Number(alturaM)
  if (!(largura > 0 && altura > 0)) return false
  campo.metros = { largura, altura }
  campo.largura = metrosParaPx(largura)
  campo.altura = metrosParaPx(altura)
  return true
}

export function inverterOrientacaoCampo(campo) {
  if (!campo) return
  const mL = campo.metros?.largura ?? pxParaMetros(campo.largura)
  const mA = campo.metros?.altura ?? pxParaMetros(campo.altura)
  if (mL && mA) {
    aplicarMetrosAoCampo(campo, mA, mL)
    return
  }
  const tmp = campo.largura
  campo.largura = campo.altura
  campo.altura = tmp
}

export function textoMetros(campo) {
  const m = campo?.metros
  if (m?.largura > 0 && m?.altura > 0) return `${m.largura} × ${m.altura} m`
  const w = pxParaMetros(campo?.largura ?? campo?.dimensoes?.largura)
  const h = pxParaMetros(campo?.altura ?? campo?.dimensoes?.altura)
  if (w && h) return `${w} × ${h} m`
  return null
}

/** Razão comprimento/largura > limiar → faixa (típico de canteiro). */
export function ehFaixa(larguraPx, alturaPx, limiar = 2.2) {
  const w = larguraPx || 1
  const h = alturaPx || 1
  return Math.max(w, h) / Math.min(w, h) >= limiar
}

export function orientacaoFaixa(larguraPx, alturaPx, limiar = 2.2) {
  if (!ehFaixa(larguraPx, alturaPx, limiar)) return null
  return (larguraPx || 0) >= (alturaPx || 0) ? 'horizontal' : 'vertical'
}
