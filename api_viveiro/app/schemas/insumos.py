# app/schemas/insumos.py
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class InsumoBase(BaseModel):
    nome: str
    tipo: str
    descricao: Optional[str] = None
    unidade_medida: Optional[str] = None
    quantidade_estoque: Optional[float] = 0
    preco_unitario: Optional[float] = 0
    valor_estoque: Optional[float] = 0
    estoque_minimo: Optional[float] = 0
    estoque_maximo: Optional[float] = None
    data_ultima_compra: Optional[date] = None
    fornecedor: Optional[str] = None

class InsumoCreate(InsumoBase):
    pass

class InsumoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    descricao: Optional[str] = None
    unidade_medida: Optional[str] = None
    quantidade_estoque: Optional[float] = None
    preco_unitario: Optional[float] = None
    valor_estoque: Optional[float] = None
    estoque_minimo: Optional[float] = None
    estoque_maximo: Optional[float] = None
    data_ultima_compra: Optional[date] = None
    fornecedor: Optional[str] = None


class InsumoMovimentacaoCreate(BaseModel):
    tipo: str = Field(..., description="entrada | saida | ajuste")
    quantidade: float = Field(..., gt=0)
    valor_total: Optional[float] = Field(None, ge=0, description="Valor pago na entrada (CMV)")
    data_movimento: Optional[date] = None
    observacao: Optional[str] = None


class InsumoMovimentacaoOut(BaseModel):
    id: int
    id_insumo: int
    tipo: str
    quantidade: float
    valor_total: Optional[float] = None
    preco_unitario: Optional[float] = None
    saldo_quantidade: float
    data_movimento: date
    observacao: Optional[str] = None

    class Config:
        orm_mode = True

class InsumoInDBBase(InsumoBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

class Insumo(InsumoInDBBase):
    pass

class InsumoComUsos(InsumoInDBBase):
    total_usos: int = 0
    quantidade_total_usada: float = 0
    valor_total_usado: float = 0