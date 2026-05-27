ALTER TABLE canteiros DROP CONSTRAINT IF EXISTS canteiros_tipo_local_check;
ALTER TABLE canteiros ADD CONSTRAINT canteiros_tipo_local_check
    CHECK (tipo_local IN ('sementeira', 'canteiro', 'armazem', 'rustificacao'));
