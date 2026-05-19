# app/schemas/pragas.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal

# TipoPraga Schemas
class TipoPragaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    metodo_identificacao: Optional[str] = None

class TipoPragaCreate(TipoPragaBase):
    pass

class TipoPragaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    metodo_identificacao: Optional[str] = None

class TipoPragaInDBBase(TipoPragaBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

class TipoPraga(TipoPragaInDBBase):
    pass

# MetodoCombate Schemas
class MetodoCombateBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    produto: Optional[str] = None
    dosagem: Optional[str] = None
    metodo_aplicacao: Optional[str] = None
    tempo_carencia: Optional[int] = None
    eficacia: Optional[str] = None
    custo_unitario: Optional[float] = None

class MetodoCombateCreate(MetodoCombateBase):
    pass

class MetodoCombateUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    produto: Optional[str] = None
    dosagem: Optional[str] = None
    metodo_aplicacao: Optional[str] = None
    tempo_carencia: Optional[int] = None
    eficacia: Optional[str] = None
    custo_unitario: Optional[float] = None

class MetodoCombateInDBBase(MetodoCombateBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

class MetodoCombate(MetodoCombateInDBBase):
    pass

# PragaPlanta Schemas
class PragaPlantaBase(BaseModel):
    id_planta: int
    id_tipo_praga: int
    data_identificacao: date
    nivel_infestacao: str
    observacoes: Optional[str] = None

class PragaPlantaCreate(PragaPlantaBase):
    @validator('nivel_infestacao')
    def validate_nivel_infestacao(cls, v):
        allowed_levels = ['BAIXO', 'MEDIO', 'ALTO', 'CRITICO']
        if v not in allowed_levels:
            raise ValueError(f'Nível de infestação deve ser um dos seguintes: {", ".join(allowed_levels)}')
        return v

class PragaPlantaUpdate(BaseModel):
    data_identificacao: Optional[date] = None
    nivel_infestacao: Optional[str] = None
    observacoes: Optional[str] = None

    @validator('nivel_infestacao')
    def validate_nivel_infestacao(cls, v):
        if v is not None:
            allowed_levels = ['BAIXO', 'MEDIO', 'ALTO', 'CRITICO']
            if v not in allowed_levels:
                raise ValueError(f'Nível de infestação deve ser um dos seguintes: {", ".join(allowed_levels)}')
        return v

class PragaPlantaInDBBase(PragaPlantaBase):
    id: int
    data_registro: datetime

    class Config:
        orm_mode = True

class PragaPlanta(PragaPlantaInDBBase):
    pass

class PragaPlantaDetalhe(PragaPlantaInDBBase):
    tipo_praga: TipoPraga
    planta_codigo: str
    especie_nome: str
    total_combates: int = 0

# CombateRealizado Schemas
class CombateRealizadoBase(BaseModel):
    id_praga_planta: int
    id_metodo_combate: int
    id_funcionario: int
    data_aplicacao: datetime
    quantidade_aplicada: Optional[float] = None
    custo_total: Optional[float] = None
    eficacia_observada: Optional[str] = None
    observacoes: Optional[str] = None

class CombateRealizadoCreate(CombateRealizadoBase):
    pass

class CombateRealizadoUpdate(BaseModel):
    data_aplicacao: Optional[datetime] = None
    quantidade_aplicada: Optional[float] = None
    custo_total: Optional[float] = None
    eficacia_observada: Optional[str] = None
    observacoes: Optional[str] = None

class CombateRealizadoInDBBase(CombateRealizadoBase):
    id: int
    data_registro: datetime

    class Config:
        orm_mode = True

class CombateRealizado(CombateRealizadoInDBBase):
    pass

class CombateRealizadoDetalhe(CombateRealizadoInDBBase):
    metodo_combate: MetodoCombate
    funcionario_nome: str
    planta_codigo: str
    tipo_praga_nome: str

