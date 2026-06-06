/** Labels de perfis — apenas exibição na UI. Enforcement vem do backend via permissions[]. */

export const ROLES_LABELS = {
  admin: 'Administrador',
  gestor: 'Gestor do Viveiro',
  campo: 'Operação de Campo',
  financeiro: 'Financeiro',
  consulta: 'Consulta',
  rh: 'Recursos Humanos',
}

/** @deprecated use ROLES_LABELS — alias para compatibilidade temporária */
export const ROLES = Object.fromEntries(
  Object.entries(ROLES_LABELS).map(([id, label]) => [
    id,
    { id, label, description: label },
  ])
)

export function perfilLabelsFromUser(user) {
  if (!user?.perfis?.length) return []
  return user.perfis.map((p) => ROLES_LABELS[p] || p)
}
