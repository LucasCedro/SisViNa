from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class TesteSementesBase(BaseModel):
    id_lote_sementes: int
    data_teste: date
    tipo_teste: str
    metodologia: Optional[str] = None
    repeticoes: int = 1
    sementes_avaliadas: Optional[int] = None
    percentual_resultado: float = Field(..., ge=0, le=100)
    observacoes: Optional[str] = None


class TesteSementesCreate(TesteSementesBase):
    pass


class TesteSementesUpdate(BaseModel):
    data_teste: Optional[date] = None
    tipo_teste: Optional[str] = None
    metodologia: Optional[str] = None
    repeticoes: Optional[int] = None
    sementes_avaliadas: Optional[int] = None
    percentual_resultado: Optional[float] = Field(None, ge=0, le=100)
    observacoes: Optional[str] = None


class TesteSementesOut(BaseModel):
    id: int
    id_lote_sementes: int
    codigo_lote: str
    id_arvore_matriz: int
    matriz_nome: str
    id_especie: Optional[int] = None
    especie_nome: Optional[str] = None
    data_teste: date
    tipo_teste: str
    metodologia: Optional[str] = None
    repeticoes: int
    sementes_avaliadas: Optional[int] = None
    percentual_resultado: float
    observacoes: Optional[str] = None
    id_funcionario: int
    funcionario_nome: str
    data_registro: datetime
    taxa_germinacao_especie_media: Optional[float] = None

    class Config:
        orm_mode = True
