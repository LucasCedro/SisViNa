-- Locais do viveiro, origem das mudas e transferência (aplicar em banco existente)
ALTER TABLE canteiros ADD COLUMN IF NOT EXISTS tipo_local VARCHAR(20) NOT NULL DEFAULT 'canteiro';
ALTER TABLE canteiros DROP CONSTRAINT IF EXISTS canteiros_tipo_local_check;
ALTER TABLE canteiros ADD CONSTRAINT canteiros_tipo_local_check
    CHECK (tipo_local IN ('sementeira', 'canteiro', 'armazem'));

ALTER TABLE plantas ADD COLUMN IF NOT EXISTS origem VARCHAR(30) NOT NULL DEFAULT 'semeadura';
ALTER TABLE plantas DROP CONSTRAINT IF EXISTS plantas_origem_check;
ALTER TABLE plantas ADD CONSTRAINT plantas_origem_check
    CHECK (origem IN ('semeadura', 'compra', 'doacao', 'ajuste'));

ALTER TABLE lotes_sementes ALTER COLUMN id_coleta_sementes DROP NOT NULL;
ALTER TABLE lotes_sementes ALTER COLUMN id_arvore_matriz DROP NOT NULL;
ALTER TABLE lotes_sementes ADD COLUMN IF NOT EXISTS origem_lote VARCHAR(30) NOT NULL DEFAULT 'coleta';
ALTER TABLE lotes_sementes DROP CONSTRAINT IF EXISTS lotes_origem_lote_check;
ALTER TABLE lotes_sementes ADD CONSTRAINT lotes_origem_lote_check
    CHECK (origem_lote IN ('coleta', 'compra', 'armazem', 'ajuste'));

CREATE TABLE IF NOT EXISTS transferencias_plantas (
    id SERIAL PRIMARY KEY,
    id_planta INTEGER NOT NULL REFERENCES plantas(id) ON DELETE CASCADE,
    id_canteiro_origem INTEGER REFERENCES canteiros(id),
    id_canteiro_destino INTEGER NOT NULL REFERENCES canteiros(id),
    status_anterior VARCHAR(20),
    status_novo VARCHAR(20) NOT NULL,
    data_transferencia TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_funcionario INTEGER REFERENCES funcionarios(id),
    observacoes TEXT
);

CREATE INDEX IF NOT EXISTS ix_plantas_origem ON plantas(origem);
CREATE INDEX IF NOT EXISTS ix_canteiros_tipo_local ON canteiros(tipo_local);
