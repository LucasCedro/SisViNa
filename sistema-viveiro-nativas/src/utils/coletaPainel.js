import { labelEstagio, labelMes } from '@/constants/coletaDominio'
import {
  ESTAGIOS_COLETAVEL,
  germinacaoLote,
  lotePrecisaTesteGerminacao,
  LIMIAR_GERM_BAIXA,
  taxaGerminacaoEspecie
} from '@/utils/coletaKpi'
import { nomePopularExibicao } from '@/utils/especiesDisplay'

/** Janela que cruza o ano (ex.: nov–fev). */
export function mesNaJanelaFrutificacao(mesAtual, mesInicio, mesFim) {
  const mes = Number(mesAtual)
  const ini = Number(mesInicio)
  const fim = Number(mesFim)
  if (!ini && !fim) return false
  if (ini && !fim) return mes === ini
  if (!ini && fim) return mes === fim
  if (ini <= fim) return mes >= ini && mes <= fim
  return mes >= ini || mes <= fim
}

export function statusJanelaColeta(matriz, mesAtual = new Date().getMonth() + 1) {
  const ini = matriz?.mes_inicio_frutificacao
  const fim = matriz?.mes_fim_frutificacao
  if (!ini && !fim) return 'sem_fenologia'
  if (!mesNaJanelaFrutificacao(mesAtual, ini, fim)) return 'fora_janela'
  const estagio = matriz?.estagio_frutificacao
  if (!estagio) return 'na_janela_sem_estagio'
  if (ESTAGIOS_COLETAVEL.has(estagio)) return 'pronta'
  return 'na_janela_aguardar'
}

function textoLocalMatriz(matriz) {
  const mun = matriz.municipio || matriz.cidade
  const partes = [matriz.imovel_nome, mun, matriz.estado].filter(Boolean)
  return partes.length ? partes.join(' · ') : '—'
}

function itemMatrizJanela(matriz) {
  return {
    matriz,
    status: statusJanelaColeta(matriz),
    especie: nomePopularExibicao(matriz.especie_nome) || '—',
    local: textoLocalMatriz(matriz),
    estagio: labelEstagio(matriz.estagio_frutificacao),
    janela:
      matriz.mes_inicio_frutificacao || matriz.mes_fim_frutificacao
        ? `${labelMes(matriz.mes_inicio_frutificacao)} – ${labelMes(matriz.mes_fim_frutificacao)}`
        : '—'
  }
}

const ORDEM_STATUS_JANELA = {
  pronta: 0,
  na_janela_aguardar: 1,
  na_janela_sem_estagio: 2,
  fora_janela: 3,
  sem_fenologia: 4
}

export function agruparMatrizesJanelaColeta(matrizes, mesAtual = new Date().getMonth() + 1) {
  const itens = (matrizes || []).map(itemMatrizJanela)
  const naJanela = itens
    .filter((i) => ['pronta', 'na_janela_aguardar', 'na_janela_sem_estagio'].includes(i.status))
    .sort((a, b) => ORDEM_STATUS_JANELA[a.status] - ORDEM_STATUS_JANELA[b.status])
  const foraJanela = itens
    .filter((i) => i.status === 'fora_janela')
    .sort((a, b) => a.matriz.nome.localeCompare(b.matriz.nome))
  const semFenologia = itens
    .filter((i) => i.status === 'sem_fenologia')
    .sort((a, b) => a.matriz.nome.localeCompare(b.matriz.nome))

  return {
    mesAtual,
    naJanela,
    foraJanela,
    semFenologia,
    totalProntas: naJanela.filter((i) => i.status === 'pronta').length
  }
}

export function listarPendenciasColeta({ lotes, testes }) {
  const pendencias = []
  let liberados = 0

  for (const lote of lotes || []) {
    if (!lote || lote.status === 'descartado') continue
    const estoque = Number(lote.quantidade_disponivel) || 0
    const germ = germinacaoLote(lote, testes)

    if (lotePrecisaTesteGerminacao(lote, testes)) {
      pendencias.push({
        id: `teste-${lote.id}`,
        tipo: 'teste_pendente',
        prioridade: 1,
        severidade: 'alerta',
        lote,
        titulo: 'Teste de germinação pendente',
        detalhe: `${lote.codigo_lote} · ${nomePopularExibicao(lote.especie_nome) || lote.matriz_nome || '—'}`,
        meta: estoque > 0 ? `${estoque.toLocaleString('pt-BR')} em estoque` : 'Sem estoque comercial',
        acao: 'teste'
      })
      continue
    }

    if (germ != null && germ < LIMIAR_GERM_BAIXA && estoque > 0) {
      pendencias.push({
        id: `germ-${lote.id}`,
        tipo: 'germ_baixa',
        prioridade: 2,
        severidade: 'critico',
        lote,
        titulo: `Germinação baixa (${germ}%)`,
        detalhe: `${lote.codigo_lote} · ${lote.matriz_nome || '—'}`,
        meta: `${estoque.toLocaleString('pt-BR')} sementes — revisar antes de semear`,
        acao: 'teste'
      })
      continue
    }

    if (germ != null && estoque > 0) {
      liberados += 1
    }
  }

  return {
    itens: pendencias.sort((a, b) => a.prioridade - b.prioridade),
    liberados
  }
}

export function listarRankingGerminacao(matrizes, lotes, testes) {
  const comTaxa = (matrizes || [])
    .map((m) => {
      const taxa =
        m.taxa_germinacao != null && m.taxa_germinacao !== ''
          ? Number(m.taxa_germinacao)
          : null
      if (taxa == null || Number.isNaN(taxa)) return null
      const mediaEspecie = taxaGerminacaoEspecie(lotes, testes, m.id_especie)
      return {
        matriz: m,
        nome: m.nome,
        especie: nomePopularExibicao(m.especie_nome) || '—',
        taxa,
        mediaEspecie
      }
    })
    .filter(Boolean)
    .sort((a, b) => b.taxa - a.taxa)

  return comTaxa
}

export function corGerminacao(taxa) {
  if (taxa >= 70) return 'boa'
  if (taxa >= 50) return 'media'
  return 'baixa'
}
