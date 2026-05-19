-- Criação do banco de dados
CREATE DATABASE viveiro_db;

-- Conectar ao banco de dados
\c viveiro_db

-- Tabela de Espécies (ID matriz)
CREATE TABLE especies (
    id SERIAL PRIMARY KEY,
    nome_cientifico VARCHAR(100) NOT NULL,
    nome_popular VARCHAR(100),
    familia VARCHAR(50),
    descricao TEXT,
    tempo_germinacao INT, -- em dias
    tempo_crescimento INT, -- em dias
    altura_maxima DECIMAL(5,2), -- em metros
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (nome_cientifico)
);

-- Tabela de Funcionários
CREATE TABLE funcionarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    rg VARCHAR(20),
    data_nascimento DATE,
    telefone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    endereco VARCHAR(200),
    cargo VARCHAR(50),
    data_contratacao DATE,
    salario DECIMAL(10,2),
    usuario VARCHAR(50) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Compradores
CREATE TABLE compradores (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('PF', 'PJ')), -- Pessoa Física ou Jurídica
    nome VARCHAR(100) NOT NULL,
    cpf_cnpj VARCHAR(18) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    endereco VARCHAR(200),
    cidade VARCHAR(50),
    estado VARCHAR(2),
    cep VARCHAR(10),
    usuario VARCHAR(50) UNIQUE,
    senha VARCHAR(255),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Tabela de Canteiros (Zonas do Viveiro)
