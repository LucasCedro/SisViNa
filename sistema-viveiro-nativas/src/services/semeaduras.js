import api from './api'

const API_V1 = '/api/v1'

export async function listSemeaduras(params = {}) {
  const { data } = await api.get(`${API_V1}/semeaduras/`, { params })
  return data
}

export async function createSemeadura(payload) {
  const { data } = await api.post(`${API_V1}/semeaduras/`, payload)
  return data
}

export async function getRastreabilidadePlanta(plantaId) {
  const { data } = await api.get(`${API_V1}/semeaduras/rastreabilidade/planta/${plantaId}`)
  return data
}
