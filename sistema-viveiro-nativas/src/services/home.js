import { getDashboardResumo } from './dashboard'
import { listPendentesTransferencia } from './plantas'
import { listPragasPlantas } from './pragas'
import { listColetasSementes } from './coletasSementes'
import { listLotesSementes } from './lotesSementes'
import { listTestesSementes } from './testesSementes'
import { listAtividades } from './atividades'
import { listVendas } from './vendas'

function parseDate(d) {
  if (!d) return null
  const s = String(d)
  return new Date(s.includes('T') ? s : `${s}T12:00:00`)
}

function diasDesde(d) {
  const dt = parseDate(d)
  if (!dt) return null
  return Math.floor((Date.now() - dt.getTime()) / 86400000)
}

export async function loadHomeData() {
  const [
    resumoRes,
    pendentesRes,
    pragasRes,
    coletasRes,
    lotesRes,
    testesRes,
    atividadesRes,
    vendasRes,
  ] = await Promise.allSettled([
    getDashboardResumo(),
    listPendentesTransferencia({ limit: 50 }),
    listPragasPlantas({ limit: 100 }),
    listColetasSementes({ limit: 15 }),
    listLotesSementes({ limit: 100 }),
    listTestesSementes({ limit: 200 }),
    listAtividades({ limit: 15 }),
    listVendas({ limit: 10 }),
  ])

  const resumo = resumoRes.status === 'fulfilled' ? resumoRes.value : null
  const pendentes = pendentesRes.status === 'fulfilled' ? pendentesRes.value : []
  const pragas = pragasRes.status === 'fulfilled' ? pragasRes.value : []
  const coletas = coletasRes.status === 'fulfilled' ? coletasRes.value : []
  const lotes = lotesRes.status === 'fulfilled' ? lotesRes.value : []
  const testes = testesRes.status === 'fulfilled' ? testesRes.value : []
  const atividades = atividadesRes.status === 'fulfilled' ? atividadesRes.value : []
  const vendas = vendasRes.status === 'fulfilled' ? vendasRes.value : []

  const lotesComTesteGerm = new Set(
    testes.filter((t) => t.tipo_teste === 'germinacao').map((t) => t.id_lote_sementes)
  )
  const lotesSemTeste = lotes.filter(
    (l) => l.status === 'ativo' && !lotesComTesteGerm.has(l.id)
  )

  const pragasAlerta = pragas.filter((p) => {
    const n = String(p.nivel_infestacao || '').toUpperCase()
    return n === 'ALTO' || n === 'CRITICO'
  })

  const pendencias = []

  if (pendentes.length) {
    pendencias.push({
      id: 'transferencia',
      nivel: pendentes.length >= 10 ? 'alto' : 'medio',
      titulo: `${pendentes.length} muda(s) aguardando transferência`,
      descricao: 'Plântulas aptas na sementeira — prontas para ir ao canteiro.',
      rota: '/producao',
      permissao: 'producao.transfer',
    })
  }

  if (pragasAlerta.length) {
    pendencias.push({
      id: 'pragas',
      nivel: 'alto',
      titulo: `${pragasAlerta.length} alerta(s) fitossanitário(s)`,
      descricao: 'Ocorrências com nível alto ou crítico registradas.',
      rota: '/fitossanidade',
      permissao: 'fitossanidade.view',
    })
  }

  if (lotesSemTeste.length) {
    pendencias.push({
      id: 'testes',
      nivel: lotesSemTeste.length >= 5 ? 'medio' : 'baixo',
      titulo: `${lotesSemTeste.length} lote(s) sem teste de germinação`,
      descricao: 'Registre qualidade antes da semeadura.',
      rota: '/coleta?aba=germinacao',
      permissao: 'coleta.view',
    })
  }

  const atividade = buildAtividadeRecente({ coletas, pragas, atividades, vendas, pendentes })

  return {
    resumo,
    pendencias,
    atividade,
    fluxo: buildFluxoCounts(resumo),
    erroApi: !resumo,
  }
}

function buildFluxoCounts(resumo) {
  if (!resumo) {
    return [
      { id: 'matriz', label: 'Matrizes', count: '—', rota: '/coleta', permissao: 'coleta.view' },
      { id: 'coleta', label: 'Coletas', count: '—', rota: '/coleta', permissao: 'coleta.view' },
      { id: 'lote', label: 'Lotes', count: '—', rota: '/coleta?aba=germinacao', permissao: 'coleta.view' },
      { id: 'sementeira', label: 'Sementeira', count: '—', rota: '/producao', permissao: 'producao.view' },
      { id: 'canteiro', label: 'Canteiro', count: '—', rota: '/viveiro', permissao: 'viveiro.view' },
      { id: 'venda', label: 'Vendas (mês)', count: '—', rota: '/vendas', permissao: 'vendas.view' },
    ]
  }
  return [
    { id: 'matriz', label: 'Matrizes', count: resumo.matrizes, rota: '/coleta', permissao: 'coleta.view' },
    { id: 'coleta', label: 'Coletas', count: resumo.coletas, rota: '/coleta', permissao: 'coleta.view' },
    { id: 'lote', label: 'Lotes ativos', count: resumo.lotes_ativos, rota: '/estoques', permissao: 'estoques.view' },
    {
      id: 'canteiro',
      label: 'Mudas ativas',
      count: resumo.mudas_ativas,
      rota: '/viveiro',
      permissao: 'viveiro.view',
    },
    {
      id: 'venda',
      label: 'Vendas (mês)',
      count: fmtMoeda(resumo.vendas_mes),
      rota: '/financeiro',
      permissao: 'financeiro.view',
    },
  ]
}

function buildAtividadeRecente({ coletas, pragas, atividades, vendas }) {
  const eventos = []

  for (const c of coletas) {
    eventos.push({
      tipo: 'coleta',
      data: c.data_coleta || c.data_registro,
      texto: `Coleta registrada — ${c.especie_nome || 'espécie'}`,
      rota: '/coleta',
    })
  }
  for (const p of pragas.slice(0, 8)) {
    eventos.push({
      tipo: 'praga',
      data: p.data_identificacao,
      texto: `Fitossanidade: ${p.tipo_praga_nome || 'ocorrência'} (${p.especie_nome || '—'})`,
      rota: '/fitossanidade',
    })
  }
  for (const a of atividades) {
    eventos.push({
      tipo: 'atividade',
      data: a.data_atividade,
      texto: `${a.tipo_atividade_nome || 'Atividade'} — ${a.especie_nome || ''}`.trim(),
      rota: '/fertilizacao',
    })
  }
  for (const v of vendas) {
    eventos.push({
      tipo: 'venda',
      data: v.data_venda,
      texto: `Venda ${v.status || ''} — R$ ${Number(v.valor_total || 0).toLocaleString('pt-BR')}`,
      rota: '/vendas',
    })
  }

  return eventos
    .filter((e) => parseDate(e.data))
    .sort((a, b) => parseDate(b.data) - parseDate(a.data))
    .slice(0, 12)
    .map((e) => ({
      ...e,
      quando: formatarQuando(e.data),
    }))
}

function formatarQuando(d) {
  const dias = diasDesde(d)
  if (dias === 0) return 'Hoje'
  if (dias === 1) return 'Ontem'
  if (dias != null && dias < 7) return `Há ${dias} dias`
  const dt = parseDate(d)
  return dt ? dt.toLocaleDateString('pt-BR') : '—'
}

function fmtMoeda(v) {
  if (v == null) return '—'
  return `R$ ${Number(v).toLocaleString('pt-BR', { maximumFractionDigits: 0 })}`
}

export { fmtMoeda }
