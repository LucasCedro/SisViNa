# app/schemas/plantas.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from decimal import Decimal

class PlantaBase(BaseModel):
    id_especie: int
    id_canteiro: Optional[int] = None
    codigo_rastreio: Optional[str] = None
    data_plantio: Optional[date] = None
    data_germinacao: Optional[date] = None
    altura_atual: Optional[float] = None
    diametro_caule: Optional[float] = None
    coordenada_x: Optional[float] = None
    coordenada_y: Optional[float] = None
    status: Optional[str] = "SEMENTE"
    observacoes: Optional[str] = None
    preco_venda: Optional[float] = None

class PlantaCreate(PlantaBase):
    @validator('status')
    def validate_status(cls, v):
        allowed_status = ['SEMENTE', 'MUDA', 'JOVEM', 'ADULTA', 'VENDIDA', 'MORTA']
        if v not in allowed_status:
            raise ValueError(f'Status deve ser um dos seguintes: {", ".join(allowed_status)}')
        return v

class PlantaUpdate(BaseModel):
    id_especie: Optional[int] = None
    id_canteiro: Optional[int] = None
    codigo_rastreio: Optional[str] = None
    data_plantio: Optional[date] = None
    data_germinacao: Optional[date] = None
    altura_atual: Optional[float] = None
    diametro_caule: Optional[float] = None
    coordenada_x: Optional[float] = None
    coordenada_y: Optional[float] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None
    preco_venda: Optional[float] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_status = ['SEMENTE', 'MUDA', 'JOVEM', 'ADULTA', 'VENDIDA', 'MORTA']
            if v not in allowed_status:
                raise ValueError(f'Status deve ser um dos seguintes: {", ".join(allowed_status)}')
        return v

class PlantaInDBBase(PlantaBase):
    id: int
    custo_atual: float
    data_cadastro: datetime

    class Config:
        orm_mode = True

class Planta(PlantaInDBBase):
    pass

class PlantaWithEspecie(PlantaInDBBase):
    especie_nome: str = None
    nome_canteiro: str = None