import { createCanteiro, updateCanteiro, deleteCanteiro } from '@/services/canteiros'
import { capacidadeDoCampo } from '@/utils/viveiroOcupacao'

export { capacidadeDoCampo }

/** Tipos do designer que viram registro em `canteiros` (usados na produção). */
export const TIPO_LOCAL_POR_COMPONENTE = {
  sementeira: 'sementeira',
  canteiro: 'canteiro',
  rustificacao: 'rustificacao',
  estoque: 'armazem',
}

export function isComponenteProdutivo(tipo) {
  return Boolean(TIPO_LOCAL_POR_COMPONENTE[tipo])
}

function areaMetros(campo) {
  const m = campo.metros
  if (m?.largura > 0 && m?.altura > 0) return Number((m.largura * m.altura).toFixed(2))
  return null
}

function payloadCanteiro(campo) {
  const tipo_local = TIPO_LOCAL_POR_COMPONENTE[campo.tipo]
  const cap = capacidadeDoCampo(campo)
  const area = areaMetros(campo)
  const partes = []
  if (cap != null) partes.push(`Capacidade: ${cap} mudas`)
  if (campo.metros?.largura && campo.metros?.altura) {
    partes.push(`${campo.metros.largura}×${campo.metros.altura} m`)
  }
  return {
    nome: (campo.nome || 'Sem nome').trim().slice(0, 50),
    tipo_local,
    area_total: area,
    descricao: partes.length ? partes.join(' · ') : null,
    ativo: true,
  }
}

/**
 * Cria ou atualiza canteiros a partir dos retângulos do designer.
 * Preenche `apiId` em cada campo produtivo.
 */
export async function sincronizarCamposComCanteiros(campos) {
  const erros = []
  for (const campo of campos) {
    if (!isComponenteProdutivo(campo.tipo)) continue
    try {
      const payload = payloadCanteiro(campo)
      if (campo.apiId) {
        await updateCanteiro(campo.apiId, payload)
      } else {
        const criado = await createCanteiro(payload)
        campo.apiId = criado.id
      }
    } catch (e) {
      const msg = e.response?.data?.detail || e.message || 'Erro ao salvar local'
      erros.push(`${campo.nome}: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`)
    }
  }
  return erros
}

export function plantaParaLayoutPersistido(planta, viewBox) {
  return {
    version: 1,
    nome: planta.nome,
    data: planta.data,
    viewBox: { width: viewBox.width, height: viewBox.height },
    campos: planta.campos,
  }
}

function extrairApiIds(campos = []) {
  return new Set(campos.filter((c) => c.apiId).map((c) => c.apiId))
}

/** Remove do banco locais produtivos que saíram do layout (vazio). */
export async function removerCanteirosAusentesDoLayout(camposAtuais, layoutAnterior) {
  const idsAtuais = extrairApiIds(camposAtuais)
  const orfaos = (layoutAnterior?.campos || []).filter((c) => c.apiId && !idsAtuais.has(c.apiId))
  const erros = []
  for (const campo of orfaos) {
    try {
      await deleteCanteiro(campo.apiId)
    } catch (e) {
      const msg = e.response?.data?.detail || 'não foi possível excluir'
      erros.push(`${campo.nome}: ${msg}`)
    }
  }
  return erros
}

export async function excluirCampoProdutivo(campo) {
  if (!campo?.apiId) return { ok: true }
  await deleteCanteiro(campo.apiId)
  return { ok: true }
}
