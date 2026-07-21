-- Banco isolado para pytest (host ou CI)
SELECT 'CREATE DATABASE viveiro_test_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'viveiro_test_db')\gexec
