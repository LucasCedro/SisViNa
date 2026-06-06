import api from './api'

const API_V1 = '/api/v1'

export async function listRegrasFiscais(params = {}) {
  const { data } = await api.get(`${API_V1}/fiscal/regras`, { params })
  return data
}

export async function createRegraFiscal(payload) {
  const { data } = await api.post(`${API_V1}/fiscal/regras`, payload)
  return data
}

export async function updateRegraFiscal(id, payload) {
  const { data } = await api.put(`${API_V1}/fiscal/regras/${id}`, payload)
  return data
}

export async function deleteRegraFiscal(id) {
  const { data } = await api.delete(`${API_V1}/fiscal/regras/${id}`)
  return data
}

export async function getEmitenteFiscal() {
  const { data } = await api.get(`${API_V1}/fiscal/emitente`)
  return data
}

export async function saveEmitenteFiscal(payload) {
  const { data } = await api.put(`${API_V1}/fiscal/emitente`, payload)
  return data
}

export async function getAmbienteNfe() {
  const { data } = await api.get(`${API_V1}/fiscal/ambiente`)
  return data
}

export async function getResumoFiscal() {
  const { data } = await api.get(`${API_V1}/fiscal/resumo`)
  return data
}

export async function listNotasFiscais(params = {}) {
  const { data } = await api.get(`${API_V1}/fiscal/notas`, { params })
  return data
}

export async function vendasPendentesNfe(limit = 50) {
  const { data } = await api.get(`${API_V1}/fiscal/vendas-pendentes`, { params: { limit } })
  return data
}

export async function previewRegraFiscal(params = {}) {
  const { data } = await api.get(`${API_V1}/fiscal/regras/preview`, { params })
  return data
}
