/** Textos de ajuda — formulário de regras fiscais (Contabilidade). */
export const AJUDA_REGRA_FISCAL = {
  nome: 'Nome interno para identificar a regra na matriz (ex.: "GO interno — muda").',
  ncm: 'NCM do produto (8 dígitos). Mudas nativas costumam usar 06029090 — confirme com o contador.',
  uf_origem: 'UF do emitente (viveiro), normalmente a UF do CNPJ cadastrado.',
  uf_destino: 'UF do comprador. Atalhos: * (qualquer), INTERNA (mesmo estado), INTERESTADUAL (outro estado — ex. GO→SP/MG/ES com uma regra), ou lista SP,MG,ES quando precisar agrupar.',
  tipo_cliente: 'Restringe a regra a pessoa física (PF), jurídica (PJ) ou qualquer (ANY).',
  tipo_operacao:
    'Doméstica = mudas nacionais (ICMS via CSOSN/DAS). Importação = origem estrangeira no SN — ICMS de importação é exceção ao DAS. Exterior = exportação (CFOP 7xxx).',
  icms_origem:
    'Código origem da mercadoria na NF-e (tag orig). 0=nacional; 1=importação direta; 2=adquirida no mercado interno. Obrigatório >= 1 em regras de importação.',
  aliquota_icms_importacao:
    'Alíquota de referência para ICMS de importação no Simples Nacional (exceção à arrecadação unificada). O recolhimento efetivo é orientado pelo contador (guia/DAS).',
  cfop_base:
    'CFOP definido pelo contador (4 dígitos). Ex.: 5101 venda interna, 6101 interestadual. Com "Ajustar 5↔6" marcado, o 1º dígito pode ser corrigido automaticamente.',
  ajustar_cfop_por_uf:
    'CFOP usa 5xxx para venda dentro do mesmo estado e 6xxx para venda interestadual. Marcado: o sistema ajusta o 1º dígito conforme UF origem × UF destino. Ex.: cadastrou 5101 e vendeu para outro estado → vira 6101.',
  csosn:
    'CSOSN do Simples Nacional (CRT=1) — 3 dígitos. Nunca use CST. Ex.: 102 tributado, 400 não tributado, 300 imune. O contador define conforme o caso.',
  ordem: 'Prioridade quando mais de uma regra serve. Número menor = maior prioridade.',
  ativo: 'Somente regras ativas entram na emissão da NF-e.',
  isento_icms:
    'Marca operação isenta de ICMS. O CSOSN deve ser coerente (ex.: 400/300). Obrigatório preencher Fundamento legal — o texto vai para as informações complementares (infCpl) da NF-e.',
  reducao_bc:
    'Percentual de redução da base de cálculo do ICMS (ex.: 60 na Conv. ICMS 100/97 interestadual). Enviado à Focus como icms_percentual_reducao_bc. Recomendado informar o fundamento legal na NF-e.',
  fundamento_legal:
    'Dispositivo legal da isenção, redução ou importação SN. Obrigatório se isento, com redução de BC ou importação. Vai para infCpl da NF-e (campo visível ao fisco e ao comprador).',
  informacoes_complementares:
    'Texto adicional na NF-e (infCpl), além do fundamento legal. Use para observações que o contador quiser destacar.',
  pis: 'Código de situação tributária do PIS no item (Focus). Se vazio, não envia.',
  cofins: 'Código de situação tributária do COFINS no item. Se vazio, não envia.',
  local_destino:
    '1 = operação interna (mesmo estado), 2 = interestadual, 3 = exterior. Automático compara UF emitente × comprador.',
  difal: 'DIFAL (EC 87/2015) em venda interestadual para consumidor final não contribuinte — segunda exceção ao DAS unificado no SN.',
  aliq_inter: 'Alíquota ICMS interestadual (%) usada no cálculo referencial do DIFAL.',
  aliq_intra: 'Alíquota ICMS interna do estado de destino (%) — referência DIFAL.',
  descricao_produto: 'Descrição do item na NF-e (ex.: "Muda de Ipê-amarelo").',
  natureza_operacao: 'Natureza da operação na NF-e (ex.: "Venda de mudas").',
  observacao: 'Nota interna do contador — não vai para a NF-e, só para o cockpit.',
}

export const LABEL_TIPO_OPERACAO = {
  domestica: 'Doméstica',
  importacao: 'Importação SN',
  exterior: 'Exterior',
}

/** Rótulo legível quando a regra não tem nome (seeds antigos). */
export function labelRegraFiscal(r) {
  if (r.nome?.trim()) return r.nome.trim()
  const dest =
    r.uf_destino === '*'
      ? 'interestadual'
      : r.uf_destino === 'INTERESTADUAL'
        ? 'interestadual'
        : r.uf_destino === 'INTERNA'
          ? 'interna'
          : r.uf_destino
  return `${r.uf_origem} → ${dest}`
}

export function resumoTributacaoRegra(r) {
  if (!r) return '—'
  const partes = []
  const top = (r.tipo_operacao || 'domestica').toLowerCase()
  if (top === 'importacao') {
    partes.push(`Origem ${r.icms_origem ?? 1}`)
    if (r.aliquota_icms_importacao) partes.push(`ICMS imp. ${r.aliquota_icms_importacao}%`)
    else partes.push('ICMS imp. SN')
  } else if (r.isento_icms) partes.push('Isento ICMS')
  else if (r.reducao_bc_icms_percent) partes.push(`Red. BC ${r.reducao_bc_icms_percent}%`)
  else if (top !== 'exterior') partes.push('CSOSN/DAS')
  if (r.aplicar_difal) {
    partes.push(`DIFAL ${r.aliquota_icms_inter ?? 12}%/${r.aliquota_icms_intra ?? 18}%`)
  }
  return partes.length ? partes.join(' · ') : 'CSOSN (Simples)'
}
