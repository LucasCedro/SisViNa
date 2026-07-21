import api from './api'

export function fetchFlorestalResumo() {
  return api.get('/api/v1/florestal/resumo').then((r) => r.data)
}

export function listGenotipos(params = {}) {
  return api.get('/api/v1/florestal/genotipos', { params }).then((r) => r.data)
}

export function createGenotipo(payload) {
  return api.post('/api/v1/florestal/genotipos', payload).then((r) => r.data)
}

export function listLotesProducao(params = {}) {
  return api.get('/api/v1/florestal/lotes', { params }).then((r) => r.data)
}

export function createLoteProducao(payload) {
  return api.post('/api/v1/florestal/lotes', payload).then((r) => r.data)
}

export function transferirLote(id, payload) {
  return api.post(`/api/v1/florestal/lotes/${id}/transferir`, payload).then((r) => r.data)
}

export function registrarPerdaLote(id, payload) {
  return api.post(`/api/v1/florestal/lotes/${id}/perda`, payload).then((r) => r.data)
}

export function listMovimentacoesLote(id) {
  return api.get(`/api/v1/florestal/lotes/${id}/movimentacoes`).then((r) => r.data)
}
