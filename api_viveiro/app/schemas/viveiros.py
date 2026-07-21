"""Schemas de unidade viveiro."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.constants.viveiro_modo import VALID_MODOS_OPERACAO


class ViveiroOut(BaseModel):
    id: int
    nome: str
    slug: str
    modo_operacao: str
    modo_label: str
    ativo: bool
    data_cadastro: Optional[datetime] = None

    class Config:
        orm_mode = True


class ViveiroCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50, regex=r"^[a-z0-9\-]+$")
    modo_operacao: str
    id_empresa: int = Field(..., ge=1)

    @validator("modo_operacao")
    def validar_modo(cls, v: str) -> str:
        if v not in VALID_MODOS_OPERACAO:
            raise ValueError(f"modo_operacao deve ser um de: {sorted(VALID_MODOS_OPERACAO)}")
        return v


class ViveiroContextOut(BaseModel):
    viveiro_ativo: ViveiroOut
    viveiros: List[ViveiroOut]
    modulos_habilitados: List[str]
    modulos_nav_desabilitados: List[str]
    pode_selecionar_viveiro: bool
