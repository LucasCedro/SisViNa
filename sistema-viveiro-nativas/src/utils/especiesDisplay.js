/**
 * Nome popular para exibição (gráficos, filtros, tabelas).
 * Usa só o primeiro sinônimo e troca hífens por espaço.
 */
export function nomePopularExibicao(nome) {
  if (!nome) return nome
  const parte = String(nome).split(',')[0].trim()
  return parte.replace(/-/g, ' ') || nome
}
