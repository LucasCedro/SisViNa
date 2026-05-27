import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import {
  ROLES,
  resolvePerfisFromUser,
  permissionsForPerfis,
  canAccess as canAccessPerfis,
} from '@/constants/roles'

export function usePermissions() {
  const auth = useAuthStore()

  const perfis = computed(() => resolvePerfisFromUser(auth.user))
  const permissions = computed(() => permissionsForPerfis(perfis.value))

  const perfilLabels = computed(() =>
    perfis.value.map((id) => ROLES[id]?.label || id)
  )

  function can(permission) {
    return canAccessPerfis(perfis.value, permission)
  }

  function canAny(...perms) {
    return perms.some((p) => can(p))
  }

  function hasRole(roleId) {
    return perfis.value.includes(roleId)
  }

  return {
    perfis,
    permissions,
    perfilLabels,
    can,
    canAny,
    hasRole,
  }
}
