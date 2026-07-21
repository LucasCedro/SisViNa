import api from './api'

export function fetchViveiroContexto(viveiroId = null) {
  const headers = {}
  if (viveiroId) headers['X-Viveiro-Id'] = String(viveiroId)
  return api.get('/api/v1/viveiros/contexto', { headers }).then((r) => r.data)
}

export function listViveiros() {
  return api.get('/api/v1/viveiros/').then((r) => r.data)
}

export function createViveiroAdmin(payload) {
  return api.post('/api/v1/admin/cockpit/viveiros', payload).then((r) => r.data)
}
