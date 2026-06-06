import api from './api'

const API_V1 = '/api/v1'

export async function getResumoEstoques() {
  const { data } = await api.get(`${API_V1}/estoques/resumo`)
  return data
}

export async function getTimelineEstoques(idEspecie) {
  const params = {}
  if (idEspecie) params.id_especie = idEspecie
  const { data } = await api.get(`${API_V1}/estoques/timeline`, { params })
  return data
}

export async function getAnaliticoDetalhe(params = {}) {
  const { data } = await api.get(`${API_V1}/estoques/analitico/detalhe`, { params })
  return data
}

export async function entradaSementesArmazem(payload) {
  const { data } = await api.post(`${API_V1}/estoques/entrada-sementes`, payload)
  return data
}

export async function registrarMovimentacaoInsumo(insumoId, payload) {
  const { data } = await api.post(`${API_V1}/insumos/${insumoId}/movimentacoes`, payload)
  return data
}

export async function listarMovimentacoesInsumo(insumoId, limit = 30) {
  const { data } = await api.get(`${API_V1}/insumos/${insumoId}/movimentacoes`, {
    params: { limit },
  })
  return data
}
