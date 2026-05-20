import api from './api'

const API_V1 = '/api/v1'

export async function listCompradores(params = {}) {
  const { data } = await api.get(`${API_V1}/compradores/`, { params })
  return data
}

export async function createComprador(payload) {
  const { data } = await api.post(`${API_V1}/compradores/`, payload)
  return data
}
