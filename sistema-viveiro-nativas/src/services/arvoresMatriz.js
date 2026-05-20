import api from './api'

const API_V1 = '/api/v1'

export async function listArvoresMatriz(params = {}) {
  const { data } = await api.get(`${API_V1}/arvores-matriz/`, { params })
  return data
}

export async function getArvoreMatriz(id) {
  const { data } = await api.get(`${API_V1}/arvores-matriz/${id}`)
  return data
}

export async function createArvoreMatriz(payload) {
  const { data } = await api.post(`${API_V1}/arvores-matriz/`, payload)
  return data
}

export async function updateArvoreMatriz(id, payload) {
  const { data } = await api.put(`${API_V1}/arvores-matriz/${id}`, payload)
  return data
}

export async function deleteArvoreMatriz(id) {
  const { data } = await api.delete(`${API_V1}/arvores-matriz/${id}`)
  return data
}
