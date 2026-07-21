import api from './api'

const API_V1 = '/api/v1'

export async function getPainelContabil(params = {}) {
  const { data } = await api.get(`${API_V1}/contabilidade/painel`, { params })
  return data
}

export async function getBalancoPatrimonial(params = {}) {
  const { data } = await api.get(`${API_V1}/contabilidade/balanco`, { params })
  return data
}

export async function getLivroCaixa(params = {}) {
  const { data } = await api.get(`${API_V1}/contabilidade/livro-caixa`, { params })
  return data
}

export async function getLivroInventario(params = {}) {
  const { data } = await api.get(`${API_V1}/contabilidade/inventario`, { params })
  return data
}

export async function getNotasExplicativas(params = {}) {
  const { data } = await api.get(`${API_V1}/contabilidade/notas-explicativas`, { params })
  return data
}
