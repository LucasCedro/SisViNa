from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, validator


class LancamentoFinanceiroBase(BaseModel):
    tipo: str
    descricao: str
    categoria: str
    data_lancamento: date
    valor: float
    forma_pagamento: Optional[str] = None
    observacoes: Optional[str] = None

    @validator("tipo")
    def validate_tipo(cls, v):
        if v not in ("CAPEX", "OPEX"):
            raise ValueError("tipo deve ser CAPEX ou OPEX")
        return v


class LancamentoFinanceiroCreate(LancamentoFinanceiroBase):
    pass


class LancamentoFinanceiroUpdate(BaseModel):
    tipo: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    data_lancamento: Optional[date] = None
    valor: Optional[float] = None
    forma_pagamento: Optional[str] = None
    observacoes: Optional[str] = None

    @validator("tipo")
    def validate_tipo(cls, v):
        if v is not None and v not in ("CAPEX", "OPEX"):
            raise ValueError("tipo deve ser CAPEX ou OPEX")
        return v


class LancamentoFinanceiro(LancamentoFinanceiroBase):
    id: int
    id_funcionario: Optional[int] = None
    data_registro: datetime

    class Config:
        orm_mode = True


class ResumoFinanceiroOut(BaseModel):
    total_capex: float = 0
    total_opex: float = 0
    receita_vendas_paga: float = 0
    receita_mes_atual: float = 0
    custo_atividades: float = 0
    custo_fitossanidade: float = 0
    custo_estoque_mudas: float = 0
    custo_operacional_total: float = 0
    mudas_ativas: int = 0
    custo_por_muda: float = 0
    resultado_liquido: float = 0


class DashboardResumoOut(BaseModel):
    especies: int = 0
    matrizes: int = 0
    coletas: int = 0
    mudas_ativas: int = 0
    lotes_ativos: int = 0
    vendas_mes: float = 0
    receita_total_paga: float = 0
    custo_operacional: float = 0
    plantas_por_especie: List[dict] = []
    ocupacao_canteiros: List[dict] = []
