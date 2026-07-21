/** Layout e textos das premissas para o gerente. */

export const CHAVE_RECIPIENTE = 'recipiente_semeadura'

export const RECIPIENTES_SEMEADURA = {
  tubete: {
    label: 'Tubete',
    singular: 'tubete',
    plural: 'tubetes',
    artigo: 'o',
  },
  saquinho: {
    label: 'Saquinho',
    singular: 'saquinho',
    plural: 'saquinhos',
    artigo: 'o',
  },
}

export function normalizarRecipiente(valor) {
  return valor === 'saquinho' ? 'saquinho' : 'tubete'
}

export function rotuloRecipiente(valor, forma = 'singular') {
  const r = RECIPIENTES_SEMEADURA[normalizarRecipiente(valor)]
  return r[forma] || r.singular
}

export function recipienteDaLista(lista) {
  const p = (lista || []).find((x) => x.chave === CHAVE_RECIPIENTE)
  return normalizarRecipiente(p?.unidade)
}

export const CHAVE_SUBSTRATO = 'substrato_tubete'
export const CHAVE_HIDROGEL = 'hidrogel_tubete'

/** Metadados de dosagem de substrato — peso (kg no estoque) ou volume (L no estoque). */
export function metaSubstrato(recipiente, unidadeInsumo = 'kg') {
  const rec = normalizarRecipiente(recipiente)
  const recLabel = rec === 'saquinho' ? 'saquinho' : 'tubete'
  const un = normUnidadeInsumo(unidadeInsumo)
  const porPeso = un === 'kg' || un === 'g'

  if (porPeso) {
    return {
      modo: 'peso',
      suffix: `gramas / ${recLabel}`,
      labelQtd: `Substrato por ${recLabel}`,
      dicaQtd:
        'Peso em gramas — estimativa prática (pese 3–5 recipientes cheios e use a média). ' +
        'Sem densidade nem conversão: o estoque fica em kg e a premissa em gramas.',
      unidadePremissa: 'g/recipiente',
      exemploCalculo: rec === 'saquinho' ? '250 g' : '30 g',
    }
  }

  if (rec === 'saquinho') {
    return {
      modo: 'volume',
      suffix: 'litros / saquinho',
      labelQtd: 'Volume de substrato por saquinho',
      dicaQtd: 'Só se o substrato no estoque estiver em litros (L). Capacidade nominal do saquinho cheio.',
      unidadePremissa: 'L/saquinho',
      exemploCalculo: '0,30 L',
    }
  }
  return {
    modo: 'volume',
    suffix: 'ml / tubete',
    labelQtd: 'Volume de substrato por tubete',
    dicaQtd: 'Só se o substrato no estoque estiver em litros (L). Capacidade nominal do tubete em ml.',
    unidadePremissa: 'ml/tubete',
    exemploCalculo: '50 ml',
  }
}

function normUnidadeInsumo(unidade) {
  const u = (unidade || '').trim().toLowerCase().replace(/\s/g, '')
  const map = {
    litro: 'l',
    litros: 'l',
    lt: 'l',
    mililitro: 'ml',
    mililitros: 'ml',
    'm³': 'm3',
    grama: 'g',
    gramas: 'g',
    quilo: 'kg',
    quilos: 'kg',
    quilograma: 'kg',
    quilogramas: 'kg',
  }
  return map[u] || u
}

function volumeSubstratoLitros(qtd, recipiente) {
  const q = Number(qtd) || 0
  if (q <= 0) return 0
  return normalizarRecipiente(recipiente) === 'saquinho' ? q : q / 1000
}