CREATE TABLE canteiros (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    descricao TEXT,
    area_total DECIMAL(10,2), -- em metros quadrados
    localizacao VARCHAR(100),
    tipo_solo VARCHAR(50),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Tabela de Plantas (Instância individual de cada planta)
CREATE TABLE plantas (
    id SERIAL PRIMARY KEY,
    id_especie INT NOT NULL REFERENCES especies(id),
    id_canteiro INT REFERENCES canteiros(id),
    codigo_rastreio VARCHAR(20) UNIQUE,
    data_plantio DATE,
    data_germinacao DATE,
    altura_atual DECIMAL(5,2),
    diametro_caule DECIMAL(5,2),
    coordenada_x DECIMAL(10,2), -- coordenada X no viveiro
    coordenada_y DECIMAL(10,2), -- coordenada Y no viveiro
    status VARCHAR(20) CHECK (status IN ('SEMENTE', 'MUDA', 'JOVEM', 'ADULTA', 'VENDIDA', 'MORTA')),
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preco_venda DECIMAL(10,2),
    custo_atual DECIMAL(10,2) DEFAULT 0.00
);

-- Tabela de Tipos de Atividades
CREATE TABLE tipos_atividades (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao TEXT,
    gera_custo BOOLEAN DEFAULT FALSE
);

-- Inserção de tipos de atividades padrão
INSERT INTO tipos_atividades (nome, descricao, gera_custo) VALUES
('PLANTIO', 'Plantio de sementes ou mudas', TRUE),
('REGA', 'Rega das plantas', TRUE),
('FERTILIZACAO', 'Aplicação de fertilizantes', TRUE),
('PODA', 'Poda de galhos ou folhas', TRUE),
('TRANSPLANTE', 'Mudança de uma planta para outro local', TRUE),
('MEDICACAO', 'Aplicação de medicamentos', TRUE),
('INSPECAO', 'Inspeção de saúde da planta', FALSE),
('VENDA', 'Venda da planta', FALSE);

-- Tabela de Tipos de Pragas
CREATE TABLE tipos_pragas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    descricao TEXT,
    metodo_identificacao TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Métodos de Combate a Pragas
CREATE TABLE metodos_combate (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    produto VARCHAR(100),
    dosagem VARCHAR(50),
    metodo_aplicacao TEXT,
    tempo_carencia INT, -- em dias
    eficacia VARCHAR(20),
    custo_unitario DECIMAL(10,2),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Pragas por Planta
CREATE TABLE pragas_plantas (
    id SERIAL PRIMARY KEY,
    id_planta INT NOT NULL REFERENCES plantas(id),
    id_tipo_praga INT NOT NULL REFERENCES tipos_pragas(id),
    data_identificacao DATE NOT NULL,
    nivel_infestacao VARCHAR(20) CHECK (nivel_infestacao IN ('BAIXO', 'MEDIO', 'ALTO', 'CRITICO')),
    observacoes TEXT,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Combates Realizados
CREATE TABLE combates_realizados (
    id SERIAL PRIMARY KEY,
    id_praga_planta INT NOT NULL REFERENCES pragas_plantas(id),
    id_metodo_combate INT NOT NULL REFERENCES metodos_combate(id),
    id_funcionario INT NOT NULL REFERENCES funcionarios(id),
    data_aplicacao TIMESTAMP NOT NULL,
    quantidade_aplicada DECIMAL(10,2),
    custo_total DECIMAL(10,2),
    eficacia_observada VARCHAR(20),
    observacoes TEXT,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Registro de Atividades
CREATE TABLE atividades (
    id SERIAL PRIMARY KEY,
    id_tipo_atividade INT NOT NULL REFERENCES tipos_atividades(id),
    id_planta INT NOT NULL REFERENCES plantas(id),
    id_funcionario INT NOT NULL REFERENCES funcionarios(id),
    data_atividade TIMESTAMP NOT NULL,
    descricao TEXT,
    custo_atividade DECIMAL(10,2) DEFAULT 0.00,
    observacoes TEXT,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Insumos
CREATE TABLE insumos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descricao TEXT,
    unidade_medida VARCHAR(20),
    quantidade_estoque DECIMAL(10,2),
    preco_unitario DECIMAL(10,2),
    data_ultima_compra DATE,
    fornecedor VARCHAR(100),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Uso de Insumos em Atividades
CREATE TABLE insumos_atividades (
    id SERIAL PRIMARY KEY,
    id_atividade INT NOT NULL REFERENCES atividades(id),
    id_insumo INT NOT NULL REFERENCES insumos(id),
    quantidade_usada DECIMAL(10,2) NOT NULL,
    custo_total DECIMAL(10,2),
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Vendas
CREATE TABLE vendas (
    id SERIAL PRIMARY KEY,
    id_comprador INT NOT NULL REFERENCES compradores(id),
    id_funcionario INT NOT NULL REFERENCES funcionarios(id),
    data_venda TIMESTAMP NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    forma_pagamento VARCHAR(20),
    status VARCHAR(20) CHECK (status IN ('PENDENTE', 'PAGO', 'CANCELADO')),
    observacoes TEXT,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Itens da Venda
CREATE TABLE itens_venda (
    id SERIAL PRIMARY KEY,
    id_venda INT NOT NULL REFERENCES vendas(id),
    id_planta INT NOT NULL REFERENCES plantas(id),
    quantidade INT NOT NULL,
    valor_unitario DECIMAL(10,2) NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    desconto DECIMAL(10,2) DEFAULT 0.00,
    data_entrega DATE,
    status_entrega VARCHAR(20) DEFAULT 'PENDENTE',
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Função para atualizar o custo atual da planta
CREATE OR REPLACE FUNCTION atualizar_custo_planta()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE plantas 
    SET custo_atual = custo_atual + NEW.custo_atividade
    WHERE id = NEW.id_planta;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar o custo da planta após nova atividade
CREATE TRIGGER trigger_atualizar_custo_planta
AFTER INSERT ON atividades
FOR EACH ROW
WHEN (NEW.custo_atividade > 0)
EXECUTE FUNCTION atualizar_custo_planta();

-- Função para atualizar o status da planta quando vendida
CREATE OR REPLACE FUNCTION atualizar_status_planta_vendida()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE plantas 
    SET status = 'VENDIDA'
    WHERE id = NEW.id_planta;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar o status da planta após venda
CREATE TRIGGER trigger_atualizar_status_planta_vendida
AFTER INSERT ON itens_venda
FOR EACH ROW
EXECUTE FUNCTION atualizar_status_planta_vendida();

-- Índices para melhorar a performance
CREATE INDEX idx_plantas_especie ON plantas(id_especie);
CREATE INDEX idx_plantas_canteiro ON plantas(id_canteiro);
CREATE INDEX idx_plantas_status ON plantas(status);
CREATE INDEX idx_atividades_planta ON atividades(id_planta);
CREATE INDEX idx_atividades_tipo ON atividades(id_tipo_atividade);
CREATE INDEX idx_atividades_funcionario ON atividades(id_funcionario);
CREATE INDEX idx_vendas_comprador ON vendas(id_comprador);
CREATE INDEX idx_itens_venda_planta ON itens_venda(id_planta);
CREATE INDEX idx_pragas_plantas_planta ON pragas_plantas(id_planta);

-- View para relatório de custos por planta
CREATE VIEW vw_custos_por_planta AS
SELECT 
    p.id AS id_planta,
    p.codigo_rastreio,
    e.nome_cientifico,
    e.nome_popular,
    p.data_plantio,
    p.status,
    p.custo_atual,
    p.preco_venda,
    (p.preco_venda - p.custo_atual) AS lucro_estimado,
    COUNT(a.id) AS qtd_atividades
FROM plantas p
JOIN especies e ON p.id_especie = e.id
LEFT JOIN atividades a ON p.id = a.id_planta
GROUP BY p.id, e.nome_cientifico, e.nome_popular;

-- View para relatório de produtividade por funcionário
CREATE VIEW vw_produtividade_funcionario AS
SELECT 
    f.id AS id_funcionario,
    f.nome,
    COUNT(a.id) AS total_atividades,
    SUM(a.custo_atividade) AS custo_total_atividades,
    COUNT(DISTINCT a.id_planta) AS total_plantas_tratadas
FROM funcionarios f
LEFT JOIN atividades a ON f.id = a.id_funcionario
WHERE f.ativo = TRUE
GROUP BY f.id, f.nome;

-- View para relatório de ocupação de canteiros
CREATE VIEW vw_ocupacao_canteiros AS
SELECT 
    c.id AS id_canteiro,
    c.nome,
    c.area_total,
    COUNT(p.id) AS total_plantas,
    COUNT(p.id) FILTER (WHERE p.status = 'SEMENTE') AS total_sementes,
    COUNT(p.id) FILTER (WHERE p.status = 'MUDA') AS total_mudas,
    COUNT(p.id) FILTER (WHERE p.status = 'JOVEM') AS total_jovens,
    COUNT(p.id) FILTER (WHERE p.status = 'ADULTA') AS total_adultas
FROM canteiros c
LEFT JOIN plantas p ON c.id = p.id_canteiro AND p.status NOT IN ('VENDIDA', 'MORTA')
GROUP BY c.id, c.nome, c.area_total;
