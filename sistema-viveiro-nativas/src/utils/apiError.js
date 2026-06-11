/** Converte detail do FastAPI (string, array 422, objeto) em texto legível. */
export function mensagemErroApi(error, fallback = 'Erro na requisição') {
  const detail = error?.response?.data?.detail
  if (detail == null || detail === '') return fallback
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item
        const campo = Array.isArray(item.loc)
          ? item.loc.filter((p) => p !== 'body').join(' → ')
          : ''
        const msg = item.msg || String(item)
        return campo ? `${campo}: ${msg}` : msg
      })
      .join('\n')
  }
  if (typeof detail === 'object') {
    return detail.msg || JSON.stringify(detail)
  }
  return fallback
}
