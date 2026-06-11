import { capacidadeDoCampo, textoBadgeOcupacao } from '@/utils/viveiroOcupacao'

const COR_POR_TIPO = {
  canteiro: '#596247',
  sementeira: '#C8A84B',
  rustificacao: '#ffe135',
  'area-trabalho': '#A4B39A',
  armazenamento: '#8E9089',
  armazem: '#8E9089',
  sede: '#6b8cae',
  lago: '#4a9fd4',
  garagem: '#8E9089',
}

const DIM = { largura: 200, altura: 120, gap: 24, cols: 4 }

export function tipoElementoFromLocal(tipoLocal) {
  if (tipoLocal === 'sementeira') return 'sementeira'
  if (tipoLocal === 'armazem') return 'armazenamento'
  if (tipoLocal === 'rustificacao') return 'rustificacao'
  return 'canteiro'
}

function tipoFromCampoDesigner(campo) {
  const t = campo.tipo
  if (t === 'sementeira') return 'sementeira'
  if (t === 'rustificacao') return 'rustificacao'
  if (t === 'estoque') return 'armazenamento'
  if (t === 'sede') return 'sede'
  if (t === 'lago') return 'lago'
  if (t === 'garagem') return 'garagem'
  if (t === 'area-trabalho' || t === 'campo') return 'area-trabalho'
  return 'canteiro'
}

function mapCampoDesignerParaElemento(campo, plantasPorCanteiro, ocupacaoPorId = {}) {
  const tipo = tipoFromCampoDesigner(campo)
  const apiId = campo.apiId
  const mudas = apiId ? plantasPorCanteiro.get(apiId) || [] : []
  const ocupacaoApi = apiId ? ocupacaoPorId[apiId] : null
  const capacidade = capacidadeDoCampo(campo)
  return {
    id: apiId ? `canteiro-${apiId}` : `designer-${campo.id}`,
    apiId: apiId || null,
    tipo,
    nome: campo.nome,
    posicao: { x: campo.x ?? 0, y: campo.y ?? 0 },
    dimensoes: { largura: campo.largura ?? 200, altura: campo.altura ?? 120 },
    metros: campo.metros || null,
    cor: campo.cor || corElemento(tipo),
    mudas,
    capacidade,
    badgeOcupacao: textoBadgeOcupacao(campo, ocupacaoApi, mudas.length),
    totalPlantas: ocupacaoApi?.total_plantas ?? mudas.length,
  }
}

/** Layout salvo no designer (API) → elementos da planta baixa na gestão. */
export function buildLayoutFromPlantaSalva(plantaSalva, canteiros, plantas = [], ocupacaoPorId = {}) {
  const campos = plantaSalva?.campos
  if (!Array.isArray(campos) || !campos.length) {
    return buildLayoutFromCanteiros(canteiros, plantas)
  }

  const plantasPorCanteiro = new Map()
  for (const p of plantas) {
    if (!p.id_canteiro) continue
    if (!plantasPorCanteiro.has(p.id_canteiro)) plantasPorCanteiro.set(p.id_canteiro, [])
    plantasPorCanteiro.get(p.id_canteiro).push(p.id)
  }

  if (!Object.keys(ocupacaoPorId).length) {
    for (const c of canteiros) {
      if (c.total_plantas != null) {
        ocupacaoPorId[c.id] = { total_plantas: c.total_plantas }
      }
    }
  }

  const elementos = campos.map((c) =>
    mapCampoDesignerParaElemento(c, plantasPorCanteiro, ocupacaoPorId)
  )

  const vb = plantaSalva.viewBox
  let maxX = vb?.width || 1000
  let maxY = vb?.height || 400
  for (const el of elementos) {
    maxX = Math.max(maxX, el.posicao.x + el.dimensoes.largura + 50)
    maxY = Math.max(maxY, el.posicao.y + el.dimensoes.altura + 50)
  }

  return {
    id: 1,
    nome: plantaSalva.nome || 'Viveiro',
    dimensoes: { largura: maxX, altura: maxY },
    elementos,
  }
}

export function corElemento(tipo) {
  return COR_POR_TIPO[tipo] || COR_POR_TIPO.canteiro
}

export function mapPlantaApi(p) {
  const dias =
    p.data_plantio && !Number.isNaN(Date.parse(p.data_plantio))
      ? Math.max(
          0,
          Math.floor((Date.now() - new Date(p.data_plantio).getTime()) / 86400000)
        )
      : null

  return {
    id: p.id,
    idCanteiro: p.id_canteiro,
    especie: p.especie_nome || '—',
    nomePopular: p.especie_nome || '—',
    dataSemeadura: p.data_plantio || p.data_germinacao || '',
    teorUmidade: null,
    tempoPermanencia: dias,
    tipoSubstrato: '—',
    temperaturaAr: null,
    temperaturaSolo: null,
    status: mapStatusUi(p.status),
    codigoRastreio: p.codigo_rastreio,
    statusApi: p.status,
  }
}

function mapStatusUi(status) {
  const s = String(status || '').toUpperCase()
  if (s === 'MORTA') return 'em-tratamento'
  if (s === 'VENDIDA') return 'em-tratamento'
  return 'saudável'
}

/** Posiciona canteiros em grade simples quando não há layout SVG salvo. */
export function buildLayoutFromCanteiros(canteiros, plantas = []) {
  const plantasPorCanteiro = new Map()
  for (const p of plantas) {
    if (!p.id_canteiro) continue
    if (!plantasPorCanteiro.has(p.id_canteiro)) plantasPorCanteiro.set(p.id_canteiro, [])
    plantasPorCanteiro.get(p.id_canteiro).push(p.id)
  }

  const elementos = canteiros.map((c, index) => {
    const col = index % DIM.cols
    const row = Math.floor(index / DIM.cols)
    const tipo = tipoElementoFromLocal(c.tipo_local)
    const mudas = plantasPorCanteiro.get(c.id) || []
    const ocupacao = { total_plantas: c.total_plantas }
    const campoFake = { tipo, config: {} }
    const capMatch = String(c.descricao || '').match(/Capacidade:\s*(\d+)/)
    if (capMatch) campoFake.config.capacidade = Number(capMatch[1])
    return {
      id: `canteiro-${c.id}`,
      apiId: c.id,
      tipo,
      nome: c.nome,
      posicao: {
        x: 50 + col * (DIM.largura + DIM.gap),
        y: 50 + row * (DIM.altura + DIM.gap),
      },
      dimensoes: { largura: DIM.largura, altura: DIM.altura },
      cor: corElemento(tipo),
      mudas,
      capacidade: capacidadeDoCampo(campoFake),
      badgeOcupacao: textoBadgeOcupacao(campoFake, ocupacao, mudas.length),
      totalPlantas: c.total_plantas ?? mudas.length,
    }
  })

  const rows = Math.max(1, Math.ceil(canteiros.length / DIM.cols))
  const altura = 50 + rows * (DIM.altura + DIM.gap) + 50
  const largura = 50 + DIM.cols * (DIM.largura + DIM.gap)

  return {
    id: 1,
    nome: 'Viveiro',
    dimensoes: { largura: Math.max(1000, largura), altura: Math.max(400, altura) },
    elementos,
  }
}
