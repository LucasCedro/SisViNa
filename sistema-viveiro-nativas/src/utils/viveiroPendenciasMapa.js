/** Metadados das pendências exibidas no mapa do viveiro. */
export const PENDENCIA_MAPA = {
  transferencia: {
    id: 'transferencia',
    rotulo: 'Transferir',
    icone: '→',
    titulo: 'Mudas aptas para transferência ao canteiro',
    rota: '/producao',
    nivel: 'medio',
  },
  rustificacao: {
    id: 'rustificacao',
    rotulo: 'Rustificar',
    icone: '↗',
    titulo: 'Mudas aptas para área de rustificação',
    rota: '/producao',
    nivel: 'medio',
  },
  fitossanidade: {
    id: 'fitossanidade',
    rotulo: 'Fitossanidade',
    icone: '⚠',
    titulo: 'Ocorrência fitossanitária (nível alto ou crítico)',
    rota: '/fitossanidade',
    nivel: 'alto',
  },
}

function pushPendencia(map, idCanteiro, tipo, count = 1) {
  if (!idCanteiro) return
  if (!map[idCanteiro]) map[idCanteiro] = []
  const existente = map[idCanteiro].find((p) => p.tipo === tipo)
  if (existente) existente.count += count
  else map[idCanteiro].push({ tipo, count, ...PENDENCIA_MAPA[tipo] })
}

function nivelPragaCritico(nivel) {
  const n = String(nivel || '').toUpperCase()
  return n === 'ALTO' || n === 'CRITICO'
}

/**
 * Agrupa pendências operacionais por `id_canteiro` para badges no mapa.
 */
export function agruparPendenciasPorCanteiro({
  pendentesTransferencia = [],
  aptasRustificacao = [],
  pragas = [],
  plantasPorId = new Map(),
}) {
  const map = {}

  for (const p of pendentesTransferencia) {
    pushPendencia(map, p.id_canteiro, 'transferencia')
  }

  for (const p of aptasRustificacao) {
    pushPendencia(map, p.id_canteiro, 'rustificacao')
  }

  for (const praga of pragas) {
    if (!nivelPragaCritico(praga.nivel_infestacao)) continue
    const idCant =
      praga.id_canteiro ??
      plantasPorId.get(praga.id_planta)?.idCanteiro ??
      plantasPorId.get(praga.id_planta)?.id_canteiro
    pushPendencia(map, idCant, 'fitossanidade')
  }

  return map
}

export function pendenciasDoCanteiro(pendenciasPorCanteiro, apiId) {
  if (!apiId || !pendenciasPorCanteiro) return []
  return pendenciasPorCanteiro[apiId] || []
}

export function temPendenciaPrioritaria(pendencias) {
  return pendencias.some((p) => p.nivel === 'alto')
}
