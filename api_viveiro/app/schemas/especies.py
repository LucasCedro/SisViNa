# app/schemas/especies.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class EspecieBase(BaseModel):
    nome_cientifico: str
    nome_popular: Optional[str] = None
    familia: Optional[str] = None
    descricao: Optional[str] = None
    tempo_germinacao: Optional[int] = None
    tempo_crescimento: Optional[int] = None
    altura_maxima: Optional[float] = None

class EspecieCreate(EspecieBase):
    pass

class EspecieUpdate(BaseModel):
    nome_cientifico: Optional[str] = None
    nome_popular: Optional[str] = None
    familia: Optional[str] = None
    descricao: Optional[str] = None
    tempo_germinacao: Optional[int] = None
    tempo_crescimento: Optional[int] = None
    altura_maxima: Optional[float] = None

class EspecieInDBBase(EspecieBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

class Especie(EspecieInDBBase):
    pass

class EspecieWithPlantasCount(EspecieInDBBase):
    total_plantas: int = 0