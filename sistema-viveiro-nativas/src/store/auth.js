import { defineStore } from 'pinia'
import { login as apiLogin, fetchMe, updateMe, resetPassword } from '../services/auth'
import { perfilLabelsFromUser } from '@/constants/roles'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    permissions: [],
    loading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    perfilLabels: (state) => perfilLabelsFromUser(state.user),
  },
  actions: {
    can(permissionName) {
      return this.permissions.includes(permissionName)
    },
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
      const data = await fetchMe()
      this.user = data
      this.permissions = Array.isArray(data.permissions) ? data.permissions : []
      const { useViveiroContextStore } = await import('./viveiroContext')
      useViveiroContextStore().applyFromAuthMe(data)
    },
    async updateProfile(payload) {
      const data = await updateMe(payload)
      this.user = data
      this.permissions = Array.isArray(data.permissions) ? data.permissions : this.permissions
      return data
    },
    async changePassword(oldPassword, newPassword) {
      await resetPassword(oldPassword, newPassword)
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
      this.permissions = []
      localStorage.removeItem('token')
      localStorage.removeItem('brotare_admin_viveiro_id')
      localStorage.removeItem('brotare_admin_empresa_id')
    },
  },
})
