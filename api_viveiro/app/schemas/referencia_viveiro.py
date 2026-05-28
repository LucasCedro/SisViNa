from typing import List, Optional

from pydantic import BaseModel


class RegraGlobalOut(BaseModel):
    chave: str
    valor_numerico: Optional[float] = None
    valor_texto: Optional[str] = None
    descricao: Optional[str] = None
    fonte: str


class EspecieFichaEmbrapaOut(BaseModel):
    id_especie: int
    nome_cientifico_ref: Optional[str] = None
    fitofisionomia: Optional[str] = None
    mes_coleta_inicio: Optional[int] = None
    mes_coleta_fim: Optional[int] = None
    armazenamento_tipo: Optional[str] = None
    armazenamento_obs: Optional[str] = None
    profundidade_semeadura_cm_min: Optional[float] = None
    profundidade_semeadura_cm_max: Optional[float] = None
    dias_inicio_germinacao: Optional[int] = None
    pct_germinacao_tipico: Optional[float] = None
    substrato_tipo: Optional[int] = None
    conduz_pleno_sol: Optional[bool] = None
    meses_permanencia_viveiro: Optional[int] = None
    meses_permanencia_viveiro_max: Optional[int] = None
    dias_rustificacao_minimo: Optional[int] = None
    altura_campo_cm_min: Optional[float] = None
    altura_campo_cm_max: Optional[float] = None
    adubacao_obs: Optional[str] = None
    observacoes_gerais: Optional[str] = None
    fonte: str

    class Config:
        orm_mode = True


class ReferenciaViveiroResumoOut(BaseModel):
    fonte: str
    regras_globais: List[RegraGlobalOut]
