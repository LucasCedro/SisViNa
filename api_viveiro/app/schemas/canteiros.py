# app/schemas/canteiros.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class CanteiroBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    area_total: Optional[float] = None
    localizacao: Optional[str] = None
    tipo_solo: Optional[str] = None
    tipo_local: Optional[str] = "canteiro"
    ativo: Optional[bool] = True

class CanteiroCreate(CanteiroBase):
    pass

class CanteiroUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    area_total: Optional[float] = None
    localizacao: Optional[str] = None
    tipo_solo: Optional[str] = None
    tipo_local: Optional[str] = None
    ativo: Optional[bool] = None

class CanteiroInDBBase(CanteiroBase):
    id: int
    data_criacao: datetime

    class Config:
        orm_mode = True

class Canteiro(CanteiroInDBBase):
    pass

class CanteiroWithOcupacao(CanteiroInDBBase):
    total_plantas: int = 0
    total_sementes: int = 0
    total_mudas: int = 0
    total_jovens: int = 0
    total_adultas: int = 0
    percentual_ocupacao: float = 0.0