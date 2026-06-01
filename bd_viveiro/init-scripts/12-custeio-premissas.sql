-- Premissas + custo lote/semeadura (idempotente)
CREATE TABLE IF NOT EXISTS financeiro_premissas (
    id SERIAL PRIMARY KEY,
    chave VARCHAR(60) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL,
    descricao TEXT,
    natureza VARCHAR(20) NOT NULL DEFAULT 'CUSTO',
    tipo_calculo VARCHAR(30) NOT NULL DEFAULT 'por_muda',
    unidade VARCHAR(40),
    valor NUMERIC(12, 4) NOT NULL DEFAULT 0,
    quantidade NUMERIC(12, 4),
    id_insumo INTEGER REFERENCES insumos(id),
    ordem INTEGER DEFAULT 0,
    ativo BOOLEAN DEFAULT TRUE,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE lotes_sementes ADD COLUMN IF NOT EXISTS valor_total DECIMAL(14,2);
ALTER TABLE lotes_sementes ADD COLUMN IF NOT EXISTS custo_unitario DECIMAL(12,4);

ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_sementes DECIMAL(12,2) DEFAULT 0;
ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_insumos DECIMAL(12,2) DEFAULT 0;
ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_indireto DECIMAL(12,2) DEFAULT 0;
ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_total DECIMAL(12,2) DEFAULT 0;
ALTER TABLE semeaduras ADD COLUMN IF NOT EXISTS custo_unitario_muda DECIMAL(12,2);

ALTER TABLE plantas ADD COLUMN IF NOT EXISTS custo_inicial DECIMAL(10,2);

INSERT INTO financeiro_premissas (chave, nome, descricao, natureza, tipo_calculo, unidade, valor, quantidade, ordem)
VALUES
('substrato_tubete', 'Substrato por tubete', 'Quantidade do insumo por tubete — custo via preço médio do estoque', 'CUSTO', 'insumo_medio', 'un/tubete', 0, 1, 10),
('agua_muda_dia', 'Água por muda/dia', 'Litros por muda/dia × preço médio (insumo água ou valor)', 'CUSTO', 'insumo_medio', 'L/muda/dia', 0, 2, 20),
('cif_energia_muda', 'CIF energia por muda', 'Rateio produtivo — entra no CMV', 'CUSTO', 'por_muda', 'R$/muda', 0, NULL, 30),
('cif_mo_producao_muda', 'MO produtiva por muda', 'Mão de obra produtiva rateada por muda do lote', 'CUSTO', 'por_muda', 'R$/muda', 0, NULL, 40),
('energia_fatura_mes', 'Energia (fatura)', 'Despesa operacional — DRE, não CMV', 'DESPESA', 'mensal', 'R$/mês', 0, NULL, 100),
('agua_fatura_mes', 'Água (fatura)', 'Despesa operacional mensal', 'DESPESA', 'mensal', 'R$/mês', 0, NULL, 110),
('salarios_admin_mes', 'Salários administrativos', 'Despesa — não compõe custo da muda', 'DESPESA', 'mensal', 'R$/mês', 0, NULL, 120),
('comissao_vendas_pct', 'Comissão de vendas', 'Percentual sobre receita — despesa comercial', 'DESPESA', 'percentual_receita', '%', 0, NULL, 130)
ON CONFLICT (chave) DO NOTHING;
