import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import { perfilLabelsFromUser } from '@/constants/roles'

export function usePermissions() {
  const auth = useAuthStore()

  const permissions = computed(() => auth.permissions)

  const perfilLabels = computed(() => perfilLabelsFromUser(auth.user))

  function can(permission) {
    return auth.can(permission)
  }

  function canAny(...perms) {
    return perms.some((p) => can(p))
  }

  function hasRole(roleId) {
    return Array.isArray(auth.user?.perfis) && auth.user.perfis.includes(roleId)
  }

  function hasAnyRole(...roleIds) {
    const perfis = auth.user?.perfis
    if (!Array.isArray(perfis) || !roleIds.length) return false
    return roleIds.some((r) => perfis.includes(r))
  }

  return {
    permissions,
    perfilLabels,
    can,
    canAny,
    hasRole,
    hasAnyRole,
  }
}
