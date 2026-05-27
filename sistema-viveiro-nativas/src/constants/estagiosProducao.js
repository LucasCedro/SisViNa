/** Estágios operacionais da muda — distintos do status biológico. */

export const ESTAGIOS = {
  em_desenvolvimento: {
    id: 'em_desenvolvimento',
    label: 'Em desenvolvimento',
    short: 'Desenvolvimento',
    contexto: 'sementeira',
    descricao: 'Plântula na sementeira, ainda não apta a ir para o canteiro.',
  },
  apta_transferencia: {
    id: 'apta_transferencia',
    label: 'Apta p/ transferência',
    short: 'Apta canteiro',
    contexto: 'sementeira',
    descricao: 'Pronta para sair da sementeira e ir para o canteiro.',
  },
  em_crescimento: {
    id: 'em_crescimento',
    label: 'Em crescimento',
    short: 'Crescimento',
    contexto: 'canteiro',
    descricao: 'Muda no canteiro, em formação.',
  },
  em_rustificacao: {
    id: 'em_rustificacao',
    label: 'Em rustificação',
    short: 'Rustificação',
    contexto: 'rustificacao',
    descricao: 'Adaptação gradual ao sol antes da venda.',
  },
  apta_venda: {
    id: 'apta_venda',
    label: 'Apta p/ venda',
    short: 'Apta venda',
    contexto: 'comercial',
    descricao: 'Pronta para comercialização (estoque comercial).',
  },
}

export function labelEstagio(id) {
  return ESTAGIOS[id]?.label || id || '—'
}
