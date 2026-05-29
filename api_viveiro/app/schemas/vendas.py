# app/schemas/vendas.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, validator, Field
from decimal import Decimal

# ItemVenda Schemas
class ItemVendaBase(BaseModel):
    id_planta: int
    quantidade: int = Field(..., gt=0)
    valor_unitario: float
    desconto: Optional[float] = 0
    data_entrega: Optional[date] = None
    status_entrega: Optional[str] = "PENDENTE"

    @validator('status_entrega')
    def validate_status_entrega(cls, v):
        allowed_status = ['PENDENTE', 'SEPARADO', 'ENTREGUE', 'CANCELADO']
        if v not in allowed_status:
            raise ValueError(f'Status de entrega deve ser um dos seguintes: {", ".join(allowed_status)}')
        return v

class ItemVendaCreate(ItemVendaBase):
    pass

class ItemVendaUpdate(BaseModel):
    quantidade: Optional[int] = Field(None, gt=0)
    valor_unitario: Optional[float] = None
    desconto: Optional[float] = None
    data_entrega: Optional[date] = None
    status_entrega: Optional[str] = None

    @validator('status_entrega')
    def validate_status_entrega(cls, v):
        if v is not None:
            allowed_status = ['PENDENTE', 'SEPARADO', 'ENTREGUE', 'CANCELADO']
            if v not in allowed_status:
                raise ValueError(f'Status de entrega deve ser um dos seguintes: {", ".join(allowed_status)}')
        return v

class ItemVendaInDBBase(ItemVendaBase):
    id: int
    id_venda: int
    valor_total: float
    data_registro: datetime

    class Config:
        orm_mode = True

class ItemVenda(ItemVendaInDBBase):
    pass

class ItemVendaDetalhe(ItemVendaInDBBase):
    codigo_planta: str
    nome_especie: str
    status_planta: str

# Venda Schemas
class VendaBase(BaseModel):
    id_comprador: int
    id_funcionario: int
    data_venda: datetime
    forma_pagamento: Optional[str] = None
    status: str = "PENDENTE"
    observacoes: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        allowed_status = ['PENDENTE', 'PAGO', 'CANCELADO']
        if v not in allowed_status:
            raise ValueError(f'Status deve ser um dos seguintes: {", ".join(allowed_status)}')
        return v

    @validator('data_venda')
    def data_venda_sem_timezone(cls, v: datetime) -> datetime:
        """Coluna TIMESTAMP WITHOUT TIME ZONE — asyncpg não aceita datetime aware."""
        if v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v

class VendaCreate(VendaBase):
    itens: List[ItemVendaCreate]

class VendaUpdate(BaseModel):
    forma_pagamento: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_status = ['PENDENTE', 'PAGO', 'CANCELADO']
            if v not in allowed_status:
                raise ValueError(f'Status deve ser um dos seguintes: {", ".join(allowed_status)}')
        return v

class VendaInDBBase(VendaBase):
    id: int
    valor_total: float
    data_registro: datetime

    class Config:
        orm_mode = True

class Venda(VendaInDBBase):
    pass


class VendaList(VendaInDBBase):
    comprador_nome: Optional[str] = None
    funcionario_nome: Optional[str] = None
    total_itens: int = 0


class VendaDetalhe(VendaInDBBase):
    comprador_nome: str
    funcionario_nome: str
    itens: List[ItemVendaDetalhe]
    avisos: List[str] = []