import api from './api'

const API_V1 = '/api/v1'

export async function getResumoEstoques() {
  const { data } = await api.get(`${API_V1}/estoques/resumo`)
  return data
}

export async function entradaSementesArmazem(payload) {
  const { data } = await api.post(`${API_V1}/estoques/entrada-sementes`, payload)
  return data
}
