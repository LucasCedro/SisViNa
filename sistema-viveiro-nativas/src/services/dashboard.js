import api from './api'

const API_V1 = '/api/v1'

export async function getDashboardResumo() {
  const { data } = await api.get(`${API_V1}/dashboard/resumo`)
  return data
}

export async function getResumoFinanceiro() {
  const { data } = await api.get(`${API_V1}/dashboard/financeiro`)
  return data
}
