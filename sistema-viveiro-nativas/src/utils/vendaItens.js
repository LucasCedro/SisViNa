/** Linha do carrinho de venda. */
export function criarLinhaVenda(especie = null) {
  return {
    uid: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    id_especie: especie?.id_especie ?? '',
    quantidade: 1,
    valorUnitario: Number(especie?.valorUnitario) || 0,
    desconto: 0,
    origem: 'auto',
    id_lote_sementes: null,
    loteKey: null,
  }
}

export function labelEspecie(item) {
  if (!item) return '—'
  return item.nomePopular || item.nomeCientifico || `Espécie #${item.id_especie}`
}

export function agruparLotes(plantas) {
  const map = new Map()
  for (const p of plantas || []) {
    const semLote = !p.id_lote_sementes
    const key = semLote ? 'sem' : String(p.id_lote_sementes)
    if (!map.has(key)) {
      map.set(key, {
        key,
        id_lote_sementes: p.id_lote_sementes ?? null,
        codigo_lote: p.codigo_lote || (semLote ? 'Sem lote vinculado' : `Lote #${p.id_lote_sementes}`),
        quantidade: 0,
        dias_min: null,
        rustificacao_ok: true,
      })
    }
    const g = map.get(key)
    g.quantidade += 1
    if (p.dias_rustificacao != null) {
      g.dias_min = g.dias_min == null ? p.dias_rustificacao : Math.min(g.dias_min, p.dias_rustificacao)
    }
    if (p.rustificacao_ok === false) g.rustificacao_ok = false
  }
  return [...map.values()].sort((a, b) => b.quantidade - a.quantidade)
}

export function subtotalLinha(linha) {
  const q = Number(linha.quantidade) || 0
  const vu = Number(linha.valorUnitario) || 0
  const desc = Number(linha.desconto) || 0
  return Math.max(0, q * vu - desc)
}

export function resumoCarrinho(linhas) {
  const validas = (linhas || []).filter((l) => l.id_especie && l.quantidade > 0)
  const totalMudas = validas.reduce((s, l) => s + Number(l.quantidade), 0)
  const subtotal = validas.reduce((s, l) => s + subtotalLinha(l), 0)
  const descontos = validas.reduce((s, l) => s + (Number(l.desconto) || 0), 0)
  return {
    linhas: validas.length,
    totalMudas,
    subtotal,
    descontos,
    total: subtotal,
  }
}

/**
 * Resolve linhas do carrinho em itens de venda (1 planta = 1 item).
 * @param {Function} fetchPlantas (idEspecie) => Promise<PlantaDisponivel[]>
 */
export async function resolverItensVenda(linhas, fetchPlantas) {
  const usados = new Set()
  const itens = []

  for (const linha of linhas) {
    if (!linha.id_especie || linha.quantidade < 1) continue

    let plantas = await fetchPlantas(Number(linha.id_especie))
    plantas = plantas.filter((p) => !usados.has(p.id))

    if (linha.origem === 'lote') {
      if (linha.id_lote_sementes == null) {
        plantas = plantas.filter((p) => !p.id_lote_sementes)
      } else {
        plantas = plantas.filter((p) => p.id_lote_sementes === linha.id_lote_sementes)
      }
    }

    if (plantas.length < linha.quantidade) {
      throw new Error(
        `Estoque insuficiente (${linha.quantidade} solicitadas, ${plantas.length} disponíveis na origem escolhida).`
      )
    }

    const descontoPorUn = (Number(linha.desconto) || 0) / linha.quantidade
    for (const p of plantas.slice(0, linha.quantidade)) {
      usados.add(p.id)
      itens.push({
        id_planta: p.id,
        quantidade: 1,
        valor_unitario: Number(linha.valorUnitario) || Number(p.preco_venda) || 0,
        desconto: descontoPorUn,
      })
    }
  }

  if (!itens.length) throw new Error('Adicione pelo menos um item ao pedido.')
  return itens
}
