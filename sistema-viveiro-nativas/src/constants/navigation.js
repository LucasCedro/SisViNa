/** Itens do menu lateral — filtrados por permissão em runtime. */
export const NAV_ITEMS = [
  { path: '/', label: 'Início', permission: 'home.view', icon: 'home' },
  { path: '/viveiro', label: 'Viveiro', permission: 'viveiro.view', icon: 'viveiro' },
  { path: '/fitossanidade', label: 'Fitossanidade', permission: 'fitossanidade.view', icon: 'fitossanidade' },
  { path: '/fertilizacao', label: 'Fertilização', permission: 'fertilizacao.view', icon: 'fertilizacao' },
  { path: '/vendas', label: 'Vendas', permission: 'vendas.view', icon: 'vendas' },
  { path: '/prescricao', label: 'Prescrição Técnica', permission: 'prescricao.view', icon: 'prescricao', hiddenInMenu: true },
  { path: '/producao', label: 'Produção', permission: 'producao.view', icon: 'producao' },
  { path: '/estoques', label: 'Estoques', permission: 'estoques.view', icon: 'estoques' },
  { path: '/coleta', label: 'Coleta de Sementes', permission: 'coleta.view', icon: 'coleta' },
  { path: '/biblioteca', label: 'Biblioteca', permission: 'biblioteca.view', icon: 'biblioteca' },
  { path: '/financeiro', label: 'Financeiro', permission: 'financeiro.view', icon: 'financeiro' },
  { path: '/contabilidade', label: 'Contabilidade', permission: 'contabilidade.view', icon: 'contabilidade' },
]
