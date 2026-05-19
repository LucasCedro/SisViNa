#!/bin/bash

# Crie um diretório para o script de inicialização
mkdir -p init-scripts

# Crie o script de inicialização do banco de dados
cat > init-scripts/01-init-schema.sql << 'EOF'
-- Esquema do banco de dados
-- Coloque aqui todo o conteúdo do arquivo postgresql-schema

-- Como o banco de dados já é criado pelo Docker Compose, remova a linha
-- de CREATE DATABASE viveiro_db e a linha \c viveiro_db
EOF

# Torne o script executável
chmod +x init-scripts/01-init-schema.sql

# Crie o arquivo docker-compose.yml
# (O conteúdo deve ser o mesmo do arquivo docker-compose.yml fornecido anteriormente)

echo "Configuração concluída! Execute 'docker-compose up -d' para iniciar o banco de dados."