function consumoSubstratoPreview(qtdPremissa, recipiente, insumo) {
  const q = Number(qtdPremissa) || 0
  if (q <= 0) return null
  const un = normUnidadeInsumo(insumo?.unidade_medida)
  if (un === 'kg' || un === 'g') {
    const kg = q / 1000
    const qtdEstoque = un === 'g' ? q : kg
    return {
      qtdEstoque,
      det: un === 'g' ? `${q} g` : `${q} g (${fmtVol(kg)} kg)`,
    }
  }
  const litros = volumeSubstratoLitros(q, recipiente)
  if (un === 'l') return { qtdEstoque: litros, det: `${fmtVol(litros)} L` }
  if (un === 'ml') return { qtdEstoque: litros * 1000, det: `${Math.round(litros * 1000)} ml` }
  return { erro: `Unidade do estoque (${insumo?.unidade_medida || '?'}) — use kg ou L` }
}

function custoSubstratoPreview(qtdPremissa, recipiente, insumo, pu) {
  if (!pu) return null
  const prev = consumoSubstratoPreview(qtdPremissa, recipiente, insumo)
  if (!prev) return null
  if (prev.erro) return prev
  const total = prev.qtdEstoque * pu
  const un = insumo?.unidade_medida || 'un'
  return { total, det: `${prev.det} × ${fmtPu(pu)}/${un}` }
}

function custoHidrogelPreview(gramas, insumo, pu) {
  const g = Number(gramas) || 0
  if (g <= 0 || !pu) return null
  const un = normUnidadeInsumo(insumo?.unidade_medida)
  if (un === 'g') return { total: g * pu, det: `${g} g × ${fmtPu(pu)}/g` }
  if (un === 'kg') return { total: (g / 1000) * pu, det: `${g} g ÷ 1000 × ${fmtPu(pu)}/kg` }
  return { erro: 'Cadastre o hidrogel em gramas (g) ou quilos (kg) no estoque.' }
}

function insumoSelecionado(ctx, idInsumo) {
  return (ctx?.insumos || []).find((i) => i.id === idInsumo)
}

export const PREMISSA_LAYOUT = {
  CUSTO: [
    {
      id: 'coleta',
      titulo: 'Coleta de sementes',
      descricao:
        'Valor homem-hora usado ao registrar cada coleta. O custo (horas × R$/h) é rateado pelas sementes do lote.',
      chaves: ['coleta_campo'],
    },
    {
      id: 'insumos',
      tituloDinamico: true,
      descricaoDinamica: true,
      configChave: CHAVE_RECIPIENTE,
      chaves: [CHAVE_RECIPIENTE, 'substrato_tubete', 'hidrogel_tubete'],
    },
    {
      id: 'utilidades_prod',
      titulo: 'Água e energia — produção',
      descricao:
        'Informe o valor pago no mês (conta real). O sistema rateia pelas mudas vivas no CMV — sem tarifa por litro nem kWh por muda.',
      chaves: ['agua_muda_dia', 'cif_energia_muda'],
    },
    {
      id: 'pessoal',
      titulo: 'Mão de obra — produção',
      descricao: 'Folha mensal total da equipe de campo — rateada pelas mudas vivas.',
      chaves: ['cif_mo_producao_muda'],
    },
  ],
  DESPESA: [
    {
      id: 'utilidades_adm',
      titulo: 'Água e energia — administração',
      descricao:
        'Valor pago no mês fora da produção. Referência na DRE — não entra no custo unitário da muda.',
      chaves: ['energia_fatura_mes', 'agua_fatura_mes'],
    },
    {
      id: 'outras',
      titulo: 'Folha e comercial',
      descricao:
        'Folha administrativa (valor total mensal) e comissão sobre vendas pagas. Referência na DRE.',
      chaves: ['salarios_admin_mes', 'comissao_vendas_pct'],
    },
  ],
}

