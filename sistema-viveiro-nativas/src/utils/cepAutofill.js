/**
 * Preenche campos de endereço a partir do retorno ViaCEP.
 * @param {'comprador'|'emitente'} variant — mapeamento de campos do formulário
 */
export function aplicarEnderecoCep(form, end, variant = 'comprador') {
  if (!form || !end) return
  if (variant === 'emitente') {
    if (end.logradouro) form.logradouro = end.logradouro
    if (end.bairro) form.bairro = end.bairro
    if (end.cidade) form.municipio = end.cidade
    if (end.estado) form.uf = end.estado
    if (end.codigo_municipio_ibge) form.codigo_municipio_ibge = end.codigo_municipio_ibge
    if (end.cep) form.cep = end.cep
    return
  }
  if (end.logradouro) form.endereco = end.logradouro
  if (end.bairro) form.bairro = end.bairro
  if (end.cidade) form.cidade = end.cidade
  if (end.estado) form.estado = end.estado
  if (end.codigo_municipio_ibge) form.codigo_municipio_ibge = end.codigo_municipio_ibge
  if (end.cep) form.cep = end.cep
}
