import api from './api'
import { downloadCsvFromRows, flattenParaCsv } from '@/utils/exportCsv'

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

/** Exporta o que está visível após os filtros da página. */
export function exportMatrizesCsvFromStore(store) {
  const rows = store.matrizesFiltradas.map(flattenParaCsv)
  downloadCsvFromRows(rows, 'matrizes.csv')
}

export function exportColetasCsvFromStore(store) {
  const rows = store.coletasFiltradas.map(flattenParaCsv)
  downloadCsvFromRows(rows, 'coletas.csv')
}

export function exportLotesCsvFromStore(store) {
  const rows = store.lotesFiltrados.map(flattenParaCsv)
  downloadCsvFromRows(rows, 'lotes.csv')
}

export function exportRastreabilidadeMatrizFromStore(store, idArvoreMatriz) {
  const matriz = store.arvoresMatriz.find((m) => m.id === idArvoreMatriz)
  const rows = []
  if (matriz) rows.push({ secao: 'MATRIZ', ...flattenParaCsv(matriz) })
  store.coletas
    .filter((c) => c.id_arvore_matriz === idArvoreMatriz)
    .forEach((c) => rows.push({ secao: 'COLETA', ...flattenParaCsv(c) }))
  store.lotes
    .filter((l) => l.id_arvore_matriz === idArvoreMatriz)
    .forEach((l) => rows.push({ secao: 'LOTE', ...flattenParaCsv(l) }))
  downloadCsvFromRows(rows, `rastreabilidade-matriz-${idArvoreMatriz}.csv`)
}

/** API (uso programático / integrações). */
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
