-- Usuário padrão: admin / Admin@123
INSERT INTO funcionarios (nome, cpf, usuario, senha, cargo, email, ativo, perfis)
VALUES (
    'Administrador',
    '000.000.000-00',
    'admin',
    '$2b$12$sIGHhhDU7Cv6KzsYSJcNOuReTYy.wkGsNrnxetlRD7km5GDRc6Kna',
    'Administrador',
    'admin@viveiro.com',
    TRUE,
    '["admin","gestor","campo","financeiro","rh","consulta"]'::json
)
ON CONFLICT (usuario) DO UPDATE SET
    perfis = COALESCE(funcionarios.perfis, EXCLUDED.perfis);
