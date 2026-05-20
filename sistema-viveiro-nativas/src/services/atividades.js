import api from './api'

const API_V1 = '/api/v1'

export async function listTiposAtividades() {
  const { data } = await api.get(`${API_V1}/atividades/tipos`)
  return data
}

export async function listAtividades(params = {}) {
  const { data } = await api.get(`${API_V1}/atividades/`, { params })
  return data
}

export async function createAtividade(payload) {
  const { data } = await api.post(`${API_V1}/atividades/`, payload)
  return data
}