export const PREMISSA_UI = {
  coleta_campo: {
    badge: 'CMV',
    campos: [
      {
        key: 'valor',
        label: 'Valor homem-hora',
        suffix: 'R$ / hora',
        dica: 'Salário + encargos ÷ horas úteis, ou diária ÷ horas do dia. Aplicado em cada coleta.',
      },
    ],
    calculo: (p) => {
      const vh = Number(p.valor) || 0
      if (!vh) return 'Informe o valor homem-hora. Na coleta, o usuário informa só as horas.'
      const exHoras = 4
      const exQtd = 500
      const total = exHoras * vh
      return `Ex.: ${exHoras} h × ${fmt(vh)}/h = ${fmt(total)} → ${fmt(total / exQtd)}/semente em ${exQtd} sementes`
    },
  },
  substrato_tubete: {
    badge: 'CMV',
    campos: (ctx) => {
      const ins = insumoSelecionado(ctx, ctx?.premissaLocal?.id_insumo)
      const meta = metaSubstrato(ctx?.recipiente, ins?.unidade_medida || 'kg')
      return [
        {
          key: 'quantidade',
          label: meta.labelQtd,
          suffix: meta.suffix,
          dica: meta.dicaQtd,
        },
        {
          key: 'id_insumo',
          label: 'Qual substrato?',
          type: 'insumo',
          insumoTipos: ['Substrato'],
          insumoUnidadesPreferidas: ['kg', 'quilo', 'quilograma', 'L', 'l'],
          dica:
            'Cadastre em Estoques em kg (saco/compra). Informe gramas por recipiente aqui — ' +
            'na transferência para o canteiro o estoque baixa automaticamente.',
        },
      ]
    },
    calculo: (p, ctx) => {
      const rec = rotuloRecipiente(ctx?.recipiente)
      const ins = { unidade_medida: p.insumo_unidade_medida }
      const meta = metaSubstrato(ctx?.recipiente, p.insumo_unidade_medida || 'kg')
      const q = Number(p.quantidade) || 0
      const pu = Number(p.preco_medio_insumo) || 0
      if (!q) return `Informe a dosagem (ex.: ${meta.exemploCalculo}).`
      if (!p.id_insumo || !pu) return 'Selecione o substrato com entrada no estoque.'
      const prev = custoSubstratoPreview(q, ctx?.recipiente, ins, pu)
      if (!prev) return '—'
      if (prev.erro) return prev.erro
      return `${prev.det} = ${fmt(prev.total)} por ${rec}`
    },
  },
  hidrogel_tubete: {
    badge: 'CMV',
    campos: (ctx) => {
      const rec = rotuloRecipiente(ctx?.recipiente)
      return [
        {
          key: 'quantidade',
          label: `Hidrogel por ${rec}`,
          suffix: 'gramas / recipiente',
          dica: 'Dosagem em gramas conforme o fabricante. Deixe 0 se não utilizar.',
        },
        {
          key: 'id_insumo',
          label: 'Qual hidrogel?',
          type: 'insumo',
          insumoTipos: ['Hidrogel'],
          insumoUnidadesPreferidas: ['g', 'kg'],
          dica: 'Cadastre em Estoques em gramas (g) ou quilos (kg).',
        },
      ]
    },
    calculo: (p, ctx) => {
      const rec = rotuloRecipiente(ctx?.recipiente)
      const q = Number(p.quantidade) || 0
      if (q <= 0) return 'Opcional — deixe 0 se não usar hidrogel.'
      const pu = Number(p.preco_medio_insumo) || 0
      if (!p.id_insumo || !pu) return 'Selecione o hidrogel com entrada no estoque.'
      const prev = custoHidrogelPreview(q, { unidade_medida: p.insumo_unidade_medida }, pu)
      if (!prev) return '—'
      if (prev.erro) return prev.erro
      return `${prev.det} = ${fmt(prev.total)} por ${rec}`
    },
  },
  agua_muda_dia: {
    badge: 'CMV',
    campos: [
      {
        key: 'valor',
        label: 'Conta de água — produção',
        suffix: 'R$ / mês',
        dica: 'Valor pago no mês com água do viveiro (Saneago, poço, caminhão-pipa). Inclui taxa mínima e faixas — use o total da conta, não R$/litro.',
      },
      {
        key: 'quantidade',
        label: 'Referência: irrigação por muda',
        suffix: 'litros / muda / mês',
        dica: 'Opcional — estimativa operacional (ex.: 60 L/muda/mês). Não entra no cálculo do CMV; o custo vem da conta mensal acima.',
      },
    ],
    calculo: (p, ctx) => {
      const mensal = Number(p.valor) || 0
      const mv = ctx?.mudasVivas || 0
      const litrosMes = Number(p.quantidade) || 0
      if (!mensal) return 'Informe quanto pagou de água da produção neste mês (ex.: R$ 1.000).'
      const base = !mv
        ? `${fmt(mensal)}/mês — dividido pelo total de mudas vivas no parque`
        : `${fmt(mensal)}/mês ÷ ${mv} mudas vivas ≈ ${fmt(mensal / mv)}/muda`
      if (litrosMes > 0) {
        return `${base} · ref. ${litrosMes} L/muda/mês`
      }
      return base
    },
  },
  cif_energia_muda: {
    badge: 'CMV',
    campos: [
      {
        key: 'valor',
        label: 'Conta de energia — produção',
        suffix: 'R$ / mês',
        dica: 'Valor pago no mês (bombas, estufas, iluminação do viveiro). Use a fatura real — não informe kWh por muda. Escritório vai na DRE.',
      },
    ],
    calculo: (p, ctx) => {
      const mensal = Number(p.valor) || 0
      const mv = ctx?.mudasVivas || 0
      if (!mensal) return 'Informe o valor da fatura de energia da produção.'
      if (!mv) return `${fmt(mensal)}/mês — dividido pelo total de mudas vivas no parque.`
      const porMuda = mensal / mv
      return `${fmt(mensal)}/mês ÷ ${mv} mudas vivas ≈ ${fmt(porMuda)}/muda`
    },
  },
  cif_mo_producao_muda: {
    badge: 'CMV',
    campos: [
      {
        key: 'valor',
        label: 'Folha mensal — produção',
        suffix: 'R$ / mês',
        dica: 'Total pago no mês com a equipe de campo (salários + encargos). Use o valor real da folha, não salário médio.',
      },
    ],
    calculo: (p, ctx) => {
      const mensal = Number(p.valor) || 0
      const mv = ctx?.mudasVivas || 0
      if (!mensal) return 'Informe o total da folha de produção paga no mês.'
      if (!mv) return `${fmt(mensal)}/mês — dividido pelo total de mudas vivas no parque (todas as espécies).`
      return `${fmt(mensal)}/mês ÷ ${mv} mudas vivas ≈ ${fmt(mensal / mv)}/muda`
    },
  },
  energia_fatura_mes: {
    badge: 'DRE',
    campos: [
      {
        key: 'valor',
        label: 'Conta de energia — administração',
        suffix: 'R$ / mês',
        dica: 'Valor pago no mês — escritório, sala de reuniões, refeitório administrativo.',
      },
    ],
    calculo: (p) => `Referência na DRE: ${fmt(p.valor)}/mês (não entra no custo da muda)`,
  },
  agua_fatura_mes: {
    badge: 'DRE',
    campos: [
      {
        key: 'valor',
        label: 'Conta de água — administração',
        suffix: 'R$ / mês',
        dica: 'Valor pago no mês — consumo fora da produção de mudas (banheiros, escritório).',
      },
    ],
    calculo: (p) => `Referência na DRE: ${fmt(p.valor)}/mês`,
  },
  salarios_admin_mes: {
    badge: 'DRE',
    campos: [
      {
        key: 'valor',
        label: 'Folha administrativa',
        suffix: 'R$ / mês',
        dica: 'Total pago no mês com gestão, financeiro e vendas (fora da produção).',
      },
    ],
    calculo: (p) => `Referência na DRE: ${fmt(p.valor)}/mês`,
  },
  comissao_vendas_pct: {
    badge: 'DRE',
    campos: [
      {
        key: 'valor',
        label: 'Comissão sobre vendas pagas',
        suffix: '%',
        dica: 'Percentual sobre o faturamento do período (vendas PAGO). Deixe 0 se não paga comissão.',
        allowEmpty: true,
      },
    ],
    calculo: (p, ctx) => {
      const pct = numPremissa(p.valor)
      if (pct === 0) return 'Sem comissão (0%) — vendedores sem percentual sobre vendas.'
      const fat = ctx?.faturamento || 0
      return fat
        ? `${pct}% × ${fmt(fat)} ≈ ${fmt(fat * (pct / 100))} no período`
        : `${pct}% sobre a receita do período`
    },
  },
}

