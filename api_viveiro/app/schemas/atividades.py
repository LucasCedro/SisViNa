# app/schemas/atividades.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal

# TipoAtividade Schemas
class TipoAtividadeBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    gera_custo: Optional[bool] = False

class TipoAtividadeCreate(TipoAtividadeBase):
    pass

class TipoAtividadeUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    gera_custo: Optional[bool] = None

class TipoAtividadeInDBBase(TipoAtividadeBase):
    id: int

    class Config:
        orm_mode = True

class TipoAtividade(TipoAtividadeInDBBase):
    pass

# Insumo Schemas
class InsumoBase(BaseModel):
    nome: str
    tipo: str
    descricao: Optional[str] = None
    unidade_medida: Optional[str] = None
    quantidade_estoque: Optional[float] = 0
    preco_unitario: Optional[float] = 0
    data_ultima_compra: Optional[datetime] = None
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
    data_ultima_compra: Optional[datetime] = None
    fornecedor: Optional[str] = None

class InsumoInDBBase(InsumoBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

class Insumo(InsumoInDBBase):
    pass

# InsumoAtividade Schemas
class InsumoAtividadeBase(BaseModel):
    id_atividade: int
    id_insumo: int
    quantidade_usada: float
    custo_total: Optional[float] = None

class InsumoAtividadeCreate(InsumoAtividadeBase):
    pass

class InsumoAtividadeUpdate(BaseModel):
    quantidade_usada: Optional[float] = None
    custo_total: Optional[float] = None

class InsumoAtividadeInDBBase(InsumoAtividadeBase):
    id: int
    data_registro: datetime

    class Config:
        orm_mode = True

class InsumoAtividade(InsumoAtividadeInDBBase):
    pass

class InsumoAtividadeDetalhe(InsumoAtividadeInDBBase):
    insumo: Insumo

# Atividade Schemas
class AtividadeBase(BaseModel):
    id_tipo_atividade: int
    id_planta: int
    id_funcionario: int
    data_atividade: datetime
    descricao: Optional[str] = None
    custo_atividade: Optional[float] = 0
    observacoes: Optional[str] = None

class AtividadeCreate(AtividadeBase):
    insumos: Optional[List[InsumoAtividadeCreate]] = None

class AtividadeUpdate(BaseModel):
    id_tipo_atividade: Optional[int] = None
    data_atividade: Optional[datetime] = None
    descricao: Optional[str] = None
    custo_atividade: Optional[float] = None
    observacoes: Optional[str] = None

class AtividadeInDBBase(AtividadeBase):
    id: int
    data_registro: datetime

    class Config:
        orm_mode = True

class Atividade(AtividadeInDBBase):
    pass

class AtividadeDetalhe(AtividadeInDBBase):
    tipo_atividade: TipoAtividade
    insumos_utilizados: List[InsumoAtividadeDetalhe] = []

class AtividadeCompleta(AtividadeInDBBase):
    tipo_atividade_nome: str
    funcionario_nome: str
    planta_codigo: str
    especie_nome: str
    total_insumos: int = 0