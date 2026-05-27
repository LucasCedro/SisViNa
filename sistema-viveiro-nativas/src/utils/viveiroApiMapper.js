const COR_POR_TIPO = {
  canteiro: '#596247',
  sementeira: '#C8A84B',
  'area-trabalho': '#A4B39A',
  armazenamento: '#8E9089',
  armazem: '#8E9089',
}

const DIM = { largura: 200, altura: 120, gap: 24, cols: 4 }

export function tipoElementoFromLocal(tipoLocal) {
  if (tipoLocal === 'sementeira') return 'sementeira'
  if (tipoLocal === 'armazem') return 'armazenamento'
  if (tipoLocal === 'rustificacao') return 'area-trabalho'
  return 'canteiro'
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
      mudas: plantasPorCanteiro.get(c.id) || [],
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
