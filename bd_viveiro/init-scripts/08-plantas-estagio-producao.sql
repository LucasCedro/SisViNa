-- Estágio operacional da muda (desenvolvimento / aptidão transferência / crescimento / aptidão venda)
ALTER TABLE plantas ADD COLUMN IF NOT EXISTS estagio_producao VARCHAR(30) NOT NULL DEFAULT 'em_desenvolvimento';
CREATE INDEX IF NOT EXISTS ix_plantas_estagio_producao ON plantas(estagio_producao);

UPDATE plantas p
SET estagio_producao = 'em_desenvolvimento'
FROM canteiros c
WHERE p.id_canteiro = c.id
  AND c.tipo_local = 'sementeira'
  AND p.status = 'SEMENTE';

UPDATE plantas p
SET estagio_producao = 'em_crescimento'
FROM canteiros c
WHERE p.id_canteiro = c.id
  AND c.tipo_local = 'canteiro'
  AND p.status IN ('MUDA', 'JOVEM', 'ADULTA');
