import api from './api'

const API_V1 = '/api/v1'

export async function listCanteiros(params = {}) {
  const { data } = await api.get(`${API_V1}/canteiros/`, { params })
  return data
}

export async function createCanteiro(payload) {
  const { data } = await api.post(`${API_V1}/canteiros/`, payload)
  return data
}

export async function updateCanteiro(id, payload) {
  const { data } = await api.put(`${API_V1}/canteiros/${id}`, payload)
  return data
}

export async function deleteCanteiro(id) {
  const { data } = await api.delete(`${API_V1}/canteiros/${id}`)
  return data
}

export async function listCanteirosComOcupacao(params = {}) {
  const { data } = await api.get(`${API_V1}/canteiros/with-ocupacao`, { params })
  return data
}
