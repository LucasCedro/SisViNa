/** Tipos de área no mapa do viveiro */
import { corPadraoTipo } from '@/constants/viveiroMapColors'

export const TIPOS_COMPONENTE = {
  CANTEIRO: 'canteiro',
  SEMENTEIRA: 'sementeira',
  RUSTIFICACAO: 'rustificacao',
  SEDE: 'sede',
  LAGO: 'lago',
  GARAGEM: 'garagem',
  AREA_TRABALHO: 'area-trabalho',
}

export const CATALOGO_PRODUTIVO = [
  {
    tipo: TIPOS_COMPONENTE.SEMENTEIRA,
    titulo: 'Sementeira',
    descricao: 'Germinação e bandejas',
    corPadrao: corPadraoTipo('sementeira'),
    grupo: 'produtivo',
  },
  {
    tipo: TIPOS_COMPONENTE.CANTEIRO,
    titulo: 'Canteiro',
    descricao: 'Mudas em tubetes (grade)',
    corPadrao: corPadraoTipo('canteiro'),
    grupo: 'produtivo',
  },
  {
    tipo: TIPOS_COMPONENTE.RUSTIFICACAO,
    titulo: 'Rustificação',
    descricao: 'Aclimatação antes do campo',
    corPadrao: corPadraoTipo('rustificacao'),
    grupo: 'produtivo',
  },
]

export const CATALOGO_VISUAL = [
  {
    tipo: TIPOS_COMPONENTE.SEDE,
    titulo: 'Sede / escritório',
    descricao: 'Apenas no croqui (sem produção)',
    corPadrao: corPadraoTipo('sede'),
    grupo: 'visual',
  },
  {
    tipo: TIPOS_COMPONENTE.LAGO,
    titulo: 'Lago / caixa d\'água',
    descricao: 'Fonte de água',
    corPadrao: corPadraoTipo('lago'),
    grupo: 'visual',
  },
  {
    tipo: TIPOS_COMPONENTE.GARAGEM,
    titulo: 'Garagem / depósito',
    descricao: 'Veículos e materiais',
    corPadrao: corPadraoTipo('garagem'),
    grupo: 'visual',
  },
  {
    tipo: TIPOS_COMPONENTE.AREA_TRABALHO,
    titulo: 'Área de trabalho',
    descricao: 'Preparo de substrato, etc.',
    corPadrao: corPadraoTipo('area-trabalho'),
    grupo: 'visual',
  },
]

/** Catálogo completo do wizard "Adicionar área" */
export const COMPONENTE_CATALOGO = [...CATALOGO_PRODUTIVO, ...CATALOGO_VISUAL]
