import { TIPOS_COMPONENTE } from '@/constants/viveiroComponentes'

const CORES_ESPACO = ['#ffe135', '#ffc42e', '#ffab28', '#ff9321', '#ff7c1c']

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

const PX_POR_METRO = 24

function dimensoesPx(payload, fallbackL, fallbackA) {
  const m = metrosPayload(payload)
  if (m) {
    return {
      largura: Math.round(m.largura * PX_POR_METRO),
      altura: Math.round(m.altura * PX_POR_METRO),
    }
  }
  return { largura: payload.largura || fallbackL, altura: payload.altura || fallbackA }
}

export function criarComponenteNoMapa(payload, index = 0) {
  const id = Date.now() + index
  const offset = 30 + (plantaOffset(index) % 5) * 40

  if (payload.tipo === TIPOS_COMPONENTE.CANTEIRO) {
    const linhas = payload.linhas || 4
    const colunas = payload.colunas || 4
    const { largura, altura } = dimensoesPx(payload, 180, 130)
    return {
      id,
      tipo: 'canteiro',
      nome: payload.nome,
      x: 20 + offset,
      y: 20 + offset,
      largura,
      altura,
      metros: metrosPayload(payload),
      cor: '#6ca234',
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
    const { largura, altura } = dimensoesPx(payload, 130, 70)
    return {
      id,
      tipo: 'sementeira',
      nome: payload.nome,
      x: 220 + offset,
      y: 20 + offset,
      largura,
      altura,
      metros: metrosPayload(payload),
      cor: '#ff9600',
      config: { capacidade: payload.capacidade || 20 }
    }
  }

  if (payload.tipo === TIPOS_COMPONENTE.RUSTIFICACAO) {
    const { largura, altura } = dimensoesPx(payload, 130, 70)
    return {
      id,
      tipo: 'rustificacao',
      nome: payload.nome,
      x: 20 + offset,
      y: 160 + offset,
      largura,
      altura,
      metros: metrosPayload(payload),
      cor: '#ffe135',
      config: { capacidade: payload.capacidade || 20 }
    }
  }

  const visuais = {
    [TIPOS_COMPONENTE.SEDE]: { cor: '#6b8cae', fallback: [100, 60] },
    [TIPOS_COMPONENTE.LAGO]: { cor: '#4a9fd4', fallback: [80, 80] },
    [TIPOS_COMPONENTE.GARAGEM]: { cor: '#8E9089', fallback: [90, 50] },
    [TIPOS_COMPONENTE.AREA_TRABALHO]: { cor: '#A4B39A', fallback: [110, 70] },
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
