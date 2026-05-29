import api from './api'

const API_V1 = '/api/v1'

export async function getViveiroLayout() {
  const { data } = await api.get(`${API_V1}/viveiro/layout/`)
  return data.layout || {}
}

export async function saveViveiroLayout(layout) {
  const { data } = await api.put(`${API_V1}/viveiro/layout/`, { layout })
  return data.layout
}
