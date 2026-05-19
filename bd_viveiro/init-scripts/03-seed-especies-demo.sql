INSERT INTO especies (nome_cientifico, nome_popular, familia, descricao, tempo_germinacao, tempo_crescimento)
VALUES
    ('Handroanthus albus', 'Ipê-amarelo', 'Bignoniaceae', 'Árvore nativa ornamental de flores amarelas.', 30, 365),
    ('Hymenaea courbaril', 'Jatobá', 'Fabaceae', 'Árvore de grande porte, frutos comestíveis.', 45, 730),
    ('Araucaria angustifolia', 'Araucária', 'Araucariaceae', 'Conífera nativa, pinhão comestível.', 60, 1095)
ON CONFLICT (nome_cientifico) DO NOTHING;
