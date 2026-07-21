import api from './api'

const BASE = '/api/v1/empresa'

export async function listEmpresaUsuarios(params = {}) {
  const { data } = await api.get(`${BASE}/usuarios`, { params })
  return data
}

export async function createEmpresaUsuario(payload) {
  const { data } = await api.post(`${BASE}/usuarios`, payload)
  return data
}

export async function updateEmpresaUsuario(id, payload) {
  const { data } = await api.put(`${BASE}/usuarios/${id}`, payload)
  return data
}

export async function deactivateEmpresaUsuario(id) {
  const { data } = await api.delete(`${BASE}/usuarios/${id}`)
  return data
}
