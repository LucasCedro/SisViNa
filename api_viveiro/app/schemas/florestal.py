"""Schemas do módulo florestal."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.constants.florestal_estagios import ESTAGIOS_ATIVOS, ESTAGIOS_FLORESTAL, TIPOS_MOVIMENTACAO


class GenotipoBase(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50)
    nome: Optional[str] = Field(None, max_length=100)
    fornecedor: Optional[str] = Field(None, max_length=100)
    material_genetico: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None


class GenotipoCreate(GenotipoBase):
    pass


class GenotipoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    fornecedor: Optional[str] = Field(None, max_length=100)
    material_genetico: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class GenotipoOut(GenotipoBase):
    id: int
    id_viveiro: int
    ativo: bool
    data_cadastro: Optional[datetime] = None

    class Config:
        orm_mode = True


class LoteProducaoCreate(BaseModel):
    id_genotipo: int
    codigo_lote: str = Field(..., min_length=1, max_length=30)
    data_entrada: date
    quantidade_inicial: int = Field(..., gt=0)
    id_canteiro: Optional[int] = None
    observacoes: Optional[str] = None


class LoteProducaoOut(BaseModel):
    id: int
    id_viveiro: int
    id_genotipo: int
    genotipo_codigo: Optional[str] = None
    genotipo_nome: Optional[str] = None
    codigo_lote: str
    data_entrada: date
    quantidade_inicial: int
    quantidade_atual: int
    estagio: str
    estagio_label: Optional[str] = None
    id_canteiro: Optional[int] = None
    observacoes: Optional[str] = None
    data_registro: Optional[datetime] = None

    class Config:
        orm_mode = True


class LoteTransferenciaRequest(BaseModel):
    estagio_destino: str
    quantidade: int = Field(..., gt=0)
    id_canteiro_destino: Optional[int] = None
    observacoes: Optional[str] = None

    @validator("estagio_destino")
    def validar_estagio(cls, v: str) -> str:
        if v not in ESTAGIOS_FLORESTAL:
            raise ValueError(f"estagio_destino inválido: {v}")
        return v


class LotePerdaRequest(BaseModel):
    quantidade: int = Field(..., gt=0)
    observacoes: Optional[str] = None


class MovimentacaoLoteOut(BaseModel):
    id: int
    id_lote_producao: int
    tipo: str
    quantidade: int
    estagio_origem: Optional[str] = None
    estagio_destino: Optional[str] = None
    id_canteiro_origem: Optional[int] = None
    id_canteiro_destino: Optional[int] = None
    observacoes: Optional[str] = None
    data_movimento: Optional[datetime] = None

    class Config:
        orm_mode = True


class FlorestalResumoOut(BaseModel):
    genotipos_ativos: int
    lotes_ativos: int
    mudas_em_producao: int
    mudas_expedicao: int
    estagios: List[str]
