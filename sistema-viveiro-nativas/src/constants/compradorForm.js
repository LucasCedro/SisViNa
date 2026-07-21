import { onlyDigits, parseInscricaoEstadual, parseUf } from '@/utils/inputMasks'

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

/** Normaliza campos mascarados antes de editar/salvar comprador. */
export function normalizarCompradorCampos(c) {
  const tipo = c?.tipo === 'PJ' ? 'PJ' : 'PF'
  const docMax = tipo === 'PJ' ? 14 : 11
  return {
    ...c,
    cpf_cnpj: onlyDigits(c?.cpf_cnpj).slice(0, docMax),
    telefone: onlyDigits(c?.telefone).slice(0, 11),
    cep: onlyDigits(c?.cep).slice(0, 8),
    codigo_municipio_ibge: onlyDigits(c?.codigo_municipio_ibge).slice(0, 7),
    inscricao_estadual: parseInscricaoEstadual(c?.inscricao_estadual),
    estado: parseUf(c?.estado),
  }
}
