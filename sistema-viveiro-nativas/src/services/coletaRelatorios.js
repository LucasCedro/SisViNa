import api from './api'

const API_V1 = '/api/v1'

function downloadBlob(response, fallbackName) {
  const disposition = response.headers['content-disposition']
  let filename = fallbackName
  if (disposition) {
    const match = disposition.match(/filename="?([^"]+)"?/)
    if (match) filename = match[1]
  }
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export async function exportMatrizesCsv() {
  const response = await api.get(`${API_V1}/coleta-relatorios/export/matrizes.csv`, {
    responseType: 'blob'
  })
  downloadBlob(response, 'matrizes.csv')
}

export async function exportColetasCsv(idArvoreMatriz = null) {
  const params = idArvoreMatriz ? { id_arvore_matriz: idArvoreMatriz } : {}
  const response = await api.get(`${API_V1}/coleta-relatorios/export/coletas.csv`, {
    params,
    responseType: 'blob'
  })
  downloadBlob(response, 'coletas.csv')
}

export async function exportLotesCsv(idArvoreMatriz = null) {
  const params = idArvoreMatriz ? { id_arvore_matriz: idArvoreMatriz } : {}
  const response = await api.get(`${API_V1}/coleta-relatorios/export/lotes.csv`, {
    params,
    responseType: 'blob'
  })
  downloadBlob(response, 'lotes.csv')
}

export async function exportRastreabilidadeMatrizCsv(idArvoreMatriz) {
  const response = await api.get(`${API_V1}/coleta-relatorios/export/rastreabilidade-matriz.csv`, {
    params: { id_arvore_matriz: idArvoreMatriz },
    responseType: 'blob'
  })
  downloadBlob(response, `rastreabilidade-matriz-${idArvoreMatriz}.csv`)
}
