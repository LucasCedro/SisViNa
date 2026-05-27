/** Perfis do SisViNa — um usuário pode ter vários perfis simultâneos. */

export const ROLES = {
  admin: {
    id: 'admin',
    label: 'Administrador',
    description: 'Acesso total ao sistema',
  },
  gestor: {
    id: 'gestor',
    label: 'Gestor do viveiro',
    description: 'Operação, estoques e vendas',
  },
  campo: {
    id: 'campo',
    label: 'Operação de campo',
    description: 'Coleta, produção e manejo das mudas',
  },
  financeiro: {
    id: 'financeiro',
    label: 'Financeiro',
    description: 'Lançamentos, custos e receitas',
  },
  rh: {
    id: 'rh',
    label: 'RH',
    description: 'Perfil de acesso (sem tela própria); combina com outros perfis',
  },
  consulta: {
    id: 'consulta',
    label: 'Consulta',
    description: 'Somente leitura',
  },
}

export const ALL_ROLE_IDS = Object.keys(ROLES)

/** Permissões granulares (união de todos os perfis do usuário). */
const EVERYONE = [...ALL_ROLE_IDS]

export const PERMISSIONS = {
  'home.view': EVERYONE,
  'coleta.view': ['admin', 'gestor', 'campo', 'consulta'],
  'coleta.create': ['admin', 'gestor', 'campo'],
  'producao.view': ['admin', 'gestor', 'campo', 'consulta'],
  'producao.transfer': ['admin', 'gestor', 'campo'],
  'viveiro.view': ['admin', 'gestor', 'campo', 'consulta'],
  'viveiro.edit': ['admin', 'gestor', 'campo'],
  'fitossanidade.view': ['admin', 'gestor', 'campo', 'consulta'],
  'fitossanidade.create': ['admin', 'gestor', 'campo'],
  'fertilizacao.view': ['admin', 'gestor', 'campo', 'consulta'],
  'fertilizacao.create': ['admin', 'gestor', 'campo'],
  'estoques.view': ['admin', 'gestor', 'campo', 'financeiro', 'consulta'],
  'estoques.edit': ['admin', 'gestor', 'campo'],
  'vendas.view': ['admin', 'gestor', 'financeiro', 'consulta'],
  'vendas.create': ['admin', 'gestor', 'financeiro'],
  'biblioteca.view': EVERYONE,
  'prescricao.view': ['admin', 'gestor', 'campo', 'consulta'],
  'financeiro.view': ['admin', 'gestor', 'financeiro', 'rh', 'consulta'],
  'financeiro.edit': ['admin', 'financeiro', 'rh'],
  'admin.users': ['admin'],
}

export function resolvePerfisFromUser(user) {
  if (!user) return []
  if (Array.isArray(user.perfis) && user.perfis.length) {
    return user.perfis.filter((p) => ROLES[p])
  }
  if (user.usuario === 'admin') return [...ALL_ROLE_IDS]
  const cargo = String(user.cargo || '').toLowerCase()
  if (cargo.includes('admin')) return ['admin', 'gestor', 'campo', 'financeiro', 'rh']
  if (cargo.includes('finance')) return ['financeiro', 'consulta']
  if (cargo.includes('rh') || cargo.includes('recursos humanos')) return ['rh', 'financeiro', 'consulta']
  if (cargo.includes('gestor')) return ['gestor', 'campo']
  return ['campo']
}

export function permissionsForPerfis(perfis) {
  const set = new Set()
  for (const [perm, allowedRoles] of Object.entries(PERMISSIONS)) {
    if (perfis.some((p) => allowedRoles.includes(p))) set.add(perm)
  }
  return set
}

export function canAccess(perfis, permission) {
  const allowed = PERMISSIONS[permission]
  if (!allowed) return false
  return perfis.some((p) => allowed.includes(p))
}
