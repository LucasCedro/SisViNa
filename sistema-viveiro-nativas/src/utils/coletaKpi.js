/** KPI de germinação: média do último teste de germinação por lote da espécie. */

export const LIMIAR_GERM_BAIXA = 50
export const LIMIAR_GERM_BOA = 70

export const ESTAGIOS_COLETAVEL = new Set(['fruto_maduro', 'fruto_seco'])

export function germinacaoLote(lote, testes) {
  if (!lote) return null
  if (lote.ultimo_teste_germinacao != null) return Number(lote.ultimo_teste_germinacao)
  const t = ultimoTesteGerminacaoLote(testes, lote.id)
  return t != null ? Number(t.percentual_resultado) : null
}

export function ultimoTesteGerminacaoLote(testes, idLote) {
  const germ = (testes || [])
    .filter((t) => t.id_lote_sementes === idLote && t.tipo_teste === 'germinacao')
    .sort((a, b) => {
      const da = new Date(a.data_teste)
      const db = new Date(b.data_teste)
      if (db - da !== 0) return db - da
      return (b.id || 0) - (a.id || 0)
    })
  return germ[0] || null
}

export function taxaGerminacaoEspecie(lotes, testes, idEspecie) {
  if (!idEspecie) return null
  const lotesEsp = (lotes || []).filter((l) => l.id_especie === idEspecie)
  const valores = lotesEsp
    .map((l) => ultimoTesteGerminacaoLote(testes, l.id))
    .filter(Boolean)
    .map((t) => Number(t.percentual_resultado))
    .filter((v) => !Number.isNaN(v))
  if (!valores.length) return null
  const media = valores.reduce((s, v) => s + v, 0) / valores.length
  return Math.round(media * 10) / 10
}

export function lotePrecisaTesteGerminacao(lote, testes) {
  if (!lote || lote.status === 'descartado') return false
  if (lote.ultimo_teste_germinacao != null) return false
  return !ultimoTesteGerminacaoLote(testes, lote.id)
}
