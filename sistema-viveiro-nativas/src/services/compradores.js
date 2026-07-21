import api from './api'

const API_V1 = '/api/v1'

export async function listCompradores(params = {}) {
  const { data } = await api.get(`${API_V1}/compradores/`, { params })
  return data
}

export async function listCompradoresWithVendas(params = {}) {
  const { data } = await api.get(`${API_V1}/compradores/with-vendas`, { params })
  return data
}

export async function getComprador(id) {
  const { data } = await api.get(`${API_V1}/compradores/${id}`)
  return data
}

export async function createComprador(payload) {
  const { data } = await api.post(`${API_V1}/compradores/`, payload)
  return data
}

export async function updateComprador(id, payload) {
  const { data } = await api.put(`${API_V1}/compradores/${id}`, payload)
  return data
}

export async function getCompradoresAnalitico(meses = 12) {
  const { data } = await api.get(`${API_V1}/compradores/analitico`, { params: { meses } })
  return data
}

export async function getCompradorNfeReadiness(id) {
  const { data } = await api.get(`${API_V1}/compradores/${id}/nfe-readiness`)
  return data
}
