import { defineStore } from 'pinia'
import { login as apiLogin, fetchMe } from '../services/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    loading: false,
    error: null
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token)
  },
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const data = await apiLogin(username, password)
        this.token = data.access_token
        localStorage.setItem('token', this.token)
        await this.loadUser()
      } catch (err) {
        this.error = err.response?.data?.detail || 'Falha no login'
        throw err
      } finally {
        this.loading = false
      }
    },
    async loadUser() {
      if (!this.token) return
      this.user = await fetchMe()
    },
    async hydrate() {
      if (this.token && !this.user) {
        try {
          await this.loadUser()
        } catch {
          this.logout()
        }
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