function numPremissa(v) {
  if (v === null || v === undefined || v === '') return 0
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

function fmt(v) {
  const n = numPremissa(v)
  if (v !== null && v !== undefined && v !== '' && !Number.isFinite(Number(v))) return '—'
  return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function fmtPu(v) {
  return Number(v).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  })
}

function fmtVol(v) {
  return Number(v).toLocaleString('pt-BR', { maximumFractionDigits: 3 })
}

export function uiPremissa(p, ctx = {}) {
  const base =
    PREMISSA_UI[p.chave] || {
      badge: p.natureza === 'CUSTO' ? 'CMV' : 'DRE',
      campos: [{ key: 'valor', label: 'Valor', suffix: p.unidade || '' }],
      calculo: () => '—',
    }
  const campos = typeof base.campos === 'function' ? base.campos(ctx) : base.campos
  return { ...base, campos }
}

export function tituloSecaoInsumos(recipiente) {
  const rec = rotuloRecipiente(recipiente)
  return `Material por ${rec}`
}

export function descricaoSecaoInsumos(recipiente) {
  const rec = rotuloRecipiente(recipiente)
  return (
    `Substrato: estoque em kg (como você compra), dosagem em gramas por ${rec} — ` +
    `estimativa prática, sem densidade. Baixa automática na transferência para o canteiro. ` +
    `Sementeira: saída manual em Estoques. Hidrogel também em gramas.`
  )
}

