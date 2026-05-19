import api from './api'

const API_V1 = '/api/v1'

export async function login(username, password) {
  const body = new URLSearchParams()
  body.append('username', username)
  body.append('password', password)

  const { data } = await api.post(`${API_V1}/auth/login`, body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
  return data
}

export async function fetchMe() {
  const { data } = await api.get(`${API_V1}/auth/me`)
  return data
}
