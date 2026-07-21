import { TIPOS_COMPONENTE } from '@/constants/viveiroComponentes'
import { METROS_PADRAO_PRODUTIVO, PX_POR_METRO, metrosParaPx } from '@/constants/viveiroDimensoes'
import { VIVEIRO_MAP_TIPO, VIVEIRO_PALETTES } from '@/constants/viveiroMapColors'

const CORES_ESPACO = VIVEIRO_PALETTES.espaco

/** Gera círculos (mudas) em grade dentro do retângulo do canteiro */
export function gerarEspacosGrade({ linhas, colunas, largura, altura, especieId = null, especieNome = null }) {
  const padding = 12
  const cols = Math.max(1, colunas)
  const rows = Math.max(1, linhas)
  const cellW = (largura - padding * 2) / cols
  const cellH = (altura - padding * 2) / rows
  const espacos = []
  let n = 0

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      n++
      espacos.push({
        id: Date.now() + n + Math.floor(Math.random() * 1000),
        tipo: 'espaco',
        nome: especieNome ? especieNome.slice(0, 12) : `M${n}`,
        x: padding + col * cellW + cellW / 2,
        y: padding + row * cellH + cellH / 2,
        raio: Math.min(8, Math.min(cellW, cellH) * 0.35),
        cor: CORES_ESPACO[n % CORES_ESPACO.length],
        especieId,
        especieNome,
        slot: n
      })
    }
  }
  return espacos
}

function dimensoesPx(payload, fallbackL, fallbackA) {
  const m = metrosPayload(payload)
  if (m) {
    return {
      largura: metrosParaPx(m.largura),
      altura: metrosParaPx(m.altura),
    }
  }
  return { largura: payload.largura || fallbackL, altura: payload.altura || fallbackA }
}

function metrosPadraoProdutivo(payload) {
  const m = metrosPayload(payload)
  if (m) return m
  return { ...METROS_PADRAO_PRODUTIVO }
}

export function criarComponenteNoMapa(payload, index = 0) {
  const id = Date.now() + index
  const offset = 30 + (plantaOffset(index) % 5) * 40

  if (payload.tipo === TIPOS_COMPONENTE.CANTEIRO) {
    const linhas = payload.linhas || 4
    const colunas = payload.colunas || 4
    const metros = metrosPadraoProdutivo(payload)
    const { largura, altura } = dimensoesPx(
      { ...payload, metrosLargura: metros.largura, metrosAltura: metros.altura },
      metrosParaPx(METROS_PADRAO_PRODUTIVO.largura),
      metrosParaPx(METROS_PADRAO_PRODUTIVO.altura)
    )
    return {
      id,
      tipo: 'canteiro',
      nome: payload.nome,
      x: 20 + offset,
      y: 20 + offset,
      largura,
      altura,
      metros,
      cor: VIVEIRO_MAP_TIPO.canteiro,
      config: {
        linhas,
        colunas,
        capacidade: linhas * colunas,
        especieId: payload.especieId,
        especieNome: payload.especieNome,
      },
    }
  }

  if (payload.tipo === TIPOS_COMPONENTE.SEMENTEIRA) {
    const metros = metrosPadraoProdutivo(payload)
    const { largura, altura } = dimensoesPx(
      { ...payload, metrosLargura: metros.largura, metrosAltura: metros.altura },
      metrosParaPx(6),
      metrosParaPx(24)
    )
    return {
      id,
      tipo: 'sementeira',
      nome: payload.nome,
      x: 220 + offset,
      y: 20 + offset,
      largura,
      altura,
      metros,
      cor: VIVEIRO_MAP_TIPO.sementeira,
      config: { capacidade: payload.capacidade || 20 }
    }
  }

  if (payload.tipo === TIPOS_COMPONENTE.RUSTIFICACAO) {
    const metros = metrosPayload(payload) || { largura: 10, altura: 8 }
    const { largura, altura } = dimensoesPx(
      { ...payload, metrosLargura: metros.largura, metrosAltura: metros.altura },
      metrosParaPx(10),
      metrosParaPx(8)
    )
    return {
      id,
      tipo: 'rustificacao',
      nome: payload.nome,
      x: 20 + offset,
      y: 160 + offset,
      largura,
      altura,
      metros,
      cor: VIVEIRO_MAP_TIPO.rustificacao,
      config: { capacidade: payload.capacidade || 20 }
    }
  }

  const visuais = {
    [TIPOS_COMPONENTE.SEDE]: { cor: VIVEIRO_MAP_TIPO.sede, fallback: [100, 60] },
    [TIPOS_COMPONENTE.LAGO]: { cor: VIVEIRO_MAP_TIPO.lago, fallback: [80, 80] },
    [TIPOS_COMPONENTE.GARAGEM]: { cor: VIVEIRO_MAP_TIPO.garagem, fallback: [90, 50] },
    [TIPOS_COMPONENTE.AREA_TRABALHO]: { cor: VIVEIRO_MAP_TIPO['area-trabalho'], fallback: [110, 70] },
  }
  const visual = visuais[payload.tipo]
  if (visual) {
    const { largura, altura } = dimensoesPx(payload, visual.fallback[0], visual.fallback[1])
    return {
      id,
      tipo: payload.tipo,
      nome: payload.nome,
      x: 120 + offset,
      y: 80 + offset,
      largura,
      altura,
      metros: metrosPayload(payload),
      cor: visual.cor,
      config: {},
    }
  }

  return null
}

function plantaOffset(i) {
  return i
}

function metrosPayload(payload) {
  const largura = Number(payload.metrosLargura)
  const altura = Number(payload.metrosAltura)
  if (largura > 0 && altura > 0) return { largura, altura }
  return null
}

const OFFSET_DUPLICAR = 40
const SUFIXO_COPIA = /(?:\s*\(cópia\)|\s*\(\d+\))$/i

/** Nome único para cópia (respeita maxlength 50 do cadastro). */
export function nomeDuplicado(nomeBase, nomesExistentes = []) {
  const set = new Set(nomesExistentes.map((n) => (n || '').trim().toLowerCase()))
  const raiz = (nomeBase || 'Área').replace(SUFIXO_COPIA, '').trim() || 'Área'
  const tentativas = [`${raiz} (cópia)`]
  for (let i = 2; i <= 99; i++) tentativas.push(`${raiz} (${i})`)
  for (const candidato of tentativas) {
    const nome = candidato.slice(0, 50)
    if (!set.has(nome.toLowerCase())) return nome
  }
  return `${raiz} ${Date.now() % 10000}`.slice(0, 50)
}

/** Clona área do croqui: novo id, sem vínculo API, deslocada no mapa. */
export function duplicarCampoNoMapa(campo) {
  if (!campo) return null
  const copia = JSON.parse(JSON.stringify(campo))
  copia.id = Date.now() + Math.floor(Math.random() * 10000)
  delete copia.apiId
  delete copia.espacos
  delete copia.canteiros
  copia.x = (Number(campo.x) || 0) + OFFSET_DUPLICAR
  copia.y = (Number(campo.y) || 0) + OFFSET_DUPLICAR
  return copia
}
