/** Metadados de cadastro de insumos — alinhado ao CMV (premissasUi + unidades_insumo). */

export const TIPOS_INSUMO = [
  {
    value: 'Substrato',
    label: 'Substrato',
    unidadeDefault: 'kg',
    unidades: [
      { value: 'kg', label: 'Quilo (kg)' },
      { value: 'm³', label: 'Metro cúbico (m³)' },
      { value: 'L', label: 'Litro (L)' },
    ],
    dicaUnidade:
      'Apenas use Litro (L) se medir estoque em volume.',
    dicaEntrada: 'Ex.: 500 kg por R$ 600 na NF → preço médio R$ 1,20/kg.',
  },
  {
    value: 'Hidrogel',
    label: 'Hidrogel',
    unidadeDefault: 'g',
    unidades: [
      { value: 'g', label: 'Grama (g)' },
      { value: 'kg', label: 'Quilo (kg)' },
    ],
    dicaUnidade: 'Cadastre em gramas ou quilos — não use volume.',
    dicaEntrada: 'Valor total da NF obrigatório na primeira entrada.',
  },
  {
    value: 'Fertilizante',
    label: 'Fertilizante',
    unidadeDefault: 'kg',
    unidades: [
      { value: 'kg', label: 'Quilo (kg)' },
      { value: 'L', label: 'Litro (L)' },
      { value: 'g', label: 'Grama (g)' },
    ],
    dicaUnidade: 'Use a mesma unidade da embalagem comprada.',
    dicaEntrada: 'Saídas manuais ou via atividades de campo.',
  },
  {
    value: 'Embalagem',
    label: 'Embalagem',
    unidadeDefault: 'un',
    unidades: [
      { value: 'un', label: 'Unidade (tubete, saquinho…)' },
      { value: 'cx', label: 'Caixa' },
      { value: 'pct', label: 'Pacote' },
    ],
    dicaUnidade: 'Tubetes, saquinhos, bandejas — conte em unidades.',
    dicaEntrada: 'Registre quantidade e valor da compra.',
  },
  {
    value: 'Defensivo',
    label: 'Defensivo',
    unidadeDefault: 'L',
    unidades: [
      { value: 'L', label: 'Litro (L)' },
      { value: 'ml', label: 'Mililitro (ml)' },
      { value: 'kg', label: 'Quilo (kg)' },
    ],
    dicaUnidade: 'Conforme rótulo do produto.',
    dicaEntrada: 'Saídas manuais conforme aplicação.',
  },
  {
    value: 'Outro',
    label: 'Outro',
    unidadeDefault: 'un',
    unidades: [
      { value: 'un', label: 'Unidade' },
      { value: 'kg', label: 'Quilo (kg)' },
      { value: 'L', label: 'Litro (L)' },
      { value: 'g', label: 'Grama (g)' },
    ],
    dicaUnidade: 'Escolha a unidade de controle do estoque.',
    dicaEntrada: 'Valor da NF na primeira entrada.',
  },
]

export function metaTipoInsumo(tipo) {
  return TIPOS_INSUMO.find((t) => t.value === tipo) || TIPOS_INSUMO[TIPOS_INSUMO.length - 1]
}

export function unidadeDefaultTipo(tipo) {
  return metaTipoInsumo(tipo).unidadeDefault
}

export const MOTIVOS_SAIDA = [
  { value: 'uso_sementeira', label: 'Uso na sementeira (manual)' },
  { value: 'transferencia_canteiro', label: 'Transferência para canteiro (automático no sistema)' },
  { value: 'aplicacao_campo', label: 'Aplicação no viveiro' },
  { value: 'perda', label: 'Perda / descarte' },
  { value: 'ajuste', label: 'Ajuste de inventário' },
  { value: 'outro', label: 'Outro' },
]

export function previewPrecoUnitario(quantidade, valorTotal) {
  const q = Number(quantidade)
  const v = Number(valorTotal)
  if (!q || q <= 0 || !v || v <= 0) return null
  return v / q
}

export function fmtPrecoUnitario(v) {
  if (v == null || !Number.isFinite(v)) return '—'
  return v.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  })
}
