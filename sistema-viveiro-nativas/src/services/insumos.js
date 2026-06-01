import api from './api'

const API_V1 = '/api/v1'

export async function listInsumos(params = {}) {
  const { data } = await api.get(`${API_V1}/insumos/`, { params })
  return data
}

export async function createInsumo(payload) {
  const { data } = await api.post(`${API_V1}/insumos/`, payload)
  return data
}
