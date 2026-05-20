-- Lançamentos financeiros (CAPEX/OPEX) + view de resumo integrado

CREATE TABLE IF NOT EXISTS lancamentos_financeiros (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('CAPEX', 'OPEX')),
    descricao VARCHAR(200) NOT NULL,
    categoria VARCHAR(80) NOT NULL,
    data_lancamento DATE NOT NULL,
    valor NUMERIC(12, 2) NOT NULL CHECK (valor >= 0),
    forma_pagamento VARCHAR(40),
    observacoes TEXT,
    id_funcionario INTEGER REFERENCES funcionarios(id),
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_lancamentos_tipo ON lancamentos_financeiros(tipo);
CREATE INDEX IF NOT EXISTS ix_lancamentos_data ON lancamentos_financeiros(data_lancamento);

CREATE OR REPLACE VIEW vw_resumo_financeiro AS
SELECT
    (SELECT COALESCE(SUM(valor), 0) FROM lancamentos_financeiros WHERE tipo = 'CAPEX') AS total_capex,
    (SELECT COALESCE(SUM(valor), 0) FROM lancamentos_financeiros WHERE tipo = 'OPEX') AS total_opex,
    (SELECT COALESCE(SUM(valor_total), 0) FROM vendas WHERE status = 'PAGO') AS receita_vendas_paga,
    (SELECT COALESCE(SUM(valor_total), 0) FROM vendas WHERE status = 'PAGO'
        AND date_trunc('month', data_venda) = date_trunc('month', CURRENT_TIMESTAMP)) AS receita_mes_atual,
    (SELECT COALESCE(SUM(custo_atividade), 0) FROM atividades) AS custo_atividades,
    (SELECT COALESCE(SUM(custo_total), 0) FROM combates_realizados) AS custo_fitossanidade,
    (SELECT COALESCE(SUM(custo_atual), 0) FROM plantas WHERE status NOT IN ('VENDIDA', 'MORTA')) AS custo_estoque_mudas,
    (SELECT COUNT(*) FROM plantas WHERE status NOT IN ('VENDIDA', 'MORTA')) AS mudas_ativas;
