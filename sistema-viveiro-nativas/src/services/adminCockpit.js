import api from './api'

const BASE = '/api/v1/admin/cockpit'

export async function fetchAdminOverview() {
  const { data } = await api.get(`${BASE}/overview`)
  return data
}

export async function fetchAdminRbac() {
  const { data } = await api.get(`${BASE}/rbac`)
  return data
}

export async function listAdminFuncionarios(params = {}) {
  const { data } = await api.get(`${BASE}/funcionarios`, { params })
  return data
}

export async function createAdminFuncionario(payload) {
  const { data } = await api.post(`${BASE}/funcionarios`, payload)
  return data
}

export async function updateAdminFuncionario(id, payload) {
  const { data } = await api.put(`${BASE}/funcionarios/${id}`, payload)
  return data
}

export async function deactivateAdminFuncionario(id) {
  const { data } = await api.delete(`${BASE}/funcionarios/${id}`)
  return data
}
