-- Tabela de árvores matrizes (coleta de sementes)
CREATE TABLE IF NOT EXISTS arvores_matriz (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    id_especie INTEGER NOT NULL REFERENCES especies(id),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    tipo_coordenada VARCHAR(20) NOT NULL DEFAULT 'geografica',
    utm_zona INTEGER,
    utm_easting NUMERIC(12, 2),
    utm_northing NUMERIC(12, 2),
    sementes_coletadas INTEGER DEFAULT 0,
    taxa_germinacao NUMERIC(5, 2),
    data_ultima_coleta DATE,
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
