import api from './api'

const API_V1 = '/api/v1'

export async function getProducaoResumo() {
  const { data } = await api.get(`${API_V1}/producao/resumo`)
  return data
}
