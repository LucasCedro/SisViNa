# app/schemas/vendas.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, validator, Field, root_validator
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


class ItemVendaPorEspecieCreate(BaseModel):
    """Venda por quantidade — o backend escolhe as mudas expedíveis."""
    id_especie: int
    quantidade: int = Field(..., gt=0)
    valor_unitario: float
    desconto: Optional[float] = 0

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
    custo_unitario: Optional[float] = None
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
    tipo_operacao_fiscal: str = Field(
        "domestica",
        description="domestica | importacao — mudas de origem estrangeira no SN",
    )

    @validator("tipo_operacao_fiscal")
    def tipo_operacao_fiscal_ok(cls, v):
        v = (v or "domestica").lower()
        if v not in ("domestica", "importacao"):
            raise ValueError("tipo_operacao_fiscal deve ser domestica ou importacao")
        return v

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
    itens: Optional[List[ItemVendaCreate]] = None
    itens_por_especie: Optional[List[ItemVendaPorEspecieCreate]] = None

    @root_validator
    def itens_ou_por_especie(cls, values):
        itens = values.get("itens") or []
        por_especie = values.get("itens_por_especie") or []
        if bool(itens) == bool(por_especie):
            raise ValueError(
                "Informe itens (plantas) ou itens_por_especie (espécie + quantidade), não ambos."
            )
        return values

class VendaUpdate(BaseModel):
    forma_pagamento: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            # PAGO só via POST /vendas/{id}/aprovar (vendas.approve)
            allowed_status = ['PENDENTE', 'CANCELADO']
            if v not in allowed_status:
                raise ValueError(
                    f'Status deve ser um dos seguintes: {", ".join(allowed_status)}. '
                    'Para marcar como PAGO use o endpoint /aprovar.'
                )
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