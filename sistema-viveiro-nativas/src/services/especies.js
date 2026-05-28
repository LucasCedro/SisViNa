import api from './api'

const API_V1 = '/api/v1'

export async function listEspecies(params = {}) {
  const { data } = await api.get(`${API_V1}/especies/`, { params })
  return data
}

export async function listEspeciesBiblioteca(params = {}) {
  const { data } = await api.get(`${API_V1}/especies/biblioteca`, { params })
  return data
}

export async function sincronizarImagensExternasBiblioteca(params = {}) {
  const { data } = await api.post(
    `${API_V1}/especies/biblioteca/sincronizar-imagens-externas`,
    null,
    { params }
  )
  return data
}

export async function getImagensExternasEspecie(id, params = {}) {
  const { data } = await api.get(`${API_V1}/especies/${id}/imagens-externas`, { params })
  return data
}
