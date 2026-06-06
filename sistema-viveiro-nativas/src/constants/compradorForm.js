/** Estado inicial — campos exigidos para NF-e. */
export function compradorVazio() {
  return {
    tipo: 'PF',
    nome: '',
    cpf_cnpj: '',
    telefone: '',
    email: '',
    endereco: '',
    numero: '',
    bairro: '',
    cidade: '',
    estado: '',
    cep: '',
    codigo_municipio_ibge: '',
    inscricao_estadual: '',
    indicador_ie: '9',
    ativo: true,
  }
}
