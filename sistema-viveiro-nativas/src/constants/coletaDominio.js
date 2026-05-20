export const TIPOS_ORIGEM = [
  { value: 'plantada', label: 'Plantada' },
  { value: 'fragmento_floresta', label: 'Fragmento de floresta' },
  { value: 'app', label: 'APP' },
  { value: 'reserva_legal', label: 'Reserva legal' },
  { value: 'remanescente', label: 'Remanescente' },
  { value: 'plantio_experimental', label: 'Plantio experimental' },
  { value: 'outro', label: 'Outro' }
]

export const ESTAGIOS_FRUTIFICACAO = [
  { value: 'pre_floracao', label: 'Pré-floração' },
  { value: 'floracao', label: 'Floração' },
  { value: 'fruto_verde', label: 'Fruto verde' },
  { value: 'fruto_maduro', label: 'Fruto maduro' },
  { value: 'fruto_seco', label: 'Fruto seco' },
  { value: 'dispersao', label: 'Dispersão' },
  { value: 'outro', label: 'Outro' }
]

export const MESES = [
  { value: 1, label: 'Jan' },
  { value: 2, label: 'Fev' },
  { value: 3, label: 'Mar' },
  { value: 4, label: 'Abr' },
  { value: 5, label: 'Mai' },
  { value: 6, label: 'Jun' },
  { value: 7, label: 'Jul' },
  { value: 8, label: 'Ago' },
  { value: 9, label: 'Set' },
  { value: 10, label: 'Out' },
  { value: 11, label: 'Nov' },
  { value: 12, label: 'Dez' }
]

export const TIPOS_TESTE = [
  { value: 'germinacao', label: 'Germinação' },
  { value: 'viabilidade', label: 'Viabilidade' },
  { value: 'tetrazolio', label: 'Tetrazólio' },
  { value: 'outro', label: 'Outro' }
]

export const STATUS_LOTE = [
  { value: 'ativo', label: 'Ativo' },
  { value: 'esgotado', label: 'Esgotado' },
  { value: 'descartado', label: 'Descartado' }
]

export function labelTipoOrigem(v) {
  return TIPOS_ORIGEM.find((t) => t.value === v)?.label || v || '—'
}

export function labelEstagio(v) {
  return ESTAGIOS_FRUTIFICACAO.find((t) => t.value === v)?.label || v || '—'
}

export function labelMes(v) {
  if (!v) return '—'
  return MESES.find((m) => m.value === Number(v))?.label || String(v)
}

export function janelaFrutificacao(matriz) {
  const ini = matriz?.mes_inicio_frutificacao
  const fim = matriz?.mes_fim_frutificacao
  if (!ini && !fim) return '—'
  if (ini && fim) return `${labelMes(ini)} – ${labelMes(fim)}`
  return labelMes(ini || fim)
}
