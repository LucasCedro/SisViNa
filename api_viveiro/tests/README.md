# Testes Automatizados - Viveiro API

Este diretório contém os testes automatizados para a API do sistema de gestão de viveiro.

## Estrutura de Testes

- `conftest.py`: Contém fixtures comuns usadas em múltiplos testes
- `test_auth.py`: Testes para autenticação e login
- `test_especies.py`: Testes para o módulo de espécies

## Executando os Testes

Para executar todos os testes:

```bash
pytest
```

Para executar testes específicos:

```bash
pytest tests/test_auth.py
pytest tests/test_especies.py
```

Para executar com detalhes:

```bash
pytest -v
```

Para gerar um relatório de cobertura:

```bash
pytest --cov=app
```

## Criando Novos Testes

Para criar testes para um novo módulo, siga o padrão:

1. Crie um arquivo `test_nome_do_modulo.py`
2. Use as fixtures existentes (`db`, `client`, `auth_headers`)
3. Organize os testes por funcionalidade
4. Marque os testes assíncronos com `@pytest.mark.asyncio`

## Banco de Dados de Teste

Os testes usam um banco de dados PostgreSQL separado chamado `viveiro_test_db`. Este banco é recriado para cada execução de teste para garantir o isolamento. Certifique-se de que este banco existe na sua instalação PostgreSQL.

## Autenticação nos Testes

A fixture `auth_headers` fornece um cabeçalho de autenticação válido para testes que exigem um usuário logado. Use-a como:

```python
async def test_protected_endpoint(client, auth_headers):
    response = await client.get(
        "/api/v1/endpoint-protegido/", 
        headers=auth_headers
    )
    assert response.status_code == 200
```

## Dicas para Testes Eficientes

1. Teste os casos de sucesso e falha
2. Verifique códigos de status e estrutura de resposta
3. Isole os testes para que não dependam do estado de outros testes
4. Use dados de teste variados para cobrir diferentes cenários
5. Teste os limites e casos extremos