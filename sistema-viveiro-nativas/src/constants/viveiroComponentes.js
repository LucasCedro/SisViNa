/** Tipos de peça LEGO do mapa do viveiro */
export const TIPOS_COMPONENTE = {
  CANTEIRO: 'canteiro',
  SEMENTEIRA: 'sementeira',
  RUSTIFICACAO: 'rustificacao'
}

export const COMPONENTE_CATALOGO = [
  {
    tipo: TIPOS_COMPONENTE.CANTEIRO,
    titulo: 'Canteiro',
    descricao: 'Área com grade de mudas (ex.: 4×4 tubetes)',
    corPadrao: '#6ca234'
  },
  {
    tipo: TIPOS_COMPONENTE.SEMENTEIRA,
    titulo: 'Sementeira',
    descricao: 'Bancada ou mesa para germinação',
    corPadrao: '#ff9600'
  },
  {
    tipo: TIPOS_COMPONENTE.RUSTIFICACAO,
    titulo: 'Área de rustificação',
    descricao: 'Aclimatação antes do campo',
    corPadrao: '#ffe135'
  }
]
