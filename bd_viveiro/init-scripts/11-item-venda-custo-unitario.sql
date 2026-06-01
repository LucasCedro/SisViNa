-- CMV snapshot no momento da venda (idempotente)
ALTER TABLE itens_venda
  ADD COLUMN IF NOT EXISTS custo_unitario DECIMAL(10,2);

UPDATE itens_venda iv
SET custo_unitario = COALESCE(p.custo_atual, 0)
FROM plantas p
WHERE p.id = iv.id_planta AND iv.custo_unitario IS NULL;
