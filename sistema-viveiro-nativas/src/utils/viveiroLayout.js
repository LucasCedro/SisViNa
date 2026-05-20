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

export function criarComponenteNoMapa(payload, index = 0) {
  const id = Date.now() + index
  const offset = 30 + (plantaOffset(index) % 5) * 40

  if (payload.tipo === TIPOS_COMPONENTE.CANTEIRO) {
    const linhas = payload.linhas || 4
    const colunas = payload.colunas || 4
    const largura = payload.largura || 180
    const altura = payload.altura || 130
    return {
      id,
      tipo: 'canteiro',
      nome: payload.nome,
      x: 20 + offset,
      y: 20 + offset,
      largura,
      altura,
      cor: '#6ca234',
      config: {
        linhas,
        colunas,
        capacidade: linhas * colunas,
        especieId: payload.especieId,
        especieNome: payload.especieNome
      },
      espacos: gerarEspacosGrade({
        linhas,
        colunas,
        largura,
        altura,
        especieId: payload.especieId,
        especieNome: payload.especieNome
      })
    }
  }

  if (payload.tipo === TIPOS_COMPONENTE.SEMENTEIRA) {
    return {
      id,
      tipo: 'sementeira',
      nome: payload.nome,
      x: 220 + offset,
      y: 20 + offset,
      largura: payload.largura || 130,
      altura: payload.altura || 70,
      cor: '#ff9600',
      config: { capacidade: payload.capacidade || 20 }
    }
  }

  if (payload.tipo === TIPOS_COMPONENTE.RUSTIFICACAO) {
    return {
      id,
      tipo: 'rustificacao',
      nome: payload.nome,
      x: 20 + offset,
      y: 160 + offset,
      largura: payload.largura || 130,
      altura: payload.altura || 70,
      cor: '#ffe135',
      config: { capacidade: payload.capacidade || 20 }
    }
  }

  return null
}

function plantaOffset(i) {
  return i
}
