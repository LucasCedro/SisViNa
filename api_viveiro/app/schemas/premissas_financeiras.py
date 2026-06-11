from typing import List, Optional

from pydantic import BaseModel, Field, validator


class PremissaBase(BaseModel):
    chave: str = Field(..., max_length=60)
    nome: str = Field(..., max_length=120)
    descricao: Optional[str] = None
    natureza: str = "CUSTO"
    tipo_calculo: str = Field(
        ...,
        description="insumo_medio | por_muda | por_lote | mensal | percentual_receita",
    )
    unidade: Optional[str] = None
    valor: float = 0
    quantidade: Optional[float] = None
    id_insumo: Optional[int] = None
    ordem: int = 0
    ativo: bool = True

    @validator("natureza")
    def validate_natureza(cls, v):
        u = (v or "").upper()
        if u not in ("CUSTO", "DESPESA"):
            raise ValueError("natureza deve ser CUSTO ou DESPESA")
        return u

class PremissaCreate(PremissaBase):
    pass


class PremissaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    natureza: Optional[str] = None
    tipo_calculo: Optional[str] = None
    unidade: Optional[str] = None
    valor: Optional[float] = None
    quantidade: Optional[float] = None
    id_insumo: Optional[int] = None
    ordem: Optional[int] = None
    ativo: Optional[bool] = None

    @validator("valor", pre=True)
    def valor_vazio_como_zero(cls, v):
        if v is None or v == "":
            return 0.0
        return v

    @validator("quantidade", pre=True)
    def quantidade_vazia_como_nulo(cls, v):
        if v is None or v == "":
            return None
        return v


class PremissaOut(PremissaBase):
    id: int
    insumo_nome: Optional[str] = None
    preco_medio_insumo: Optional[float] = None

    class Config:
        orm_mode = True


class CusteioLoteDetalheOut(BaseModel):
    custo_sementes: float = 0
    custo_insumos: float = 0
    custo_indireto: float = 0
    custo_total: float = 0
    custo_unitario_muda: Optional[float] = None
    itens_premissa: List[dict] = Field(default_factory=list)


class DespesasEstimadasOut(BaseModel):
    comissao_estimada: float = 0
    despesas_fixas_mes: float = 0
    premissas_despesa: List[PremissaOut] = Field(default_factory=list)
