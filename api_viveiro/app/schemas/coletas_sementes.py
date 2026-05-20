from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ColetaSementesBase(BaseModel):
    id_arvore_matriz: int
    data_coleta: date
    quantidade_sementes: int = Field(..., gt=0)
    observacoes: Optional[str] = None


class ColetaSementesCreate(ColetaSementesBase):
    gerar_lote: bool = True


class ColetaSementesUpdate(BaseModel):
    data_coleta: Optional[date] = None
    quantidade_sementes: Optional[int] = Field(None, gt=0)
    observacoes: Optional[str] = None


class ColetaSementesOut(BaseModel):
    id: int
    id_arvore_matriz: int
    matriz_nome: str
    id_especie: int
    especie_nome: Optional[str] = None
    id_funcionario: int
    funcionario_nome: str
    data_coleta: date
    quantidade_sementes: int
    observacoes: Optional[str] = None
    data_registro: datetime
    lotes: List[Any] = []

    class Config:
        orm_mode = True
