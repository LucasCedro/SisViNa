/** Distância máxima (px) para encaixar bordas ao arrastar. */
export const SNAP_THRESHOLD = 14

export function boundsCampo(c) {
  return {
    left: c.x,
    top: c.y,
    right: c.x + c.largura,
    bottom: c.y + c.altura,
    cx: c.x + c.largura / 2,
    cy: c.y + c.altura / 2,
    w: c.largura,
    h: c.altura,
  }
}

function melhorSnap(atual, candidatos, threshold) {
  let best = null
  let min = threshold + 1
  for (const { delta, valor } of candidatos) {
    const d = Math.abs(delta)
    if (d <= threshold && d < min) {
      min = d
      best = valor
    }
  }
  return best
}

/**
 * Ajusta x/y de um campo para alinhar bordas ou centros com outros campos.
 */
export function snapCampo(campo, todos, threshold = SNAP_THRESHOLD) {
  const b = boundsCampo(campo)
  const others = (todos || []).filter((o) => o.id !== campo.id)
  if (!others.length) return { x: campo.x, y: campo.y }

  const candX = []
  const candY = []

  for (const o of others) {
    const ob = boundsCampo(o)
    candX.push(
      { delta: ob.left - b.left, valor: ob.left },
      { delta: ob.right - b.right, valor: ob.right - b.w },
      { delta: ob.left - b.right, valor: ob.left - b.w },
      { delta: ob.right - b.left, valor: ob.right },
      { delta: ob.cx - b.cx, valor: ob.cx - b.w / 2 }
    )
    candY.push(
      { delta: ob.top - b.top, valor: ob.top },
      { delta: ob.bottom - b.bottom, valor: ob.bottom - b.h },
      { delta: ob.top - b.bottom, valor: ob.top - b.h },
      { delta: ob.bottom - b.top, valor: ob.bottom },
      { delta: ob.cy - b.cy, valor: ob.cy - b.h / 2 }
    )
  }

  const nx = melhorSnap(b.left, candX, threshold)
  const ny = melhorSnap(b.top, candY, threshold)

  return {
    x: Math.max(0, nx ?? campo.x),
    y: Math.max(0, ny ?? campo.y),
  }
}

export function snapVarios(campos, todos, threshold = SNAP_THRESHOLD) {
  for (const c of campos) {
    const pos = snapCampo(c, todos, threshold)
    c.x = pos.x
    c.y = pos.y
  }
}

const ALINHAR = {
  esquerda: (b) => b.left,
  direita: (b) => b.right,
  'centro-h': (b) => b.cx,
  topo: (b) => b.top,
  base: (b) => b.bottom,
  'centro-v': (b) => b.cy,
}

/**
 * Alinha um conjunto de campos a uma borda ou centro comum.
 * @param {'esquerda'|'direita'|'centro-h'|'topo'|'base'|'centro-v'} modo
 */
export function alinharCampos(campos, modo) {
  if (!campos?.length || campos.length < 2) return
  const fn = ALINHAR[modo]
  if (!fn) return

  const bounds = campos.map((c) => ({ c, b: boundsCampo(c) }))
  const ref = fn(bounds[0].b)

  for (const { c, b } of bounds) {
    if (modo === 'esquerda') c.x = ref
    else if (modo === 'direita') c.x = ref - b.w
    else if (modo === 'centro-h') c.x = ref - b.w / 2
    else if (modo === 'topo') c.y = ref
    else if (modo === 'base') c.y = ref - b.h
    else if (modo === 'centro-v') c.y = ref - b.h / 2
  }
}

/** Espaça uniformemente entre o primeiro e o último (ordem por x ou y). */
export function distribuirCampos(campos, eixo = 'horizontal') {
  if (!campos?.length || campos.length < 3) return
  const sorted = [...campos].sort((a, b) =>
    eixo === 'horizontal' ? a.x - b.x : a.y - b.y
  )
  const first = boundsCampo(sorted[0])
  const last = boundsCampo(sorted[sorted.length - 1])
  const span =
    eixo === 'horizontal'
      ? last.left - first.left
      : last.top - first.top
  const step = span / (sorted.length - 1)
  sorted.forEach((c, i) => {
    if (i === 0 || i === sorted.length - 1) return
    if (eixo === 'horizontal') c.x = Math.round(first.left + step * i)
    else c.y = Math.round(first.top + step * i)
  })
}
