import { defineStore } from 'pinia'
import { fetchViveiroContexto } from '@/services/viveiros'

const STORAGE_KEY = 'brotare_admin_viveiro_id'

/** Contexto de unidade viveiro (nativo/florestal) — seletor exclusivo admin. */
export const useViveiroContextStore = defineStore('viveiroContext', {
  state: () => ({
    ativo: null,
    lista: [],
    modulosHabilitados: [],
    modulosNavDesabilitados: [],
    podeSelecionar: false,
    loaded: false,
  }),
  getters: {
    modoOperacao: (s) => s.ativo?.modo_operacao || 'nativo',
    modoLabel: (s) => s.ativo?.modo_label || 'Nativo',
    isFlorestal: (s) => s.ativo?.modo_operacao === 'florestal',
    headerViveiroId: (s) => {
      if (!s.podeSelecionar) return null
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? Number(stored) : s.ativo?.id ?? null
    },
  },
  actions: {
    applyFromAuthMe(user) {
      if (!user) return
      this.ativo = user.viveiro_ativo || null
      this.lista = user.viveiros || []
      this.modulosHabilitados = user.modulos_habilitados || []
      this.modulosNavDesabilitados = user.modulos_nav_desabilitados || []
      this.podeSelecionar = Boolean(user.pode_selecionar_viveiro)
      this.loaded = true
    },
    async refreshContexto() {
      const data = await fetchViveiroContexto(this.headerViveiroId)
      this.ativo = data.viveiro_ativo
      this.lista = data.viveiros
      this.modulosHabilitados = data.modulos_habilitados
      this.modulosNavDesabilitados = data.modulos_nav_desabilitados
      this.podeSelecionar = data.pode_selecionar_viveiro
      this.loaded = true
      return data
    },
    async selectViveiro(id, { reloadUser = true } = {}) {
      if (!this.podeSelecionar) return
      localStorage.setItem(STORAGE_KEY, String(id))
      await this.refreshContexto()
      if (reloadUser) {
        const { useAuthStore } = await import('./auth')
        await useAuthStore().loadUser()
      }
    },
    clearAdminSelection() {
      localStorage.removeItem(STORAGE_KEY)
    },
    navModuleDisabled(moduleKey) {
      return this.modulosNavDesabilitados.includes(moduleKey)
    },
  },
})
