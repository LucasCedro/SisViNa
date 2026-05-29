/** Remove legado visual (círculos por muda, campos aninhados) do layout do editor. */
export function sanitizarCamposLayout(campos) {
  const saida = []

  for (const item of campos || []) {
    if (item.tipo === 'campo' && Array.isArray(item.canteiros)) {
      for (const nested of item.canteiros) {
        saida.push(limparCampo({ ...nested, x: (item.x || 0) + (nested.x || 0), y: (item.y || 0) + (nested.y || 0) }))
      }
      continue
    }
    if (item.tipo === 'espaco') continue
    saida.push(limparCampo(item))
  }

  return saida
}

function limparCampo(c) {
  const clone = { ...c }
  delete clone.espacos
  delete clone.canteiros
  return clone
}
