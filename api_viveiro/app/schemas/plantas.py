# app/schemas/plantas.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.constants.estagios_producao import ESTAGIOS_VALIDOS


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
    estagio_producao: Optional[str] = "em_desenvolvimento"
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

    @validator("estagio_producao")
    def validate_estagio(cls, v):
        if v is not None and v not in ESTAGIOS_VALIDOS:
            raise ValueError(f'Estágio deve ser um de: {", ".join(ESTAGIOS_VALIDOS)}')
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
    estagio_producao: Optional[str] = None
    observacoes: Optional[str] = None
    preco_venda: Optional[float] = None

    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            allowed_status = ["SEMENTE", "MUDA", "JOVEM", "ADULTA", "VENDIDA", "MORTA"]
            if v not in allowed_status:
                raise ValueError(f'Status deve ser um dos seguintes: {", ".join(allowed_status)}')
        return v

    @validator("estagio_producao")
    def validate_estagio(cls, v):
        if v is not None and v not in ESTAGIOS_VALIDOS:
            raise ValueError(f'Estágio deve ser um de: {", ".join(ESTAGIOS_VALIDOS)}')
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
    """Agregado do estoque comercial (plantas em estagio apta_venda)."""

    id_especie: int
    nome_popular: Optional[str] = None
    nome_cientifico: str
    quantidade: int
    valor_unitario: float
    localizacao: Optional[str] = None
    status_predominante: Optional[str] = None
    estagio_comercial: str = "apta_venda"


class PlantaDisponivelVenda(BaseModel):
    """Muda expedível com rastreio de lote — usada no formulário de venda."""

    id: int
    id_especie: int
    codigo_rastreio: Optional[str] = None
    id_lote_sementes: Optional[int] = None
    codigo_lote: Optional[str] = None
    preco_venda: Optional[float] = None
    custo_atual: float = 0
    nome_canteiro: Optional[str] = None
    dias_rustificacao: Optional[int] = None
    rustificacao_ok: bool = True

    class Config:
        orm_mode = True


class AtualizarPrecoEspecie(BaseModel):
    preco_venda: float = Field(..., gt=0)
