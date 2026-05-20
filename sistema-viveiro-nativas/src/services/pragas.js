import api from './api'

const API_V1 = '/api/v1'

export async function listTiposPragas() {
  const { data } = await api.get(`${API_V1}/pragas/tipos`)
  return data
}

export async function listPragasPlantas(params = {}) {
  const { data } = await api.get(`${API_V1}/pragas/plantas`, { params })
  return data
}

export async function createPragaPlanta(payload) {
  const { data } = await api.post(`${API_V1}/pragas/plantas`, payload)
  return data
}

export async function createCombate(payload) {
  const { data } = await api.post(`${API_V1}/pragas/combates`, payload)
  return data
}
