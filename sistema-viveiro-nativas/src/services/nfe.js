import api from './api'

const API_V1 = '/api/v1'

export async function emitirNfe(vendaId) {
  const { data } = await api.post(`${API_V1}/nfe/emit/${vendaId}`)
  return data
}

export async function getNfeStatus(nfeId) {
  const { data } = await api.get(`${API_V1}/nfe/${nfeId}/status`)
  return data
}

export async function listNotasVenda(vendaId) {
  const { data } = await api.get(`${API_V1}/nfe/venda/${vendaId}`)
  return data
}

export async function getNfeAmbiente() {
  const { data } = await api.get(`${API_V1}/nfe/ambiente`)
  return data
}

export async function getEmitenteFiscal() {
  const { data } = await api.get(`${API_V1}/nfe/emitente`)
  return data
}
