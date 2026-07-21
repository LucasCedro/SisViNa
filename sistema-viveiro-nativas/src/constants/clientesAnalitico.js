export const ROLES_RESUMO_FINANCEIRO_CLIENTES = ['admin', 'gestor', 'financeiro']

export const PERIODOS_CLIENTES = [
  { meses: 6, label: '6 meses' },
  { meses: 12, label: '12 meses' },
  { meses: 24, label: '24 meses' },
  { meses: 0, label: 'Todo período' },
]

export const RANKINGS_CLIENTES = [
  { id: 'por_lucro', label: 'Maior lucro', hint: 'Receita − CMV das mudas vendidas' },
  { id: 'por_receita', label: 'Maior faturamento', hint: 'Quem mais comprou em R$' },
  { id: 'por_fidelidade', label: 'Mais fiéis', hint: 'Mais pedidos no período' },
  { id: 'precisam_atencao', label: 'Precisam atenção', hint: 'Sumiram há 90+ dias' },
]

export const STATUS_RELACIONAMENTO = {
  lead: { label: 'Sem compra', tone: 'muted' },
  novo: { label: 'Novo', tone: 'info' },
  ativo: { label: 'Ativo', tone: 'ok' },
  recorrente: { label: 'Fiel', tone: 'success' },
  dormindo: { label: 'Sumiu', tone: 'warn' },
  inativo: { label: 'Inativo', tone: 'danger' },
}

export function fmtMoeda(v) {
  return Number(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function fmtData(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR')
}
