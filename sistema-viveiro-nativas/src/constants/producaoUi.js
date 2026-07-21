/** Rótulos e textos padronizados da página Produção. */

export const PRODUCAO_MODO = {
  MASSA: 'massa',
  INDIVIDUAL: 'individual',
}

export const PRODUCAO_MODO_LABEL = {
  [PRODUCAO_MODO.MASSA]: 'Por quantidade',
  [PRODUCAO_MODO.INDIVIDUAL]: 'Individual',
}

/** Frase curta abaixo do toggle de modo em cada painel operacional. */
export const PRODUCAO_MODO_AJUDA =
  'Por quantidade: informe espécie e quantidade (ideal para milhares de mudas). Individual: muda a muda, para ajustes pontuais.'

export const PRODUCAO_ACOES_LOTE = {
  marcarTodos: 'Marcar todos',
  preencherDisponivel: 'Preencher disponível',
  limpar: 'Limpar',
  filtrarEspecie: 'Filtrar espécie',
}

export const PRODUCAO_RESUMO = {
  especies: (n) => `${n} espécie(s)`,
  mudas: (n) => `${n.toLocaleString('pt-BR')} muda(s)`,
  sementes: (n) => `${n.toLocaleString('pt-BR')} semente(s)`,
}

/** Prazo recomendado na área de rustificação antes de liberar para venda (Embrapa). */
export const RUSTIFICACAO_DIAS_MINIMO = 30
