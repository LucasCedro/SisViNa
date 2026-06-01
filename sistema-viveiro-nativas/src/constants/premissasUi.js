/** Layout e textos das premissas para o gerente. */

export const PREMISSA_LAYOUT = {
  CUSTO: [
    {
      id: 'insumos',
      titulo: 'Material por tubete',
      descricao: 'Escolha o item em Estoques e informe a quantidade usada em cada tubete na semeadura.',
      chaves: ['substrato_tubete', 'hidrogel_tubete'],
    },
    {
      id: 'utilidades_prod',
      titulo: 'Água e energia — produção',
      descricao:
        'Custos das áreas produtivas. A energia é rateada automaticamente pelas mudas vivas; na irrigação você informa volume e tarifa da água.',
      chaves: ['agua_muda_dia', 'cif_energia_muda'],
    },
    {
      id: 'pessoal',
      titulo: 'Mão de obra — produção',
      descricao: 'Equipe de campo rateada pelo total de mudas vivas no viveiro.',
      chaves: ['cif_mo_producao_muda'],
    },
  ],
  DESPESA: [
    {
      id: 'utilidades_adm',
      titulo: 'Água e energia — administração',
      descricao:
        'Escritório, refeitório e áreas comuns. Entram na DRE como referência — não compõem o custo da muda.',
      chaves: ['energia_fatura_mes', 'agua_fatura_mes'],
    },
    {
      id: 'outras',
      titulo: 'Folha e comercial',
      descricao: 'Despesas fixas e comissão sobre vendas pagas no período.',
      chaves: ['salarios_admin_mes', 'comissao_vendas_pct'],
    },
  ],
}

