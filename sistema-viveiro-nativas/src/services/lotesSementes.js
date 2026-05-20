import api from './api'

const API_V1 = '/api/v1'

export async function listLotesSementes(params = {}) {
  const { data } = await api.get(`${API_V1}/lotes-sementes/`, { params })
  return data
}

export async function createLoteSementes(payload) {
  const { data } = await api.post(`${API_V1}/lotes-sementes/`, payload)
  return data
}

export async function updateLoteSementes(id, payload) {
  const { data } = await api.put(`${API_V1}/lotes-sementes/${id}`, payload)
  return data
}
