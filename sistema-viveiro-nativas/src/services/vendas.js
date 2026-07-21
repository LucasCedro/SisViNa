import api from './api'

const API_V1 = '/api/v1'

export async function listVendas(params = {}) {
  const { data } = await api.get(`${API_V1}/vendas/`, { params })
  return data
}

export async function getVenda(id) {
  const { data } = await api.get(`${API_V1}/vendas/${id}`)
  return data
}

export async function createVenda(payload) {
  const { data } = await api.post(`${API_V1}/vendas/`, payload)
  return data
}

export async function updateVenda(id, payload) {
  const { data } = await api.put(`${API_V1}/vendas/${id}`, payload)
  return data
}

export async function aprovarVenda(id) {
  const { data } = await api.post(`${API_V1}/vendas/${id}/aprovar`)
  return data
}
