import api from './api'

const API_V1 = '/api/v1'

export async function listTestesSementes(params = {}) {
  const { data } = await api.get(`${API_V1}/testes-sementes/`, { params })
  return data
}

export async function createTesteSementes(payload) {
  const { data } = await api.post(`${API_V1}/testes-sementes/`, payload)
  return data
}

export async function updateTesteSementes(id, payload) {
  const { data } = await api.put(`${API_V1}/testes-sementes/${id}`, payload)
  return data
}

export async function deleteTesteSementes(id) {
  const { data } = await api.delete(`${API_V1}/testes-sementes/${id}`)
  return data
}
