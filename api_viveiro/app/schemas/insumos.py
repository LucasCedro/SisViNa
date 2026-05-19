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
    data_ultima_compra: Optional[date] = None
    fornecedor: Optional[str] = None

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