export const PREMISSA_UI = {
  substrato_tubete: {
    badge: 'CMV',
    campos: [
      {
        key: 'quantidade',
        label: 'Substrato por tubete',
        suffix: 'kg, L ou un.',
        dica: 'Média que vai em cada tubete na semeadura.',
      },
      {
        key: 'id_insumo',
        label: 'Qual substrato?',
        type: 'insumo',
        insumoTipos: ['Substrato'],
        dica: 'Cadastre em Estoques → Insumos (tipo Substrato).',
      },
    ],
    calculo: (p) => {
      const q = Number(p.quantidade) || 0
      const pu = Number(p.preco_medio_insumo) || 0
      if (!q || !pu) return 'Informe a quantidade e selecione o substrato com entrada no estoque.'
      return `${q} × ${fmt(pu)} = ${fmt(q * pu)} por tubete`
    },
  },
  hidrogel_tubete: {
    badge: 'CMV',
    campos: [
      {
        key: 'quantidade',
        label: 'Hidrogel por tubete',
        suffix: 'g ou un.',
        dica: 'Dosagem por tubete conforme o fabricante.',
      },
      {
        key: 'id_insumo',
        label: 'Qual hidrogel?',
        type: 'insumo',
        insumoTipos: ['Hidrogel'],
        dica: 'Cadastre em Estoques → Insumos (tipo Hidrogel).',
      },
    ],
    calculo: (p) => {
      const q = Number(p.quantidade) || 0
      const pu = Number(p.preco_medio_insumo) || 0
      if (!q || !pu) return 'Informe a dosagem e selecione o hidrogel com entrada no estoque.'
      return `${q} × ${fmt(pu)} = ${fmt(q * pu)} por tubete`
    },
  },
  agua_muda_dia: {
    badge: 'CMV',
    campos: [
      {
        key: 'quantidade',
        label: 'Água irrigada por muda',
        suffix: 'litros / dia',
        dica: 'Estimativa de água de rede, poço ou reservatório — processo de irrigação, não é insumo de estoque.',
      },
      {
        key: 'valor',
        label: 'Tarifa da água',
        suffix: 'R$ / litro',
        dica: 'Ex.: fatura R$ 800 ÷ 80.000 L consumidos = R$ 0,01/L.',
      },
    ],
    calculo: (p) => {
      const q = Number(p.quantidade) || 0
      const tarifa = Number(p.valor) || 0
      if (!q || !tarifa) return 'Informe litros por muda e a tarifa (R$/litro).'
      return `${q} L × ${fmtTarifa(tarifa)}/L = ${fmt(q * tarifa)} por muda/dia`
    },
  },
  cif_energia_muda: {
    badge: 'CMV',
    campos: [
      {
        key: 'valor',
        label: 'Fatura mensal — áreas produtivas',
        suffix: 'R$ / mês',
        dica: 'Bombas, estufas, iluminação do viveiro. Não inclua escritório (use a despesa de administração).',
      },
    ],
    calculo: (p, ctx) => {
      const mensal = Number(p.valor) || 0
      const mv = ctx?.mudasVivas || 0
      if (!mensal) return 'Informe o valor da fatura de energia da produção.'
      if (!mv) return `${fmt(mensal)}/mês — o rateio por muda aparece quando houver mudas vivas no sistema.`
      const porMuda = mensal / mv
      return `${fmt(mensal)}/mês ÷ ${mv} mudas ≈ ${fmt(porMuda)}/muda (automático na semeadura)`
    },
  },
  cif_mo_producao_muda: {
    badge: 'CMV',
    campos: [
      {
        key: 'quantidade',
        label: 'Pessoas na produção',
        suffix: 'funcionários',
        dica: 'Equipe de semeadura, canteiro e rustificação.',
      },
      {
        key: 'valor',
        label: 'Salário médio',
        suffix: 'R$ / mês',
        dica: 'Média salarial da equipe de campo.',
      },
    ],
    calculo: (p, ctx) => {
      const n = Number(p.quantidade) || 0
      const s = Number(p.valor) || 0
      const mv = ctx?.mudasVivas || 0
      if (!n || !s) return 'Informe quantas pessoas e o salário médio mensal.'
      const mensal = n * s
      const porMuda = mv > 0 ? mensal / mv : 0
      return `Folha ${fmt(mensal)}/mês ÷ ${mv || '?'} mudas ≈ ${mv ? fmt(porMuda) : '—'}/muda`
    },
  },
  energia_fatura_mes: {
    badge: 'DRE',
    campos: [
      {
        key: 'valor',
        label: 'Fatura mensal — administração',
        suffix: 'R$ / mês',
        dica: 'Escritório, sala de reuniões, refeitório administrativo.',
      },
    ],
    calculo: (p) => `Referência na DRE: ${fmt(p.valor)}/mês (não entra no custo da muda)`,
  },
  agua_fatura_mes: {
    badge: 'DRE',
    campos: [
      {
        key: 'valor',
        label: 'Fatura mensal — administração',
        suffix: 'R$ / mês',
        dica: 'Consumo fora das áreas de produção de mudas.',
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
        dica: 'Gestão, financeiro, vendas (fora da produção).',
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
        dica: 'Percentual sobre o faturamento do período (vendas PAGO).',
      },
    ],
    calculo: (p, ctx) => {
      const pct = Number(p.valor) || 0
      const fat = ctx?.faturamento || 0
      return fat
        ? `${pct}% × ${fmt(fat)} ≈ ${fmt(fat * (pct / 100))} no período`
        : `${pct}% sobre a receita do período`
    },
  },
}

function fmt(v) {
  return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function fmtTarifa(v) {
  return Number(v).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  })
}

export function uiPremissa(p) {
  return (
    PREMISSA_UI[p.chave] || {
      badge: p.natureza === 'CUSTO' ? 'CMV' : 'DRE',
      campos: [{ key: 'valor', label: 'Valor', suffix: p.unidade || '' }],
      calculo: () => '—',
    }
  )
}

export function secoesPremissas(natureza, lista) {
  const layout = PREMISSA_LAYOUT[natureza] || []
  const byChave = Object.fromEntries((lista || []).map((p) => [p.chave, p]))
  return layout
    .map((sec) => ({
      ...sec,
      itens: sec.chaves.map((k) => byChave[k]).filter(Boolean),
    }))
    .filter((sec) => sec.itens.length > 0)
}

export function insumosParaCampo(insumos, campo) {
  if (campo.type !== 'insumo') return []
  const tipos = campo.insumoTipos
  if (!tipos?.length) return insumos
  return insumos.filter((i) => tipos.includes(i.tipo))
}