export function unidadePremissaSubstrato(recipiente, unidadeInsumo = 'kg') {
  return metaSubstrato(recipiente, unidadeInsumo).unidadePremissa
}

export function secoesPremissas(natureza, lista, recipiente = 'tubete') {
  const layout = PREMISSA_LAYOUT[natureza] || []
  const byChave = Object.fromEntries((lista || []).map((p) => [p.chave, p]))
  return layout
    .map((sec) => {
      const itens = sec.chaves.map((k) => byChave[k]).filter(Boolean)
      const titulo = sec.tituloDinamico ? tituloSecaoInsumos(recipiente) : sec.titulo
      const descricao = sec.descricaoDinamica ? descricaoSecaoInsumos(recipiente) : sec.descricao
      const cards = sec.configChave
        ? itens.filter((p) => p.chave !== sec.configChave)
        : itens
      const config = sec.configChave ? byChave[sec.configChave] : null
      return {
        ...sec,
        titulo,
        descricao,
        itens: cards,
        configPremissa: config,
      }
    })
    .filter((sec) => sec.itens.length > 0 || sec.configPremissa)
}

export function insumosParaCampo(insumos, campo) {
  if (campo.type !== 'insumo') return []
  let lista = insumos || []
  const tipos = campo.insumoTipos
  if (tipos?.length) lista = lista.filter((i) => tipos.includes(i.tipo))
  const pref = campo.insumoUnidadesPreferidas
  if (!pref?.length) return lista
  const prefNorm = new Set(pref.map((u) => normUnidadeInsumo(u)))
  const ok = lista.filter((i) => prefNorm.has(normUnidadeInsumo(i.unidade_medida)))
  return ok.length ? ok : lista
}
