-- Espelho da migração Alembic 09 (instalações via init-scripts)
CREATE TABLE IF NOT EXISTS viveiro_regras_globais (
    chave VARCHAR(80) PRIMARY KEY,
    valor_numerico NUMERIC(12, 4),
    valor_texto TEXT,
    descricao TEXT,
    fonte VARCHAR(200) NOT NULL DEFAULT 'SisViNa',
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS especies_ficha_embrapa (
    id_especie INTEGER PRIMARY KEY REFERENCES especies(id) ON DELETE CASCADE,
    nome_cientifico_ref VARCHAR(150),
    fitofisionomia TEXT,
    mes_coleta_inicio SMALLINT,
    mes_coleta_fim SMALLINT,
    armazenamento_tipo VARCHAR(40),
    armazenamento_obs TEXT,
    profundidade_semeadura_cm_min NUMERIC(4, 2),
    profundidade_semeadura_cm_max NUMERIC(4, 2),
    dias_inicio_germinacao INTEGER,
    pct_germinacao_tipico NUMERIC(5, 2),
    substrato_tipo SMALLINT,
    conduz_pleno_sol BOOLEAN,
    meses_permanencia_viveiro INTEGER,
    meses_permanencia_viveiro_max INTEGER,
    dias_rustificacao_minimo INTEGER,
    altura_campo_cm_min NUMERIC(5, 2),
    altura_campo_cm_max NUMERIC(5, 2),
    adubacao_obs TEXT,
    observacoes_gerais TEXT,
    fonte VARCHAR(200) NOT NULL DEFAULT 'SisViNa',
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE plantas ADD COLUMN IF NOT EXISTS data_inicio_estagio_atual DATE;

INSERT INTO viveiro_regras_globais (chave, valor_numerico, descricao, fonte) VALUES
    ('rustificacao_dias_minimo', 30, 'Permanência mínima na rustificação.', 'SisViNa'),
    ('rustificacao_inicio_antes_plantio_dias', 60, 'Retirada gradual de sombreamento.', 'SisViNa'),
    ('altura_campo_cerrado_cm_min', 20, 'Altura mínima Cerrado.', 'SisViNa'),
    ('altura_campo_cerrado_cm_max', 30, 'Altura máxima típica Cerrado.', 'SisViNa'),
    ('altura_campo_floresta_cm_min', 50, 'Altura mínima floresta.', 'SisViNa'),
    ('permanencia_viveiro_meses_tipico', 5, 'Permanência média no viveiro.', 'SisViNa'),
    ('permanencia_viveiro_meses_max', 12, 'Permanência máxima citada.', 'SisViNa'),
    ('rega_germinacao_vezes_dia', 2, 'Regas na emergência.', 'SisViNa'),
    ('rega_rustificacao_vezes_dia', 1, 'Rega na rustificação.', 'SisViNa'),
    ('coleta_fracao_maxima_arvore', 0.5, 'Fração máxima de frutos por árvore.', 'SisViNa')
ON CONFLICT (chave) DO NOTHING;
