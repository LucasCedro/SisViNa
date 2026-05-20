from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoteSementesBase(BaseModel):
    id_coleta_sementes: Optional[int] = None
    quantidade_inicial: Optional[int] = None
    data_formacao_lote: Optional[date] = None
    beneficiamento: Optional[str] = None
    condicoes_armazenamento: Optional[str] = None
    observacoes: Optional[str] = None
    status: str = "ativo"


class LoteSementesCreate(LoteSementesBase):
    codigo_lote: Optional[str] = None


class LoteSementesUpdate(BaseModel):
    beneficiamento: Optional[str] = None
    condicoes_armazenamento: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None
    quantidade_disponivel: Optional[int] = Field(None, ge=0)


class LoteSementesEntradaArmazem(BaseModel):
    id_especie: int
    quantidade: int
    id_arvore_matriz: Optional[int] = None
    codigo_lote: Optional[str] = None
    origem_lote: str = "armazem"
    beneficiamento: Optional[str] = None
    condicoes_armazenamento: Optional[str] = None
    observacoes: Optional[str] = None


class LoteSementesOut(BaseModel):
    id: int
    codigo_lote: str
    id_coleta_sementes: Optional[int] = None
    id_arvore_matriz: Optional[int] = None
    origem_lote: str = "coleta"
    matriz_nome: Optional[str] = None
    id_especie: int
    especie_nome: Optional[str] = None
    quantidade_inicial: int
    quantidade_disponivel: int
    data_formacao_lote: date
    data_coleta: Optional[date] = None
    beneficiamento: Optional[str] = None
    condicoes_armazenamento: Optional[str] = None
    status: str
    observacoes: Optional[str] = None
    data_registro: datetime
    ultimo_teste_germinacao: Optional[float] = None

    class Config:
        orm_mode = True
