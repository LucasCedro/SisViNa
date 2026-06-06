/** Consulta CEP — ViaCEP (público, sem token). */

export async function buscarCep(cep) {
  const digits = String(cep || '').replace(/\D/g, '')
  if (digits.length !== 8) {
    throw new Error('CEP deve ter 8 dígitos')
  }

  const res = await fetch(`https://viacep.com.br/ws/${digits}/json/`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) {
    throw new Error('Falha ao consultar CEP')
  }
  const data = await res.json()
  if (data.erro) {
    throw new Error('CEP não encontrado')
  }

  return {
    logradouro: data.logradouro || '',
    bairro: data.bairro || '',
    cidade: data.localidade || '',
    estado: (data.uf || '').toUpperCase(),
    codigo_municipio_ibge: data.ibge || '',
    cep: digits,
  }
}

export function formatarCep(valor) {
  const d = String(valor || '').replace(/\D/g, '').slice(0, 8)
  if (d.length <= 5) return d
  return `${d.slice(0, 5)}-${d.slice(5)}`
}
