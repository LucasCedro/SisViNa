# app/schemas/especies.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class EspecieBase(BaseModel):
    nome_cientifico: str
    nome_popular: Optional[str] = None
    familia: Optional[str] = None
    descricao: Optional[str] = None
    tempo_germinacao: Optional[int] = None
    tempo_crescimento: Optional[int] = None
    altura_maxima: Optional[float] = None

class EspecieCreate(EspecieBase):
    pass

class EspecieUpdate(BaseModel):
    nome_cientifico: Optional[str] = None
    nome_popular: Optional[str] = None
    familia: Optional[str] = None
    descricao: Optional[str] = None
    tempo_germinacao: Optional[int] = None
    tempo_crescimento: Optional[int] = None
    altura_maxima: Optional[float] = None

class EspecieInDBBase(EspecieBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

class Especie(EspecieInDBBase):
    pass

class EspecieWithPlantasCount(EspecieInDBBase):
    total_plantas: int = 0


class FichaTecnicaBibliotecaOut(BaseModel):
    mes_coleta_inicio: Optional[int] = None
    mes_coleta_fim: Optional[int] = None
    armazenamento_tipo: Optional[str] = None
    profundidade_semeadura_cm_min: Optional[float] = None
    profundidade_semeadura_cm_max: Optional[float] = None
    dias_inicio_germinacao: Optional[int] = None
    pct_germinacao_tipico: Optional[float] = None
    substrato_tipo: Optional[int] = None
    conduz_pleno_sol: Optional[bool] = None
    meses_permanencia_viveiro: Optional[int] = None
    meses_permanencia_viveiro_max: Optional[int] = None
    fitofisionomia: Optional[str] = None

    class Config:
        orm_mode = True


class EspecieBibliotecaOut(BaseModel):
    id: int
    nome_cientifico: str
    nome_popular: Optional[str] = None
    familia: Optional[str] = None
    descricao: Optional[str] = None
    tempo_germinacao: Optional[int] = None
    tempo_crescimento: Optional[int] = None
    altura_maxima: Optional[float] = None
    resumo_manejo: Optional[str] = None
    imagem_arvore: Optional[str] = None
    imagem_semente: Optional[str] = None
    imagem_folha: Optional[str] = None
    imagem_capa: Optional[str] = None
    total_fotos: int = 0
    imagens_externas: Optional[List[str]] = None
    ficha_tecnica: Optional[FichaTecnicaBibliotecaOut] = None


class ImagensExternasOut(BaseModel):
    id_especie: int
    nome_cientifico: str
    urls: List[str] = []
    cache_atualizado_em: Optional[datetime] = None


class SincronizarImagensExternasOut(BaseModel):
    processadas: int
    com_imagem: int
    sem_imagem: int
    erros: int
    erro: Optional[str] = None