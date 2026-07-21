import api from './api'

const API_V1 = '/api/v1'

export async function listPlantas(params = {}) {
  const { data } = await api.get(`${API_V1}/plantas/`, { params })
  return data
}

export async function listPlantasComRelacoes(params = {}) {
  const { data } = await api.get(`${API_V1}/plantas/with-relations`, { params })
  return data
}

export async function getEstoqueResumo() {
  const { data } = await api.get(`${API_V1}/plantas/estoque-resumo`)
  return data
}

/** Plantas individuais aptas à venda (única origem para itens de venda). */
export async function listPlantasDisponiveisVenda(idEspecie, limit = 500) {
  const { data } = await api.get(`${API_V1}/plantas/disponiveis-venda`, {
    params: { id_especie: idEspecie, limit },
  })
  return data
}

/** Mudas expedíveis com lote, canteiro e dias na rustificação — formulário de venda. */
export async function listPlantasDisponiveisVendaDetalhado(idEspecie, params = {}) {
  const { data } = await api.get(`${API_V1}/plantas/disponiveis-venda/detalhado`, {
    params: { id_especie: idEspecie, ...params },
  })
  return data
}

export async function atualizarPrecoEspecie(idEspecie, precoVenda) {
  const { data } = await api.patch(`${API_V1}/plantas/preco-especie/${idEspecie}`, {
    preco_venda: precoVenda
  })
  return data
}

export async function createPlanta(payload) {
  const { data } = await api.post(`${API_V1}/plantas/`, payload)
  return data
}

export async function createPlantasBulk(payload, quantidade) {
  const { data } = await api.post(`${API_V1}/plantas/bulk`, payload, {
    params: { quantidade }
  })
  return data
}

export async function updatePlanta(id, payload) {
  const { data } = await api.put(`${API_V1}/plantas/${id}`, payload)
  return data
}

export async function deletePlanta(id) {
  const { data } = await api.delete(`${API_V1}/plantas/${id}`)
  return data
}

export async function listPendentesTransferencia(params = {}) {
  const { data } = await api.get(`${API_V1}/plantas/pendentes-transferencia`, { params })
  return data
}

export async function listEmDesenvolvimentoSementeira(params = {}) {
  const { data } = await api.get(`${API_V1}/plantas/em-desenvolvimento-sementeira`, { params })
  return data
}

export async function listEmCrescimentoCanteiro(params = {}) {
  const { data } = await api.get(`${API_V1}/plantas/em-crescimento-canteiro`, { params })
  return data
}

export async function listEmRustificacao(params = {}) {
  const { data } = await api.get(`${API_V1}/plantas/em-rustificacao`, { params })
  return data
}

export async function listAptasRustificacaoCanteiro(params = {}) {
  const { data } = await api.get(
    `${API_V1}/plantas/aptas-rustificacao-canteiro`,
    { params },
  )
  return data
}

export async function transferirRustificacao(payload) {
  const { data } = await api.post(`${API_V1}/plantas/transferir-rustificacao`, payload)
  return data
}

export async function atualizarEstagioProducao(payload) {
  const { data } = await api.post(`${API_V1}/plantas/atualizar-estagio`, payload)
  return data
}

export async function promoverMudas(payload) {
  const { data } = await api.post(`${API_V1}/plantas/promover-mudas`, payload)
  return data
}

export async function getResumoOperacaoLote(etapa, params = {}) {
  const { data } = await api.get(`${API_V1}/plantas/resumo-operacao-lote`, {
    params: { etapa, ...params },
  })
  return data
}

export async function atualizarEstagioLote(payload) {
  const { data } = await api.post(`${API_V1}/plantas/atualizar-estagio-lote`, payload)
  return data
}

export async function promoverMudasLote(payload) {
  const { data } = await api.post(`${API_V1}/plantas/promover-mudas-lote`, payload)
  return data
}

export async function transferirRustificacaoLote(payload) {
  const { data } = await api.post(`${API_V1}/plantas/transferir-rustificacao-lote`, payload)
  return data
}

export async function cadastroLotePlantas(payload) {
  const { data } = await api.post(`${API_V1}/plantas/cadastro-lote`, payload)
  return data
}
