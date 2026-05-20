# app/schemas/plantas.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


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
    origem: Optional[str] = "semeadura"
    observacoes: Optional[str] = None
    preco_venda: Optional[float] = None
    id_lote_sementes: Optional[int] = None


class PlantaCreate(PlantaBase):
    @validator("status")
    def validate_status(cls, v):
        allowed_status = ["SEMENTE", "MUDA", "JOVEM", "ADULTA", "VENDIDA", "MORTA"]
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

    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            allowed_status = ["SEMENTE", "MUDA", "JOVEM", "ADULTA", "VENDIDA", "MORTA"]
            if v not in allowed_status:
                raise ValueError(f'Status deve ser um dos seguintes: {", ".join(allowed_status)}')
        return v


class PlantaInDBBase(PlantaBase):
    id: int
    custo_atual: float
    origem: str = "semeadura"
    data_cadastro: datetime

    class Config:
        orm_mode = True


class Planta(PlantaInDBBase):
    pass


class PlantaWithEspecie(PlantaInDBBase):
    especie_nome: Optional[str] = None
    nome_canteiro: Optional[str] = None


class EstoqueResumoItem(BaseModel):
    id_especie: int
    nome_popular: Optional[str] = None
    nome_cientifico: str
    quantidade: int
    valor_unitario: float
    localizacao: Optional[str] = None
    status_predominante: Optional[str] = None


class AtualizarPrecoEspecie(BaseModel):
    preco_venda: float = Field(..., gt=0)
