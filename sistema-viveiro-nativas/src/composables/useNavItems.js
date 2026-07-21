import { computed } from 'vue'
import { HomeIcon } from '@heroicons/vue/24/outline'
import {
  NAV_ITEMS,
  MOBILE_NAV_PATHS,
  MOBILE_NAV_SHORT_LABELS,
} from '@/constants/navigation'
import { NAV_ICONS } from '@/constants/navIcons'
import { usePermissions } from '@/composables/usePermissions'
import { useViveiroContextStore } from '@/store/viveiroContext'

function filterNavItem(item, can, viveiro) {
  if (item.hiddenInMenu) return false
  if (!can(item.permission)) return false
  if (item.moduleKey && viveiro.navModuleDisabled(item.moduleKey)) return false
  return true
}

/** Itens do menu lateral — permissão RBAC + pipeline do viveiro ativo */
export function useSidebarNavItems() {
  const { can } = usePermissions()
  const viveiro = useViveiroContextStore()

  return computed(() =>
    NAV_ITEMS.filter((item) => filterNavItem(item, can, viveiro)).map((item) => ({
      ...item,
      iconComponent: NAV_ICONS[item.icon] || HomeIcon,
    }))
  )
}

/** Bottom nav mobile — subset operacional + mesma regra de permissão */
export function useMobileNavItems() {
  const { can } = usePermissions()
  const viveiro = useViveiroContextStore()

  return computed(() =>
    NAV_ITEMS.filter(
      (item) =>
        MOBILE_NAV_PATHS.includes(item.path) && filterNavItem(item, can, viveiro)
    ).map((item) => ({
      ...item,
      shortLabel: MOBILE_NAV_SHORT_LABELS[item.path] || item.label,
      iconComponent: NAV_ICONS[item.icon] || HomeIcon,
    }))
  )
}
