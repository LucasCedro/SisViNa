/** Capacidade declarada no componente do layout (wizard / designer). */
export function capacidadeDoCampo(campo) {
  if (!campo) return null
  if (campo.config?.capacidade != null) return Number(campo.config.capacidade)
  if (campo.tipo === 'canteiro' && campo.config?.linhas && campo.config?.colunas) {
    return campo.config.linhas * campo.config.colunas
  }
  return null
}

export function totalPlantasOcupacao(ocupacao, mudasCount = 0) {
  if (ocupacao?.total_plantas != null) return ocupacao.total_plantas
  return mudasCount
}

export function podeExcluirArea(ocupacao, mudasCount = 0) {
  return totalPlantasOcupacao(ocupacao, mudasCount) === 0
}

/** Texto do badge: "3/20" ou "3" se sem capacidade. */
export function textoBadgeOcupacao(campo, ocupacao, mudasCount = 0) {
  const total = totalPlantasOcupacao(ocupacao, mudasCount)
  const cap = capacidadeDoCampo(campo)
  if (cap != null && cap > 0) return `${total}/${cap}`
  return total > 0 ? String(total) : '0'
}

export function mapOcupacaoPorApiId(canteirosComOcupacao = []) {
  const map = {}
  for (const c of canteirosComOcupacao) {
    map[c.id] = {
      total_plantas: c.total_plantas ?? 0,
      total_sementes: c.total_sementes ?? 0,
      total_mudas: c.total_mudas ?? 0,
    }
  }
  return map
}
