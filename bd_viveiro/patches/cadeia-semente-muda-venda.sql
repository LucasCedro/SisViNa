-- View: cadeia completa da semente coletada até a venda da muda
-- Aplicar em bancos que já rodaram 05/06; instalações novas usam coleta-producao-cadeia.sql

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
