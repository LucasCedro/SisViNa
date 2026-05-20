-- =============================================================================
-- SisViNa — Cadeia persistente: matriz → coleta → lote → teste → semeadura → muda → venda
-- Script único de domínio (coleta, lotes, testes, semeadura, rastreio e view até venda).
-- Ordem: após 04-arvores-matriz.sql
-- =============================================================================

-- Coletas (eventos de campo)
CREATE TABLE IF NOT EXISTS coletas_sementes (
    id SERIAL PRIMARY KEY,
    id_arvore_matriz INTEGER NOT NULL REFERENCES arvores_matriz(id) ON DELETE CASCADE,
    id_funcionario INTEGER NOT NULL REFERENCES funcionarios(id),
    data_coleta DATE NOT NULL,
    quantidade_sementes INTEGER NOT NULL CHECK (quantidade_sementes > 0),
    observacoes TEXT,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_coletas_sementes_matriz ON coletas_sementes(id_arvore_matriz);
CREATE INDEX IF NOT EXISTS ix_coletas_sementes_data ON coletas_sementes(data_coleta);

-- Procedência e fenologia na matriz
ALTER TABLE arvores_matriz ADD COLUMN IF NOT EXISTS municipio VARCHAR(100);
ALTER TABLE arvores_matriz ADD COLUMN IF NOT EXISTS imovel_nome VARCHAR(200);
ALTER TABLE arvores_matriz ADD COLUMN IF NOT EXISTS tipo_origem VARCHAR(50);
ALTER TABLE arvores_matriz ADD COLUMN IF NOT EXISTS numero_autorizacao VARCHAR(120);
ALTER TABLE arvores_matriz ADD COLUMN IF NOT EXISTS observacoes_legais TEXT;
ALTER TABLE arvores_matriz ADD COLUMN IF NOT EXISTS mes_inicio_frutificacao SMALLINT;
ALTER TABLE arvores_matriz ADD COLUMN IF NOT EXISTS mes_fim_frutificacao SMALLINT;
ALTER TABLE arvores_matriz ADD COLUMN IF NOT EXISTS estagio_frutificacao VARCHAR(80);
ALTER TABLE arvores_matriz ADD COLUMN IF NOT EXISTS fenologia_observacoes TEXT;

-- Lote (estoque rastreável de sementes)
CREATE TABLE IF NOT EXISTS lotes_sementes (
    id SERIAL PRIMARY KEY,
    codigo_lote VARCHAR(50) NOT NULL UNIQUE,
    id_coleta_sementes INTEGER NOT NULL REFERENCES coletas_sementes(id) ON DELETE CASCADE,
    id_arvore_matriz INTEGER NOT NULL REFERENCES arvores_matriz(id) ON DELETE CASCADE,
    id_especie INTEGER NOT NULL REFERENCES especies(id),
    quantidade_inicial INTEGER NOT NULL CHECK (quantidade_inicial > 0),
    quantidade_disponivel INTEGER NOT NULL CHECK (quantidade_disponivel >= 0),
    data_formacao_lote DATE NOT NULL,
    beneficiamento TEXT,
    condicoes_armazenamento TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'ativo',
    observacoes TEXT,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_lotes_sementes_matriz ON lotes_sementes(id_arvore_matriz);
CREATE INDEX IF NOT EXISTS ix_lotes_sementes_coleta ON lotes_sementes(id_coleta_sementes);

-- Testes de qualidade (germinação / viabilidade por lote)
CREATE TABLE IF NOT EXISTS testes_sementes (
    id SERIAL PRIMARY KEY,
    id_lote_sementes INTEGER NOT NULL REFERENCES lotes_sementes(id) ON DELETE CASCADE,
    data_teste DATE NOT NULL,
    tipo_teste VARCHAR(40) NOT NULL,
    metodologia TEXT,
    repeticoes INTEGER DEFAULT 1,
    sementes_avaliadas INTEGER,
    percentual_resultado NUMERIC(5, 2) NOT NULL,
    observacoes TEXT,
    id_funcionario INTEGER NOT NULL REFERENCES funcionarios(id),
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_testes_sementes_lote ON testes_sementes(id_lote_sementes);

-- Semeadura no viveiro (uso de sementes do lote → origem das mudas)
CREATE TABLE IF NOT EXISTS semeaduras (
    id SERIAL PRIMARY KEY,
    id_lote_sementes INTEGER NOT NULL REFERENCES lotes_sementes(id),
    id_canteiro INTEGER REFERENCES canteiros(id),
    data_semeadura DATE NOT NULL,
    quantidade_sementes_usadas INTEGER NOT NULL CHECK (quantidade_sementes_usadas > 0),
    quantidade_mudas_obtidas INTEGER,
    observacoes TEXT,
    id_funcionario INTEGER NOT NULL REFERENCES funcionarios(id),
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_semeaduras_lote ON semeaduras(id_lote_sementes);

-- Vínculo da muda com origem (FK em plantas — tabela já existe no schema base)
ALTER TABLE plantas ADD COLUMN IF NOT EXISTS id_lote_sementes INTEGER REFERENCES lotes_sementes(id);
ALTER TABLE plantas ADD COLUMN IF NOT EXISTS id_semeadura INTEGER REFERENCES semeaduras(id);

-- View: origem da muda (até semeadura)
CREATE OR REPLACE VIEW vw_rastreabilidade_muda AS
SELECT
    p.id AS id_planta,
    p.codigo_rastreio,
    p.status AS status_planta,
    p.data_plantio,
    e.id AS id_especie,
    COALESCE(e.nome_popular, e.nome_cientifico) AS especie_nome,
    ls.codigo_lote,
    ls.id AS id_lote,
    c.id AS id_coleta,
    c.data_coleta,
    m.id AS id_arvore_matriz,
    m.nome AS matriz_nome,
    m.imovel_nome,
    m.municipio,
    m.tipo_origem,
    m.numero_autorizacao,
    s.id AS id_semeadura,
    s.data_semeadura,
    s.quantidade_sementes_usadas
FROM plantas p
LEFT JOIN semeaduras s ON p.id_semeadura = s.id
LEFT JOIN lotes_sementes ls ON COALESCE(p.id_lote_sementes, s.id_lote_sementes) = ls.id
LEFT JOIN coletas_sementes c ON ls.id_coleta_sementes = c.id
LEFT JOIN arvores_matriz m ON ls.id_arvore_matriz = m.id
LEFT JOIN especies e ON p.id_especie = e.id;

-- View: cadeia completa até venda (itens_venda → vendas)
CREATE OR REPLACE VIEW vw_cadeia_semente_muda_venda AS
SELECT
    p.id AS id_planta,
    p.codigo_rastreio,
    p.status AS status_planta,
    p.data_plantio,
    ls.codigo_lote,
    m.nome AS matriz_nome,
    c.data_coleta,
    s.data_semeadura,
    iv.id AS id_item_venda,
    iv.quantidade AS qtd_vendida,
    iv.valor_unitario,
    v.id AS id_venda,
    v.data_venda,
    v.status AS status_venda,
    comp.nome AS comprador_nome
FROM plantas p
LEFT JOIN semeaduras s ON p.id_semeadura = s.id
LEFT JOIN lotes_sementes ls ON COALESCE(p.id_lote_sementes, s.id_lote_sementes) = ls.id
LEFT JOIN coletas_sementes c ON ls.id_coleta_sementes = c.id
LEFT JOIN arvores_matriz m ON ls.id_arvore_matriz = m.id
LEFT JOIN itens_venda iv ON iv.id_planta = p.id
LEFT JOIN vendas v ON v.id = iv.id_venda
LEFT JOIN compradores comp ON comp.id = v.id_comprador;

CREATE OR REPLACE VIEW vw_coletas_sementes_bi AS
SELECT
    c.id,
    c.data_coleta,
    c.quantidade_sementes,
    c.observacoes,
    c.data_registro,
    m.id AS id_arvore_matriz,
    m.nome AS matriz_nome,
    m.cidade,
    m.estado,
    e.id AS id_especie,
    COALESCE(e.nome_popular, e.nome_cientifico) AS especie_nome,
    f.id AS id_funcionario,
    f.nome AS funcionario_nome
FROM coletas_sementes c
INNER JOIN arvores_matriz m ON c.id_arvore_matriz = m.id
INNER JOIN especies e ON m.id_especie = e.id
INNER JOIN funcionarios f ON c.id_funcionario = f.id;

-- Retrocompat: coletas antigas sem lote
INSERT INTO lotes_sementes (
    codigo_lote, id_coleta_sementes, id_arvore_matriz, id_especie,
    quantidade_inicial, quantidade_disponivel, data_formacao_lote, status, observacoes
)
SELECT
    'LS-' || EXTRACT(YEAR FROM c.data_coleta)::int || '-' ||
    LPAD(c.id_arvore_matriz::text, 3, '0') || '-' || LPAD(c.id::text, 4, '0'),
    c.id,
    c.id_arvore_matriz,
    m.id_especie,
    c.quantidade_sementes,
    c.quantidade_sementes,
    c.data_coleta,
    'ativo',
    'Lote gerado na migração'
FROM coletas_sementes c
INNER JOIN arvores_matriz m ON c.id_arvore_matriz = m.id
WHERE NOT EXISTS (
    SELECT 1 FROM lotes_sementes ls WHERE ls.id_coleta_sementes = c.id
);
