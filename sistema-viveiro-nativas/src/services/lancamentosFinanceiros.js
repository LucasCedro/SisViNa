import api from './api'

const API_V1 = '/api/v1'

export async function listLancamentos(params = {}) {
  const { data } = await api.get(`${API_V1}/lancamentos-financeiros/`, { params })
  return data
}

export async function createLancamento(payload) {
  const { data } = await api.post(`${API_V1}/lancamentos-financeiros/`, payload)
  return data
}

export async function updateLancamento(id, payload) {
  const { data } = await api.put(`${API_V1}/lancamentos-financeiros/${id}`, payload)
  return data
}

export async function deleteLancamento(id) {
  const { data } = await api.delete(`${API_V1}/lancamentos-financeiros/${id}`)
  return data
}
