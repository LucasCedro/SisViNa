/** Validação local de comprador para NF-e (espelha backend — feedback instantâneo no form). */

export function errosCompradorLocal(c) {
  const erros = []
  if (!c) return erros

  const doc = (c.cpf_cnpj || '').replace(/\D/g, '')
  if (c.tipo === 'PF' && doc.length !== 11) erros.push('CPF inválido (11 dígitos)')
  if (c.tipo === 'PJ' && doc.length !== 14) erros.push('CNPJ inválido (14 dígitos)')
  if (!(c.endereco || '').trim()) erros.push('Endereço obrigatório')
  if (!(c.numero || '').trim()) erros.push('Número do endereço obrigatório')
  if (!(c.bairro || '').trim()) erros.push('Bairro obrigatório')
  if (!(c.cidade || '').trim()) erros.push('Município obrigatório')
  if (!(c.estado || '').trim() || (c.estado || '').length !== 2) erros.push('UF obrigatória (2 letras)')
  if ((c.cep || '').replace(/\D/g, '').length !== 8) erros.push('CEP inválido (8 dígitos)')
  if ((c.codigo_municipio_ibge || '').replace(/\D/g, '').length !== 7) {
    erros.push('Código IBGE obrigatório (7 dígitos)')
  }
  return erros
}
