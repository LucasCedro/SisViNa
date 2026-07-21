/** Itens do menu lateral — ordem = fluxo operacional; filtrados por permissão em runtime. */
export const NAV_ITEMS = [
  { path: '/', label: 'Início', permission: 'home.view', icon: 'home', moduleKey: 'home' },
  { path: '/coleta', label: 'Coleta Sementes', permission: 'coleta.view', icon: 'coleta', moduleKey: 'coleta' },
  { path: '/producao', label: 'Produção', permission: 'producao.view', icon: 'producao', moduleKey: 'producao' },
  { path: '/florestal', label: 'Produção Florestal', permission: 'florestal.view', icon: 'producao', moduleKey: 'florestal' },
  { path: '/viveiro', label: 'Viveiro', permission: 'viveiro.view', icon: 'viveiro', moduleKey: 'viveiro' },
  { path: '/fertilizacao', label: 'Fertilização', permission: 'fertilizacao.view', icon: 'fertilizacao', moduleKey: 'fertilizacao' },
  { path: '/fitossanidade', label: 'Fitossanidade', permission: 'fitossanidade.view', icon: 'fitossanidade', moduleKey: 'fitossanidade' },
  { path: '/estoques', label: 'Compras/Estoques', permission: 'estoques.view', icon: 'estoques', moduleKey: 'estoques' },
  { path: '/vendas', label: 'Vendas', permission: 'vendas.view', icon: 'vendas', moduleKey: 'vendas' },
  { path: '/financeiro', label: 'Financeiro', permission: 'financeiro.view', icon: 'financeiro', moduleKey: 'financeiro' },
  { path: '/contabilidade', label: 'Contabilidade', permission: 'contabilidade.view', icon: 'contabilidade', moduleKey: 'contabilidade' },
  { path: '/biblioteca', label: 'Biblioteca', permission: 'biblioteca.view', icon: 'biblioteca', moduleKey: 'biblioteca' },
  { path: '/prescricao', label: 'Prescrição Técnica', permission: 'prescricao.view', icon: 'prescricao', moduleKey: 'prescricao', hiddenInMenu: true },
]

/** Bottom nav mobile — módulos operacionais de campo (Sprint 1 mobile). */
export const MOBILE_NAV_PATHS = ['/', '/coleta', '/producao', '/fitossanidade', '/fertilizacao']

export const MOBILE_NAV_SHORT_LABELS = {
  '/': 'Início',
  '/coleta': 'Coleta',
  '/producao': 'Produção',
  '/fitossanidade': 'Fitoss.',
  '/fertilizacao': 'Fertil.',
}
