from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ColetaSementesBase(BaseModel):
    id_arvore_matriz: int
    data_coleta: date
    quantidade_sementes: int = Field(..., gt=0)
    sementes_reservadas_teste: int = Field(0, ge=0)
    horas_campo: Optional[float] = Field(None, ge=0, description="Horas de mão de obra em campo")
    observacoes: Optional[str] = None


class ColetaSementesCreate(ColetaSementesBase):
    gerar_lote: bool = True


class ColetaSementesUpdate(BaseModel):
    data_coleta: Optional[date] = None
    quantidade_sementes: Optional[int] = Field(None, gt=0)
    sementes_reservadas_teste: Optional[int] = Field(None, ge=0)
    horas_campo: Optional[float] = Field(None, ge=0)
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
    sementes_reservadas_teste: int = 0
    horas_campo: Optional[float] = None
    custo_campo_total: Optional[float] = None
    observacoes: Optional[str] = None
    data_registro: datetime
    lotes: List[Any] = []

    class Config:
        orm_mode = True


class CustoCampoReferenciaOut(BaseModel):
    valor_hora: float = 0
    premissa_ativa: bool = False
    nome: str = "Mão de obra de coleta"

    class Config:
        orm_mode = True
