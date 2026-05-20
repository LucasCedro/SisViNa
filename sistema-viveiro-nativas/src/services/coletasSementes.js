import api from './api'

const API_V1 = '/api/v1'

export async function listColetasSementes(params = {}) {
  const { data } = await api.get(`${API_V1}/coletas-sementes/`, { params })
  return data
}

export async function createColetaSementes(payload) {
  const { data } = await api.post(`${API_V1}/coletas-sementes/`, payload)
  return data
}

export async function updateColetaSementes(id, payload) {
  const { data } = await api.put(`${API_V1}/coletas-sementes/${id}`, payload)
  return data
}

export async function deleteColetaSementes(id) {
  const { data } = await api.delete(`${API_V1}/coletas-sementes/${id}`)
  return data
}
