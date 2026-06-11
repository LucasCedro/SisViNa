-- Limpa dados operacionais do viveiro; preserva funcionarios e catálogo de referência.
-- Uso:
--   Get-Content bd_viveiro\patches\limpar-operacional-manter-usuarios.sql -Raw |
--     docker compose exec -T postgres psql -U viveiro_admin -d viveiro_db

BEGIN;

TRUNCATE TABLE
  notas_fiscais_itens,
  notas_fiscais,
  regras_fiscais,
  emitente_fiscal,
  itens_venda,
  vendas,
  compradores,
  transferencias_plantas,
  combates_realizados,
  pragas_plantas,
  insumos_atividades,
  atividades,
  insumo_movimentacoes,
  insumos,
  lancamentos_financeiros,
  financeiro_premissas,
  semeaduras,
  testes_sementes,
  lotes_sementes,
  coletas_sementes,
  plantas,
  arvores_matriz,
  canteiros,
  viveiro_layout
RESTART IDENTITY CASCADE;

COMMIT;
