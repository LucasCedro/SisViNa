import api from './api'

const API_V1 = '/api/v1'

export async function listFuncionarios(params = {}) {
  const { data } = await api.get(`${API_V1}/funcionarios/`, { params })
  return data
}

export async function listFuncionariosComStats(params = {}) {
  const { data } = await api.get(`${API_V1}/funcionarios/with-stats`, { params })
  return data
}

export async function updateFuncionario(id, payload) {
  const { data } = await api.put(`${API_V1}/funcionarios/${id}`, payload)
  return data
}
