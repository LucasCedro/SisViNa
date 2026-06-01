import api from './api'

const API_V1 = '/api/v1'

export async function getPainelFinanceiro(params = {}) {
  const { data } = await api.get(`${API_V1}/financeiro/painel`, { params })
  return data
}

export async function listPremissas(params = {}) {
  const { data } = await api.get(`${API_V1}/financeiro/premissas`, { params })
  return data
}

export async function createPremissa(payload) {
  const { data } = await api.post(`${API_V1}/financeiro/premissas`, payload)
  return data
}

export async function updatePremissa(id, payload) {
  const { data } = await api.put(`${API_V1}/financeiro/premissas/${id}`, payload)
  return data
}

export async function deletePremissa(id) {
  const { data } = await api.delete(`${API_V1}/financeiro/premissas/${id}`)
  return data
}
