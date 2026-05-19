import api from './api'

const API_V1 = '/api/v1'

export async function listEspecies(params = {}) {
  const { data } = await api.get(`${API_V1}/especies/`, { params })
  return data
}
